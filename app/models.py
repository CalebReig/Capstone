"""
This file contains classes associating with the application database.
The database contains 3 tables: Role, User, Patient
"""
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime


class Permission:
    """
    This class hold constants for permissions
    The permissions are exponential factors of 2 so that permissions can be checked
    via binary AND operators.

    example:
    user with the following permissions:
    VIEW = 1
    WRITE = 2
    (add)

    binary: 0011

    function () #check if user has Permissions ADMIN + VIEW + WRITE binary: 0111

    0111 & 0011 == 0111 #False it equals 0011

    """
    VIEW = 1
    WRITE = 2
    ADMIN = 4

class Role(db.Model):
    """
    Class to store roles for the user that will allow different users privileges

    Attributes
    ----------
    id : int
        a unique identifier for the role --primary key for the db
    name : str
        the name of the role
    default : bool
        if the role is the default (default True)
    permissions : int
        the permissions of the role (default 4)

    Methods
    -------
    add_permission(perm)
        Adds the perm to the permissions attribute

    remove_permission(perm)
        Subtracts the perm from the permissions attribute

    reset_permission()
        Resets the permission attribute to 0

    has_permission(perm)
        Checks if the the perm is included in the permissions attribute via binary AND
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=True, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic') #link to 'users' table

    def init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0 #sets permissions to 0

    def __repr__(self):
        return '<Role %r>' % self.name

    def add_permission(self, perm):
        """
        Adds the perm to the permissions attribute
        :param perm: int permission
        """
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        """
        Subtracts the perm from the permissions attribute
        :param perm: int permission
        """
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """
        Resets the permission attribute to 0
        """
        self.permissions = 0

    def has_permission(self, perm):
        """
        Checks if the the perm is included in the permissions attribute via binary AND
        :param perm: int permission
        """
        return self.permissions & perm == perm #binary AND

    @staticmethod
    def insert_roles():
        """
        This function creates all roles and gives them proper permissions.
        This should be called from the command line.
        """
        roles = {
            'User': [Permission.VIEW],
            'Technician': [Permission.VIEW, Permission.WRITE],
            'Administrator': [Permission.VIEW, Permission.WRITE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    """
    Class representing the users of the application

    Attributes
    ----------
    id : int
        a unique identifier for the user --primary key for the db

    first_name : str
        the user's first name

    last_name : str
        the user's last name

    position : str
        the user's job position

    location : str
        the user's location

    email : str
        a unique email that is associated with the user

    new_email : str
        a temporary place holder for a new email when a user requests to change their email

    password_hash : str
        a hash of the user's password --note: password is not stored in the database

    confirmed : bool
        if the user has confirmed their email address (default False)

    role_id : int
        id of the role that the user holds -- foreign key to the 'roles' table

    Methods
    -------
    verify_password(password)
        verifies the input password, when hashed, matches the password hash

    generate_confirmation_token(expiration=3600):
        generates a token to confirm the user account that will expire after a
        given amount of time

    confirm(token)
        confirms if the given token matches the generated confirmation token

    generate_reset_token(expiration=3600)
        generates a token to reset the password that will expire after a given amount of time

    can(self, perm)
        checks if the user has the given permission

    is_administrator(self)
        checks if the user is an administrator
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64), index=True)
    position = db.Column(db.String(64))
    location = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    new_email = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    patients = db.relationship('Patient', backref='provider', lazy='dynamic') #link to 'patients' table


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None: #gives new user the default role ('User') unless they have the admin email
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % (self.first_name + ' ' + self.last_name)

    @property
    def password(self):
        #Makes password unreadable
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        #creates password hash when a password is input
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        verifies that a inputted password is matched with the password hash
        :param password: string
            The input password
        :return: Return True if hashed password matches hash
        """
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        """
        generates a token based off of the users id that will be used to confirm their account
        :param expiration: int (default 3600)
            time in seconds for when the token will expire
        :return: Returns json mapping 'confirm' to a serialized token
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        """
        confirms the users account if the proper token associating with the users id is input
        :param token: string
            the token given by the user
        :return: Returns true if the tokens match, else false
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        """
        generates a token based off of the users id that will be used to reset their password
        :param expiration: int (default 3600)
            time in seconds form when the token will expire
        :return: Returns json mapping 'reset' to a serialized token
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        """
        Resets the user's password if the correct token is given
        :param token: string
            the user given token
        :param new_password: string
            the new password given by the user
        :return: Returns True if the correct token was given and the password change, else False
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def can(self, perm):
        """
        Checks if the user has a permission
        :param perm: Permission
        :return: Returns True if the user has the permission
        """
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        """
        Checks if the user has admin permissions
        :return: Returns True if the user has admin permissions
        """
        return self.can(Permission.ADMIN)

class AnonymousUser(AnonymousUserMixin):
    """
    Class for anonymous users
    """
    def can(self, perm):
        """
        Checks if the user has a permission
        :param perm: Permission
        :return: Returns True if the user has the permission
        """
        return False

    def is_administrator(self):
        """
        Checks if the user has admin permissions
        :return: Returns True if the user has admin permissions
        """
        return False


@login_manager.user_loader
def load_user(user_id):
    #loads a user based on their id. used to login users
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser


class Patient(db.Model):
    """
    Class representing the users of the application

    Attributes
    ----------
    id : int
        a unique identifier for the patient --primary key for the db


    first_name : str
        the patient's first name

    last_name : str
        the patient's last name

    email : str
        the patient's email (optional)

    dob_year : int
        the patient's birth year

    dob_month : int
     the patient's birth month

    dob_day : int
        the patient's birth day

    sex : bool
        False for Male, True for Female

    last_seen : datetime
        The last time the patient was seen (default = utcnow)

    provider_id : int
        the id of the patient's primary provider -- foriegn key to the 'users' table

    chest_pain_type : str
        type of chest pain for the heart disease test

    resting_bp : int
        resting blood pressure for the heart disease test

    cholesterol : int
        cholesterol level for the heart disease test

    fasting_bs : bool
        False is fasting blood sugar is less than 120 mg/dl for the heart disease test

    resting_ecg : str
        resting electrocardiogram results for the heart disease test

    max_hr : int
        maximum heart rate for the heart disease test

    exercise_angina : bool
        if the patient has exercise induced angina for the heart disease test

    old_peak : float
        oldpeak for the heart disease test

    st_slope : str
        the slope of the peak exercise ST segment for the heart disease test

    at_risk_for_heart_disease : bool
        if the patient is at risk for heart disease as predicted by an AI

    heart_disease_test_results : bool
        if the patient has had heart disease test results submitted
    """
    __tablename__ = 'patients'
    #Start basic attributes
    #----------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True)
    dob_year = db.Column(db.Integer)
    dob_month = db.Column(db.Integer)
    dob_day = db.Column(db.Integer)
    sex = db.Column(db.Boolean)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow())
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #Start heart disease test attributes
    #----------------------------------------------------------------------
    chest_pain_type = db.Column(db.String(64))
    resting_bp = db.Column(db.Integer)
    cholesterol = db.Column(db.Integer)
    fasting_bs = db.Column(db.Boolean)
    resting_ecg = db.Column(db.String(64))
    max_hr = db.Column(db.Integer)
    exercise_angina = db.Column(db.Boolean)
    old_peak = db.Column(db.Float)
    st_slope = db.Column(db.String(64))
    at_risk_for_heart_disease = db.Column(db.Boolean)
    heart_disease_test_results = db.Column(db.Boolean)

