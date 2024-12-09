from flask import Blueprint, render_template
from models import User, User_Read_Books, Reviews  # Import your models
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Fetch user-specific data
    user_id = current_user.id
    books_completed = User_Read_Books.query.filter_by(user_id=user_id, read_status="completed").count()
    currently_reading = User_Read_Books.query.filter_by(user_id=user_id, read_status="reading").count()
    total_reviews = Reviews.query.filter_by(user_id=user_id).count()

    return render_template(
        'dashboard.html',
        books_completed=books_completed,
        currently_reading=currently_reading,
        total_reviews=total_reviews
    )