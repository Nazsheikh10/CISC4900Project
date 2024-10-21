from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from .forms import LoginForm, RegisterForm, PasswordResetRequestForm, PasswordResetForm
from models import User
from extensions import db, bcrypt, login_manager, mail
from flask_mail import Message

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate token and send email
            token = user.get_reset_token()  
            send_reset_email(user, token) 
            flash('An email has been sent with instructions to reset your password.', 'info')
        else:
            flash('No account found with that email.', 'warning')
        return redirect(url_for('auth.login'))  # Redirect to login after request
    return render_template('reset_request.html', title='Reset Password', form=form)

def send_reset_email(user, token):
    msg = Message('Password Reset Request',
                  sender='naz.sheikh10@bcmail.cuny.edu', 
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('auth.reset_token', token=token, _external=True)}
    If you did not make this request, simply ignore this email and no changes will be made.
    '''
    mail.send(msg)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', title='Reset Password', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

