import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sentinews.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB limit
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or '240e271a14ab436bb96c9baf3db79133'  # Get from https://newsapi.org/
    
    # Multiple news API keys for fallback options
    GNEWS_API_KEY = os.environ.get('GNEWS_API_KEY') or ''  # Get from https://gnews.io/
    NEWSDATA_API_KEY = os.environ.get('NEWSDATA_API_KEY') or ''  # Get from https://newsdata.io/