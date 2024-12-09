from flask import Blueprint, render_template, current_app, request
from flask_login import current_user
from extensions import db

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(401)
def unauthorized_error(e):
    user_info = f"User ID: {current_user.id}" if current_user.is_authenticated else "Unauthenticated user"
    current_app.logger.warning(f"401 error: {e}, URL: {request.url}, {user_info}")
    return render_template('401.html'), 401

@errors.app_errorhandler(404)
def page_not_found(e):
    current_app.logger.warning(f"404 error: {e}, URL: {request.url}")
    return render_template('404.html'), 404

@errors.app_errorhandler(500)
def internal_error(e):
    db.session.rollback()  # Rollback the session in case of internal error
    user_info = f"User ID: {current_user.id}" if current_user.is_authenticated else "Unauthenticated user"
    current_app.logger.error(f"500 error: {e}, URL: {request.url}, {user_info}")
    return render_template('500.html'), 500