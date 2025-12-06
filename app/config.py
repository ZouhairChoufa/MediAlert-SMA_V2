import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key'
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    ORS_API_KEY = os.environ.get('ORS_API_KEY')
    ABSTRACT_API_KEY = os.environ.get('ABSTRACT_API_KEY')
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH') or 'config/firebase-credentials.json'
    
    # Groq Configuration
    GROQ_MODEL = "llama-3.3-70b-versatile"
    
    # ORS Configuration
    ORS_BASE_URL = "https://api.openrouteservice.org"
    
    # Abstract API Configuration
    ABSTRACT_API_URL = "https://ipgeolocation.abstractapi.com/v1/"