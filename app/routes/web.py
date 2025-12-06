from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.location_service import LocationService
from app.routes.api import alert_storage

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    return render_template('index.html')

@web_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@web_bp.route('/alert')
def alert_form():
    # Auto-fill location using IP geolocation
    location_service = LocationService()
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    location_data = location_service.get_location_by_ip(user_ip)
    
    return render_template('alert_form.html', location_data=location_data)

@web_bp.route('/tracking/<alert_id>')
def tracking(alert_id):
    """Tracking page for emergency alert"""
    if alert_id in alert_storage:
        alert_data = alert_storage[alert_id]
        return render_template('tracking.html', 
                             alert_id=alert_id,
                             patient=alert_data['patient'])
    return redirect(url_for('web.dashboard'))