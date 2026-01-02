from flask import Flask
from app.config_settings import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Context processor for Firebase config
    @app.context_processor
    def inject_firebase_config():
        return {
            'firebase_api_key': os.getenv('FIREBASE_API_KEY'),
            'firebase_auth_domain': os.getenv('FIREBASE_AUTH_DOMAIN'),
            'firebase_database_url': os.getenv('FIREBASE_DATABASE_URL'),
            'firebase_project_id': os.getenv('FIREBASE_PROJECT_ID'),
            'firebase_storage_bucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
            'firebase_messaging_sender_id': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            'firebase_app_id': os.getenv('FIREBASE_APP_ID'),
            'firebase_measurement_id': os.getenv('FIREBASE_MEASUREMENT_ID')
        }
    
    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.api import api_bp
    from app.routes.chat import chat_bp
    from app.routes.auth import auth_bp
    from app.routes.patient import patient_bp
    from app.routes.admin import admin_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.emergency_chat import emergency_chat_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(emergency_chat_bp)
    
    return app