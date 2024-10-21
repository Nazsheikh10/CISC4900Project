from flask_login import UserMixin
from sqlalchemy import Enum
from datetime import datetime, timezone, timedelta
from extensions import db
from flask import current_app
import jwt

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)    # User_ID
    username = db.Column(db.String(20), nullable=False, unique=True)   # username
    email = db.Column(db.String(120), nullable=False, unique=True)      # email_address
    password = db.Column(db.String(80), nullable=False)         # hashed_password

    def get_reset_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id,
                           'exp': datetime.utcnow() + timedelta(seconds=expires_in)},
                          current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except Exception:
            return None
        return User.query.get(user_id)

class Books(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True)  # Book_ID
    api_id = db.Column(db.String(50), nullable=False)  # API_ID
    title = db.Column(db.String(100), nullable=False)  # Title
    author = db.Column(db.String(100), nullable=False)  # Author
    description = db.Column(db.Text, nullable=True)  # Description
    cover_page = db.Column(db.String(200), nullable=True)  # Cover_page (URL)

class User_Read_Books(db.Model):
    __tablename__ = 'user_read_books'

    record_id = db.Column(db.Integer, primary_key=True) # Record_ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   #connecting to User table
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False) #connecting to Books table

    #Adding enum for reading status
    read_status_enum = ('reading', 'completed', 'to-read')
    read_status = db.Column(Enum(*read_status_enum, name=read_status_enum), nullable=False)

    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) #adds the current time stamp of when the book was added to the table

    user = db.relationship('User', backref=db.backref('read_books', lazy=True))
    book = db.relationship('Books', backref=db.backref('user_read_books', lazy=True))

class Reviews(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)  # Unique record ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to Users table
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)  # Foreign key to Books table
    rating = db.Column(db.Float, nullable=False)  # Rating (1-5 stars)
    review_text = db.Column(db.Text, nullable=True)  # Brief note on the book
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Timestamp of when the book was reviewed

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))  # Relationship to User
    book = db.relationship('Books', backref=db.backref('reviews', lazy=True))  # Relationship to Books

class Recommendations(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)  # Unique record ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to Users table
    recommend_book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)  # Foreign key to recommended Books
    based_on_book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)  # Foreign key to the basis book
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # Timestamp when the recommendation was added

    user = db.relationship('User', backref=db.backref('recommendations', lazy=True))  # Relationship to User
    recommended_book = db.relationship('Books', foreign_keys=[recommend_book_id], backref=db.backref('recommended_for', lazy=True))  # Relationship to recommended Books
    based_on_book = db.relationship('Books', foreign_keys=[based_on_book_id], backref=db.backref('basis_for_recommendations', lazy=True))  # Relationship to the basis book

