from datetime import datetime
from app import db
from app.models.user import User, UserConnection  # Import UserConnection from user.py

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    upload_id = db.Column(db.Integer, db.ForeignKey('uploaded_texts.id', ondelete='CASCADE'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = db.relationship('User', backref='analysis_results')
    shared_with = db.relationship('SharedAnalysis', backref='analysis', cascade='all, delete-orphan')
    # Relationship to uploaded text - if the upload is deleted, all analysis results will be deleted too
    upload = db.relationship('UploadedText', backref=db.backref('analysis_results', cascade='all, delete-orphan'), single_parent=True)

    def __repr__(self):
        return f'<AnalysisResult {self.title}>'

class SharedAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis_result.id', ondelete='CASCADE'), nullable=False)
    permission = db.Column(db.String(20), default="view-only")
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='shared_with_me')
    
    def __repr__(self):
        return f'<SharedAnalysis {self.analysis_id} shared with {self.user_id}>'

# UserConnection model is now imported from user.py, removing duplicate definition
