from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Veuillez vous connecter pour accéder à cette page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Veuillez vous connecter pour accéder à cette page', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Accès refusé: droits administrateur requis', 'error')
            return redirect(url_for('web.index'))
        return f(*args, **kwargs)
    return decorated_function
