from flask import Flask
from extensions import db, login_manager, bcrypt, migrate, jwt, mail
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = 'secretkey'
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure logging
    if not os.path.exists('logs'):
        os.makedirs('logs')

    jwt.init_app(app)  # Attach JWT to app
    mail.init_app(app)  # Initialize Flask-Mail with the app

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))

    app.logger.addHandler(file_handler)
    app.logger.info("Application has started.")  # Log application start

    # Import and register blueprints
    from blueprints.auth.routes import auth
    from blueprints.books.routes import books
    from blueprints.main.routes import main
    from blueprints.errors.handlers import errors

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(books, url_prefix='/books')
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
