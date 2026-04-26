from flask import Flask, render_template, request, redirect, url_for
from models import db, Patient, Appointment, Treatment
from datetime import datetime

import json
import logging
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'instance' / 'clinic.db'
CONFIG_FILE = BASE_DIR / 'config' / 'clinic_config.json'
LOG_FILE_NAME = 'clinic.log'

##
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:1234@127.0.0.1:3308/dental_clinic'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


def load_config() -> str:
    if not CONFIG_FILE.exists():
        raise RuntimeError(
            'System is not configured yet. Please run Setup.exe first.'
        )

    try:
        with CONFIG_FILE.open('r', encoding='utf-8') as config_file:
            config_data = json.load(config_file)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            'Configuration file is invalid. Please run Setup.exe again.'
        ) from exc

    log_directory = str(config_data.get('log_directory', '')).strip()
    if not log_directory:
        raise RuntimeError(
            'Configuration is incomplete. Please run Setup.exe again.'
        )

    return log_directory


def setup_logging(log_directory: str) -> None:
    log_dir = Path(log_directory).expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / LOG_FILE_NAME

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False


log_directory = load_config()
setup_logging(log_directory)
app.logger.info('Application started successfully')


@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f'404 Not Found | path={request.path}')
    return 'page not found', 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.exception('500 Internal Server Error')
    return 'internal server error', 500


@app.route('/')
def home():
    app.logger.info('Home page opened')

    try:
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        done_appointments = Appointment.query.filter_by(status='Done').count()
        total_treatments = Treatment.query.count()

        all_treatments = Treatment.query.all()
        total_revenue = sum(treatment.total_cost for treatment in all_treatments)
        total_paid = sum(treatment.paid_amount for treatment in all_treatments)
        total_remaining = total_revenue - total_paid

        latest_patients = Patient.query.order_by(Patient.id.desc()).limit(5).all()
        latest_appointments = Appointment.query.order_by(Appointment.id.desc()).limit(5).all()

        return render_template(
            'index.html',
            total_patients=total_patients,
            total_appointments=total_appointments,
            done_appointments=done_appointments,
            total_treatments=total_treatments,
            total_revenue=total_revenue,
            total_paid=total_paid,
            total_remaining=total_remaining,
            latest_patients=latest_patients,
            latest_appointments=latest_appointments
        )

    except Exception:
        app.logger.exception('Error while loading home page')
        return 'Error Loading MainPage', 500


@app.route('/patients')
def patients():
    search_query = request.args.get('search', '')
    app.logger.info('Patients page opened')

    try:
        if search_query:
            all_patients = Patient.query.filter(
                Patient.full_name.ilike(f'%{search_query}%')
            ).all()
        else:
            all_patients = Patient.query.all()

        return render_template('patients.html', patients=all_patients, search_query=search_query)

    except Exception:
        app.logger.exception('Error while loading patients page')
        return 'Error Loading PatientsPage', 500


@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        full_name = request.form.get('full_name', '').strip()
        if not full_name:
            full_name = f'{first_name} {last_name}'.strip()

        date_of_birth_raw = request.form.get('date_of_birth')
        date_of_birth = None

        if date_of_birth_raw:
            date_of_birth = datetime.strptime(date_of_birth_raw, '%Y-%m-%d').date()

        new_patient = Patient(
            title=request.form.get('title'),
            first_name=first_name,
            last_name=last_name,
            preferred_first_name=request.form.get('preferred_first_name'),
            date_of_birth=date_of_birth,
            gender=request.form.get('gender'),

            full_name=full_name,

            phone=request.form.get('phone'),
            email=request.form.get('email'),

            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            post_code=request.form.get('post_code'),
            country=request.form.get('country'),

            notes=request.form.get('notes'),
            medical_information=request.form.get('medical_information'),
            appointment_notes=request.form.get('appointment_notes'),

            occupation=request.form.get('occupation'),
            emergency_contact=request.form.get('emergency_contact'),
            medicare_number=request.form.get('medicare_number')
        )

        db.session.add(new_patient)
        db.session.commit()

        return redirect(url_for('patients'))

    return render_template('add_patient.html')


@app.route('/patients/<int:patient_id>')
def patient_detail(patient_id):
    app.logger.info(f'Patient detail page opened | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        total_cost_sum = sum(treatment.total_cost for treatment in patient.treatments)
        total_paid_sum = sum(treatment.paid_amount for treatment in patient.treatments)
        total_remaining_sum = sum(treatment.remaining_amount for treatment in patient.treatments)

        return render_template(
            'patient_detail.html',
            patient=patient,
            total_cost_sum=total_cost_sum,
            total_paid_sum=total_paid_sum,
            total_remaining_sum=total_remaining_sum
        )

    except Exception:
        app.logger.exception(f'Error while loading patient detail | patient_id={patient_id}')
        return 'Error Loading PatientsInfo', 500


@app.route('/patients/<int:patient_id>/appointments/add', methods=['GET', 'POST'])
def add_appointment(patient_id):
    app.logger.info(f'Add appointment page/request | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        if request.method == 'POST':
            appointment_date = request.form['appointment_date'].replace('T', ' ')
            reason = request.form['reason']
            status = request.form['status']

            new_appointment = Appointment(
                patient_id=patient.id,
                appointment_date=appointment_date,
                reason=reason,
                status=status
            )

            db.session.add(new_appointment)
            db.session.commit()

            app.logger.info(
                f'Appointment added successfully | appointment_id={new_appointment.id}, patient_id={patient.id}'
            )

            return redirect(url_for('patient_detail', patient_id=patient.id))

        return render_template('add_appointment.html', patient=patient)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to add appointment | patient_id={patient_id}')
        return 'Error Loading AppointmentInfo', 500


@app.route('/patients/<int:patient_id>/treatments/add', methods=['GET', 'POST'])
def add_treatment(patient_id):
    app.logger.info(f'Add treatment page/request | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        if request.method == 'POST':
            treatment_date = request.form['treatment_date'].replace('T', ' ')
            procedure_type = request.form['procedure_type']
            tooth_number = request.form['tooth_number']
            notes = request.form['notes']
            total_cost = request.form['total_cost']
            paid_amount = request.form['paid_amount']

            new_treatment = Treatment(
                patient_id=patient.id,
                treatment_date=treatment_date,
                procedure_type=procedure_type,
                tooth_number=tooth_number,
                notes=notes,
                total_cost=float(total_cost) if total_cost else 0,
                paid_amount=float(paid_amount) if paid_amount else 0
            )

            db.session.add(new_treatment)
            db.session.commit()

            app.logger.info(
                f'Treatment added successfully | treatment_id={new_treatment.id}, patient_id={patient.id}'
            )

            return redirect(url_for('patient_detail', patient_id=patient.id))

        return render_template('add_treatment.html', patient=patient)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to add treatment | patient_id={patient_id}')
        return 'Error Adding Treatment', 500


@app.route('/appointments')
def appointments():
    search_query = request.args.get('search', '')

    if search_query:
        appointments = Appointment.query.join(Patient).filter(
            Patient.full_name.ilike(f"%{search_query}%")
        ).all()
    else:
        appointments = Appointment.query.all()

    return render_template(
        'appointments.html',
        appointments=appointments,
        search_query=search_query
    )


@app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
def edit_patient(patient_id):
    app.logger.info(f'Edit patient page/request | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        if request.method == 'POST':
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()

            full_name = request.form.get('full_name', '').strip()
            if not full_name:
                full_name = f'{first_name} {last_name}'.strip()

            date_of_birth_raw = request.form.get('date_of_birth')
            date_of_birth = None
            if date_of_birth_raw:
                date_of_birth = datetime.strptime(date_of_birth_raw, '%Y-%m-%d').date()

            patient.title = request.form.get('title')
            patient.first_name = first_name
            patient.last_name = last_name
            patient.preferred_first_name = request.form.get('preferred_first_name')
            patient.date_of_birth = date_of_birth
            patient.gender = request.form.get('gender')
            patient.full_name = full_name

            patient.phone = request.form.get('phone')
            patient.email = request.form.get('email')

            patient.address = request.form.get('address')
            patient.city = request.form.get('city')
            patient.state = request.form.get('state')
            patient.post_code = request.form.get('post_code')
            patient.country = request.form.get('country')

            patient.notes = request.form.get('notes')
            patient.medical_information = request.form.get('medical_information')
            patient.appointment_notes = request.form.get('appointment_notes')

            patient.occupation = request.form.get('occupation')
            patient.emergency_contact = request.form.get('emergency_contact')
            patient.medicare_number = request.form.get('medicare_number')

            db.session.commit()

            app.logger.info(f'Patient updated successfully | patient_id={patient.id}')
            return redirect(url_for('patient_detail', patient_id=patient.id))

        return render_template('edit_patient.html', patient=patient)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to edit patient | patient_id={patient_id}')
        return 'Failed to edit patient', 500
    
    
@app.route('/appointments/<int:appointment_id>/delete', methods=['GET', 'POST'])
def delete_appointment(appointment_id):
    app.logger.warning(f'Delete appointment page/request | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if request.method == 'POST':
            patient_id = appointment.patient_id
            db.session.delete(appointment)
            db.session.commit()

            app.logger.info(f'Appointment deleted successfully | appointment_id={appointment_id}')
            return redirect(url_for('patient_detail', patient_id=patient_id))

        return render_template('delete_appointment.html', appointment=appointment)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to delete appointment | appointment_id={appointment_id}')
        return 'Failed to delete appointment', 500


@app.route('/appointments/<int:appointment_id>/done')
def mark_appointment_done(appointment_id):
    app.logger.info(f'Mark appointment as done request | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = 'Done'
        db.session.commit()

        app.logger.info(f'Appointment marked as done | appointment_id={appointment.id}')
        return redirect(url_for('appointments'))

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to mark appointment as done | appointment_id={appointment_id}')
        return 'Failed to mark appointment as done', 500


@app.route('/appointments/<int:appointment_id>/cancel')
def mark_appointment_cancelled(appointment_id):
    app.logger.info(f'Mark appointment as cancelled request | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = 'Cancelled'
        db.session.commit()

        app.logger.info(f'Appointment marked as cancelled | appointment_id={appointment.id}')
        return redirect(url_for('appointments'))

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to mark appointment as cancelled | appointment_id={appointment_id}')
        return 'Failed to mark appointment as cancelled', 500


@app.route('/appointments/<int:appointment_id>/edit', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    app.logger.info(f'Edit appointment page/request | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if request.method == 'POST':
            appointment.appointment_date = request.form['appointment_date'].replace('T', ' ')
            appointment.reason = request.form['reason']
            appointment.status = request.form['status']

            db.session.commit()

            app.logger.info(f'Appointment updated successfully | appointment_id={appointment.id}')
            return redirect(url_for('patient_detail', patient_id=appointment.patient_id))

        return render_template('edit_appointment.html', appointment=appointment)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to edit appointment | appointment_id={appointment_id}')
        return 'Failed to edit appointment', 500


@app.route('/treatments/<int:treatment_id>/edit', methods=['GET', 'POST'])
def edit_treatment(treatment_id):
    app.logger.info(f'Edit treatment page/request | treatment_id={treatment_id}')

    try:
        treatment = Treatment.query.get_or_404(treatment_id)

        if request.method == 'POST':
            treatment.treatment_date = request.form['treatment_date'].replace('T', ' ')
            treatment.procedure_type = request.form['procedure_type']
            treatment.tooth_number = request.form['tooth_number']
            treatment.notes = request.form['notes']
            treatment.total_cost = float(request.form['total_cost']) if request.form['total_cost'] else 0
            treatment.paid_amount = float(request.form['paid_amount']) if request.form['paid_amount'] else 0

            db.session.commit()

            app.logger.info(f'Treatment updated successfully | treatment_id={treatment.id}')
            return redirect(url_for('patient_detail', patient_id=treatment.patient_id))

        return render_template('edit_treatment.html', treatment=treatment)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to edit treatment | treatment_id={treatment_id}')
        return 'Failed to edit treatment', 500


@app.route('/patients/<int:patient_id>/delete', methods=['GET', 'POST'])
def delete_patient(patient_id):
    app.logger.warning(f'Delete patient page/request | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        if request.method == 'POST':
            db.session.delete(patient)
            db.session.commit()

            app.logger.info(f'Patient deleted successfully | patient_id={patient_id}')
            return redirect(url_for('patients'))

        return render_template('delete_patient.html', patient=patient)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to delete patient | patient_id={patient_id}')
        return 'Failed to delete patient', 500


@app.route('/treatments/<int:treatment_id>/delete', methods=['GET', 'POST'])
def delete_treatment(treatment_id):
    app.logger.warning(f'Delete treatment page/request | treatment_id={treatment_id}')

    try:
        treatment = Treatment.query.get_or_404(treatment_id)

        if request.method == 'POST':
            patient_id = treatment.patient_id
            db.session.delete(treatment)
            db.session.commit()

            app.logger.info(f'Treatment deleted successfully | treatment_id={treatment_id}')
            return redirect(url_for('patient_detail', patient_id=patient_id))

        return render_template('delete_treatment.html', treatment=treatment)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to delete treatment | treatment_id={treatment_id}')
        return 'Failed to delete treatment', 500


if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Database tables created successfully or already exist')
        except Exception:
            app.logger.exception('Failed to create database tables')

    app.logger.info('Flask app is running')
    app.run(debug=True)
