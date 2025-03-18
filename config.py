from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")
TWILIO_ACCOUNT_SID=os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_PHONE_NUMBER=os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_AUTH_TOKEN=os.getenv("TWILIO_AUTH_TOKEN")

