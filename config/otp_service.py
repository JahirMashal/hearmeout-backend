import os
import random
import string
# import time
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

# MongoDB Connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["dev2hearmeout"]
otp_collection = db["otp_attempts"]

# Twilio Credentials (Store in .env file)
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=6))

# def send_sms(phone, otp):
#     """Simulate sending an SMS with the OTP."""
#     print(f"OTP for {phone}: {otp}")  # Replace with actual SMS API
#     return True

def send_sms(phone, otp):
    """Send an OTP via SMS using Twilio API."""
    try:
        message = twilio_client.messages.create(
            body=f"Your OTP for HearMeOut is: {otp}. Valid for 10 minutes.",
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        return message.sid  # Returns Twilio message ID if successful
    except Exception as e:
        print(f"Twilio Error: {e}")
        return None

def send_otp(phone):
    """Generate and send OTP, enforcing attempt limits."""
    user_attempt = otp_collection.find_one({"phone": phone})
    now = datetime.now(timezone.utc)
    
    # Check if the user has exceeded the daily limit (3 OTP requests per day)
    if user_attempt and user_attempt["otp_requests"] >= 3:
        if now < user_attempt["reset_time"]:
            return {"message": "Your attempt limit has been exhausted. Please try tomorrow."}, 429
        else:
            otp_collection.delete_one({"phone": phone})  # Reset attempts
    
    # Generate new OTP and store attempt count
    otp = generate_otp()
    send_sms(phone, otp)
    if not send_sms(phone, otp):
        return {"message": "Failed to send OTP. Please try again."}, 500
    
    otp_data = {
        "phone": phone,
        "otp": otp,
        "otp_requests": 1 if not user_attempt else user_attempt["otp_requests"] + 1,
        "wrong_attempts": 0,
        "expires_at": now + timedelta(minutes=10),  # OTP expires in 10 minutes
        "reset_time": (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)  # Reset next day
        # "reset_time": now.replace(hour=0, minute=0, second=0) + timedelta(days=1)  # Reset next day
    }
    
    otp_collection.update_one({"phone": phone}, {"$set": otp_data}, upsert=True)
    return {"message": "OTP sent successfully."}, 200

def verify_otp(phone, user_otp):
    """Verify OTP with wrong attempt limits."""
    user_attempt = otp_collection.find_one({"phone": phone})
    now = datetime.now(timezone.utc)
    
    if not user_attempt:
        return {"message": "No OTP request found for this number."}, 400
    
    # Check if OTP expired
    if now > user_attempt["expires_at"]:
        otp_collection.delete_one({"phone": phone})
        return {"message": "OTP expired. Request a new one."}, 400
    
    # Check if user exceeded wrong attempts (3 wrong attempts → 10 min block)
    if user_attempt["wrong_attempts"] >= 3:
        return {"message": "Too many wrong attempts. Try again after 10 minutes."}, 429
    
    # Validate OTP
    if user_otp == user_attempt["otp"]:
        otp_collection.delete_one({"phone": phone})  # OTP used, remove from DB
        return {"message": "OTP verified successfully."}, 200
    else:
        otp_collection.update_one({"phone": phone}, {"$inc": {"wrong_attempts": 1}})
        return {"message": "Incorrect OTP. Please try again."}, 400
