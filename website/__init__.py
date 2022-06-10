from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_cors import CORS
import redis
from flask_session import Session

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    # SECRET_KEY = os.environ["SECRET_KEY"]

    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True
    # SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'

    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERNAMENT'] = False
    app.config['SESSION_USER_SIGNER'] = True
    app.config['SESSION_REDIS'] = redis.from_url("redis://127.0.0.1:6379")

    app.config['SECRET_KEY'] = 'lskjdahjsdh'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # app.config.from_object(ApplicationConfig)
    db.init_app(app)
    server_session = Session(app)

    CORS(app, supports_credentials=True)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Database criada!!!')
