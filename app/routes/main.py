from flask import Blueprint, render_template, session, request, redirect, url_for
from flask_login import login_required
from ..utils.ngram_utils import get_multiple_ngrams


main_bp = Blueprint('main', __name__)

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

@main_bp.route('/visualization')
@login_required
def visualization():
    # Get four types of analysis results from session
    sentiment_data = session.get('sentiment_data', None)
    ner_data = session.get('ner_data', None) 
    word_freq_data = session.get('word_freq_data', None)
    
    # Get original text content
    text_content = session.get('text_content', 'No text analyzed yet.')
    
    # Regenerate the N-gram data
    if text_content and text_content != 'No text analyzed yet.':
        ngram_data = get_multiple_ngrams(text_content)

        # cleaning is done before storing the session to prevent contamination
        word_freq_data = {
            'top_words': [{'word': item['ngram'], 'count': item['count']} for item in ngram_data['unigrams']['ngrams']]
        }

        session['word_freq_data'] = word_freq_data
    else:
        ngram_data = None

    return render_template(
        'visualization.html', 
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

