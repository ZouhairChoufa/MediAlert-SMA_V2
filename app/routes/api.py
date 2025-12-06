from flask import Blueprint, request, jsonify, session
import threading
import uuid
import sys
import json
from app.services.firebase_service import FirebaseService
# Updated import to use the correct Crew class
from app.crew.crew import SystemeUrgencesMedicalesCrew
from app.services.geolocation import GeolocationService
from app.services.smart_dispatch import SmartDispatchEngine

api_bp = Blueprint('api', __name__)

# Store alert data temporarily
alert_storage = {}

# Initialize services
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
        manual = {'address': data.get('localisation'), 'lat': data.get('lat'), 'lng': data.get('lng')}
        # Note: request.remote_addr might need proxy handling in production
        ip = geolocation_service.get_ip_location(request.remote_addr)
        
        location = geolocation_service.merge_all_location_sources(gps, manual, ip)
        
        # Smart dispatch (initial logic before CrewAI)
        emergency_level = data.get('emergency_level', 2)
        dispatch_result = smart_dispatch.dispatch_ambulance(
            location['lat'], location['lng'], emergency_level
        )
        
        # Generate alert ID
        alert_id = str(uuid.uuid4())[:8]
        
        # Store alert data
        alert_storage[alert_id] = {
            'patient': data,
            'location': location,
            'dispatch': dispatch_result,
            'status': 'processing',
            'logs': []
        }
        
        # Trigger crew processing in background
        def process_crew():
            try:
                print(f"\n[AGENT] Starting crew processing for alert {alert_id}", flush=True)
                sys.stdout.flush()
                alert_storage[alert_id]['logs'].append('[SYSTEM] Initialisation crew...')
                
                # Create inputs for the Crew
                # We map the data to the variables expected in tasks.yaml ({nom_prenom}, etc.)
                crew_inputs = {
                    'nom_prenom': data.get('nom_prenom'),
                    'age': data.get('age'),
                    'sexe': data.get('sexe'),
                    'symptomes': data.get('symptomes'),
                    'localisation': data.get('localisation') or location.get('address'),
                    'nv_urgence': data.get('emergency_level', 'Non spécifié')
                }

                # Initialize and run the Crew
                crew = SumiSystemeUrgenceMedicaleIntelligentCrew().crew()
                result = crew.kickoff(inputs=crew_inputs)
                
                # --- PRINT RESULT TO TERMINAL ---
                print("\n" + "="*50)
                print(f"✅ FINAL CREW OUTPUT for Alert {alert_id}:")
                print("="*50)
                print(result)
                print("="*50 + "\n", flush=True)
                # --------------------------------
                
                alert_storage[alert_id]['result'] = str(result)
                alert_storage[alert_id]['status'] = 'completed'
                print(f"[AGENT] Crew processing completed for alert {alert_id}", flush=True)
                
            except Exception as e:
                alert_storage[alert_id]['status'] = 'error'
                alert_storage[alert_id]['error'] = str(e)
                print(f"[ERROR] Crew processing failed: {e}", flush=True)
                sys.stdout.flush()
        
        thread = threading.Thread(target=process_crew)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'alert_id': alert_id,
            'message': 'Alerte créée et traitement en cours',
            'dispatch': dispatch_result
        })
        
    except Exception as e:
        print(f"Error in create_alert: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alert/<alert_id>/data', methods=['GET'])
def get_alert_data(alert_id):
    """Get alert data for tracking page"""
    if alert_id in alert_storage:
        return jsonify(alert_storage[alert_id])
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