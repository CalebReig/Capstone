"""
This file contains all the forms for webpages under the 'auth' blueprint
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    #Form to login
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')


class CreateAccountForm(FlaskForm):
    #Form to create an account
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    first_name = StringField('First Name',validators=[DataRequired(), Length(1, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    position = StringField('Job Position', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired(), EqualTo('re_password', 'Passwords must match.')])
    re_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        #validates email is not taken
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')



class EmailForm(FlaskForm):
    #Form to confirm user's email when password needs to be reset
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Submit')


    def validate_email(self, field):
        #validates that the email is registered
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is not registered.')


class NewEmailForm(FlaskForm):
    #Form for adding a new email address to the user account
    email = EmailField('New Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        #validates that the email is not taken
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class PasswordResetForm(FlaskForm):
    #form to create new password
    password = PasswordField(validators=[DataRequired(), EqualTo('re_password', 'Passwords must match.')])
    re_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Reset')



