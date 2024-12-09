from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, Email, NumberRange
from models import User

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    email = StringField(validators=[InputRequired(), Length(
        min=4, max=120)], render_kw={"placeholder": "Email"})
    
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
        min=4, max=120)], render_kw={"Placeholder": "Password"})

    submit = SubmitField("Login")

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

class ReviewForm(FlaskForm):
    rating = FloatField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    review_text = TextAreaField('Your review', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    wants_reminder = BooleanField('Receive Reminder Emails')
    submit = SubmitField('Update Profile')