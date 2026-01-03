from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.location_service import LocationService
from app.services.firebase_service import FirebaseService
from app.decorators import login_required
import uuid
import json
from datetime import datetime

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    return render_template('index.html')

@web_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@web_bp.route('/alert', methods=['GET', 'POST'])
@login_required
def alert_form():
    if request.method == 'GET':
        # Auto-fill location using IP geolocation
        location_service = LocationService()
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        location_data = location_service.get_location_by_ip(user_ip)
        return render_template('alert_form.html', location_data=location_data)
    
    # POST - Create Alert
    try:
        # 1. Get Form Data
        form_data = {
            'nom_prenom': request.form.get('nom_prenom'),
            'age': int(request.form.get('age')),
            'sexe': request.form.get('sexe'),
            'symptomes': request.form.get('symptomes'),
            'localisation': request.form.get('localisation')
        }
        
        # 2. Generate UUID
        alert_id = str(uuid.uuid4())[:8]
        
        # 3. Save Initial "Pending" Data to Firebase
        firebase_service = FirebaseService()
        alerts_collection = firebase_service.get_collection('alerts')
        
        initial_data = {
            'patient': form_data,
            'status': 'En attente',
            'username': session.get('user'),
            'created_at': datetime.utcnow().isoformat()
        }
        
        alerts_collection.document(alert_id).set(initial_data)
        flash('Alerte créée avec succès!', 'success')
        
        try:
            # 4. Run Crew
            from app.crew.crew import SystemeUrgencesMedicalesCrew
            
            inputs = {
                'nom_prenom': form_data['nom_prenom'],
                'age': form_data['age'],
                'sexe': form_data['sexe'],
                'symptomes': form_data['symptomes'],
                'localisation': form_data['localisation']
            }
            
            medialert_crew = SystemeUrgencesMedicalesCrew()
            result = medialert_crew.crew().kickoff(inputs=inputs)
            
            # 5. Parse JSON (Handle potential markdown wrapping)
            json_str = result.raw if hasattr(result, 'raw') else str(result)
            cleaned_json = json_str.replace('```json', '').replace('```', '').strip()
            output_data = json.loads(cleaned_json)
            
            # 6. Prepare Update Dict
            updates = {
                'status': 'Terminé',
                'hospital_name': output_data.get('hospital_name'),
                'distance_km': output_data.get('distance'),
                'eta_minutes': output_data.get('eta'),
                'medical_team': output_data.get('medical_team'),
                'full_report': output_data.get('ui_view'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # 7. Update Firebase
            alerts_collection.document(alert_id).update(updates)
            
        except Exception as e:
            print(f"Crew Error: {e}")
            # Update status to Error in Firebase
            alerts_collection.document(alert_id).update({
                'status': 'Erreur',
                'error': str(e),
                'updated_at': datetime.utcnow().isoformat()
            })
            flash('Erreur lors du traitement de l\'alerte', 'error')
        
        return redirect(url_for('patient.profile'))
        
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
        return redirect(url_for('web.alert_form'))

@web_bp.route('/tracking/<alert_id>')
@login_required
def tracking(alert_id):
    """Tracking page for emergency alert"""
    firebase = FirebaseService()
    alerts_collection = firebase.get_collection('alerts')
    doc = alerts_collection.document(alert_id).get()
    
    if doc.exists:
        alert_data = doc.to_dict()
        return render_template('tracking.html', 
                             alert_id=alert_id,
                             patient=alert_data.get('patient', {}))
    return redirect(url_for('web.dashboard'))

@web_bp.route('/delete_alert/<alert_id>', methods=['POST'])
@login_required
def delete_alert(alert_id):
    """Delete an alert from the database"""
    firebase = FirebaseService()
    if firebase.delete_alert(alert_id):
        flash('Alerte supprimée avec succès', 'success')
    else:
        flash('Erreur lors de la suppression', 'error')
    return redirect(url_for('patient.profile'))