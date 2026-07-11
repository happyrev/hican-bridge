from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import db, login_manager
from app.models import User, JournalEntry # Will create models.py in next step

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('journal.dashboard')) # Redirect to journal blueprint
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user: # In a real app, you'd verify password here
            login_user(user)
            return redirect(url_for('journal.dashboard')) # Redirect to journal blueprint
        flash('Invalid username or password')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            new_user = User(
                username=request.form['username'],
                name=request.form['name'],
                age=int(request.form.get('age', 0)),
                bio=request.form.get('bio', '')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('journal.dashboard')) # Redirect to journal blueprint
        except Exception as e:
            flash(f"Registration failed: {str(e)}")
            return render_template('register.html', error=str(e))
    return render_template('register.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
