"""
This file contains all forms used under the 'main' blueprint
"""
from flask_wtf import FlaskForm
from wtforms import SearchField, StringField, EmailField, SubmitField, \
    BooleanField, SelectField, DateField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from ..models import Role, User


class SearchForm(FlaskForm):
    #form for searching (users/patients)
    search = SearchField()


class AccountInfoForm(FlaskForm):
    #form for updating user info
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    position = StringField('Job Position', validators=[DataRequired(), Length(1, 64)])
    location = StringField('Location', validators=[DataRequired(), Length(1, 64)])
    update = SubmitField('Update')



class EditProfileAdminForm(FlaskForm):
    #form for updating user info for ADMINS
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64),
                                            Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    position = StringField('Job Position', validators=[DataRequired(), Length(1, 64)])
    location = StringField('Location', validators=[DataRequired(), Length(1, 64)])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Update')

    def __init__(self, user, *args, **kwargs):
        #fills the roles select box with available roles
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in
                             Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        #validates email is not registered to another user
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class AddPatientForm(FlaskForm):
    #form for adding a patient
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email (Optional)')
    dob = DateField('DOB', validators=[DataRequired()])
    sex = SelectField('Sex', coerce=int, choices=[(0,'M'), (1,'F')])
    provider = SelectField('Primary Provider', coerce=int)
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        #fills select box with list of providers
        super(AddPatientForm, self).__init__(*args, **kwargs)
        self.provider.choices = [(user.id, user.last_name + ', ' + user.first_name)
                                 for user in User.query.order_by(User.last_name).all()]


class AddPatientRecordForm(FlaskForm):
    #form for adding a patient record (test)
    test_type = SelectField('Test Type', choices=[
        'Heart Disease Test'
    ])
    submit = SubmitField('Select')


class HeartDiseaseTestForm(FlaskForm):
    #form for adding heart disease test info
    chest_pain_type = SelectField('Chest Pain Type',
                                  choices=[('TA', 'Typical Angina'),
                                           ('ATA', 'Atypical Angina'),
                                           ('NAP', 'Non-Anginal Pain'),
                                           ('ASY', 'Asymptomatic')],
                                  validators=[DataRequired()])
    resting_bp = IntegerField('Resting BP', validators=[DataRequired()])
    cholesterol = IntegerField('Cholesterol', validators=[DataRequired()])
    fasting_bs = SelectField('Fasting Blood Sugar > 120 mg/dl',
                             choices=[(0, 'No'), (1, 'Yes')],
                             validators=[DataRequired()])
    resting_ecg = SelectField('Resting Electrocardiogram Results',
                              choices=[('Normal', 'Normal'),
                                        ('ST', 'ST-T Wave Abnormality'),
                                       ('LVH', 'Left Ventricular Hypertrophy')],
                              validators=[DataRequired()])
    max_hr = IntegerField('Maximum Heart Rate', validators=[DataRequired()])
    exercise_angina = SelectField('Exercise-Induced Angina',
                             choices=[(0, 'No'), (1, 'Yes')],
                                  validators=[DataRequired()])
    old_peak = FloatField('Oldpeak')
    st_slope = SelectField('Slope of Peak Exercise ST Segment',
                              choices=[('Up', 'Upsloping'),
                                        ('Flat', 'Flat'),
                                       ('Down', 'Downsloping')],
                           validators=[DataRequired()])
    submit = SubmitField('Add')