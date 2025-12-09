from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.decorators import login_required, admin_required
from app.models.user import UserStore
from app.services.system_logs_service import SystemLogsService

admin_bp = Blueprint('admin', __name__)
user_store = UserStore()
logs_service = SystemLogsService()

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    user_role = session.get('role', 'user')
    if user_role != 'admin':
        return render_template('admin/access_denied.html')
    
    from app.services.firebase_service import FirebaseService
    firebase = FirebaseService()
    
    users = user_store.get_all_users()
    recent_logs = logs_service.get_recent_logs(limit=10)
    
    # Get stats from Firestore
    alerts_collection = firebase.get_collection('alerts')
    total_alerts = len(list(alerts_collection.stream()))
    active_alerts = len(list(alerts_collection.where('status', '==', 'processing').stream()))
    
    stats = {
        'total_users': len(users),
        'total_alerts': total_alerts,
        'active_alerts': active_alerts
    }
    
    return render_template('admin/dashboard.html', users=users, recent_logs=recent_logs, stats=stats)

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
        logs_service.log_event('admin_create_user', f'Admin created user: {username}', session.get('user'), {'new_user': username, 'role': role})
        flash('Utilisateur créé avec succès', 'success')
    else:
        flash('Nom d\'utilisateur déjà existant', 'error')
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
