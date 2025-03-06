import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token
from twilio.rest import Client
from config.jwt_auth import init_jwt
from connection import init_db

app = Flask(__name__)
CORS(app)

# Initialize MongoDB Connection and JWT
mongo = init_db(app)
jwt = init_jwt(app)
# jwt = init_jwt(app) # type: ignore



if __name__ == "__main__":
    app.run(debug=True)