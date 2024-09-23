from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os
from sqlalchemy import Enum
from datetime import datetime, timezone
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.getcwd(), "database.db")}'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)    # User_ID
    username = db.Column(db.String(20), nullable=False, unique=True)   # username
    email = db.Column(db.String(120), nullable=False, unique=True)      # email_address
    password = db.Column(db.String(80), nullable=False)         # hashed_password

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


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    email = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Email"})
    
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"Placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_username = User.query.filter_by(
            username=username.data).first()
        
        if existing_username:
            raise ValidationError(
                "Username already exists. Please choose a different one."
            )


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"Placeholder": "Password"})

    submit = SubmitField("Login")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
