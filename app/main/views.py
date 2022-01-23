"""
This file contains all views falling under the 'main' blueprint
"""
from flask import render_template, redirect, flash, url_for, request, abort
from flask_login import login_required, current_user
from . import main
from .forms import SearchForm, AccountInfoForm, EditProfileAdminForm, AddPatientForm, \
    AddPatientRecordForm, HeartDiseaseTestForm
from .. import db
from ..models import User, Role, Permission, Patient
from ..decorators import admin_required, permission_required
from datetime import datetime



@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    #homepage
    #displays table of patients and users
    patient_form = SearchForm()
    user_form = SearchForm()
    users = User.query.order_by(User.last_name.asc()).all()
    patients = Patient.query.order_by(Patient.last_name.asc()).all()
    if patient_form.validate_on_submit() and patient_form.data['search']:
        patients = Patient.query.filter(Patient.last_name.like(patient_form.data['search'])).all()
    elif user_form.validate_on_submit() and user_form.data['search']:
        users = User.query.filter(User.last_name.like(user_form.data['search'])).all()
    return render_template('index.html',
                           patient_form=patient_form,
                           user_form=user_form,
                           users=users,
                           patients=patients)

@main.route('/profile/<int:id>')
@login_required
def profile(id):
    #user profiles
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('profile.html', user=user)


@main.route('/profile/<int:id>/edit-admin', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    #edit user profiles for admin
    user = User.query.filter_by(id=id).first_or_404()
    form = EditProfileAdminForm(user=user)
    if request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.position.data = user.position
        form.location.data = user.location
        form.email.data = user.email
        form.confirmed.data = user.confirmed
        form.role.data = user.role_id
    if request.method == 'POST' and form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.position = form.position.data
        user.location = form.location.data
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated')
        return redirect(url_for('main.profile', id=id))
    return render_template('edit_profile.html', user=user, form=form)

@main.route('/profile/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    #edit profile for user
    user = User.query.filter_by(id=id).first_or_404()
    if current_user != user: #can only edit your own profile
        abort(403)
    form = AccountInfoForm()
    if request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.position.data = user.position
        form.location.data = user.location
    if request.method == 'POST' and form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.position = form.position.data
        user.location = form.location.data
        db.session.add(user)
        db.session.commit()
        flash('Your information has been updated')
        return redirect(url_for('main.profile', id=id))
    return render_template('edit_profile.html', user=user, form=form)


@main.route('/ai-models')
@login_required
def models():
    #page for describing AI models used
    return render_template('ai_models.html')


@main.route('/about')
@login_required
def about():
    #page for details on the app
    return render_template('about.html')


@main.route('/add-patient', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def add_patient():
    #page for adding a new patient
    form = AddPatientForm()
    if form.validate_on_submit():
        patient = Patient()
        patient.first_name = form.first_name.data
        patient.last_name = form.last_name.data
        patient.email = form.email.data
        patient.sex = form.sex.data
        patient.dob_year = form.dob.data.year
        patient.dob_month = form.dob.data.month
        patient.dob_day = form.dob.data.day
        patient.provider_id = form.provider.data
        db.session.add(patient)
        db.session.commit()
        flash('Patient Added.')
        patient = Patient.query.filter_by(last_name=patient.last_name,
                                          first_name=patient.first_name,
                                          dob_year=patient.dob_year,
                                          dob_month=patient.dob_month,
                                          dob_day=patient.dob_day).first()
        return redirect(url_for('main.patient_record', id=patient.id))
    return render_template('add_patient.html', form=form)


@main.route('/patient/<int:id>', methods=['GET', 'POST'])
@login_required
def patient_record(id):
    #form for a patient's record
    patient = Patient.query.filter_by(id=id).first_or_404()
    form = AddPatientRecordForm() #option to add a new record(test)
    if form.validate_on_submit():
        test_forms = {'Heart Disease Test': 'main.heart_disease_test'}
        url = test_forms[form.test_type.data]
        return redirect(url_for(url, id=id))
    return render_template('patient_record.html', patient=patient, form=form)


@main.route('/patient/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def edit_patient_info(id):
    #page to edit a patients record
    patient = Patient.query.filter_by(id=id).first_or_404()
    form = AddPatientForm()
    if form.validate_on_submit():
        patient.first_name = form.first_name.data
        patient.last_name = form.last_name.data
        patient.email = form.email.data
        patient.sex = form.sex.data
        patient.dob_year = form.dob.data.year
        patient.dob_month = form.dob.data.month
        patient.dob_day = form.dob.data.day
        patient.provider_id = form.provider.data
        db.session.add(patient)
        db.session.commit()
        flash('Patient information has been updated')
        return redirect(url_for('main.patient_record', id=patient.id))

    form.first_name.data = patient.first_name
    form.last_name.data = patient.last_name
    form.email.data = patient.email
    form.sex.data = patient.sex
    patient.dob_year = form.dob.data = datetime(year=patient.dob_year,
                                                month=patient.dob_month,
                                                day=patient.dob_day)
    form.provider.data = patient.provider_id
    return render_template('edit_patient_record.html',
                           form=form,
                           patient=patient)


@main.route('/patient/<int:id>/heart-disease-test', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def heart_disease_test(id):
    #page to input heart disease test results
    patient = Patient.query.filter_by(id=id).first_or_404()
    form = HeartDiseaseTestForm()
    if form.validate_on_submit():
        patient.chest_pain_type = form.chest_pain_type.data
        patient.resting_bp = form.resting_bp.data
        patient.cholesterol = form.cholesterol.data
        patient.fasting_bs = form.fasting_bs.data == 1
        patient.resting_ecg = form.resting_ecg.data
        patient.max_hr = form.max_hr.data
        patient.exercise_angina = form.exercise_angina.data == 1
        patient.old_peak = form.old_peak.data
        patient.st_slope = form.st_slope.data
        patient.heart_disease_test_results = True
        patient.last_seen = datetime.utcnow()
        db.session.add(patient)
        db.session.commit()
        flash('Test Results Added')
        return redirect(url_for('main.patient_record', id=patient.id))
    return render_template('add_test_results.html',
                           header='Heart Disease',
                           form=form,
                           patient=patient)



@main.route('/delete-user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    #deletes a given user
    User.query.filter_by(id=id).delete()
    db.session.commit()
    flash('User has been deleted.')
    return redirect(url_for('main.index'))


@main.route('/delete-patient/<int:id>')
@login_required
@admin_required
def delete_patient(id):
    #deletes a given patient
    Patient.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Patient has been deleted.')
    return redirect(url_for('main.index'))