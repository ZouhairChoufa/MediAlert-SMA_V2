import os
from dotenv import load_dotenv
# Load .env from project root if present

load_dotenv()

# Also attempt to load config/.env (common repo layout) so keys defined there are picked up

_config_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env')

if os.path.exists(_config_env):

    load_dotenv(_config_env)

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
    
    # Infermedica Configuration
    INFERMEDICA_APP_ID = os.environ.get('INFERMEDICA_APP_ID')
    INFERMEDICA_APP_KEY = os.environ.get('INFERMEDICA_APP_KEY')
    INFERMEDICA_API_URL = os.environ.get('INFERMEDICA_API_URL') or 'https://api.infermedica.com/v3'