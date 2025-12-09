from flask import Blueprint, render_template, session, redirect, url_for
from app.decorators import login_required, admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_dashboard():
    user_role = session.get('role', 'user')
    if user_role != 'admin':
        return render_template('admin/access_denied.html')
    return render_template('admin/dashboard.html')
