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

@main_bp.route('/visualization')
@login_required
def visualization():
    from app.models import UploadedText
    from flask_login import current_user
    from app.models import AnalysisResult
    from app import db
    import json
    from flask import render_template_string
    from datetime import datetime
    
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
        ngram_data = None

    # Render the visualization template with the analysis data
    rendered_template = render_template(
        'visualization.html', 
        sentiment_data=sentiment_data,
        ngram_data=ngram_data, 
        ner_data=ner_data,
        word_freq_data=word_freq_data,
        analyzed_text=text_content
    )
    
    # Save the analysis result to the database if it doesn't already exist
    if upload_id and sentiment_data and ngram_data and ner_data and word_freq_data:
        # Get the uploaded text
        uploaded_text = UploadedText.query.get(upload_id)
        if uploaded_text and uploaded_text.user_id == current_user.id:
            # Check if we already have a result for this specific upload
            existing_result = AnalysisResult.query.filter_by(
                title=f"Analysis of {uploaded_text.title or 'Untitled Text'}",
                owner_id=current_user.id
            ).all()
            
            # Instead of creating a duplicate, delete any existing analysis for this text
            for result in existing_result:
                db.session.delete(result)
            
            # Create new analysis result (fresh copy - no duplicates)
            title = f"Analysis of {uploaded_text.title or 'Untitled Text'}"
            
            # Capture the important parts of the analysis as HTML
            sentiment_section = render_template_string("""
                <h3>Sentiment Analysis</h3>
                <p>Overall Sentiment: <strong>{{ sentiment.sentiment }}</strong></p>
                <p>Compound Score: <strong>{{ sentiment.compound_score|round(2) }}</strong></p>
                <p>Positive: {{ (sentiment.positive_score*100)|round(1) }}%, 
                   Neutral: {{ (sentiment.neutral_score*100)|round(1) }}%, 
                   Negative: {{ (sentiment.negative_score*100)|round(1) }}%</p>
            """, sentiment=sentiment_data)
            
            word_freq_section = render_template_string("""
                <h3>Word Frequency Analysis</h3>
                <p>Total Words: {{ freq.total_words }}</p>
                <p>Unique Words: {{ freq.unique_words }}</p>
                <p>Top 5 Words:</p>
                <ul>
                {% for word in freq.top_words[:5] %}
                    <li>{{ word.word }}: {{ word.count }}</li>
                {% endfor %}
                </ul>
            """, freq=word_freq_data)
            
            # Combine the sections
            content = f"""
                <div class="analysis-result">
                    <h2>Analysis Results for: {uploaded_text.title or 'Untitled'}</h2>
                    <div class="analysis-text">
                        <h3>Analyzed Text Preview</h3>
                        <p>{text_content[:300]}...</p>
                    </div>
                    <div class="analysis-sections">
                        {sentiment_section}
                        {word_freq_section}
                    </div>
                    <p><em>Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</em></p>
                </div>
            """
            
            # Create the analysis result record
            result = AnalysisResult(
                title=title,
                content=content,
                owner_id=current_user.id
            )
            
            # Save to database
            db.session.add(result)
            db.session.commit()
    
    # Return the rendered template
    return rendered_template

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

@main_bp.route('/analyze/<int:upload_id>')
@login_required
def analyze_upload(upload_id):
    """Direct analysis of a previously uploaded text"""
    from app.models import UploadedText
    from flask_login import current_user
    from ..utils.sentiment_utils import get_sentiment_summary
    from ..utils.ngram_utils import get_multiple_ngrams
    from ..utils.ner_utils import perform_ner_analysis
    from ..utils.word_frequency_utils import analyze_word_frequency
    
    try:
        # Get the uploaded text from the database
        upload = UploadedText.query.get_or_404(upload_id)
        
        # Security check - ensure user can only see their own uploads
        if upload.user_id != current_user.id:
            flash("You don't have permission to view this upload", 'danger')
            return redirect(url_for('main.upload'))
            
        # Get the content
        text_content = upload.content
        
        if text_content:
            # Perform all analysis again (or for the first time)
            sentiment_data = get_sentiment_summary(text_content)
            ngram_data = get_multiple_ngrams(text_content)
            ner_data = perform_ner_analysis(text_content)
            word_freq_data = analyze_word_frequency(text_content)
            
            # Store in session for the visualization page
            session['sentiment_data'] = sentiment_data
            session['ngram_data'] = ngram_data
            session['ner_data'] = ner_data
            session['word_freq_data'] = word_freq_data
            session['upload_id'] = upload_id
            session['text_content'] = text_content[:500] + "..." if len(text_content) > 500 else text_content
            
            # Redirect to visualization page
            return redirect(url_for('main.visualization'))
        else:
            flash('No content available for analysis', 'warning')
            return redirect(url_for('main.upload'))
            
    except Exception as e:
        flash(f'Error retrieving upload: {str(e)}', 'danger')
        return redirect(url_for('main.upload'))

