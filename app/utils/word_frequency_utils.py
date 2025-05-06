import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string

def download_nltk_resources():
    """
    Download NLTK resources needed for word frequency analysis
    """
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

# Initialize NLTK resource download
download_nltk_resources()

def analyze_word_frequency(text, top_k=20):
    """
    Analyze word frequency in text
    
    Parameters:
    text (str): Text to analyze
    top_k (int): Number of top frequency words to return
    
    Returns:
    dict: Dictionary containing most common words and their frequencies
    """
    # Convert to lowercase and tokenize
    tokens = word_tokenize(text.lower())
    
    # Remove punctuation and special characters
    tokens = [word for word in tokens if word not in string.punctuation]
    
    # Remove stopwords (common words with no significant meaning)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Calculate word frequencies
    word_counts = Counter(filtered_tokens)
    
    # Get top K most common words
    top_words = word_counts.most_common(top_k)
    
    return {
        'total_words': len(tokens),
        'unique_words': len(set(tokens)),
        'top_words': [{'word': word, 'count': count} for word, count in top_words]
    }