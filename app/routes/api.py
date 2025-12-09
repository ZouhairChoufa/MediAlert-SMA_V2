from flask import Blueprint, request, jsonify, session
import threading
import uuid
import sys
import json
from datetime import datetime
from firebase_admin import firestore
from app.services.firebase_service import FirebaseService
from app.services.system_logs_service import SystemLogsService
from app.services.emergency_orchestrator import EmergencyOrchestrator
import asyncio
from app.services.geolocation import GeolocationService
from app.services.smart_dispatch import SmartDispatchEngine
from app.decorators import login_required

api_bp = Blueprint('api', __name__)

# Initialize services
firebase_service = FirebaseService()
alerts_collection = firebase_service.get_collection('alerts')
logs_service = SystemLogsService()
geolocation_service = GeolocationService()
smart_dispatch = SmartDispatchEngine()



@api_bp.route('/detect-ip-location', methods=['POST'])
def detect_ip_location():
    """Detect user location from IP address"""
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        location = geolocation_service.get_ip_location(ip_address)
        
        if location:
            return jsonify({
                'success': True,
                'location': location
            })
        return jsonify({'success': False, 'error': 'Could not detect location'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alert', methods=['POST'])
@login_required
def create_alert():
    """Create new emergency alert with smart dispatch"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['nom_prenom', 'age', 'sexe', 'symptomes']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Merge location sources
        gps = data.get('gps_coords')
        lat = float(data.get('lat')) if data.get('lat') else None
        lng = float(data.get('lng')) if data.get('lng') else None
        manual = {'address': data.get('localisation'), 'lat': lat, 'lng': lng}
        ip = geolocation_service.get_ip_location(request.remote_addr)
        
        location = geolocation_service.merge_all_location_sources(gps, manual, ip)
        
        # Validate location has coordinates
        if not location.get('lat') or not location.get('lng'):
            return jsonify({'error': 'Unable to determine location coordinates'}), 400
        
        # Smart dispatch (initial logic before CrewAI)
        emergency_level = int(data.get('emergency_level', 2))
        dispatch_result = smart_dispatch.dispatch_ambulance(
            float(location['lat']), float(location['lng']), emergency_level
        )
        
        # Generate alert ID
        alert_id = str(uuid.uuid4())[:8]
        
        # Store alert data in Firestore (flatten all nested objects)
        alert_data = {
            'patient': json.loads(json.dumps(data, default=str)),
            'location': json.loads(json.dumps(location, default=str)),
            'dispatch_info': json.dumps(dispatch_result, default=str),
            'status': 'processing',
            'logs': [],
            'username': session.get('user'),
            'created_at': datetime.utcnow().isoformat()
        }
        alerts_collection.document(alert_id).set(alert_data)
        
        # Log alert creation
        logs_service.log_event('alert_created', f'New alert created: {alert_id}', session.get('user'), {'alert_id': alert_id, 'patient': data.get('nom_prenom')})
        
        # Trigger async workflow in background
        username = session.get('user')
        def run_async_workflow():
            try:
                print(f"\n[ORCHESTRATOR] Starting workflow for alert {alert_id}", flush=True)
                orchestrator = EmergencyOrchestrator()
                asyncio.run(orchestrator.run_workflow(
                    alert_id,
                    float(location['lat']),
                    float(location['lng']),
                    emergency_level
                ))
                print(f"[ORCHESTRATOR] Workflow completed for alert {alert_id}", flush=True)
                logs_service.log_event('alert_completed', f'Alert workflow completed: {alert_id}', username, {'alert_id': alert_id})
            except Exception as e:
                alerts_collection.document(alert_id).update({
                    'status': 'ERROR',
                    'error': str(e)
                })
                print(f"[ERROR] Workflow failed: {e}", flush=True)
        
        thread = threading.Thread(target=run_async_workflow)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'alert_id': alert_id,
            'message': 'Alerte créée et traitement en cours',
            'dispatch': json.loads(json.dumps(dispatch_result, default=str))
        })
        
    except Exception as e:
        print(f"Error in create_alert: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alert/<alert_id>/data', methods=['GET'])
@login_required
def get_alert_data(alert_id):
    """Get alert data for tracking page with real-time updates"""
    doc = alerts_collection.document(alert_id).get()
    if doc.exists:
        data = doc.to_dict()
        # Return structured data for frontend
        return jsonify({
            'status': data.get('status', 'processing'),
            'logs': data.get('logs', []),
            'route_phase': data.get('route_phase'),
            'route_geometry': data.get('route_geometry'),
            'eta_minutes': data.get('eta_minutes'),
            'selected_hospital': data.get('selected_hospital'),
            'ambulance': data.get('ambulance'),
            'patient': data.get('patient'),
            'location': data.get('location'),
            'completed_at': data.get('completed_at'),
            'total_time_minutes': data.get('total_time_minutes')
        })
    return jsonify({'error': 'Alert not found'}), 404

@api_bp.route('/status/<alert_id>')
def get_alert_status(alert_id):
    """Get current status of an alert"""
    try:
        firebase_service = FirebaseService()
        alert_data = firebase_service.get_alert(alert_id)
        
        if not alert_data:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Mock route data for demo (would come from crew results)
        route_data = {
            'coordinates': [[33.5731, -7.5898], [33.5892, -7.6031]],
            'eta_minutes': 8
        }
        
        # Mock hospital data
        hospital_data = {
            'name': 'CHU Ibn Rochd',
            'service': 'Urgences',
            'distance_km': 2.5,
            'bed_number': 'A-12'
        }
        
        return jsonify({
            'alert': alert_data,
            'route_data': route_data,
            'hospital': hospital_data,
            'eta_minutes': 8
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alerts/active')
def get_active_alerts():
    """Get currently active alerts"""
    # Mock active alert for demo
    active_alert = {
        'id': 'demo-123',
        'patient_name': 'Jean Dupont',
        'age': 45,
        'severity': 2,
        'symptoms': 'Douleur thoracique',
        'status': 'en_route'
    }
    
    return jsonify({'alert': active_alert})

@api_bp.route('/alerts/recent')
def get_recent_alerts():
    """Get recent alerts for dashboard table"""
    # Mock recent alerts for demo
    recent_alerts = [
        {
            'id': 'alert-1',
            'patient_name': 'Marie Martin',
            'severity': 1,
            'status': 'completed',
            'created_at': '2024-01-15T10:30:00Z',
            'eta': '5 min'
        },
        {
            'id': 'alert-2',
            'patient_name': 'Pierre Durand',
            'severity': 3,
            'status': 'en_route',
            'created_at': '2024-01-15T11:15:00Z',
            'eta': '12 min'
        }
    ]
    
    return jsonify({'alerts': recent_alerts})