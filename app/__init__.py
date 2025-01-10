import os
from flask import Flask
from .routes import main_bp  # Make sure the Blueprint is imported

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '../templates')
    )

    # Register the blueprint
    app.register_blueprint(main_bp)

    # Other app configurations can go here (e.g., database, sessions, etc.)
    return app
