import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
    
    # Gmail API settings
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'],
        # 'https://www.googleapis.com/auth/gmail.send'  # Add this line
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'