from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.decorators import login_required
from app.models.patient import PatientStore
from app.services.firebase_service import FirebaseService

patient_bp = Blueprint('patient', __name__)
patient_store = PatientStore()
firebase_service = FirebaseService()
alerts_collection = firebase_service.get_collection('alerts')

@patient_bp.route('/profile')
@login_required
def profile():
    username = session.get('user')
    patient = patient_store.get_profile(username)
    
    if not patient:
        return render_template('patient/create_profile.html')
    
    return render_template('patient/profile.html', patient=patient)

@patient_bp.route('/profile/create', methods=['POST'])
@login_required
def create_profile():
    username = session.get('user')
    
    profile = patient_store.create_profile(
        username=username,
        nom_prenom=request.form.get('nom_prenom'),
        age=int(request.form.get('age')),
        sexe=request.form.get('sexe'),
        email=request.form.get('email'),
        phone=request.form.get('phone', ''),
        address=request.form.get('address', ''),
        blood_type=request.form.get('blood_type', ''),
        allergies=request.form.get('allergies', '').split(',') if request.form.get('allergies') else []
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
            blood_type=request.form.get('blood_type', ''),
            allergies=request.form.get('allergies', '').split(',') if request.form.get('allergies') else []
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
    alerts = [doc.to_dict() | {'alert_id': doc.id} for doc in alerts_collection.where('username', '==', username).stream()]
    
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
    return render_template('patient/alert_detail.html', alert=alert, patient=patient)
