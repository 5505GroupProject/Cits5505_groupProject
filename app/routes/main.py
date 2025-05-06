from flask import Blueprint, render_template, session
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/share')
@login_required
def share():
    return render_template('share.html')

@main_bp.route('/upload')
@login_required
def upload():
    return render_template('upload.html')

@main_bp.route('/visualization')
@login_required
def visualization():
    analyzed_text = session.get('analyzedText', 'No text analyzed yet.')
    summary = "The sentiment analysis indicates a generally positive outlook in the submitted content."
    return render_template('visualization.html', analyzed_text=analyzed_text, summary=summary)

@main_bp.route('/protected-route')
@login_required
def protected_route():
    # Your route logic
    pass

