from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegisterForm, PasswordResetRequestForm, PasswordResetForm, UpdateProfileForm
from models import User
from extensions import db, bcrypt, login_manager, mail, scheduler
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
        email = form.email.data
        username = form.username.data
        password = form.password.data

        hashed_password = bcrypt.generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)

        #Add the new user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f'Account created for {username}!', 'success')
            return redirect(url_for('auth.login'))
        except:
            db.session.rollback()
            flash('Something went wrong. Please try again.', 'danger')
        
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
                  sender='littracks.app@gmail.com', 
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

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()  # Assuming this form has fields for username, email, and wants_reminder

    if request.method == 'POST':
        if form.validate_on_submit():
            # Update user profile fields with data from the form
            current_user.username = form.username.data
            current_user.email = form.email.data

            # Update wants_reminder based on the checkbox in the form
            current_user.wants_reminder = 'wants_reminder' in request.form

            # Commit the changes to the database
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('auth.profile'))

    # Populate the form with the current user's details for GET request
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.wants_reminder.data = current_user.wants_reminder

    return render_template('profile.html', form=form)


@auth.route('/update_reminder_preference', methods=['POST'])
@login_required
def update_reminder_preference():
    data = request.get_json()
    wants_reminder = data.get('wants_reminder', False)
    current_user.wants_reminder = wants_reminder
    db.session.commit()
    return jsonify({"message": "Preference updated successfully."})

@scheduler.task('interval', id='send_reminders', hours=24)
def send_reminder_emails():
    with scheduler.app.app_context():
        users = User.query.filter_by(wants_reminder=True).all()
        for user in users:
            send_reminder_email(user)

def send_reminder_email(user):
    msg = Message('Your Reading Reminder',
                  sender='littracks.app@gmail.com',
                  recipients=[user.email])
    msg.body = f"Hello {user.username},\n\nJust a reminder to keep reading your favorite books!\n\nIf you no longer wish to receive these reminders, you can unsubscribe via your profile page."
    mail.send(msg)
