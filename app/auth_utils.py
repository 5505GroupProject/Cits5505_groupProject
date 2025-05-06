from flask import session, current_app
from flask_login import current_user
import secrets
import string
import os

def generate_csrf_token(length=32):
    """
    Generate a secure CSRF token.
    
    Args:
        length: Length of the token
        
    Returns:
        str: A secure random token
    """
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token

def set_csrf_token():
    """
    Set a CSRF token in the session if it doesn't exist.
    
    Returns:
        str: The CSRF token
    """
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
    return session['csrf_token']

def validate_csrf_token(token):
    """
    Validate a CSRF token against the one stored in the session.
    
    Args:
        token: The token to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    session_token = session.get('csrf_token')
    print(f"Token received: {token}")
    print(f"Token in session: {session_token}")
    
    # More reliable check:
    if token and session_token and token == session_token:
        return True
    return False