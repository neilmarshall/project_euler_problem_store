from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()

from app.views.index_route import app_bp
from app.views.search_route import search_bp

from config import Config

def create_app(config_object=Config):

    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(app_bp)
    app.register_blueprint(search_bp)

    return app

