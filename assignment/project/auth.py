from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User

from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    # Store the originally requested URL in the session
    session['next_url'] = request.args.get('next')
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = request.form.get('remember')  # This is a checkbox

    user = User.query.filter_by(email=email).first() # Check if the user actually exists

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'error')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)

    # Redirect to the originally requested URL or the profile page
    next_url = session.pop('next_url', None)
    return redirect(next_url or url_for('main.profile'))

@auth.route('/signup', methods=['GET', 'POST']) # Add this
def signup(): 
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        # If this returns a user, then the email already exists in database
        if user:
            flash('Email address already exists', 'error')
            return redirect(url_for('auth.signup'))

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


