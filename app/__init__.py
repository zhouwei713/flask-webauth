# coding = utf-8
"""
@author: zhou
@time:2019/1/15 11:14
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_cors import CORS
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_github import GitHub
from flask_mail import Mail

db = SQLAlchemy()
cors = CORS()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()
github = GitHub()
mail = Mail()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    github.init_app(app)
    mail.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .api_1_0 import api_1_0 as api_blueprint
    app.register_blueprint(api_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
