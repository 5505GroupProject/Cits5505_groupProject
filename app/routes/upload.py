from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import UploadedText
from app import db
from flask_wtf.csrf import validate_csrf, ValidationError
import os
import traceback

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route('/text', methods=['POST'])
@login_required
def upload_text():
    try:
        content = request.form.get('content')
        if not content or len(content.strip()) == 0:
            return jsonify({'error': 'No content provided'}), 400
            
        new_upload = UploadedText(
            user_id=current_user.id,
            content=content,
            filename='text_input.txt',
            file_type='text'
        )
        
        db.session.add(new_upload)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Content uploaded successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/file', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files are allowed'}), 400
        
        try:
            file_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({'error': 'File encoding not supported. Please use UTF-8 encoded text files.'}), 400
            
        if len(file_content.strip()) == 0:
            return jsonify({'error': 'File is empty'}), 400
            
        new_upload = UploadedText(
            user_id=current_user.id,
            content=file_content,
            filename=secure_filename(file.filename),
            file_type='file'
        )
        
        db.session.add(new_upload)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'upload_id': new_upload.id,
            'content': file_content
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
        uploads = UploadedText.query.filter_by(user_id=current_user.id).order_by(UploadedText.created_at.desc()).all()
        
        upload_list = [{
            'id': upload.id,
            'filename': upload.filename,
            'created_at': upload.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'preview': upload.content[:100] + '...' if len(upload.content) > 100 else upload.content,
            'file_type': upload.file_type
        } for upload in uploads]
        
        return jsonify({
            'success': True,
            'uploads': upload_list
        }), 200
        
    except Exception as e:
        error_details = traceback.format_exc()
        current_app.logger.error(f"List uploads error: {str(e)}\n{error_details}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500