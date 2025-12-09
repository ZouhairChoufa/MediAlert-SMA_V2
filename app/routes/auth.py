from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import UserStore

auth_bp = Blueprint('auth', __name__)
user_store = UserStore()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = user_store.authenticate(username, password)
        if user:
            session['user'] = username
            session['role'] = user.role
            flash('Connexion réussie!', 'success')
            return redirect(url_for('web.index'))
        
        flash('Identifiants incorrects', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('auth/register.html')
        
        user = user_store.create_user(username, email, password)
        if user:
            flash('Compte créé avec succès! Connectez-vous.', 'success')
            return redirect(url_for('auth.login'))
        
        flash('Nom d\'utilisateur déjà existant', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('auth.login'))
