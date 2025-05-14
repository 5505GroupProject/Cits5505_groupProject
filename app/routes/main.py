from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import login_required
from ..utils.ngram_utils import get_multiple_ngrams
from ..utils.word_frequency_utils import analyze_word_frequency


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/analyze')
@login_required
def analyze():
    from app.models import UploadedText
    from flask_login import current_user
    
    # Get four types of analysis results from session
    sentiment_data = session.get('sentiment_data', None)
    ner_data = session.get('ner_data', None) 
    word_freq_data = session.get('word_freq_data', None)
    
    # Get the upload_id from the session
    upload_id = session.get('upload_id', None)
    
    # Try to get the full text content from the database if possible
    if upload_id:
        uploaded_text = UploadedText.query.get(upload_id)
        if uploaded_text and uploaded_text.user_id == current_user.id:
            # Get the full text directly from the database
            text_content = uploaded_text.content
        else:
            # Fallback to session data
            text_content = session.get('text_content', 'No text analyzed yet.')
    else:
        # Fallback to session data
        text_content = session.get('text_content', 'No text analyzed yet.')
    
    # Regenerate the N-gram data
    if text_content and text_content != 'No text analyzed yet.':
        ngram_data = get_multiple_ngrams(text_content)

        # Use the proper word frequency analysis function
        word_freq_data = analyze_word_frequency(text_content)

        session['word_freq_data'] = word_freq_data
    else:
        ngram_data = None    # Render the analysis template with the analysis data
    return render_template(
        'analyze.html', 
        sentiment_data=sentiment_data,
        ngram_data=ngram_data, 
        ner_data=ner_data,
        word_freq_data=word_freq_data,
        analyzed_text=text_content
    )

@main_bp.route('/protected-route')
@login_required
def protected_route():
    # Your route logic
    pass

@main_bp.route('/upload')
@login_required
def upload():
    return render_template('upload.html')

@main_bp.route('/profile')
@login_required
def profile():
    """Redirect to the auth profile page."""
    return redirect(url_for('auth.profile'))

@main_bp.route('/cleanup-orphaned-results')
@login_required
def cleanup_orphaned_results():
    """Utility route to clean up orphaned analysis results"""
    from app.models import AnalysisResult
    from app import db
    from flask_login import current_user
    
    try:
        # Get all analysis results for the current user
        results = AnalysisResult.query.filter_by(owner_id=current_user.id).all()
        
        # Counter for deleted items
        deleted_count = 0
        
        # Delete the results that have no associated upload
        for result in results:
            if result.upload_id is None:
                db.session.delete(result)
                deleted_count += 1
        
        # Commit the changes
        db.session.commit()
        
        flash(f'Successfully cleaned up {deleted_count} orphaned analysis results', 'success')
        return redirect(url_for('share.shared_page'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error cleaning up orphaned results: {str(e)}', 'danger')
        return redirect(url_for('main.home'))

