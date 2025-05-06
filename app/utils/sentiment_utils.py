import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# 下载必要的NLTK资源（仅首次运行时需要）
def download_nltk_resources():
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        nltk.download('vader_lexicon')

# 初始化下载NLTK资源
download_nltk_resources()

def analyze_sentiment(text):
    """
    使用NLTK的VADER情感分析器分析文本情感
    返回一个包含情感分数的字典
    """
    # 初始化情感分析器
    sia = SentimentIntensityAnalyzer()
    
    # 获取情感分数
    sentiment_scores = sia.polarity_scores(text)
    
    # 添加文本情感标签
    if sentiment_scores['compound'] >= 0.05:
        sentiment_scores['sentiment'] = 'Positive'
    elif sentiment_scores['compound'] <= -0.05:
        sentiment_scores['sentiment'] = 'Negative'
    else:
        sentiment_scores['sentiment'] = 'Neutral'
    
    return sentiment_scores

def get_sentiment_summary(text):
    """
    分析文本并返回简洁的总结信息
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