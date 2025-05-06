import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk.data

# Download necessary NLTK resources (only needed for first run)
def download_nltk_resources():
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon')

# Initialize NLTK resource download
download_nltk_resources()

def analyze_sentiment(text):
    """
    Use NLTK's VADER sentiment analyzer to analyze text sentiment
    Returns a dictionary containing sentiment scores
    """
    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Get sentiment scores
    sentiment_scores = sia.polarity_scores(text)
    
    # Add text sentiment label
    if sentiment_scores['compound'] >= 0.05:
        sentiment_scores['sentiment'] = 'Positive'
    elif sentiment_scores['compound'] <= -0.05:
        sentiment_scores['sentiment'] = 'Negative'
    else:
        sentiment_scores['sentiment'] = 'Neutral'
    
    return sentiment_scores

def get_sentiment_summary(text):
    """
    Analyze text and return a concise summary
    """
    scores = analyze_sentiment(text)
    
    summary = {
        'compound_score': scores['compound'],
        'sentiment': scores['sentiment'],
        'positive_score': scores['pos'],
        'negative_score': scores['neg'],
        'neutral_score': scores['neu'],
    }
    
    return summary