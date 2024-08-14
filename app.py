from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://root:example@mongo:27017/', serverSelectionTimeoutMS=5000)
db = client.flaskdb
users_collection = db.users

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    user_data = request.form
    name = user_data.get('name')
    email = user_data.get('email')
    if not name or not email:
        return render_template('index.html', message='Please provide both name and email.')
    
    users_collection.insert_one({'name': name, 'email': email})
    return render_template('index.html', message='User added successfully.')

@app.route('/users')
def get_users():
    users = list(users_collection.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
