from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.decorators import login_required, admin_required
from app.models.user import UserStore
from app.services.system_logs_service import SystemLogsService
from app.services.firebase_service import FirebaseService
from firebase_admin import firestore

admin_bp = Blueprint('admin', __name__)
user_store = UserStore()
logs_service = SystemLogsService()
firebase = FirebaseService()

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    user_role = session.get('role', 'user')
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
    role = request.form.get('role', 'user')
    
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
    user_role = session.get('role', 'user')
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


