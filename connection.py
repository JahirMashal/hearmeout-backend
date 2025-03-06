import os
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI")

# def init_db(app):
#     app.config["MONGO_URI"] = MONGO_URI
#     mongo = PyMongo(app)
#     return mongo

def init_db(app):
    """Initialize MongoDB connection"""
    try:
        # MongoDB Atlas connection string
        MONGO_URI = os.getenv("MONGO_URI")  # Store in .env file for security

        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        
        # Select database (change to your actual database name)
        db = client["dev2hearmeout"]
        
        print("✅ MongoDB connected successfully!")
        return db
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        return None