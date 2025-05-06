from flask import Blueprint, render_template, session, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import UploadedText  # Changed from Upload to UploadedText
from app import db
import os

main_bp = Blueprint('main', __name__)

# Define allowed file types
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/share')
@login_required
def share():
    return render_template('share.html')

@main_bp.route('/upload', methods=['GET', 'POST'])
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
                    # Process file upload
                    # ... your file processing code ...
                    
                    # For simplicity, just return success and reload the page
                    flash('File uploaded successfully!', 'success')
                    return redirect(url_for('main.upload'))
                
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
                    
                    # Flash success message and redirect to same page
                    flash('Text content uploaded successfully!', 'success')
                    return redirect(url_for('main.upload'))
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

@main_bp.route('/visualization')
@login_required
def visualization():
    analyzed_text = session.get('analyzedText', 'No text analyzed yet.')
    summary = "The sentiment analysis indicates a generally positive outlook in the submitted content."
    return render_template('visualization.html', analyzed_text=analyzed_text, summary=summary)

@main_bp.route('/protected-route')
@login_required
def protected_route():
    # Your route logic
    pass

@main_bp.route('/api/uploads/history')
@login_required
def get_upload_history():
    try:
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

@main_bp.route('/view/<int:upload_id>')
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

