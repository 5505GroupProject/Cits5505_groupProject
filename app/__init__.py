from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

# Create extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # If not in config, set a secure secret key for sessions
    if 'SECRET_KEY' not in app.config:
        app.config['SECRET_KEY'] = os.urandom(24).hex()
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    # Import other blueprints as needed
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    # Register other blueprints
    
    return app