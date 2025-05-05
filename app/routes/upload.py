from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Upload
from app import db
from flask_wtf.csrf import validate_csrf
import os
import traceback

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route('/text', methods=['POST'])
@login_required
def upload_text():
    """Handle text upload from textarea."""
    try:
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        validate_csrf(csrf_token)
        
        # Get form data
        content = request.form.get('content')
        
        # Validate content
        if not content or len(content.strip()) == 0:
            return jsonify({'error': 'No content provided'}), 400
            
        # Create new upload record
        new_upload = Upload(
            user_id=current_user.id,
            content=content,
            filename=None  # No filename for direct text input
        )
        
        db.session.add(new_upload)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Content uploaded successfully',
            'upload_id': new_upload.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        current_app.logger.error(f"Text upload error: {str(e)}\n{error_details}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@upload_bp.route('/file', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload (.txt files)."""
    try:
        # Check if file part exists
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Check file extension
        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files are allowed'}), 400
        
        # Read file content
        try:
            file_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({'error': 'File encoding not supported. Please use UTF-8 encoded text files.'}), 400
            
        # Ensure content is not empty
        if len(file_content.strip()) == 0:
            return jsonify({'error': 'File is empty'}), 400
            
        # Create new upload record
        new_upload = Upload(
            user_id=current_user.id,
            content=file_content,
            filename=secure_filename(file.filename)
        )
        
        db.session.add(new_upload)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'upload_id': new_upload.id,
            'content': file_content  # Return the content to display in textarea
        }), 200
        
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        current_app.logger.error(f"File upload error: {str(e)}\n{error_details}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@upload_bp.route('/list', methods=['GET'])
@login_required
def list_uploads():
    """Get list of user's uploads."""
    try:
        uploads = Upload.query.filter_by(user_id=current_user.id).order_by(Upload.created_at.desc()).all()
        
        upload_list = [{
            'id': upload.id,
            'filename': upload.filename if upload.filename else 'Direct text input',
            'created_at': upload.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'preview': upload.content[:100] + '...' if len(upload.content) > 100 else upload.content
        } for upload in uploads]
        
        return jsonify({
            'success': True,
            'uploads': upload_list
        }), 200
        
    except Exception as e:
        error_details = traceback.format_exc()
        current_app.logger.error(f"List uploads error: {str(e)}\n{error_details}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500