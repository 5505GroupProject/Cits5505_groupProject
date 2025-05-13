from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

# Setup Flask-Login's user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Add the password field if it doesn't exist
    password_hash = db.Column(db.String(256))  # Store password hash, not plaintext
    # Profile picture path
    profile_picture = db.Column(db.String(200), nullable=True, default=None)
    
    # Other columns...
    
    def set_password(self, password):
        """Set the password hash for the user."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    # Define property to maintain compatibility with your existing code
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

# New model to track user connections for sharing
class UserConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    connected_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationships for easy lookup in both directions
    user = db.relationship('User', foreign_keys=[user_id], backref='connections')
    connected_user = db.relationship('User', foreign_keys=[connected_user_id], backref='connected_to')
    
    def __repr__(self):
        return f'<UserConnection {self.user_id} -> {self.connected_user_id}>'
    
    # Ensure uniqueness of connections
    __table_args__ = (
        db.UniqueConstraint('user_id', 'connected_user_id', name='unique_user_connection'),
    )