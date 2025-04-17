# Cits5505_groupProject

/news-sentiment-app
├── app/                   
│   ├── __init__.py          # Initializes the Flask app, SQLAlchemy, and other extensions.
│   ├── models.py            # SQLAlchemy models (e.g., User, NewsItem, Analysis, Share).
│   ├── forms.py             # Flask-WTF forms for handling user inputs (login, registration, upload, etc.).
│   ├── nlp.py               # Module encapsulating the NLP sentiment analysis logic.
│   ├── routes/              
│   │   ├── __init__.py      # Registers the blueprints for different sections of the app.
│   │   ├── auth.py          # Authentication routes (sign up, login, logout).
│   │   ├── news.py          # Routes for uploading news content and triggering analysis.
│   │   ├── visualize.py     # Routes for visualizing analyzed sentiment data.
│   │   └── share.py         # Routes for managing data sharing among users.
│   ├── templates/           
│   │   ├── base.html        # Base template with common elements (header, navigation, footer).
│   │   ├── index.html       # Introductory view describing the app and providing login/signup options.
│   │   ├── upload.html      # Template for uploading or inputting news content.
│   │   ├── visualize.html   # Template for displaying sentiment analysis results.
│   │   └── share.html       # Template for managing sharing settings.
│   └── static/              
│       ├── css/             
│       │   └── style.css    # Custom CSS styles.
│       ├── js/              
│       │   └── main.js      # Custom JavaScript for interactivity.
│       └── images/          # Image assets (icons, logos, etc.).
├── instance/                
│   └── config.py            # Instance-specific settings (e.g., secret keys, database URI) that are not version-controlled.
├── config.py                # Global configuration settings for different environments (development, production, etc.).
├── run.py                   # Entry point for launching the Flask web server.
├── requirements.txt         # Lists all dependencies.
└── README.md                # Project overview, setup instructions, and development guidelines.
