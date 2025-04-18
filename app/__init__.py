from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Initialize the database and create a default admin user
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', email='admin@example.com', password='admin123')
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')  # Render login page for GET requests

    # Handle POST request for login
    data = request.get_json()  # Parse JSON data from the request
    username = data.get('username')
    password = data.get('password')

    # Check if the user exists and the password matches
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')  # Render register page for GET requests

    # Handle POST request for registration
    data = request.get_json()  # Parse JSON data from the request
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Validate username length
    if len(username) < 3 or len(username) > 20:
        return jsonify({'message': 'Username must be between 3 and 20 characters.'}), 400

    # Check if username is already taken
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already taken'}), 400

    # Validate passwords match
    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    # Check if email is already registered
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    # Create a new user
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 200

@app.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('forgot_password.html')  # Render forgot password page

@app.route('/test')
def test():
    return "Welcome to the test page!"

