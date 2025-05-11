import nltk
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from collections import Counter
import string
import re

# Download necessary NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Define the symbol set, including Unicode symbols
PUNCTUATION = string.punctuation + '“”‘’—…·–—'
STOP_WORDS = set(nltk.corpus.stopwords.words('english'))

def clean_token(token):
    """
    Clear out all symbols and special characters, and only keep letters and numbers
    """
    # Use regular expressions to match non-letters and non-numbers for filtering
    cleaned_token = re.sub(r'[^a-zA-Z0-9]', '', token)
    return cleaned_token if cleaned_token.lower() not in STOP_WORDS else None


def analyze_ngrams(text, n=2, top_k=10):
    """
    Analyze text and extract top N-grams
    
    Parameters:
    - text: the input text to analyze
    - n: the size of N-gram (default: 2 for bigrams)
    - top_k: number of top N-grams to return
    
    Returns:
    - Dictionary with top N-grams and their counts
    """
    # Tokenize the text
    tokens = word_tokenize(text.lower())

    # Clean the symbols and filter out the empty tokens
    tokens = [clean_token(token) for token in tokens if clean_token(token)]

    # Generate N-grams
    n_grams = list(ngrams(tokens, n))
    
    # Count N-grams
    n_gram_counts = Counter(n_grams)
    
    # Get top K N-grams
    top_n_grams = n_gram_counts.most_common(top_k)
    
    # Format for output - convert tuples to strings for JSON serialization
    result = {
        'n': n,
        'ngrams': [
            {
                'ngram': ' '.join(gram),
                'count': count
            }
            for gram, count in top_n_grams
        ]
    }
    
    return result

def get_multiple_ngrams(text):
    """
    Get analysis for uni-grams, bi-grams, and tri-grams
    
    Parameters:
    - text: the input text to analyze
    
    Returns:
    - Dictionary with results for uni-grams, bi-grams, and tri-grams
    """
    unigrams = analyze_ngrams(text, n=1, top_k=10)
    bigrams = analyze_ngrams(text, n=2, top_k=10)
    trigrams = analyze_ngrams(text, n=3, top_k=10)
    
    return {
        'unigrams': unigrams,
        'bigrams': bigrams,
        'trigrams': trigrams
    }
