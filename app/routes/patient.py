from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.decorators import login_required
from app.models.patient import PatientStore
from app.models.user import UserStore
from app.services.firebase_service import FirebaseService
from firebase_admin import firestore

patient_bp = Blueprint('patient', __name__)
patient_store = PatientStore()
user_store = UserStore()
firebase_service = FirebaseService()
alerts_collection = firebase_service.get_collection('alerts')

@patient_bp.route('/profile')
@login_required
def profile():
    username = session.get('user')
    user = user_store.get_user(username)
    patient = patient_store.get_profile(username)
    
    if not patient:
        # Get user email for pre-filling
        user_email = user.email if user else ''
        return render_template('patient/create_profile.html', user_email=user_email)
    
    # Get search query
    search_query = request.args.get('search', '').lower().strip()
    
    # Fetch user's alerts from Firestore, ordered by created_at descending
    try:
        alerts_query = alerts_collection.where(filter=firestore.FieldFilter('username', '==', username)).order_by('created_at', direction=firestore.Query.DESCENDING)
        alerts = [doc.to_dict() | {'alert_id': doc.id} for doc in alerts_query.stream()]
    except Exception as e:
        # Fallback without ordering if created_at field doesn't exist
        alerts_query = alerts_collection.where(filter=firestore.FieldFilter('username', '==', username))
        alerts = [doc.to_dict() | {'alert_id': doc.id} for doc in alerts_query.stream()]
    
    # Debug: Print first alert structure
    if alerts:
        print(f"DEBUG ALERT DATA: {alerts[0]}")
        print(f"DEBUG ALERT KEYS: {list(alerts[0].keys())}")
        print(f"DEBUG ALERT STATUS: '{alerts[0].get('status', 'NO_STATUS_FIELD')}'")
    else:
        print("DEBUG: No alerts found")
    
    # Parse and normalize alert data
    normalized_alerts = []
    for alert in alerts:
        normalized_alert = alert.copy()
        
        # Parse patient data if it's a JSON string
        if 'patient' in alert and isinstance(alert['patient'], str):
            try:
                import json
                normalized_alert['patient'] = json.loads(alert['patient'])
            except:
                pass
        
        # Parse dispatch_info if it's a JSON string
        if 'dispatch_info' in alert and isinstance(alert['dispatch_info'], str):
            try:
                import json
                normalized_alert['dispatch_result'] = json.loads(alert['dispatch_info'])
            except:
                pass
        
        normalized_alerts.append(normalized_alert)
    
    # Filter alerts by search query (symptoms or hospital)
    if search_query:
        filtered_alerts = []
        for alert in normalized_alerts:
            # Search in symptoms/description
            symptoms = alert.get('patient', {}).get('symptomes', '') or alert.get('description', '')
            # Search in hospital name
            hospital_name = ''
            if alert.get('dispatch_result'):
                hospital_name = alert['dispatch_result'].get('hospital', {}).get('name', '')
            
            if (search_query in symptoms.lower() or search_query in hospital_name.lower()):
                filtered_alerts.append(alert)
        normalized_alerts = filtered_alerts
    
    return render_template('patient/profile.html', patient=patient, user=user, alerts=normalized_alerts, search_query=search_query)

@patient_bp.route('/profile/create', methods=['POST'])
@login_required
def create_profile():
    username = session.get('user')
    
    # Validate phone number
    phone = request.form.get('phone', '').strip()
    if phone and (not phone.isdigit() or len(phone) != 10):
        flash('Le numéro de téléphone doit contenir exactement 10 chiffres', 'error')
        user = user_store.get_user(username)
        user_email = user.email if user else ''
        return render_template('patient/create_profile.html', user_email=user_email)
    
    profile = patient_store.create_profile(
        username=username,
        nom_prenom=request.form.get('nom_prenom'),
        age=int(request.form.get('age')),
        sexe=request.form.get('sexe'),
        email=request.form.get('email'),
        phone=phone,
        address=request.form.get('address', ''),
        blood_type=request.form.get('blood_type', '')
    )
    
    if profile:
        flash('Profil créé avec succès!', 'success')
    else:
        flash('Erreur lors de la création du profil', 'error')
    
    return redirect(url_for('patient.profile'))

@patient_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    username = session.get('user')
    patient = patient_store.get_profile(username)
    
    if not patient:
        return redirect(url_for('patient.profile'))
    
    if request.method == 'POST':
        patient_store.update_profile(
            username=username,
            phone=request.form.get('phone', ''),
            address=request.form.get('address', ''),
            blood_type=request.form.get('blood_type', '')
        )
        flash('Profil mis à jour avec succès!', 'success')
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/edit_profile.html', patient=patient)

@patient_bp.route('/alerts')
@login_required
def alerts_history():
    username = session.get('user')
    patient = patient_store.get_profile(username)
    
    if not patient:
        return redirect(url_for('patient.profile'))
    
    # Fetch user's alerts from Firestore
    alerts = [doc.to_dict() | {'alert_id': doc.id} for doc in alerts_collection.where(filter=firestore.FieldFilter('username', '==', username)).stream()]
    
    return render_template('patient/alerts_history.html', patient=patient, alerts=alerts)

@patient_bp.route('/alert/<alert_id>')
@login_required
def alert_detail(alert_id):
    username = session.get('user')
    patient = patient_store.get_profile(username)
    
    if not patient:
        return redirect(url_for('patient.profile'))
    
    # Fetch alert from Firestore
    doc = alerts_collection.document(alert_id).get()
    if not doc.exists or doc.to_dict().get('username') != username:
        flash('Alerte non trouvée', 'error')
        return redirect(url_for('patient.alerts_history'))
    
    alert = doc.to_dict() | {'alert_id': alert_id}
    
    # Parse JSON strings like in profile route
    if 'patient' in alert and isinstance(alert['patient'], str):
        try:
            import json
            alert['patient'] = json.loads(alert['patient'])
        except:
            pass
    
    if 'dispatch_info' in alert and isinstance(alert['dispatch_info'], str):
        try:
            import json
            dispatch_result = json.loads(alert['dispatch_info'])
            alert['dispatch_result'] = dispatch_result
            
            # Extract hospital data for template compatibility
            if dispatch_result.get('hospital'):
                hospital = dispatch_result['hospital']
                alert['hospital_name'] = hospital.get('name', '')
                alert['distance_km'] = hospital.get('distance_km', '')
                alert['eta_minutes'] = hospital.get('eta_minutes', '')
        except:
            pass
    
    # Also check for direct fields saved by EmergencyOrchestrator
    if not alert.get('hospital_name') and alert.get('selected_hospital'):
        alert['hospital_name'] = alert['selected_hospital'].get('name', '')
    if not alert.get('distance_km'):
        alert['distance_km'] = alert.get('distance_km', 0)
    if not alert.get('eta_minutes'):
        alert['eta_minutes'] = alert.get('eta_minutes', 0)
    if not alert.get('doctors') and alert.get('medical_team'):
        alert['doctors'] = alert.get('medical_team', [])
    
    return render_template('patient/alert_detail.html', alert=alert, patient=patient)
