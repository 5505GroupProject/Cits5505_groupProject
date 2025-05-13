from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import User
from app import db
from app.forms import (
    LoginForm, RegistrationForm, ResetPasswordRequestForm, 
    ResetPasswordForm, UpdateProfileForm, ChangePasswordForm, DeleteAccountForm
)
import secrets
import string
import os
import random
from datetime import datetime, timedelta

# Define blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Invalid username or password'}), 401
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        
        # Handle AJAX vs regular form submission for success case
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            next_page = request.args.get('next')
            redirect_url = next_page or url_for('main.home')
            return jsonify({'success': 'Login successful!', 'redirect': redirect_url}), 200
        else:
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))

    # For AJAX form validation errors
    if form.errors and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'error': form.errors}), 400
        
    return render_template('login.html', form=form)

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
            form = ResetPasswordRequestForm(formdata=None)
            form.email.data = email
            
            if not form.validate_on_submit():
                error_messages = {field: errors[0] for field, errors in form.errors.items()}
                if is_ajax:
                    return jsonify({'error': error_messages}), 400
                else:
                    for field, error in error_messages.items():
                        flash(f"{field.title()}: {error}", 'danger')
                    return redirect(url_for('auth.reset_password'))
            
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
                
            form = ResetPasswordForm()
            form.password.data = request.form.get('new_password')
            form.confirm_password.data = request.form.get('confirm_password')
            
            if not form.validate_on_submit():
                error_messages = {field: errors[0] for field, errors in form.errors.items()}
                if is_ajax:
                    return jsonify({'error': error_messages}), 400
                else:
                    for field, error in error_messages.items():
                        flash(f"{field.title()}: {error}", 'danger')
                    return redirect(url_for('auth.set_new_password'))
                
            # Update the user's password
            user = User.query.filter_by(email=session.get('reset_email')).first()
            if user:
                user.set_password(form.password.data)
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
    
    form = ResetPasswordForm()
    return render_template('reset_password.html', email=session.get('reset_email'), form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    
    if request.method == 'POST':
        # Manual validation for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = RegistrationForm(formdata=None)
            form.username.data = request.form.get('username')
            form.email.data = request.form.get('email')
            form.password.data = request.form.get('password')
            form.confirm_password.data = request.form.get('confirm_password')
            
            if not form.validate():
                error_messages = {field: errors[0] for field, errors in form.errors.items()}
                return jsonify({'error': error_messages}), 400
            
            try:
                # Create new user using form data
                new_user = User(username=form.username.data, email=form.email.data)
                new_user.set_password(form.password.data)
                
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
        
        # Regular form submission (non-AJAX)
        elif form.validate_on_submit():
            new_user = User(username=form.username.data, email=form.email.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Your account has been created!', 'success')
            return redirect(url_for('main.home'))
    
    # If GET request or validation fails for non-AJAX request
    return render_template('login.html', form=form)

@auth_bp.route('/profile', methods=['GET', 'POST', 'DELETE'])
@login_required
def profile():
    """Handle user profile management."""
    user = User.query.get(current_user.id)
    
    # Initialize forms
    update_form = UpdateProfileForm(user.username, user.email)
    password_form = ChangePasswordForm()
    delete_form = DeleteAccountForm()
    
    if request.method == 'GET':
        # Pre-populate form fields
        update_form.username.data = user.username
        update_form.email.data = user.email
        return render_template('profile.html', user=user, update_form=update_form, 
                               password_form=password_form, delete_form=delete_form)
    
    elif request.method == 'POST':
        action = request.form.get('action')
        
        # Update profile picture
        if action == 'update_profile_picture':
            if 'profile_picture' not in request.files:
                return jsonify({'error': 'No file part'}), 400
                
            file = request.files['profile_picture']
            
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
                
            if file and allowed_file(file.filename):
                # Generate a secure filename with timestamp to avoid duplicates
                filename = secure_filename(f"{current_user.username}_{int(datetime.now().timestamp())}{os.path.splitext(file.filename)[1]}")
                
                # Create avatars directory if it doesn't exist
                avatars_dir = os.path.join(current_app.static_folder, 'uploads', 'avatars')
                if not os.path.exists(avatars_dir):
                    os.makedirs(avatars_dir)
                
                # Save the file
                file_path = os.path.join(avatars_dir, filename)
                file.save(file_path)
                
                # Delete old profile picture if exists
                if user.profile_picture:
                    old_file_path = os.path.join(avatars_dir, user.profile_picture)
                    try:
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    except Exception as e:
                        # Just log the error, but continue with updating
                        print(f"Error removing old profile picture: {e}")
                
                # Update user record
                user.profile_picture = filename
                db.session.commit()
                
                return jsonify({
                    'success': 'Profile picture updated successfully!',
                    'profile_picture_url': url_for('static', filename=f'uploads/avatars/{filename}')
                }), 200
            else:
                return jsonify({'error': 'File type not allowed. Please upload a JPG, PNG, or GIF image.'}), 400
        
        # Update username and email
        elif action == 'update_profile':
            # Handle update_form validation
            update_form = UpdateProfileForm(user.username, user.email)
            update_form.username.data = request.form.get('username')
            update_form.email.data = request.form.get('email')
            
            if not update_form.validate_on_submit():
                return jsonify({'error': update_form.errors}), 400
            
            user.username = update_form.username.data
            user.email = update_form.email.data
            db.session.commit()
            return jsonify({'success': 'Profile updated successfully!'}), 200
        
        # Update password
        elif action == 'update_password':
            # Handle password_form validation
            password_form = ChangePasswordForm()
            password_form.current_password.data = request.form.get('current_password')
            password_form.new_password.data = request.form.get('new_password')
            password_form.confirm_password.data = request.form.get('confirm_password')
            
            if not password_form.validate_on_submit():
                return jsonify({'error': password_form.errors}), 400
            
            if not user.check_password(password_form.current_password.data):
                return jsonify({'error': {'current_password': 'Current password is incorrect'}}), 400
                
            user.set_password(password_form.new_password.data)
            db.session.commit()
            return jsonify({'success': 'Password updated successfully!'}), 200
        
        # Handle account deletion via POST
        elif action == 'delete_account':
            # Handle delete_form validation
            delete_form = DeleteAccountForm()
            delete_form.password.data = request.form.get('password')
            delete_form.confirm.data = request.form.get('confirm') == 'on'
            
            if not delete_form.validate_on_submit():
                return jsonify({'error': delete_form.errors}), 400
                
            if not user.check_password(delete_form.password.data):
                return jsonify({'error': {'password': 'Password is incorrect'}}), 400
            
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
        delete_form = DeleteAccountForm()
        delete_form.password.data = data.get('password')
        delete_form.confirm.data = data.get('confirm', False)
        
        if not delete_form.validate():
            return jsonify({'error': delete_form.errors}), 400
            
        if not user.check_password(delete_form.password.data):
            return jsonify({'error': {'password': 'Password is incorrect'}}), 400
        
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

# Debug routes can be kept for development but should be disabled in production
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