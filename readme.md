Below is the `README.md` code formatted and ready to be pasted into your GitHub repository:

```markdown
# Docker & MongoDB Setup Guide 🐳🍃

This guide provides instructions on setting up a MongoDB instance using Docker, connecting to it, and managing the containers with Docker Compose.

## 1. Create Docker Network 🌐

To create a Docker network, use the following command:

```bash
docker network create m-network
```

Output:
```
047b67dedf113b602d88ced383b911568adc51d3b0f044d2caac0ae810de8175
```

## 2. Set Up MongoDB 🛠️

You can set up a MongoDB instance using the following Docker command:

```bash
docker run -d --network m-network --name raj-mongo \
    -e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
    -e MONGO_INITDB_ROOT_PASSWORD=secret \
    mongo
```

For more details, refer to the [MongoDB Docker Hub page](https://hub.docker.com/_/mongo).

## 3. Get Docker IP Address 📡

To retrieve the Docker IP address, use the following command:

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' raj-mongo
```

## 4. Debug MongoDB Connection 🐛

If you need to debug the MongoDB connection using MongoDB Scanner, you can install `mongosh` and run the following command:

```bash
mongosh "mongodb://mongoadmin:secret@localhost:27017/?authSource=admin"
```

## 5. Manage Containers with Docker Compose 🧩

To start the containers with Docker Compose:

```bash
docker-compose -f mongo-docker-compose.yml up -d
```

To stop and remove the containers:

```bash
docker-compose -f mongo-docker-compose.yml down
```

### Example Docker Compose Down Output

```bash
$ docker-compose -f mongo-docker-compose.yml down
time="2024-08-14T23:44:50+05:30" level=warning msg="D:\\SingamsHUB\\app\\mongo-docker-compose.yml: `version` is obsolete"
 Container mongo-express  Stopping
 Container flask-app  Stopping
 Container mongo-express  Stopped
 Container mongo-express  Removing
 Container mongo-express  Removed
 Container flask-app  Stopped
 Container flask-app  Removing
 Container flask-app  Removed
 Container mongo  Stopping
 Container mongo  Stopped
 Container mongo  Removing
 Container mongo  Removed
 Network app_default  Removing
 Network app_default  Removed
```

---

You can paste this `README.md` code directly into your GitHub repository's README file.