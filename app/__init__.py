from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from flask_wtf.csrf import CSRFProtect
import os

# Initialize extensions before they are registered with the app
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=None):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Load configurations
    if config_class:
        app.config.from_object(config_class)
    else:
        # Default configuration
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'static_file_server')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize and configure extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Add route for the main page to load the login interface
    @app.route('/')
    def index():
        return render_template('login.html')
    
    # Add route for the upload page that users will be redirected to after login
    @app.route('/upload')
    @login_required
    def upload():
        from flask_login import current_user
        return render_template('upload.html', user=current_user)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        
    return app

# For backwards compatibility and easier imports
app = create_app()

