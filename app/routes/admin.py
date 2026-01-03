from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.decorators import login_required, admin_required
from app.models.user import UserStore
from app.services.system_logs_service import SystemLogsService
from app.services.firebase_service import FirebaseService
from firebase_admin import firestore, auth
import csv
import io

admin_bp = Blueprint('admin', __name__)
user_store = UserStore()
logs_service = SystemLogsService()
firebase = FirebaseService()

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    user_role = session.get('role', 'patient')
    if user_role != 'admin':
        return render_template('admin/access_denied.html')
    
    users = user_store.get_all_users()
    recent_logs = logs_service.get_recent_logs(limit=10)
    
    # Get stats from Firestore
    alerts_collection = firebase.get_collection('alerts')
    total_alerts = len(list(alerts_collection.stream()))
    active_alerts = len(list(alerts_collection.where('status', '==', 'processing').stream()))
    
    # Get theme toggle setting
    settings_doc = firebase.db.collection('system_settings').document('theme_control').get()
    theme_toggle_enabled = settings_doc.to_dict().get('enabled', True) if settings_doc.exists else True
    
    stats = {
        'total_users': len(users),
        'total_alerts': total_alerts,
        'active_alerts': active_alerts
    }
    
    return render_template('admin/dashboard.html', users=users, recent_logs=recent_logs, stats=stats, theme_toggle_enabled=theme_toggle_enabled)

@admin_bp.route('/admin/user/create', methods=['POST'])
@login_required
def create_user():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'patient')
    
    user = user_store.create_user(username, email, password, role)
    if user:
        flash(f'L\'utilisateur {email} a été créé avec succès (Rôle: {role.capitalize()}).', 'success')
    else:
        flash('Email déjà utilisé ou erreur de création', 'error')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/user/<username>/role', methods=['POST'])
@login_required
def update_role(username):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    new_role = request.form.get('role')
    if user_store.update_user_role(username, new_role):
        logs_service.log_event('admin_update_role', f'Admin updated role for {username}', session.get('user'), {'target_user': username, 'new_role': new_role})
        flash('Rôle mis à jour', 'success')
    else:
        flash('Utilisateur introuvable', 'error')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/user/<username>/delete', methods=['POST'])
@login_required
def delete_user(username):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if username == session.get('user'):
        flash('Vous ne pouvez pas supprimer votre propre compte', 'error')
    elif user_store.delete_user(username):
        logs_service.log_event('admin_delete_user', f'Admin deleted user: {username}', session.get('user'), {'deleted_user': username})
        flash('Utilisateur supprimé', 'success')
    else:
        flash('Utilisateur introuvable', 'error')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/settings/theme-toggle', methods=['POST'])
@login_required
def toggle_theme_setting():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    enabled = request.json.get('enabled', True)
    
    firebase.db.collection('system_settings').document('theme_control').set({
        'enabled': enabled,
        'updated_by': session.get('user'),
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    
    logs_service.log_event('admin_theme_toggle', f'Admin {"enabled" if enabled else "disabled"} theme toggle for all users', session.get('user'), {'enabled': enabled})
    
    return jsonify({'success': True, 'enabled': enabled})

@admin_bp.route('/api/settings/theme-toggle', methods=['GET'])
def get_theme_setting():
    settings_doc = firebase.db.collection('system_settings').document('theme_control').get()
    enabled = settings_doc.to_dict().get('enabled', True) if settings_doc.exists else True
    return jsonify({'enabled': enabled})

@admin_bp.route('/admin/agents-documentation')
@login_required
def agents_documentation():
    user_role = session.get('role', 'patient')
    if user_role != 'admin':
        return render_template('admin/access_denied.html')
    
    return render_template('admin/agents_documentation.html')

@admin_bp.route('/admin/test')
def test_route():
    return "Test route works"

@admin_bp.route('/admin/user/<username>')
@login_required
def user_detail_view(username):
    if session.get('role') != 'admin':
        return render_template('admin/access_denied.html')
    
    # Get user and patient data
    user = user_store.get_user(username)
    if not user:
        flash('Utilisateur introuvable', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    from app.models.patient import PatientStore
    patient_store = PatientStore()
    patient = patient_store.get_profile(username)
    
    # Get user's alerts from Firestore
    try:
        alerts_query = firebase.db.collection('alerts').where(filter=firestore.FieldFilter('username', '==', username)).order_by('created_at', direction=firestore.Query.DESCENDING)
        alerts = [doc.to_dict() | {'alert_id': doc.id} for doc in alerts_query.stream()]
    except Exception as e:
        # Fallback without ordering if index doesn't exist
        alerts_query = firebase.db.collection('alerts').where(filter=firestore.FieldFilter('username', '==', username))
        alerts = [doc.to_dict() | {'alert_id': doc.id} for doc in alerts_query.stream()]
    
    # Parse alert data
    normalized_alerts = []
    for alert in alerts:
        normalized_alert = alert.copy()
        if 'patient' in alert and isinstance(alert['patient'], str):
            try:
                import json
                normalized_alert['patient'] = json.loads(alert['patient'])
            except:
                pass
        if 'dispatch_info' in alert and isinstance(alert['dispatch_info'], str):
            try:
                import json
                normalized_alert['dispatch_result'] = json.loads(alert['dispatch_info'])
            except:
                pass
        normalized_alerts.append(normalized_alert)
    
    return render_template('admin/user_detail_view.html', user=user, patient=patient, alerts=normalized_alerts, username=username)

@admin_bp.route('/admin/import-users', methods=['POST'])
@login_required
def import_users():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.csv'):
        flash('Veuillez sélectionner un fichier CSV valide', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    success_count = 0
    error_count = 0
    
    try:
        # 1. Lecture Robuste (utf-8-sig gère les fichiers Excel)
        content = file.stream.read().decode("utf-8-sig")
        stream = io.StringIO(content)
        
        # 2. Détection du séparateur (Virgule ou Point-Virgule ?)
        # On regarde la première ligne pour voir ce qui est le plus fréquent
        first_line = content.split('\n')[0]
        delimiter = ';' if first_line.count(';') > first_line.count(',') else ','
        print(f"DEBUG: Séparateur détecté = '{delimiter}'")

        csv_input = csv.DictReader(stream, delimiter=delimiter)
        
        # 3. Nettoyage des en-têtes (Headers)
        # Parfois on a " Role" au lieu de "Role". On normalise tout.
        if csv_input.fieldnames:
            csv_input.fieldnames = [name.strip() for name in csv_input.fieldnames]
            print(f"DEBUG: Colonnes détectées = {csv_input.fieldnames}")

        for row in csv_input:
            try:
                row_lower = {k.lower(): v for k, v in row.items() if k}

                full_name = row_lower.get('full name') or row_lower.get('nom') or ''
                email = row_lower.get('email', '').strip()
                password = row_lower.get('password', '').strip()
                ville = row_lower.get('ville', '').strip()
                specialite = row_lower.get('specialite', '').strip()
                
                # --- DETECTION DU ROLE ---
                raw_role = row_lower.get('role', '').strip().lower()
                
                # Mapping large pour accepter toutes les variantes
                if raw_role in ['medecin', 'médecin', 'medcin', 'doctor', 'docteur', 'dr', 'physician']:
                    role = 'medecin'
                elif raw_role in ['admin', 'administrateur', 'root']:
                    role = 'admin'
                else:
                    role = 'patient' # Fallback
                
                # Debug spécifique pour voir pourquoi un médecin devient patient
                if role == 'patient' and raw_role != 'patient' and raw_role != '':
                    print(f"⚠️ ATTENTION: Rôle '{raw_role}' non reconnu -> forcé à 'patient'")

                if not all([full_name, email, password]):
                    print(f"❌ Données manquantes pour : {email}")
                    error_count += 1
                    continue
                
                # Generate username from email
                username = email.split('@')[0]
                
                # Create/Get Firebase Auth user
                try:
                    user_record = auth.create_user(
                        email=email,
                        password=password,
                        display_name=full_name
                    )
                    uid = user_record.uid
                except auth.EmailAlreadyExistsError:
                    user_record = auth.get_user_by_email(email)
                    uid = user_record.uid
                
                # Prepare data
                user_data = {
                    'uid': uid,
                    'username': username,
                    'nom': full_name,
                    'email': email,
                    'role': role,
                    'ville': ville,
                    'created_at': firestore.SERVER_TIMESTAMP
                }
                
                if role == 'medecin':
                    user_data['specialite'] = specialite
                    user_data['patients_assignes'] = []
                elif role == 'patient':
                    # On n'écrase pas l'historique s'il existe déjà
                    doc = firebase.db.collection('users').document(username).get()
                    if not doc.exists:
                        user_data['historique_medical'] = []
                
                firebase.db.collection('users').document(username).set(user_data, merge=True)
                print(f"✅ Importé: {username} en tant que {role.upper()}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Erreur ligne: {e}")
                error_count += 1
        
        if success_count > 0:
            flash(f'{success_count} utilisateur(s) importé(s)', 'success')
        if error_count > 0:
            flash(f'{error_count} erreur(s). Voir terminal.', 'error')
            
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        flash(f'Erreur lecture fichier: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_dashboard'))