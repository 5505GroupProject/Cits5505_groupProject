from app import app, db
from config import Config

if __name__ == '__main__':
    # Print startup information
    print("Starting application...")
    print("Debug mode: True")
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)