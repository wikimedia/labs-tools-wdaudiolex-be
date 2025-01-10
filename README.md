Comprehensive README for WDAudioLEx-BE Tool Backend
Overview

The WDAudioLEx-BE Tool Backend is a backend system built using Flask, providing functionality to support login authentication via the MediaWiki API. This project is structured to facilitate modular development and deployment, using best practices in Python development, Flask frameworks, and integration with third-party APIs for secure login.
Features

    Flask-based Backend: Lightweight, scalable, and easy to extend.
    Secure Authentication: Implements MediaWiki's API for robust login mechanisms using action=login and action=clientlogin.
    Virtual Environment Integration: Manage dependencies effectively to ensure a consistent development experience.
    Modular Architecture: Organized project structure for easy navigation and updates.

Project Structure

WDAudioLEx-BE/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── routes.py          # Route definitions
│   ├── forms.py           # Flask-WTF forms
│   ├── static/            # Static files (CSS, JS, images)
│   └── templates/         # HTML templates for rendering views
├── clientlogin.py         # MediaWiki API integration for authentication
├── requirements.txt       # List of dependencies
├── config.py              # Configuration settings
├── run.py                 # Main application entry point
└── README.md              # Project documentation

Installation
1. Prerequisites

    Python Version: Flask supports Python 3.9 and newer. Ensure you have Python installed.
    Flask Dependencies:
        Werkzeug: Implements WSGI.
        Jinja: Template rendering engine.
        MarkupSafe: Ensures template safety.
        ItsDangerous: Protects session cookies.
        Click: For command-line functionality.
        Blinker (Optional): Enables signal handling in Flask.

2. Setup
Step 1: Clone the Repository

git clone https://github.com/your-repo/WDAudioLEx-BE.git
cd WDAudioLEx-BE

Step 2: Create a Virtual Environment

python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

Step 3: Install Dependencies

pip install -r requirements.txt

Step 4: Run the Application

python run.py

Access the application at http://127.0.0.1:5000.
Login Authentication with MediaWiki API

The project integrates MediaWiki's login system for user authentication. Two methods are supported:
Method 1: Using action=login

Steps:

    Fetch a login token using action=query&meta=tokens.
    Submit the login request using the lgtoken, username, and password.

Sample Code:

response = S.post(
    url="https://your-wiki-site/api.php",
    data={
        "action": "login",
        "lgname": "your_username",
        "lgpassword": "your_password",
        "lgtoken": "your_login_token",
        "format": "json"
    }
)

Method 2: Using action=clientlogin

This method is suited for interactive applications. It follows these steps:

    Fetch login fields using action=query&meta=authmanagerinfo.
    Obtain a login token.
    Submit the clientlogin request with the necessary fields.

Sample Code:

response = S.post(
    url="https://your-wiki-site/api.php",
    data={
        "action": "clientlogin",
        "username": "your_username",
        "password": "your_password",
        "loginreturnurl": "http://127.0.0.1:5000/",
        "logintoken": "your_login_token",
        "format": "json"
    }
)

Configuration

The application configuration is managed in config.py. Update the following settings as per your environment:

class Config:
    SECRET_KEY = "your_secret_key"
    FLASK_ENV = "development"
    DEBUG = True

Templates

The HTML templates are located in the app/templates/ directory and styled using Bootstrap for responsive design.

Example Template (Login Form):

<!DOCTYPE html>
<html lang="en">
<head>
    <title>Login</title>
    <link rel="stylesheet" href="static/bootstrap/css/bootstrap.min.css">
</head>
<body>
<div class="container">
    <h2>MediaWiki Log In</h2>
    <form method="post">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" name="username" class="form-control" id="username" required>
        </div>
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" name="password" class="form-control" id="password" required>
        </div>
        <button type="submit" class="btn btn-primary">Log In</button>
    </form>
</div>
</body>
</html>

Testing

The application uses Flask's built-in test client for unit testing.

Example Test:

def test_login_page():
    response = app.test_client().get('/')
    assert response.status_code == 200

Run tests with:

pytest


