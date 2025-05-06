from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import UploadedText
from app import db
from flask_wtf.csrf import validate_csrf, ValidationError
from app.utils.sentiment_utils import get_sentiment_summary
import os
import traceback

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

# Define allowed file types
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['GET', 'POST'])
@login_required
def upload():
    # Get recent uploads for display regardless of whether it's GET or POST
    recent_uploads = UploadedText.query.filter_by(user_id=current_user.id).order_by(UploadedText.created_at.desc()).all()
    
    if request.method == 'POST':
        try:
            # Get title if provided
            title = request.form.get('title', '').strip() or None
            
            # Handle file upload
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename.strip() != '':
                    if not file.filename.endswith('.txt'):
                        flash('Only .txt files are supported!', 'danger')
                        return redirect(url_for('upload.upload'))
                    
                    # Read and process the file content
                    try:
                        file_content = file.read().decode('utf-8')
                    except UnicodeDecodeError:
                        flash('File encoding not supported. Please use UTF-8 encoded text files.', 'danger')
                        return redirect(url_for('upload.upload'))
                    
                    if len(file_content.strip()) == 0:
                        flash('Uploaded file is empty!', 'danger')
                        return redirect(url_for('upload.upload'))
                    
                    # Create the UploadedText entry
                    new_upload = UploadedText(
                        user_id=current_user.id,
                        title=title or secure_filename(file.filename),
                        content=file_content,
                        filename=secure_filename(file.filename),
                        file_type='file'
                    )
                    
                    db.session.add(new_upload)
                    db.session.commit()
                    
                    # Perform sentiment analysis
                    sentiment_data = get_sentiment_summary(file_content)
                    
                    # Store data in session for test page
                    session['sentiment_data'] = sentiment_data
                    session['text_content'] = file_content[:1000] + '...' if len(file_content) > 1000 else file_content
                    session['upload_id'] = new_upload.id
                    
                    # Flash success message and redirect to test page
                    flash('File uploaded and analyzed successfully!', 'success')
                    return redirect(url_for('upload.test_page'))
                else:
                    flash('No file selected!', 'warning')
                
            # Handle text upload
            elif 'content' in request.form:
                text_content = request.form.get('content', '').strip()
                if text_content:
                    # Create new upload
                    new_upload = UploadedText(
                        user_id=current_user.id,
                        title=title or 'Text Upload',
                        content=text_content,
                        filename='text_input.txt',
                        file_type='text'
                    )
                    db.session.add(new_upload)
                    db.session.commit()
                    
                    # Perform sentiment analysis
                    sentiment_data = get_sentiment_summary(text_content)
                    
                    # Store data in session for test page
                    session['sentiment_data'] = sentiment_data
                    session['text_content'] = text_content[:1000] + '...' if len(text_content) > 1000 else text_content
                    session['upload_id'] = new_upload.id
                    
                    # Flash success message and redirect to test page
                    flash('Text content uploaded and analyzed successfully!', 'success')
                    return redirect(url_for('upload.test_page'))
                else:
                    flash('No content provided!', 'danger')
            
            else:
                flash('No data submitted!', 'danger')
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Upload error: {str(e)}")
            flash(f'Error: {str(e)}', 'danger')

    # Render template with uploads for both GET and unsuccessful POST
    return render_template('upload.html', uploads=recent_uploads)

# 添加新路由用于显示情感分析结果
@upload_bp.route('/test-page', methods=['GET'])
@login_required
def test_page():
    # 从session获取情感分析数据
    sentiment_data = session.get('sentiment_data')
    text_content = session.get('text_content')
    upload_id = session.get('upload_id')
    
    # 渲染test_page模板并传入分析结果
    return render_template('test_page.html', 
                          sentiment_data=sentiment_data,
                          text_content=text_content,
                          upload_id=upload_id)

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

@upload_bp.route('/history', methods=['GET'])
@login_required
def get_upload_history():
    try:
        # Check if current_user is authenticated and has an id
        if not current_user or not hasattr(current_user, 'id'):
            current_app.logger.error("User not properly authenticated for upload history")
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
            
        uploads = UploadedText.query.filter_by(user_id=current_user.id).order_by(UploadedText.created_at.desc()).all()
        
        uploads_list = []
        for upload in uploads:
            # Handle possible None values in content
            content = upload.content or ""
            preview = content[:100] + '...' if len(content) > 100 else content
            
            uploads_list.append({
                'id': upload.id,
                'title': getattr(upload, 'title', None) or 'Untitled',
                'filename': getattr(upload, 'filename', None) or 'text_input.txt',
                'created_at': upload.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'preview': preview,
                'file_type': getattr(upload, 'file_type', 'text')
            })
        
        return jsonify({
            'success': True,
            'uploads': uploads_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in upload history: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Could not retrieve upload history: {str(e)}'
        }), 500

@upload_bp.route('/view/<int:upload_id>', methods=['GET'])
@login_required
def view_upload(upload_id):
    try:
        upload = UploadedText.query.get_or_404(upload_id)
        
        # Security check - ensure user can only see their own uploads
        if upload.user_id != current_user.id:
            return render_template('error.html', message="You don't have permission to view this upload"), 403
            
        return render_template('view_upload.html', upload=upload)
        
    except Exception as e:
        current_app.logger.error(f"Error viewing upload: {str(e)}")
        return render_template('error.html', message=f"An error occurred: {str(e)}"), 500