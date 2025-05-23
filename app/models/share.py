from datetime import datetime
from app import db
import json
from app.models.user import User, UserConnection  # Import UserConnection from user.py

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_result'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Original text content
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    upload_id = db.Column(db.Integer, db.ForeignKey('uploaded_texts.id', ondelete='CASCADE'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    url_path = db.Column(db.String(100), nullable=True, unique=True)  # Unique URL path for direct access
    
    # Analysis results stored as JSON
    sentiment_data = db.Column(db.Text, nullable=True)
    ngram_data = db.Column(db.Text, nullable=True)
    ner_data = db.Column(db.Text, nullable=True)
    word_freq_data = db.Column(db.Text, nullable=True)
    
    # Relationships
    owner = db.relationship('User', backref='analysis_results')
    shared_with = db.relationship('SharedAnalysis', backref='analysis', cascade='all, delete-orphan')
    # Relationship to uploaded text - if the upload is deleted, all analysis results will be deleted too
    upload = db.relationship('UploadedText', backref=db.backref('analysis_results', cascade='all, delete-orphan'), single_parent=True)

    def __repr__(self):
        return f'<AnalysisResult {self.title}>'
        
    @property
    def sentiment_json(self):
        """Return sentiment_data as a Python object"""
        if self.sentiment_data:
            return json.loads(self.sentiment_data)
        return None
    
    @property
    def ngram_json(self):
        """Return ngram_data as a Python object"""
        if self.ngram_data:
            return json.loads(self.ngram_data)
        return None
    
    @property
    def ner_json(self):
        """Return ner_data as a Python object"""
        if self.ner_data:
            return json.loads(self.ner_data)
        return None
    
    @property
    def word_freq_json(self):
        """Return word_freq_data as a Python object"""
        if self.word_freq_data:
            return json.loads(self.word_freq_data)
        return None

class SharedAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_result.id', ondelete='CASCADE'), nullable=False)
    sharer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # ID of the user who shared this analysis
    permission = db.Column(db.String(20), default="view-only")
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Duplicated fields from AnalysisResult for efficient access
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=True)  
    original_owner_id = db.Column(db.Integer, nullable=True)
    upload_id = db.Column(db.Integer, nullable=True)
    analysis_created_at = db.Column(db.DateTime, nullable=True)
    url_path = db.Column(db.String(100), nullable=True)
    
    # Analysis results stored as JSON
    sentiment_data = db.Column(db.Text, nullable=True)
    ngram_data = db.Column(db.Text, nullable=True)
    ner_data = db.Column(db.Text, nullable=True)
    word_freq_data = db.Column(db.Text, nullable=True)
      # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='shared_with_me')
    sharer = db.relationship('User', foreign_keys=[sharer_id], backref='shared_by_me')
    
    def __repr__(self):
        return f'<SharedAnalysis {self.analysis_id} shared with {self.user_id}>'
        
    @property
    def sentiment_json(self):
        """Return sentiment_data as a Python object"""
        if self.sentiment_data:
            return json.loads(self.sentiment_data)
        return None
    
    @property
    def ngram_json(self):
        """Return ngram_data as a Python object"""
        if self.ngram_data:
            return json.loads(self.ngram_data)
        return None
    
    @property
    def ner_json(self):
        """Return ner_data as a Python object"""
        if self.ner_data:
            return json.loads(self.ner_data)
        return None
    
    @property
    def word_freq_json(self):
        """Return word_freq_data as a Python object"""
        if self.word_freq_data:
            return json.loads(self.word_freq_data)
        return None

# UserConnection model is now imported from user.py, removing duplicate definition
