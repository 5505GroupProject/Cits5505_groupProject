from datetime import datetime
from app import db

class UploadedText(db.Model):
    __tablename__ = 'uploaded_texts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=True)
    file_type = db.Column(db.String(50), default='text')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UploadedText {self.id}>'