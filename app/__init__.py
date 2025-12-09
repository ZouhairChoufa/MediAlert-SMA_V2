from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.api import api_bp
    from app.routes.chat import chat_bp
    from app.routes.auth import auth_bp
    from app.routes.patient import patient_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(admin_bp)
    
    return app