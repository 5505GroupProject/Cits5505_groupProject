
```markdown
# Cits5505 Group Project

## Environment Setup

### 1. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
If a `requirements.txt` file exists, install dependencies with:
```bash
pip install -r requirements.txt
```

If `requirements.txt` is empty, manually install Flask and SQLAlchemy:
```bash
pip install flask flask-sqlalchemy
```

### 3. Initialize the Database
Run the following commands to create the SQLite database:
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

### 4. Run the Application
Start the Flask development server:
```bash
python app.py
```

### 5. Access the Application
Open your browser and go to:
```
http://127.0.0.1:5000/
```
```