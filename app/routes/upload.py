from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import UploadedText
from app import db
from flask_wtf.csrf import validate_csrf, ValidationError
from app.utils.sentiment_utils import get_sentiment_summary
from app.utils.ngram_utils import get_multiple_ngrams
from app.utils.ner_utils import perform_ner_analysis
from app.utils.word_frequency_utils import analyze_word_frequency
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
    # For GET requests, always explicitly query the latest uploads
    if request.method == 'GET':
        # Force database query to get fresh data, regardless of session state
        if current_user and hasattr(current_user, 'id'):
            recent_uploads = UploadedText.query.filter_by(user_id=current_user.id).order_by(UploadedText.created_at.desc()).all()
        else:
            recent_uploads = []
            
        return render_template('upload.html', uploads=recent_uploads)
    
    # From here on, we're handling POST requests
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
                
                # Perform N-gram analysis
                ngram_data = get_multiple_ngrams(file_content)
                
                # Perform NER analysis
                ner_data = perform_ner_analysis(file_content)
                
                # Perform word frequency analysis
                word_freq_data = analyze_word_frequency(file_content)
                
                # Store data in session for visualization page
                session['sentiment_data'] = sentiment_data
                session['ngram_data'] = ngram_data
                session['ner_data'] = ner_data
                session['word_freq_data'] = word_freq_data
                session['text_content'] = file_content[:1000] + '...' if len(file_content) > 1000 else file_content
                session['upload_id'] = new_upload.id
                
                # Flash success message and redirect to visualization page
                flash('File uploaded and analyzed successfully!', 'success')
                return redirect(url_for('main.visualization'))
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
                
                # Perform N-gram analysis
                ngram_data = get_multiple_ngrams(text_content)
                
                # Perform NER analysis
                ner_data = perform_ner_analysis(text_content)
                
                # Perform word frequency analysis
                word_freq_data = analyze_word_frequency(text_content)
                
                # Store data in session for visualization page
                session['sentiment_data'] = sentiment_data
                session['ngram_data'] = ngram_data
                session['ner_data'] = ner_data
                session['word_freq_data'] = word_freq_data
                session['text_content'] = text_content[:1000] + '...' if len(text_content) > 1000 else text_content
                session['upload_id'] = new_upload.id
                
                # Flash success message and redirect to visualization page
                flash('Text content uploaded and analyzed successfully!', 'success')
                return redirect(url_for('main.visualization'))
            else:
                flash('No content provided!', 'danger')
        
        else:
            flash('No data submitted!', 'danger')
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload error: {str(e)}")
        flash(f'Error: {str(e)}', 'danger')
    
    # If we get here, it means there was an error or invalid submission
    # Redirect back to the upload page (this prevents form resubmission on refresh)
    return redirect(url_for('upload.upload'))

# Added new route to display sentiment analysis and N-gram analysis results
@upload_bp.route('/test-page', methods=['GET'])
@login_required
def test_page():
    # Get analysis data from session
    sentiment_data = session.get('sentiment_data')
    ngram_data = session.get('ngram_data')
    ner_data = session.get('ner_data')
    word_freq_data = session.get('word_freq_data')
    text_content = session.get('text_content')
    upload_id = session.get('upload_id')
    
    # Render test_page template and pass analysis results
    return render_template('test_page.html', 
                          sentiment_data=sentiment_data,
                          ngram_data=ngram_data,
                          ner_data=ner_data,
                          word_freq_data=word_freq_data,
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
        
        # Perform text analysis
        sentiment_data = get_sentiment_summary(content)
        ngram_data = get_multiple_ngrams(content)
        ner_data = perform_ner_analysis(content)
        word_freq_data = analyze_word_frequency(content)
        
        return jsonify({
            'success': True,
            'message': 'Content uploaded successfully!',
            'sentiment_data': sentiment_data,
            'ngram_data': ngram_data,
            'ner_data': ner_data,
            'word_freq_data': word_freq_data,
            'upload_id': new_upload.id
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
        
        # Perform text analysis
        sentiment_data = get_sentiment_summary(file_content)
        ngram_data = get_multiple_ngrams(file_content)
        ner_data = perform_ner_analysis(file_content)
        word_freq_data = analyze_word_frequency(file_content)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'upload_id': new_upload.id,
            'sentiment_data': sentiment_data,
            'ngram_data': ngram_data,
            'ner_data': ner_data,
            'word_freq_data': word_freq_data,
            'content': file_content[:1000] + '...' if len(file_content) > 1000 else file_content
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

@upload_bp.route('/delete/<int:upload_id>', methods=['DELETE'])
@login_required
def delete_upload(upload_id):
    """Delete a user's upload."""
    try:
        # Get the CSRF token from the header
        csrf_token = request.headers.get('X-CSRFToken')
        
        # Validate CSRF token
        try:
            validate_csrf(csrf_token)
        except ValidationError:
            return jsonify({
                'success': False,
                'error': 'Invalid CSRF token. Please refresh the page and try again.'
            }), 400
            
        upload = UploadedText.query.get_or_404(upload_id)
        
        # Security check - ensure user can only delete their own uploads
        if upload.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': "You don't have permission to delete this upload"
            }), 403
            
        # Delete the upload
        db.session.delete(upload)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Upload deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        current_app.logger.error(f"Delete upload error: {str(e)}\n{error_details}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500