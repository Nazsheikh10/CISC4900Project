from flask import Blueprint, render_template, current_app
from extensions import db
import logging

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def page_not_found(e):
    current_app.logger.error(f"400 error: {e}")
    return render_template('404.html'), 404

@errors.app_errorhandler(500)
def internal_error(e):
    db.session.rollback()  # Rollback the session in case of internal error
    current_app.logger.error(f"500 error: {e}")
    return render_template('500.html'), 500