"""
Initializes the Flask application, sets up extensions (DB, Login, CSRF),
and registers all application blueprints for modular routing.
"""

from flask import Flask
from app.extensions import db, login_manager, csrf
from app.auth.routes import auth
from app.main.routes import main
from app.project.routes import project

# This function creates and configures the Flask app
def create_app():
    app = Flask(__name__)
    
    # Load development configuration directly (no .env file used)
    app.config.from_object('config.DevelopmentConfig')

    # Initialize app with extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Set login view for @login_required redirects
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models so they get registered with SQLAlchemy
    from app import models

    # Create all database tables
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(project)

    return app

# To retrieve user from session
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


