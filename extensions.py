from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import jwt
from flask_jwt_extended import JWTManager
from flask_mail import Mail

mail = Mail()

jwt = JWTManager()  # Initialize the JWTManager instance

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()