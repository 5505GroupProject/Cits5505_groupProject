from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
import secrets
import string
import os
import random
from datetime import datetime, timedelta

# Define blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember_me'))

        user = User.query.filter_by(username=username).first()
        
        # Use the check_password method from the User model
        if user is None or not user.check_password(password):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Invalid username or password'}), 401
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        
        # Handle AJAX vs regular form submission for success case
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            next_page = request.args.get('next')
            redirect_url = next_page or url_for('main.home')
            return jsonify({'success': 'Login successful!', 'redirect': redirect_url}), 200
        else:
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Send verification code
        if action == 'send_code':
            user = User.query.filter_by(email=email).first()
            if not user:
                if is_ajax:
                    return jsonify({'error': 'No account found with that email address.'}), 404
                else:
                    flash('No account found with that email address.', 'danger')
                    return redirect(url_for('auth.reset_password'))
            
            verification_code = ''.join(random.choices('0123456789', k=6))
            session['reset_email'] = email
            session['verification_code'] = verification_code
            session['code_expiry'] = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
            
            # In production, we would send email here
            success_msg = f'Verification code: {verification_code} (this would be emailed in production)'
            
            if is_ajax:
                return jsonify({'success': success_msg}), 200
            else:
                flash(success_msg, 'info')
                return redirect(url_for('auth.reset_password'))
            
        # Verify code
        elif action == 'verify_code':
            verification_code = request.form.get('verification_code')
            
            if (session.get('verification_code') == verification_code and 
                session.get('reset_email') == email and 
                session.get('code_expiry', 0) > datetime.utcnow().timestamp()):
                
                # Store a flag in session that this user is verified for password reset
                session['password_reset_verified'] = True
                
                if is_ajax:
                    return jsonify({
                        'success': 'Code verified successfully!',
                        'redirect': url_for('auth.set_new_password')
                    }), 200
                else:
                    return redirect(url_for('auth.set_new_password'))
            else:
                error_msg = 'Invalid or expired verification code.'
                if is_ajax:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'danger')
                    return redirect(url_for('auth.reset_password'))
                
        # Handle setting a new password
        elif action == 'set_password':
            # Verify the user completed previous steps
            if not session.get('password_reset_verified') or not session.get('reset_email'):
                error_msg = 'Please verify your email first.'
                if is_ajax:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'danger')
                    return redirect(url_for('auth.reset_password'))
                
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not new_password or not confirm_password:
                error_msg = 'Please enter a new password.'
                if is_ajax:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'danger')
                    return redirect(url_for('auth.set_new_password'))
                
            if new_password != confirm_password:
                error_msg = 'Passwords do not match.'
                if is_ajax:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'danger')
                    return redirect(url_for('auth.set_new_password'))
                
            # Update the user's password
            user = User.query.filter_by(email=session.get('reset_email')).first()
            if user:
                user.set_password(new_password)
                db.session.commit()
                
                # Clear all reset-related session data
                session.pop('reset_email', None)
                session.pop('verification_code', None)
                session.pop('code_expiry', None)
                session.pop('password_reset_verified', None)
                
                success_msg = 'Your password has been reset. You can now log in.'
                if is_ajax:
                    return jsonify({
                        'success': success_msg,
                        'redirect': url_for('auth.login')
                    }), 200
                else:
                    flash(success_msg, 'success')
                    return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@auth_bp.route('/set-new-password', methods=['GET', 'POST'])
def set_new_password():
    # Ensure user has verified their identity
    if not session.get('password_reset_verified') or not session.get('reset_email'):
        flash('Please verify your email first.', 'danger')
        return redirect(url_for('auth.reset_password'))
        
    return render_template('reset_password.html', email=session.get('reset_email'))

@auth_bp.route('/debug-login/<username>/<password>')
def debug_login(username, password):
    """Debug route to check login credentials"""
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({
            'user_exists': False,
            'message': f'No user found with username: {username}'
        })
    
    # Use the check_password method instead of direct comparison
    password_match = user.check_password(password)
    
    return jsonify({
        'user_exists': True,
        'username': user.username,
        'email': user.email,
        'password_field_exists': hasattr(user, 'password'),
        'password_stored': user.password[:20] + '...' if hasattr(user, 'password') else 'No password field',
        'password_match': password_match,
        'password_check_method': 'user.check_password method'
    })

@auth_bp.route('/debug-user-model')
def debug_user_model():
    """Debug route to check user model fields"""
    # Get table info from SQLAlchemy
    table = User.__table__
    columns = [column.name for column in table.columns]
    
    # Get a sample user if available
    sample_user = User.query.first()
    sample_data = None
    if sample_user:
        sample_data = {col: getattr(sample_user, col) for col in columns}
        # Don't return password hash in response
        if 'password_hash' in sample_data:
            sample_data['password_hash'] = '[REDACTED]'
    
    return jsonify({
        'model_name': User.__name__,
        'table_name': table.name,
        'columns': columns,
        'sample_data': sample_data
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
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
        
        try:
            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            
            # Add to database
            db.session.add(new_user)
            db.session.commit()
            
            # Log the user in
            login_user(new_user)
            
            return jsonify({
                'success': 'Registration successful!', 
                'redirect': url_for('main.home')
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
    # If not a POST request (which shouldn't happen with this route)
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST', 'DELETE'])
@login_required
def profile():
    """Handle user profile management."""
    user = User.query.get(current_user.id)
    
    if request.method == 'GET':
        return render_template('profile.html', user=user)
    
    elif request.method == 'POST':
        action = request.form.get('action')
        
        # Update username
        if action == 'update_username':
            new_username = request.form.get('username')
            if not new_username:
                return jsonify({'error': 'Username is required'}), 400
                
            # Check if username is already in use by another account
            existing_username = User.query.filter(User.username == new_username, User.id != current_user.id).first()
            if existing_username:
                return jsonify({'error': 'Username already in use'}), 400
            
            user.username = new_username
            db.session.commit()
            return jsonify({'success': 'Username updated successfully!'}), 200
        
        # Update email
        elif action == 'update_email':
            new_email = request.form.get('email')
            if not new_email:
                return jsonify({'error': 'Email is required'}), 400
                
            # Check if email is already in use by another account
            existing_email = User.query.filter(User.email == new_email, User.id != current_user.id).first()
            if existing_email:
                return jsonify({'error': 'Email already in use'}), 400
            
            user.email = new_email
            db.session.commit()
            return jsonify({'success': 'Email updated successfully!'}), 200
        
        # Update password
        elif action == 'update_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_password or not new_password or not confirm_password:
                return jsonify({'error': 'All fields are required'}), 400
                
            if not user.check_password(current_password):
                return jsonify({'error': 'Current password is incorrect'}), 400
                
            if new_password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
                
            user.set_password(new_password)
            db.session.commit()
            return jsonify({'success': 'Password updated successfully!'}), 200
        
        # Handle account deletion via POST
        elif action == 'delete_account':
            # Verify password before deletion for security
            password = request.form.get('password')
            
            if not password:
                return jsonify({'error': 'Password required for account deletion'}), 400
                
            if not user.check_password(password):
                return jsonify({'error': 'Password is incorrect'}), 400
            
            try:
                # Delete user's data
                db.session.delete(user)
                db.session.commit()
                logout_user()
                
                return jsonify({
                    'success': 'Account deleted successfully',
                    'redirect': url_for('main.home')
                }), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'An error occurred: {str(e)}'}), 500
            
        return jsonify({'error': 'Invalid action'}), 400
    
    # Handle DELETE method for account deletion (if needed for API clients)
    elif request.method == 'DELETE':
        # Get JSON data if available
        data = request.get_json(silent=True) or {}
        password = data.get('password')
        
        if not password:
            return jsonify({'error': 'Password required for account deletion'}), 400
            
        if not user.check_password(password):
            return jsonify({'error': 'Password is incorrect'}), 400
        
        try:
            db.session.delete(user)
            db.session.commit()
            logout_user()
            
            return jsonify({
                'success': 'Account deleted successfully',
                'redirect': url_for('main.home')
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
    # Invalid method
    return jsonify({'error': 'Method not allowed'}), 405