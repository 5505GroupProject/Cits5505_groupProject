# SentiNews Project

## Introduction
SentiNews is a Flask-based web application that allows users to upload and analyze text data. It features user authentication, file uploads, sentiment analysis, named entity recognition, and visualization capabilities.

## Setup and Installation

### Prerequisites
- Python 3.10 or higher
- Chrome browser (for running Selenium tests)
- Git

### Getting Started

1. **Clone the Repository**
```bash
git clone https://github.com/5505GroupProject/Cits5505_groupProject.git
cd Cits5505_groupProject
```

2. **Create and Activate Virtual Environment**
```bash
python -m venv venv
# For Windows
venv\Scripts\activate
# For Linux/macOS
# source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Set Up the Database**
```bash
# If this is the first time setup and migrations folder doesn't exist
flask db init

# Or if you already have a migrations folder (most common case)
# Just create migration script and apply
flask db migrate
flask db upgrade
```

5. **Run the Application**
```bash
flask run
# Or alternatively
python run.py
```

The application will be accessible at: http://localhost:5000

## Testing

```bash
# Run unit tests
python tests/unit_tests.py

# Run Selenium tests
# Note: Make sure the Flask application is running at http://localhost:5000 before running Selenium tests
# Open a separate terminal and run: flask run
python tests/selenium_tests.py
```

## Project Structure

- `app/`: Core application code
  - `models/`: Database models
  - `routes/`: Application routes and controllers
  - `static/`: CSS, JavaScript, and image files
  - `templates/`: HTML templates
  - `utils/`: Utility functions for analysis

- `migrations/`: Database migration scripts
- `tests/`: Test files
- `instance/`: Contains application instance data (database)

## Features
- User authentication and profile management
- Text file upload and management
- Natural Language Processing analysis:
  - Sentiment analysis
  - Named Entity Recognition
  - N-gram analysis
  - Word frequency analysis
- Data visualization
- Sharing analysis results

## Notes
- The database file (`sentinews.db`) must be present in the `instance/` directory
- Make sure your Chrome browser version matches the ChromeDriver version for Selenium tests

## Declaration of AI Tools Usage 
- Our team have used AI tools to assist completing the project by following ways: 
  - Write codes and comments directly. 
  - Write the documents about the project. 
  - Query doubts and receive suggestions to improve the codes, documents or project quality. 