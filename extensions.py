from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import jwt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta

mail = Mail()

scheduler = APScheduler()

jwt = JWTManager()  # Initialize the JWTManager instance

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()