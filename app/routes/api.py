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



@api_bp.route('/geocode', methods=['POST'])

def geocode_address():

    """Geocode a manual address text to coordinates"""

    try:

        data = request.get_json()

        address = data.get('address', '').strip()

        

        if not address:

            return jsonify({'success': False, 'error': 'No address provided'}), 400

        

        print(f'[Geocode API] Received address: {address}')

        

        result = geolocation_service.geocode_address(address)

        

        if result and result.get('lat') and result.get('lng'):

            return jsonify({

                'success': True,

                'lat': result['lat'],

                'lng': result['lng'],

                'display_name': result.get('display_name', address)

            })

        else:

            return jsonify({'success': False, 'error': 'Could not geocode address'}), 400

    except Exception as e:

        print(f'[Geocode API] Exception: {str(e)}')

        return jsonify({'error': str(e)}), 500



@api_bp.route('/detect-ip-location', methods=['POST'])

def detect_ip_location():

    """Detect user location from IP address"""

    try:

        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

        location = geolocation_service.get_ip_location(ip_address)

        

        if location:

            return jsonify({'success': True, 'location': location})

        return jsonify({'success': False, 'error': 'Could not detect location'}), 400

    except Exception as e:

        return jsonify({'error': str(e)}), 500



@api_bp.route('/alert', methods=['POST'])

@login_required

def create_alert():

    """Create new emergency alert with smart dispatch"""

    try:

        print("\n" + "="*60)

        print("API: ALERT CREATION REQUEST")

        print("="*60)

        

        data = request.get_json()

        

        required_fields = ['nom_prenom', 'age', 'sexe', 'symptomes']

        for field in required_fields:

            if field not in data:

                return jsonify({'error': f'Missing field: {field}'}), 400

        

        print(f"\n[API] Patient: {data.get('nom_prenom')}, Age: {data.get('age')}")

        

        # Merge location sources

        gps = data.get('gps_coords')

        lat = float(data.get('lat')) if data.get('lat') else None

        lng = float(data.get('lng')) if data.get('lng') else None

        manual = {'address': data.get('localisation'), 'lat': lat, 'lng': lng}

        ip = geolocation_service.get_ip_location(request.remote_addr)

        

        location = geolocation_service.merge_all_location_sources(gps, manual, ip)

        

        if not location.get('lat') or not location.get('lng'):

            return jsonify({'error': 'Unable to determine location coordinates'}), 400

        

        # Smart dispatch

        emergency_level = int(data.get('emergency_level', 2))

        dispatch_result = smart_dispatch.dispatch_ambulance(

            float(location['lat']), float(location['lng']), emergency_level

        )

        

        # Generate alert ID

        alert_id = str(uuid.uuid4())[:8]

        

        # Store alert data in Firestore

        alert_data = {

            'patient': json.loads(json.dumps(data, default=str)),

            'location': json.loads(json.dumps(location, default=str)),

            'dispatch_info': json.dumps(dispatch_result, default=str),

            'emergency_level': emergency_level,

            'status': 'processing',

            'logs': [],

            'username': session.get('user'),

            'created_at': datetime.utcnow().isoformat()

        }
          # --- CORRECTION DISTANCES RÉELLES ---

        if dispatch_result and 'mission' in dispatch_result:

            # On récupère les vraies valeurs calculées par ORS dans smart_dispatch.py

            alert_data['dist_amb_pat'] = dispatch_result['mission'].get('dist_leg1_km', 0)

            alert_data['dist_pat_hosp'] = dispatch_result['mission'].get('dist_leg2_km', 0)

        else:

            alert_data['dist_amb_pat'] = 0

            alert_data['dist_pat_hosp'] = 0
        
        alerts_collection.document(alert_id).set(alert_data)
        
        # Log alert creation
        logs_service.log_event('alert_created', f'New alert created: {alert_id}', session.get('user'), {'alert_id': alert_id})

        username = session.get('user')
        def run_async_workflow():
            try:
                print(f"\n[ORCHESTRATOR] Starting workflow for alert {alert_id}", flush=True)
                orchestrator = EmergencyOrchestrator()
                asyncio.run(orchestrator.run_workflow(
                    alert_id,
                    float(location['lat']),
                    float(location['lng']),
                    emergency_level,
                    data.get('symptomes', 'Non spécifié'),
                    str(data.get('age', 'Inconnu'))
                ))
                print(f"[ORCHESTRATOR] Workflow completed for alert {alert_id}", flush=True)
            except Exception as e:
                alerts_collection.document(alert_id).update({'status': 'ERROR', 'error': str(e)})
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
    try:
        doc = alerts_collection.document(alert_id).get()
        if doc.exists:
            data = doc.to_dict()
        # --- AFFINAGE AFFICHAGE ---
        dist_amb_pat = data.get('dist_amb_pat', 0)
        dist_pat_hosp = data.get('dist_pat_hosp', 0)
        # Si jamais les données manquent (vieilles alertes), on met un fallback
        if dist_pat_hosp == 0 and data.get('selected_hospital'):
            dist_pat_hosp = data['selected_hospital'].get('distance_km', 0)
        return jsonify({
            'status': data.get('status', 'processing'),
            'logs': data.get('logs', []),
            'route_active': data.get('route_active'), 
            'route_red': data.get('route_red'),
            'route_blue': data.get('route_blue'),
            'dist_amb_pat': dist_amb_pat,
            'dist_pat_hosp': dist_pat_hosp,
            'severity_level': data.get('emergency_level', 2),
            'eta_minutes': data.get('eta_minutes'),
            'selected_hospital': data.get('selected_hospital'),
            'ambulance': data.get('ambulance'),
            'patient': data.get('patient'),
            'location': data.get('location'),
            'medical_protocol': data.get('medical_protocol')
        })
        return jsonify({'error': 'Alert not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/status/<alert_id>')
def get_alert_status(alert_id):
    try:
        doc = alerts_collection.document(alert_id).get()
        if not doc.exists:
            return jsonify({'error': 'Alert not found'}), 404
        return jsonify({'alert': doc.to_dict(), 'eta_minutes': doc.to_dict().get('eta_minutes', 0)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/alerts/active')
def get_active_alerts():
    return jsonify({'alert': None}) 

@api_bp.route('/alerts/recent')
def get_recent_alerts():
    return jsonify({'alerts': []})