from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

from config import Config


db = SQLAlchemy()
#migrate = Migrate()

def create_app():
    app = Flask(__name__)
    # Load configurations from config.py
    app.config.from_object(Config)
    # Initialize extensions
    db.init_app(app)
    #migrate.init_app(app, db)
    # Register blueprints
    #from .routes import main as main_blueprint
    #app.register_blueprint(main_blueprint)
    with app.app_context():
        from . import models, routes
    return app