import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

def init_jwt(app):
    """Initialize JWT configuration in Flask app"""
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")  # Load secret key from .env
    jwt = JWTManager(app)
    return jwt


# # Function to generate JWT token
# def generate_token(user_id):
#     access_token = create_access_token(identity=user_id)
#     return access_token

# Function to generate JWT token with 1-day expiry
def generate_token(user_id):
    return create_access_token(identity=user_id, expires_delta=timedelta(days=1))