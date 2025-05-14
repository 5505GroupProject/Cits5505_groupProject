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
    from app.models import UploadedText, AnalysisResult
    from flask_login import current_user
    from app import db
    import json
    
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
            
            # Store the analysis results in the database
            try:
                # Convert the data structures to JSON for storage
                sentiment_json = json.dumps(sentiment_data) if sentiment_data else None
                ner_json = json.dumps(ner_data) if ner_data else None
                word_freq_json = json.dumps(word_freq_data) if word_freq_data else None
                
                # Create a title for the analysis result using the uploaded text title
                title = f"Analysis of {uploaded_text.title}"
                
                # Check if an analysis result already exists for this upload
                existing_analysis = AnalysisResult.query.filter_by(upload_id=upload_id, owner_id=current_user.id).first()
                
                # Regenerate the N-gram data
                if text_content and text_content != 'No text analyzed yet.':
                    ngram_data = get_multiple_ngrams(text_content)
                    ngram_json = json.dumps(ngram_data)
                    
                    # Use the proper word frequency analysis function
                    word_freq_data = analyze_word_frequency(text_content)
                    word_freq_json = json.dumps(word_freq_data)
                    
                    session['word_freq_data'] = word_freq_data
                else:
                    ngram_data = None
                    ngram_json = None
                  # Generate a unique URL path
                import uuid
                import hashlib
                
                if existing_analysis:
                    # Update the existing analysis result
                    existing_analysis.content = text_content
                    existing_analysis.sentiment_data = sentiment_json
                    existing_analysis.ngram_data = ngram_json
                    existing_analysis.ner_data = ner_json
                    existing_analysis.word_freq_data = word_freq_json
                    
                    # If URL path doesn't exist, create one
                    if not existing_analysis.url_path:
                        unique_id = str(uuid.uuid4())
                        hash_id = hashlib.md5(f"{unique_id}-{current_user.id}".encode()).hexdigest()[:10]
                        existing_analysis.url_path = f"{current_user.id}-{hash_id}"
                    
                    analysis_id = existing_analysis.id
                    url_path = existing_analysis.url_path
                else:
                    # Create a unique URL path
                    unique_id = str(uuid.uuid4())
                    hash_id = hashlib.md5(f"{unique_id}-{current_user.id}".encode()).hexdigest()[:10]
                    url_path = f"{current_user.id}-{hash_id}"
                    
                    # Create a new analysis result
                    new_analysis = AnalysisResult(
                        title=title,
                        content=text_content,
                        sentiment_data=sentiment_json,
                        ngram_data=ngram_json,
                        ner_data=ner_json,
                        word_freq_data=word_freq_json,
                        owner_id=current_user.id,
                        upload_id=upload_id,
                        url_path=url_path
                    )
                    db.session.add(new_analysis)
                    
                db.session.commit()
                
                # Get the analysis ID for redirection
                if not existing_analysis:
                    analysis_id = new_analysis.id
                
                flash('Analysis results saved to database', 'success')
                
                # Redirect to the unique URL
                return redirect(url_for('main.view_analysis_by_path', url_path=url_path))
            except Exception as e:
                flash(f'Error saving analysis results: {str(e)}', 'danger')
                db.session.rollback()
        else:
            # Fallback to session data
            text_content = session.get('text_content', 'No text analyzed yet.')
            
            # Regenerate the N-gram data
            if text_content and text_content != 'No text analyzed yet.':
                ngram_data = get_multiple_ngrams(text_content)
                word_freq_data = analyze_word_frequency(text_content)
                session['word_freq_data'] = word_freq_data
            else:
                ngram_data = None
    else:
        # Fallback to session data
        text_content = session.get('text_content', 'No text analyzed yet.')
        
        # Regenerate the N-gram data
        if text_content and text_content != 'No text analyzed yet.':
            ngram_data = get_multiple_ngrams(text_content)
            word_freq_data = analyze_word_frequency(text_content)
            session['word_freq_data'] = word_freq_data
        else:
            ngram_data = None
            
    # Get previous analysis results for the current user
    previous_analyses = AnalysisResult.query.filter_by(owner_id=current_user.id).order_by(AnalysisResult.created_at.desc()).limit(5).all()
    
    # Render the analysis template with the analysis data
    return render_template(
        'analyze.html', 
        sentiment_data=sentiment_data,
        ngram_data=ngram_data, 
        ner_data=ner_data,
        word_freq_data=word_freq_data,
        analyzed_text=text_content,
        previous_analyses=previous_analyses
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

@main_bp.route('/analysis/<string:url_path>')
@login_required
def view_analysis_by_path(url_path):
    """View a specific analysis result by its URL path"""
    from app.models import AnalysisResult
    from flask_login import current_user
    import json
    
    # Get the analysis result
    analysis = AnalysisResult.query.filter_by(url_path=url_path).first_or_404()
    
    # Check if the current user owns the analysis or has shared access
    if analysis.owner_id != current_user.id:
        from app.models import SharedAnalysis
        # Check if the analysis is shared with the current user
        shared = SharedAnalysis.query.filter_by(
            user_id=current_user.id,
            analysis_id=analysis.id
        ).first()
        if not shared:
            flash('You do not have permission to view this analysis', 'danger')
            return redirect(url_for('main.home'))
    
    # Parse the JSON data
    sentiment_data = None
    ngram_data = None
    ner_data = None
    word_freq_data = None
    
    if analysis.sentiment_data:
        sentiment_data = json.loads(analysis.sentiment_data)
    
    if analysis.ngram_data:
        ngram_data = json.loads(analysis.ngram_data)
    
    if analysis.ner_data:
        ner_data = json.loads(analysis.ner_data)
    
    if analysis.word_freq_data:
        word_freq_data = json.loads(analysis.word_freq_data)
    
    # Get previous analysis results for the current user
    previous_analyses = AnalysisResult.query.filter_by(owner_id=current_user.id).order_by(AnalysisResult.created_at.desc()).limit(5).all()
    
    # Render the analysis template with the data
    return render_template(
        'analyze.html',
        sentiment_data=sentiment_data,
        ngram_data=ngram_data,
        ner_data=ner_data,
        word_freq_data=word_freq_data,
        analyzed_text=analysis.content,
        is_saved_analysis=True,
        analysis=analysis,
        previous_analyses=previous_analyses
    )

