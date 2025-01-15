import streamlit as st
import boto3
from PIL import Image
import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile

# Initialize AWS clients
textract_client = boto3.client('textract', region_name='ap-south-1')  # Specify your region
bedrock_client = boto3.client("bedrock-runtime", region_name="ap-south-1")

def extract_text_from_image(image_file):
    # Open the image file
    image = Image.open(image_file)
    
    # Convert image to RGB (if it has an alpha channel or other unsupported color model)
    image = image.convert("RGB")
    
    # Convert the image to bytes for AWS Textract
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Ensure that the byte array is not empty
    if not img_byte_arr:
        raise ValueError("Uploaded image is empty.")
    
    # Call AWS Textract to analyze the document (Corrected FeatureTypes)
    try:
        response = textract_client.detect_document_text(
            Document={'Bytes': img_byte_arr}
        )
    except Exception as e:
        st.error(f"Error calling AWS Textract: {e}")
        return ""

    # Extract text from response
    extracted_text = ''
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            extracted_text += item['Text'] + '\n'
    
    return extracted_text

def generate_terraform_code(extracted_services):
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # Add a more detailed prompt that asks for step-by-step instructions and a complete setup
    prompt = f"""
    Step by step, create Terraform files for the following AWS services: {', '.join(extracted_services)}. 
    The Terraform code should follow this structure:

    1. **Repository Structure**:
        - Create a GitHub repository for Terraform code.
        - Add all the necessary files and directories for the project.
        - Organize the modules in a clean structure (e.g., `modules/s3`, `modules/lambda`).
        - Include `main.tf`, `variables.tf`, `terraform.tfstate`, `vars/dev.tfvars`, `vars/prod.tfvars`, and any necessary module files.

    2. **Complete Terraform Code**:
        - Provide the content for `main.tf`, `variables.tf`, and modules for each of the extracted services (e.g., S3, Lambda).
        - Use modules for each service to make the code more modular and reusable.

    3. **Deploying the Code to AWS**:
        - Step-by-step guide for deploying the Terraform project to AWS.
        - Commands for initializing, planning, applying, and managing state.

    4. **GitHub Repository Creation**:
        - Create a new GitHub repository:
          - Run `git init` to initialize the repo.
          - Use `git remote add origin <repository-url>` to link to a remote repo.
          - Push your changes using `git push -u origin master`.
          - Make sure to add a `.gitignore` for Terraform files (`*.tfstate`, etc.).
        - Commit and push the code to GitHub.

    5. **CI/CD Pipeline Creation**:
        - Create a CI/CD pipeline to automate the Terraform deployments to AWS:
          - Use AWS CodePipeline to automate deployments triggered from GitHub.
          - Set up AWS CodeBuild with a `buildspec.yml` file to run Terraform commands (`init`, `plan`, `apply`).
          - Configure AWS IAM roles to allow Terraform to access and manage AWS resources securely.
          - Use AWS Lambda or other triggers to automate deployment to production once a change is detected in the GitHub repo.

    The services to be used are: {', '.join(extracted_services)}.
    """
    
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    request = json.dumps(native_request)

    try:
        streaming_response = bedrock_client.invoke_model_with_response_stream(modelId=model_id, body=request)
    except Exception as e:
        st.error(f"Error invoking model: {e}")
        return ""

    # Initialize a buffer to accumulate the response content
    terraform_code = ""
    for event in streaming_response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            terraform_code += chunk["delta"].get("text", "")
    
    return terraform_code

# Function to generate a PDF document with the full Terraform setup instructions
def generate_pdf(content):
    # Create a temporary file to store the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter
    
    # Set up the PDF with the title and content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, height - 40, "Terraform Setup Guide")

    c.setFont("Helvetica", 10)
    text_object = c.beginText(30, height - 60)
    text_object.setFont("Helvetica", 10)
    text_object.setTextOrigin(30, height - 60)

    # Split the content into multiple lines
    lines = content.split("\n")
    line_height = 12  # Adjust based on font size
    y_position = height - 60
    
    # Add content to the PDF and handle page breaks
    for line in lines:
        if y_position < 40:  # If content goes beyond the page
            c.showPage()
            c.setFont("Helvetica", 10)
            y_position = height - 60
        text_object.textLine(line)
        y_position -= line_height
    
    c.drawText(text_object)
    c.showPage()
    c.save()
    
    return temp_file.name

# Streamlit user interface
st.title("AWS Textract and Terraform Code Generator")

# Upload image or document
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Extract text from uploaded file
    with st.spinner("Extracting text..."):
        try:
            text = extract_text_from_image(uploaded_file)
            if text:
                # Show extracted text
                st.subheader("Extracted Text:")
                st.text_area("Text", text, height=500)  # Adjusted height

                # Extract AWS service names from the text
                aws_services = ["ec2", "s3", "lambda", "rds", "dynamodb", "sns", "sqs", "iam", "vpc", "cloudfront", "cloudwatch", "ecs", "eks", "route 53", "elastic beanstalk", "elasticache", "codebuild", "codedeploy", "codepipeline", "cloudformation", "cloudtrail", "kms", "secrets manager", "acm", "waf", "guardduty", "macie", "athena", "redshift", "quicksight", "appsync", "kinesis", "step functions", "appstream", "iot core", "sagemaker", "comprehend", "rekognition", "textract", "translate", "personalize", "forecast", "pinpoint", "cloud9", "workspaces", "workdocs", "workmail", "fsx", "storage gateway", "efs", "datasync", "glue", "migration hub", "snowball", "outposts", "aws elemental mediaconvert", "aws elemental mediapackage", "aws elemental mediastore", "aws elemental medialive", "aws elemental mediatailor", "timestream", "quantum ledger database", "lake formation", "elasticsearch service", "api gateway", "cognito", "lex", "polly", "transcribe", "rekognition", "dms", "mcs", "connect", "chime", "honeycode", "control tower", "audit manager", "well-architected tool", "amazon worklink", "macie", "fsx", "auto scaling", "elastic load balancing", "target groups", "aws backup", "aws batch", "secrets manager", "aws cost explorer", "aws license manager", "aws personal health dashboard", "aws marketplace", "aws budgets", "aws snowcone", "aws cloud map", "aws glue databrew", "amazon mq", "aws chatbot", "aws iot device defender", "aws iot analytics", "aws iot things graph", "aws elemental live", "aws elemental conductor", "aws systems manager", "aws license manager", "aws codestar", "aws snowmobile", "amazon elastic file system", "aws resource groups", "aws transfer for sftp", "aws amplify", "aws appconfig", "amazon inspector", "aws apprunner", "aws iq", "amazon eventbridge", "aws proton", "amazon elastic inference", "aws x-ray", "aws sso", "aws dms", "aws data exchange", "aws glue data catalog", "aws cloudtrail insights", "amazon cognito sync", "aws global accelerator", "aws security hub", "aws batch", "amazon textract", "amazon elastic inference", "amazon route 53 resolver", "aws systems manager session manager"]
                extracted_services = [service for service in aws_services if service in text.lower()]

                if extracted_services:
                    st.subheader("Extracted AWS Services:")
                    st.write(", ".join(extracted_services))

                    # Generate Terraform code based on the extracted services
                    with st.spinner("Generating Terraform code..."):
                        terraform_code = generate_terraform_code(extracted_services)
                        if terraform_code:
                            st.subheader("Generated Terraform Code:")
                            chunk_size = 2000  # Adjust based on output size
                            for i in range(0, len(terraform_code), chunk_size):
                                st.code(terraform_code[i:i+chunk_size], language="hcl")

                            # Generate PDF document
                            with st.spinner("Generating PDF..."):
                                pdf_path = generate_pdf(terraform_code)
                                
                                # Provide the download link for the PDF
                                with open(pdf_path, "rb") as f:
                                    st.download_button("Download PDF", f, file_name="terraform_setup_guide.pdf")
                        else:
                            st.warning("Failed to generate Terraform code.")
                else:
                    st.warning("No recognizable AWS services found in the image.")
            else:
                st.warning("No text found in the image.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
