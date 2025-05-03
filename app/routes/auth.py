from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
from app import db
from flask_wtf.csrf import validate_csrf
import traceback  # Add this import to get detailed error information

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration with CSRF protection."""
    # Validate CSRF token
    try:
        csrf_token = request.form.get('csrf_token')
        validate_csrf(csrf_token)
    except Exception as csrf_error:
        print(f"CSRF Error: {str(csrf_error)}")
        return jsonify({'error': 'CSRF token validation failed'}), 400
    
    # Get form data
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate data
    if not username or not email or not password or not confirm_password:
        return jsonify({'error': 'All fields are required'}), 400
        
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    # Check if username or email already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400
    
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user with secure password hash
    try:
        print(f"Creating new user with username: {username}, email: {email}")
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log in the new user
        login_user(new_user)
        return jsonify({'success': 'Registration successful!', 'redirect': '/upload'}), 200
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        print(f"Registration Error: {str(e)}")
        print(f"Traceback: {error_details}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
        
@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login with CSRF protection."""
    # Validate CSRF token
    try:
        csrf_token = request.form.get('csrf_token')
        validate_csrf(csrf_token)
    except:
        return jsonify({'error': 'CSRF token validation failed'}), 400
    
    # Get form data
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember_me') else False
    
    # Validate user
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Log in user
    login_user(user, remember=remember)
    return jsonify({'success': 'Login successful!', 'redirect': '/upload'}), 200
    
@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('index'))