"""
This file contains all the views for webpages that fall under the 'auth' blueprint
"""
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from . import auth
from .forms import LoginForm, CreateAccountForm, EmailForm, PasswordResetForm, NewEmailForm
from .. import db
from ..models import User
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    #login page -- unauthenticated users are redirected here
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    #logouts user and redirects them back to login
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('auth.login'))

@auth.route('/create_account', methods=['GET', 'POST'])
def create_account():
    #page for account creation
    form = CreateAccountForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    position=form.position.data,
                    location=form.location.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', #sends confirmation email
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/create_account.html',
                           form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    #confirms users email address and allows them to login
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        login_user(current_user)
        flash('You have confirmed your account.')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect('main.index')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    #resends a confirmation email
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    #before user makes request will check if they are confirmed
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))



@auth.route('/unconfirmed')
def unconfirmed():
    #display screen to tell users that the have not confirmed yet
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/reset-password', methods=['GET', 'POST'])
def confirm_email():
    #confirms the user's email and sends them a token via email to reset their password
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password', #sends the email with token
                       'auth/email/password_reset', first=user.first_name,
                       last=user.last_name, token=token)
            flash('An email with a link to reset your password has been sent.')
            return redirect(url_for('auth.login'))
    return render_template('auth/confirm_email.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    #resets the users password if proper token is given
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('You have successfully reset your password.')
            return redirect(url_for('auth.login'))
        else:
            flash('The password reset link is invalid or has expired.')
            return redirect('auth.login')
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email():
    #takes new email for user and sends a confirmation email to that address
    form = NewEmailForm()
    if form.validate_on_submit():
        user = current_user
        user.new_email = form.email.data
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(form.email.data, 'Change Email', #sends email
                    'auth/email/change_email', first=user.first_name,
                    last=user.last_name, token=token)
        flash('An email with a link to confirm your new email address has been sent.')
        return redirect(url_for('main.profile', first=user.first_name,
                                last=user.last_name, id=user.id))
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>', methods=['GET', 'POST'])
@login_required
def update_email(token):
    #updates the user's email to the new email address
    if current_user.confirm(token):
        current_user.email = current_user.new_email
        current_user.new_email = None
        db.session.add(current_user)
        db.session.commit()
        flash('Your new email has been confirmed and your account has been updated.')
        return redirect(url_for('main.profile', first=current_user.first_name,
                        last=current_user.last_name, id=current_user.id))

