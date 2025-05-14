from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..utils.ngram_utils import get_multiple_ngrams
from ..utils.word_frequency_utils import analyze_word_frequency
from app.models import UploadedText, AnalysisResult, SharedAnalysis
from app import db
import json
import uuid
import hashlib


main_bp = Blueprint('main', __name__)

# Helper function to generate a URL path
def _generate_url_path():
    """Generate a unique URL path for an analysis result"""
    unique_id = str(uuid.uuid4())
    hash_id = hashlib.md5(f"{unique_id}-{current_user.id}".encode()).hexdigest()[:10]
    return f"{current_user.id}-{hash_id}"

# Helper function to process text content and generate analysis data
def _process_text_content(text_content):
    """Process text content and generate analysis data"""
    result = {
        'ngram_data': None,
        'word_freq_data': None
    }
    
    if text_content and text_content != 'No text analyzed yet.':
        # Generate N-gram data
        result['ngram_data'] = get_multiple_ngrams(text_content)
        
        # Generate word frequency data
        result['word_freq_data'] = analyze_word_frequency(text_content)
        
        # Store word frequency data in session
        session['word_freq_data'] = result['word_freq_data']
    
    return result

# Helper function to load analysis data from an analysis object
def _load_analysis_data(analysis):
    """Load and parse analysis data from an analysis object"""
    result = {
        'sentiment_data': None,
        'ngram_data': None,
        'ner_data': None,
        'word_freq_data': None
    }
    
    if analysis:
        if analysis.sentiment_data:
            result['sentiment_data'] = json.loads(analysis.sentiment_data)
        
        if analysis.ngram_data:
            result['ngram_data'] = json.loads(analysis.ngram_data)
        
        if analysis.ner_data:
            result['ner_data'] = json.loads(analysis.ner_data)
        
        if analysis.word_freq_data:
            result['word_freq_data'] = json.loads(analysis.word_freq_data)
    
    return result

# Helper function to get previous analyses
def _get_previous_analyses():
    """Get previous analysis results for the current user"""
    return AnalysisResult.query.filter_by(owner_id=current_user.id) \
        .order_by(AnalysisResult.created_at.desc()).limit(5).all()

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/analyze')
@main_bp.route('/analysis/<string:url_path>')
@login_required
def analyze(url_path=None):
    """
    Unified route to handle both new analysis and viewing existing analysis
    If url_path is provided, it loads an existing analysis
    If no url_path, it creates a new analysis based on upload_id or session data
    """
    # Check if we're viewing an existing analysis
    if url_path:
        # Get the analysis result
        analysis = AnalysisResult.query.filter_by(url_path=url_path).first_or_404()
        
        # Check if the current user owns the analysis or has shared access
        if analysis.owner_id != current_user.id:
            # Check if the analysis is shared with the current user
            shared = SharedAnalysis.query.filter_by(
                user_id=current_user.id,
                analysis_id=analysis.id
            ).first()
            if not shared:
                flash('You do not have permission to view this analysis', 'danger')
                return redirect(url_for('main.home'))
        
        # Load analysis data from the analysis object
        analysis_data = _load_analysis_data(analysis)
        
        # Get previous analysis results for the current user
        previous_analyses = _get_previous_analyses()
        
        # Render the analysis template with the data
        return render_template(
            'analyze.html',
            sentiment_data=analysis_data['sentiment_data'],
            ngram_data=analysis_data['ngram_data'],
            ner_data=analysis_data['ner_data'],
            word_freq_data=analysis_data['word_freq_data'],
            analyzed_text=analysis.content,
            is_saved_analysis=True,
            analysis=analysis,
            previous_analyses=previous_analyses
        )
    
    # Creating a new analysis based on upload_id or session data
    # Get analysis results from session
    sentiment_data = session.get('sentiment_data', None)
    ner_data = session.get('ner_data', None) 
    word_freq_data = session.get('word_freq_data', None)
    
    # Get the upload_id from the session
    upload_id = session.get('upload_id', None)
    text_content = 'No text analyzed yet.'
    ngram_data = None
    
    # Try to get the text content from database if possible
    if upload_id:
        uploaded_text = UploadedText.query.get(upload_id)
        if uploaded_text and uploaded_text.user_id == current_user.id:
            # Get the full text directly from the database
            text_content = uploaded_text.content
            
            # Store the analysis results in the database
            try:
                # Process the text content to get analysis data
                analysis_results = _process_text_content(text_content)
                ngram_data = analysis_results['ngram_data']
                word_freq_data = analysis_results['word_freq_data']
                
                # Convert data to JSON for storage
                sentiment_json = json.dumps(sentiment_data) if sentiment_data else None
                ner_json = json.dumps(ner_data) if ner_data else None
                ngram_json = json.dumps(ngram_data) if ngram_data else None
                word_freq_json = json.dumps(word_freq_data) if word_freq_data else None
                
                # Create a title for the analysis result
                title = f"Analysis of {uploaded_text.title}"
                
                # Check if an analysis result already exists
                existing_analysis = AnalysisResult.query.filter_by(
                    upload_id=upload_id, 
                    owner_id=current_user.id
                ).first()
                
                if existing_analysis:
                    # Update the existing analysis result
                    existing_analysis.content = text_content
                    existing_analysis.sentiment_data = sentiment_json
                    existing_analysis.ngram_data = ngram_json
                    existing_analysis.ner_data = ner_json
                    existing_analysis.word_freq_data = word_freq_json
                    
                    # If URL path doesn't exist, create one
                    if not existing_analysis.url_path:
                        existing_analysis.url_path = _generate_url_path()
                    
                    url_path = existing_analysis.url_path
                else:
                    # Create a unique URL path
                    url_path = _generate_url_path()
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
                flash('Analysis results saved to database', 'success')
                
                # Redirect to the unique URL path
                return redirect(url_for('main.analyze', url_path=url_path))
            except Exception as e:
                flash(f'Error saving analysis results: {str(e)}', 'danger')
                db.session.rollback()
        else:
            # Fallback to session data
            text_content = session.get('text_content', 'No text analyzed yet.')
            
            # Process the text content
            analysis_results = _process_text_content(text_content)
            ngram_data = analysis_results['ngram_data']
            word_freq_data = analysis_results['word_freq_data']
    else:
        # Fallback to session data
        text_content = session.get('text_content', 'No text analyzed yet.')
        
        # Process the text content
        analysis_results = _process_text_content(text_content)
        ngram_data = analysis_results['ngram_data']
        word_freq_data = analysis_results['word_freq_data']
    
    # Get previous analysis results for the current user
    previous_analyses = _get_previous_analyses()
    
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

# The view_analysis_by_path route has been merged with the analyze route

