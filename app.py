from flask import Flask, render_template, request, redirect, url_for
from models import db, Patient, Appointment, Treatment, Payment, PaymentAllocation
from datetime import datetime, timedelta, time

import json
import logging
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
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
APPOINTMENT_REASONS = {
    'Check-up',
    'Cleaning',
    'Filling',
    'Root Canal',
    'Extraction',
    'Crown / Bridge',
    'Braces / Orthodontics',
    'Whitening',
    'Emergency Pain',
    'Follow-up'
}
PATIENT_GENDERS = {
    'Male',
    'Female'
}
TREATMENT_PRICES = {
    'Check-up': 25000,
    'Cleaning': 50000,
    'Filling': 75000,
    'Root Canal': 150000,
    'Extraction': 80000,
    'Crown / Bridge': 200000,
    'Braces / Orthodontics': 300000,
    'Whitening': 120000,
    'Emergency Pain': 60000,
    'Follow-up': 20000
}

TREATMENT_PROCEDURE_TYPES = set(TREATMENT_PRICES.keys())


@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f'404 Not Found | path={request.path}')
    return 'page not found', 404
def parse_treatment_money(total_cost_raw, paid_amount_raw):
    total_cost_raw = str(total_cost_raw or '').strip()
    paid_amount_raw = str(paid_amount_raw or '').strip()

    try:
        total_cost = float(total_cost_raw) if total_cost_raw else 0
        paid_amount = float(paid_amount_raw) if paid_amount_raw else 0
    except ValueError:
        return None, None, 'Total cost and paid amount must be valid numbers.'

    if total_cost < 0:
        return None, None, 'Total cost cannot be negative.'

    if paid_amount < 0:
        return None, None, 'Paid amount cannot be negative.'

    if paid_amount > total_cost:
        return None, None, 'Paid amount cannot be greater than total cost.'

    return total_cost, paid_amount, None

def parse_patient_data(form):
    first_name = form.get('first_name', '').strip()
    last_name = form.get('last_name', '').strip()
    gender = form.get('gender', '').strip()
    date_of_birth_raw = form.get('date_of_birth', '').strip()

    if not first_name:
        return None, 'First name is required.'

    if not last_name:
        return None, 'Last name is required.'

    if not gender:
        return None, 'Gender is required.'

    if gender not in PATIENT_GENDERS:
        return None, 'Invalid gender value.'

    if not date_of_birth_raw:
        return None, 'Date of birth is required.'

    try:
        date_of_birth = datetime.strptime(date_of_birth_raw, '%Y-%m-%d').date()
    except ValueError:
        return None, 'Date of birth must be a valid date.'

    patient_data = {
        'title': form.get('title'),
        'first_name': first_name,
        'last_name': last_name,
        'preferred_first_name': form.get('preferred_first_name'),
        'date_of_birth': date_of_birth,
        'gender': gender,
        'phone': form.get('phone'),
        'email': form.get('email'),
        'address': form.get('address'),
        'city': form.get('city'),
        'state': form.get('state'),
        'post_code': form.get('post_code'),
        'country': form.get('country'),
        'notes': form.get('notes'),
        'medical_information': form.get('medical_information'),
        'appointment_notes': form.get('appointment_notes'),
        'occupation': form.get('occupation'),
        'emergency_contact': form.get('emergency_contact'),
        'medicare_number': form.get('medicare_number')
    }

    return patient_data, None

def parse_appointment_data(form):
    appointment_date_raw = form.get('appointment_date', '').strip()
    reason = form.get('reason', '').strip()

    if not appointment_date_raw:
        return None, 'Appointment date and time is required.'

    try:
        appointment_date = datetime.strptime(appointment_date_raw, '%Y-%m-%dT%H:%M')
    except ValueError:
        return None, 'Appointment date and time must be valid.'

    now = datetime.now().replace(second=0, microsecond=0)
    max_appointment_date = now + timedelta(days=30)

    clinic_start_time = time(8, 0)
    clinic_end_time = time(18, 0)

    if appointment_date < now:
        return None, 'Appointment date and time cannot be in the past.'

    if appointment_date > max_appointment_date:
        return None, 'Appointment date cannot be more than 30 days from today.'

    if appointment_date.time() < clinic_start_time or appointment_date.time() > clinic_end_time:
        return None, 'Appointment time must be between 08:00 and 18:00.'

    if not reason:
        return None, 'Appointment reason is required.'

    if reason not in APPOINTMENT_REASONS:
        return None, 'Invalid appointment reason.'

    appointment_data = {
        'appointment_date': appointment_date,
        'reason': reason
    }

    return appointment_data, None

def get_appointment_datetime_limits():
    now = datetime.now().replace(second=0, microsecond=0)
    max_appointment_date = now + timedelta(days=30)

    return (
        now.strftime('%Y-%m-%dT%H:%M'),
        max_appointment_date.strftime('%Y-%m-%dT%H:%M')
    )
    
def parse_payment_amount(payment_amount_raw, remaining_amount):
    payment_amount_raw = str(payment_amount_raw or '').strip()

    if not payment_amount_raw:
        return None, 'Payment amount is required.'

    try:
        payment_amount = float(payment_amount_raw)
    except ValueError:
        return None, 'Payment amount must be a valid number.'

    if payment_amount <= 0:
        return None, 'Payment amount must be greater than 0.'

    if payment_amount > remaining_amount:
        return None, 'Payment amount cannot be greater than the remaining amount.'

    return payment_amount, None

def parse_invoice_payment_amount(payment_amount_raw):
    payment_amount_raw = str(payment_amount_raw or '').strip()

    if not payment_amount_raw:
        return None, 'Payment amount is required.'

    try:
        payment_amount = float(payment_amount_raw)
    except ValueError:
        return None, 'Payment amount must be a valid number.'

    if payment_amount <= 0:
        return None, 'Payment amount must be greater than 0.'

    return payment_amount, None

def allocate_patient_payments_to_invoices(patient_id):
    patient_payments = (
        Payment.query
        .filter_by(patient_id=patient_id)
        .order_by(Payment.payment_date.asc(), Payment.id.asc())
        .all()
    )

    unpaid_invoices = (
        Appointment.query
        .filter(Appointment.patient_id == patient_id)
        .join(Treatment)
        .distinct()
        .order_by(Appointment.appointment_date.asc(), Appointment.id.asc())
        .all()
    )

    for payment in patient_payments:
        remaining_payment = payment.unallocated_amount

        if remaining_payment <= 0:
            continue

        for appointment in unpaid_invoices:
            if remaining_payment <= 0:
                break

            invoice_outstanding = appointment.outstanding_amount

            if invoice_outstanding <= 0:
                continue

            allocation_amount = min(remaining_payment, invoice_outstanding)

            allocation = PaymentAllocation(
                payment_id=payment.id,
                appointment_id=appointment.id,
                amount=allocation_amount
            )

            db.session.add(allocation)
            db.session.flush()

            remaining_payment -= allocation_amount

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
        scheduled_appointments = Appointment.query.filter_by(status='Scheduled').count()
        done_appointments = Appointment.query.filter_by(status='Done').count()
        total_treatments = Treatment.query.count()

        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        today_scheduled_appointments = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .filter(Appointment.status == 'Scheduled')
            .order_by(Appointment.appointment_date.asc())
            .all()
        )

        today_done_appointments = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .filter(Appointment.status == 'Done')
            .order_by(Appointment.appointment_date.asc())
            .all()
        )

        all_treatments = Treatment.query.all()
        all_payments = Payment.query.all()

        total_revenue = sum(treatment.total_cost for treatment in all_treatments)
        total_paid = sum(payment.amount for payment in all_payments)
        total_remaining = total_revenue - total_paid

        patient_search = request.args.get('patient_search', '')
        patient_sort = request.args.get('patient_sort', 'id')
        patient_order = request.args.get('patient_order', 'desc')

        appointment_search = request.args.get('appointment_search', '')
        appointment_sort = request.args.get('appointment_sort', 'date')
        appointment_order = request.args.get('appointment_order', 'desc')

        patients_query = Patient.query

        if patient_search:
            patients_query = patients_query.filter(
                (Patient.first_name.ilike(f'%{patient_search}%')) |
                (Patient.last_name.ilike(f'%{patient_search}%')) |
                (Patient.phone.ilike(f'%{patient_search}%')) |
                (Patient.email.ilike(f'%{patient_search}%')) |
                (Patient.city.ilike(f'%{patient_search}%'))
            )

        patient_sort_columns = {
            'id': Patient.id,
            'first_name': Patient.first_name,
            'last_name': Patient.last_name,
            'phone': Patient.phone,
            'email': Patient.email,
            'city': Patient.city
        }

        patient_sort_column = patient_sort_columns.get(patient_sort, Patient.id)

        if patient_order == 'asc':
            patients_query = patients_query.order_by(patient_sort_column.asc())
        else:
            patients_query = patients_query.order_by(patient_sort_column.desc())

        latest_patients = patients_query.limit(5).all()

        appointments_query = Appointment.query.join(Patient)

        if appointment_search:
            appointments_query = appointments_query.filter(
                (Patient.first_name.ilike(f'%{appointment_search}%')) |
                (Patient.last_name.ilike(f'%{appointment_search}%')) |
                (Appointment.reason.ilike(f'%{appointment_search}%')) |
                (Appointment.status.ilike(f'%{appointment_search}%'))
            )

        appointment_sort_columns = {
            'id': Appointment.id,
            'patient': Patient.first_name,
            'date': Appointment.appointment_date,
            'reason': Appointment.reason,
            'status': Appointment.status
        }

        appointment_sort_column = appointment_sort_columns.get(
            appointment_sort,
            Appointment.appointment_date
        )

        if appointment_order == 'asc':
            appointments_query = appointments_query.order_by(appointment_sort_column.asc())
        else:
            appointments_query = appointments_query.order_by(appointment_sort_column.desc())

        latest_appointments = appointments_query.limit(5).all()

        return render_template(
            'index.html',
            total_patients=total_patients,
            total_appointments=total_appointments,
            scheduled_appointments=scheduled_appointments,
            done_appointments=done_appointments,
            total_treatments=total_treatments,
            total_revenue=total_revenue,
            total_paid=total_paid,
            total_remaining=total_remaining,
            today_scheduled_appointments=today_scheduled_appointments,
            today_done_appointments=today_done_appointments,
            latest_patients=latest_patients,
            latest_appointments=latest_appointments,
            patient_search=patient_search,
            patient_sort=patient_sort,
            patient_order=patient_order,
            appointment_search=appointment_search,
            appointment_sort=appointment_sort,
            appointment_order=appointment_order
        )

    except Exception:
        app.logger.exception('Error while loading home page')
        return 'Error Loading MainPage', 500


@app.route('/dashboard/patients-table')
def dashboard_patients_table():
    patient_search = request.args.get('patient_search', '')
    patient_sort = request.args.get('patient_sort', 'id')
    patient_order = request.args.get('patient_order', 'desc')

    patients_query = Patient.query

    if patient_search:
        patients_query = patients_query.filter(
            (Patient.first_name.ilike(f'%{patient_search}%')) |
            (Patient.last_name.ilike(f'%{patient_search}%')) |
            (Patient.phone.ilike(f'%{patient_search}%')) |
            (Patient.email.ilike(f'%{patient_search}%')) |
            (Patient.city.ilike(f'%{patient_search}%'))
        )

    patient_sort_columns = {
        'id': Patient.id,
        'first_name': Patient.first_name,
        'last_name': Patient.last_name,
        'phone': Patient.phone,
        'email': Patient.email,
        'city': Patient.city
    }

    patient_sort_column = patient_sort_columns.get(patient_sort, Patient.id)

    if patient_order == 'asc':
        patients_query = patients_query.order_by(patient_sort_column.asc())
    else:
        patients_query = patients_query.order_by(patient_sort_column.desc())

    latest_patients = patients_query.limit(5).all()

    return render_template(
        'partials/_latest_patients_table.html',
        latest_patients=latest_patients,
        patient_search=patient_search,
        patient_sort=patient_sort,
        patient_order=patient_order
    )
    
@app.route('/dashboard/appointments-table')
def dashboard_appointments_table():
    appointment_search = request.args.get('appointment_search', '')
    appointment_sort = request.args.get('appointment_sort', 'date')
    appointment_order = request.args.get('appointment_order', 'desc')

    appointments_query = Appointment.query.join(Patient)

    if appointment_search:
        appointments_query = appointments_query.filter(
            (Patient.first_name.ilike(f'%{appointment_search}%')) |
            (Patient.last_name.ilike(f'%{appointment_search}%')) |
            (Appointment.reason.ilike(f'%{appointment_search}%')) |
            (Appointment.status.ilike(f'%{appointment_search}%'))
        )

    appointment_sort_columns = {
        'id': Appointment.id,
        'patient': Patient.first_name,
        'date': Appointment.appointment_date,
        'reason': Appointment.reason,
        'status': Appointment.status
    }

    appointment_sort_column = appointment_sort_columns.get(
        appointment_sort,
        Appointment.appointment_date
    )

    if appointment_order == 'asc':
        appointments_query = appointments_query.order_by(appointment_sort_column.asc())
    else:
        appointments_query = appointments_query.order_by(appointment_sort_column.desc())

    latest_appointments = appointments_query.limit(5).all()

    return render_template(
        'partials/_latest_appointments_table.html',
        latest_appointments=latest_appointments,
        appointment_search=appointment_search,
        appointment_sort=appointment_sort,
        appointment_order=appointment_order
    )


@app.route('/patients')
def patients():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    app.logger.info('Patients page opened')

    try:
        query = Patient.query

        if search_query:
            query = query.filter(
                (Patient.first_name.ilike(f'%{search_query}%')) |
                (Patient.last_name.ilike(f'%{search_query}%')) |
                (Patient.phone.ilike(f'%{search_query}%')) |
                (Patient.email.ilike(f'%{search_query}%')) |
                (Patient.city.ilike(f'%{search_query}%'))
            )

        sort_columns = {
            'id': Patient.id,
            'first_name': Patient.first_name,
            'last_name': Patient.last_name,
            'phone': Patient.phone,
            'email': Patient.email,
            'city': Patient.city,
            'date_of_birth': Patient.date_of_birth
        }

        sort_column = sort_columns.get(sort_by, Patient.id)

        if order == 'asc':
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return render_template(
            'patients.html',
            patients=pagination.items,
            pagination=pagination,
            search_query=search_query,
            sort_by=sort_by,
            order=order
        )

    except Exception:
        app.logger.exception('Error while loading patients page')
        return 'Error Loading PatientsPage', 500
    
    
@app.route('/appointments/<int:appointment_id>/session')
def appointment_session(appointment_id):
    app.logger.info(f'Appointment session opened | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        treatments = Treatment.query.filter_by(
            appointment_id=appointment.id
        ).order_by(Treatment.id.desc()).all()
        
        previous_treatments = (
            Treatment.query
            .join(Appointment)
            .filter(Appointment.patient_id == appointment.patient_id)
            .filter(Treatment.appointment_id != appointment.id)
            .order_by(Treatment.treatment_date.desc(), Treatment.id.desc())
            .all()
        )
        

        total_cost_sum = appointment.invoice_total
        total_paid_sum = appointment.total_paid
        total_remaining_sum = appointment.balance
        credit_amount = appointment.credit

        return render_template(
            'appointment_session.html',
            appointment=appointment,
            patient=appointment.patient,
            treatments=treatments,
            total_cost_sum=total_cost_sum,
            total_paid_sum=total_paid_sum,
            total_remaining_sum=total_remaining_sum,
            credit_amount=credit_amount,
            previous_treatments=previous_treatments,
        )

    except Exception:
        app.logger.exception(
            f'Failed to open appointment session | appointment_id={appointment_id}'
        )
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to open appointment session.',
            back_url=url_for('appointments')
        ), 500
    
@app.route('/appointments/<int:appointment_id>/treatments/add', methods=['GET', 'POST'])
def add_treatment_to_appointment(appointment_id):
    app.logger.info(f'Add treatment to appointment | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status != 'Scheduled':
            return render_template(
                'error_message.html',
                title='Action Not Allowed',
                message='Cannot add treatment because this appointment session is closed or cancelled.',
                back_url=url_for('appointment_session', appointment_id=appointment.id)
            ), 403

        if request.method == 'POST':
            treatment_date = appointment.appointment_date
            procedure_type = request.form.get('procedure_type', '').strip()

            if procedure_type not in TREATMENT_PROCEDURE_TYPES:
                return render_template(
                    'add_treatment.html',
                    appointment=appointment,
                    patient=appointment.patient,
                    treatment_prices=TREATMENT_PRICES,
                    error_message='Invalid treatment procedure type.'
                ), 400

            tooth_number = request.form.get('tooth_number', '').strip()
            notes = request.form.get('notes', '').strip()

            total_cost = TREATMENT_PRICES[procedure_type]

            new_treatment = Treatment(
                appointment_id=appointment.id,
                treatment_date=treatment_date,
                procedure_type=procedure_type,
                tooth_number=tooth_number,
                notes=notes,
                total_cost=total_cost
            )

            db.session.add(new_treatment)
            db.session.commit()

            app.logger.info(
                f'Treatment added successfully | treatment_id={new_treatment.id}, appointment_id={appointment.id}'
            )

            return redirect(url_for('appointment_session', appointment_id=appointment.id))

        return render_template(
            'add_treatment.html',
            appointment=appointment,
            patient=appointment.patient,
            treatment_prices=TREATMENT_PRICES
        )

    except Exception:
        db.session.rollback()
        app.logger.exception(
            f'Failed to add treatment to appointment | appointment_id={appointment_id}'
        )
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to add treatment.',
            back_url=url_for('appointment_session', appointment_id=appointment_id)
        ), 500

@app.route('/appointments/<int:appointment_id>/end-session', methods=['POST'])
def end_appointment_session(appointment_id):
    app.logger.info(f'End appointment session request | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status != 'Scheduled':
            return render_template(
                'error_message.html',
                title='Action Not Allowed',
                message='Only scheduled appointments can be ended.',
                back_url=url_for('appointment_session', appointment_id=appointment.id)
            ), 400

        appointment.status = 'Done'
        db.session.commit()

        app.logger.info(
            f'Appointment session ended successfully | appointment_id={appointment.id}'
        )

        return redirect(url_for('appointment_session', appointment_id=appointment.id))

    except Exception:
        db.session.rollback()
        app.logger.exception(
            f'Failed to end appointment session | appointment_id={appointment_id}'
        )
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to end appointment session.',
            back_url=url_for('appointment_session', appointment_id=appointment_id)
        ), 500


@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        patient_data, patient_error = parse_patient_data(request.form)

        if patient_error:
            return render_template(
                'add_patient.html',
                error_message=patient_error
            ), 400

        new_patient = Patient(**patient_data)

        db.session.add(new_patient)
        db.session.commit()

        return redirect(url_for('patients'))

    return render_template('add_patient.html')


@app.route('/patients/<int:patient_id>')
def patient_detail(patient_id):
    app.logger.info(f'Patient detail page opened | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        appointment_sort = request.args.get('appointment_sort', 'date')
        appointment_order = request.args.get('appointment_order', 'desc')

        treatment_sort = request.args.get('treatment_sort', 'date')
        treatment_order = request.args.get('treatment_order', 'desc')

        active_tab = request.args.get('tab', 'appointments')

        appointment_sort_columns = {
            'id': Appointment.id,
            'date': Appointment.appointment_date,
            'reason': Appointment.reason,
            'status': Appointment.status
        }

        appointment_sort_column = appointment_sort_columns.get(
            appointment_sort,
            Appointment.appointment_date
        )

        appointments_query = Appointment.query.filter_by(patient_id=patient.id)

        if appointment_order == 'asc':
            appointments_query = appointments_query.order_by(appointment_sort_column.asc())
        else:
            appointments_query = appointments_query.order_by(appointment_sort_column.desc())

        patient_appointments = appointments_query.all()

        treatment_sort_columns = {
            'id': Treatment.id,
            'date': Treatment.treatment_date,
            'procedure_type': Treatment.procedure_type,
            'tooth_number': Treatment.tooth_number,
        }

        treatment_sort_column = treatment_sort_columns.get(
            treatment_sort,
            Treatment.treatment_date
        )

        treatments_query = (
            Treatment.query
            .join(Appointment)
            .filter(Appointment.patient_id == patient.id)
        )

        if treatment_order == 'asc':
            treatments_query = treatments_query.order_by(treatment_sort_column.asc())
        else:
            treatments_query = treatments_query.order_by(treatment_sort_column.desc())

        patient_treatments = treatments_query.all()

        total_cost_sum = patient.total_invoice_amount
        total_paid_sum = patient.total_payments_amount
        total_remaining_sum = patient.outstanding_amount
        credit_amount = patient.credit_amount

        return render_template(
            'patient_detail.html',
            patient=patient,
            patient_appointments=patient_appointments,
            patient_treatments=patient_treatments,
            total_cost_sum=total_cost_sum,
            total_paid_sum=total_paid_sum,
            total_remaining_sum=total_remaining_sum,
            credit_amount=credit_amount,
            appointment_sort=appointment_sort,
            appointment_order=appointment_order,
            treatment_sort=treatment_sort,
            treatment_order=treatment_order,
            active_tab=active_tab
        )

    except Exception:
        app.logger.exception(f'Error while loading patient detail | patient_id={patient_id}')
        return 'Error Loading PatientsInfo', 500
    
    
@app.route('/patients/<int:patient_id>/appointments-table')
def patient_appointments_table(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    appointment_sort = request.args.get('appointment_sort', 'date')
    appointment_order = request.args.get('appointment_order', 'desc')

    sort_columns = {
        'id': Appointment.id,
        'date': Appointment.appointment_date,
        'reason': Appointment.reason,
        'status': Appointment.status
    }

    sort_column = sort_columns.get(appointment_sort, Appointment.appointment_date)

    query = Appointment.query.filter_by(patient_id=patient.id)

    if appointment_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    patient_appointments = query.all()

    return render_template(
        'partials/_patient_appointments_table.html',
        patient=patient,
        patient_appointments=patient_appointments,
        appointment_sort=appointment_sort,
        appointment_order=appointment_order
    )
    
@app.route('/patients/<int:patient_id>/treatments-table')
def patient_treatments_table(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    treatment_sort = request.args.get('treatment_sort', 'date')
    treatment_order = request.args.get('treatment_order', 'desc')

    sort_columns = {
        'id': Treatment.id,
        'date': Treatment.treatment_date,
        'procedure_type': Treatment.procedure_type,
        'tooth_number': Treatment.tooth_number,
    }

    sort_column = sort_columns.get(treatment_sort, Treatment.treatment_date)

    query = (
        Treatment.query
        .join(Appointment)
        .filter(Appointment.patient_id == patient.id)
    )

    if treatment_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    patient_treatments = query.all()

    return render_template(
        'partials/_patient_treatments_table.html',
        patient=patient,
        patient_treatments=patient_treatments,
        treatment_sort=treatment_sort,
        treatment_order=treatment_order
    )


@app.route('/patients/<int:patient_id>/appointments/add', methods=['GET', 'POST'])
def add_appointment(patient_id):
    app.logger.info(f'Add appointment page/request | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        if request.method == 'POST':
            appointment_data, appointment_error = parse_appointment_data(request.form)

            if appointment_error:
                return render_template(
                    'add_appointment.html',
                    patient=patient,
                    error_message=appointment_error,
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime
                ), 400

            new_appointment = Appointment(
                patient_id=patient.id,
                appointment_date=appointment_data['appointment_date'],
                reason=appointment_data['reason'],
                status='Scheduled'
            )

            db.session.add(new_appointment)
            db.session.commit()

            app.logger.info(
                f'Appointment added successfully | appointment_id={new_appointment.id}, patient_id={patient.id}'
            )

            return redirect(url_for('patient_detail', patient_id=patient.id))

        return render_template(
            'add_appointment.html',
            patient=patient,
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime
        )

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to add appointment | patient_id={patient_id}')
        return 'Error Loading AppointmentInfo', 500


@app.route('/patients/<int:patient_id>/treatments/add')
def add_treatment(patient_id):
    app.logger.warning(
        f'Legacy add treatment route opened | patient_id={patient_id}'
    )

    return (
        'Treatments must be added from an appointment session.',
        400
    )
    
    
@app.route('/payments')
def payments():
    app.logger.info('Payments page opened')

    try:
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'date')
        order = request.args.get('order', 'desc')

        all_payments = (
            Payment.query
            .join(Patient)
            .all()
        )

        if search_query:
            search_lower = search_query.lower()

            def matches_payment(payment):
                patient = payment.patient
                payment_number = f'pay-{payment.id}'.lower()
                payment_date = (
                    payment.payment_date.strftime('%Y-%m-%d %H:%M').lower()
                    if payment.payment_date else ''
                )

                searchable_values = [
                    payment_number,
                    str(payment.id),
                    patient.first_name or '',
                    patient.last_name or '',
                    patient.phone or '',
                    str(payment.amount),
                    str(payment.allocated_amount),
                    str(payment.unallocated_amount),
                    payment.notes or '',
                    payment_date
                ]

                return any(search_lower in str(value).lower() for value in searchable_values)

            all_payments = [
                payment
                for payment in all_payments
                if matches_payment(payment)
            ]

        sort_key_map = {
            'id': lambda payment: payment.id,
            'date': lambda payment: payment.payment_date or datetime.min,
            'patient': lambda payment: (
                payment.patient.first_name or '',
                payment.patient.last_name or ''
            ),
            'amount': lambda payment: payment.amount,
            'allocated': lambda payment: payment.allocated_amount,
            'credit': lambda payment: payment.unallocated_amount
        }

        sort_key = sort_key_map.get(sort_by, sort_key_map['date'])
        reverse_order = order != 'asc'

        all_payments = sorted(
            all_payments,
            key=sort_key,
            reverse=reverse_order
        )

        return render_template(
            'payments.html',
            payments=all_payments,
            search_query=search_query,
            sort_by=sort_by,
            order=order
        )

    except Exception:
        app.logger.exception('Failed to load payments page')
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to load payments.',
            back_url=url_for('home')
        ), 500


@app.route('/payments/add', methods=['GET', 'POST'])
def add_patient_payment():
    app.logger.info('Add patient payment page/request')

    try:
        patients = Patient.query.order_by(
            Patient.first_name.asc(),
            Patient.last_name.asc()
        ).all()

        selected_patient_id = request.args.get('patient_id', type=int)
        selected_patient = None

        if selected_patient_id:
            selected_patient = Patient.query.get(selected_patient_id)

        if request.method == 'POST':
            patient_id = request.form.get('patient_id', type=int)
            payment_amount_raw = request.form.get('payment_amount', '')
            notes = request.form.get('notes', '').strip()

            patient = Patient.query.get(patient_id)

            if not patient:
                return render_template(
                    'add_patient_payment.html',
                    patients=patients,
                    selected_patient_id=selected_patient_id,
                    selected_patient=selected_patient,
                    error_message='Please select a valid patient.'
                ), 400

            payment_amount, payment_error = parse_invoice_payment_amount(payment_amount_raw)

            if payment_error:
                return render_template(
                    'add_patient_payment.html',
                    patients=patients,
                    selected_patient_id=patient_id,
                    selected_patient=patient,
                    error_message=payment_error
                ), 400

            new_payment = Payment(
                patient_id=patient.id,
                amount=payment_amount,
                notes=notes
            )

            db.session.add(new_payment)
            db.session.flush()

            allocate_patient_payments_to_invoices(patient.id)

            db.session.commit()

            app.logger.info(
                f'Patient payment added successfully | patient_id={patient.id}, payment_id={new_payment.id}, amount={payment_amount}'
            )

            return redirect(url_for('payments'))

        return render_template(
            'add_patient_payment.html',
            patients=patients,
            selected_patient_id=selected_patient_id,
            selected_patient=selected_patient
        )

    except Exception:
        db.session.rollback()
        app.logger.exception('Failed to add patient payment')
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to add payment.',
            back_url=url_for('payments')
        ), 500


    
@app.route('/invoices')
def invoices():
    app.logger.info('Invoices page opened')

    try:
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'date')
        order = request.args.get('order', 'desc')

        invoice_appointments = (
            Appointment.query
            .join(Treatment)
            .distinct()
            .all()
        )

        if search_query:
            search_lower = search_query.lower()

            def matches_invoice(appointment):
                patient = appointment.patient
                invoice_number = f'inv-{appointment.id}'.lower()
                appointment_date = (
                    appointment.appointment_date.strftime('%Y-%m-%d %H:%M').lower()
                    if appointment.appointment_date else ''
                )

                searchable_values = [
                    invoice_number,
                    str(appointment.id),
                    patient.first_name or '',
                    patient.last_name or '',
                    patient.phone or '',
                    appointment.status or '',
                    appointment_date
                ]

                return any(search_lower in str(value).lower() for value in searchable_values)

            invoice_appointments = [
                appointment
                for appointment in invoice_appointments
                if matches_invoice(appointment)
            ]

        sort_key_map = {
            'id': lambda appointment: appointment.id,
            'patient': lambda appointment: (
                appointment.patient.first_name or '',
                appointment.patient.last_name or ''
            ),
            'date': lambda appointment: appointment.appointment_date or datetime.min,
            'treatments': lambda appointment: appointment.treatments_count,
            'total': lambda appointment: appointment.invoice_total,
            'payments': lambda appointment: appointment.total_paid,
            'outstanding': lambda appointment: appointment.balance,
            'status': lambda appointment: appointment.invoice_status
        }

        sort_key = sort_key_map.get(sort_by, sort_key_map['date'])
        reverse_order = order != 'asc'

        invoice_appointments = sorted(
            invoice_appointments,
            key=sort_key,
            reverse=reverse_order
        )

        return render_template(
            'invoices.html',
            invoice_appointments=invoice_appointments,
            search_query=search_query,
            sort_by=sort_by,
            order=order
        )

    except Exception:
        app.logger.exception('Failed to load invoices page')
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to load invoices.',
            back_url=url_for('home')
        ), 500

@app.route('/invoices/<int:appointment_id>')
def view_invoice(appointment_id):
    app.logger.info(f'Invoice detail page opened | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if not appointment.has_invoice:
            return render_template(
                'error_message.html',
                title='No Invoice Available',
                message='This appointment has no treatments, so there is no invoice to view.',
                back_url=url_for('invoices')
            ), 400

        return render_template(
            'invoice_detail.html',
            appointment=appointment,
            patient=appointment.patient,
            treatments=appointment.treatments
        )

    except Exception:
        app.logger.exception(f'Failed to load invoice detail | appointment_id={appointment_id}')
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to load invoice.',
            back_url=url_for('invoices')
        ), 500

@app.route('/appointments')
def appointments():
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort', 'date')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Appointment.query.join(Patient)

    if search_query:
        query = query.filter(
            (Patient.first_name.ilike(f'%{search_query}%')) |
            (Patient.last_name.ilike(f'%{search_query}%'))
        )

    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    sort_columns = {
        'id': Appointment.id,
        'patient': Patient.first_name,
        'date': Appointment.appointment_date,
        'status': Appointment.status,
        'reason': Appointment.reason
    }

    sort_column = sort_columns.get(sort_by, Appointment.appointment_date)

    if order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template(
        'appointments.html',
        appointments=pagination.items,
        pagination=pagination,
        search_query=search_query,
        status_filter=status_filter,
        sort_by=sort_by,
        order=order
    )


@app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
def edit_patient(patient_id):
    app.logger.info(f'Edit patient page/request | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        if request.method == 'POST':
            patient_data, patient_error = parse_patient_data(request.form)

            if patient_error:
                return render_template(
                    'edit_patient.html',
                    patient=patient,
                    mode='edit',
                    error_message=patient_error
                ), 400

            for field, value in patient_data.items():
                setattr(patient, field, value)
                
            db.session.commit()

            app.logger.info(f'Patient updated successfully | patient_id={patient.id}')
            return redirect(url_for('patient_detail', patient_id=patient.id))

        return render_template(
            'edit_patient.html',
            patient=patient,
            mode='edit'
        )

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to edit patient | patient_id={patient_id}')
        return 'Failed to edit patient', 500
    
    
@app.route('/patients/<int:patient_id>/view')
def view_patient(patient_id):
    app.logger.info(f'View patient page opened | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        return render_template(
            'edit_patient.html',
            patient=patient,
            mode='view'
        )

    except Exception:
        app.logger.exception(f'Failed to view patient | patient_id={patient_id}')
        return 'Failed to view patient', 500
    
    
@app.route('/appointments/<int:appointment_id>/delete', methods=['GET', 'POST'])
def delete_appointment(appointment_id):
    app.logger.warning(f'Delete appointment page/request | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status == 'Done':
            return render_template(
                'error_message.html',
                title='Action Not Allowed',
                message='Cannot delete a completed appointment because it may contain important medical or payment history.',
                back_url=url_for('patient_detail', patient_id=appointment.patient_id)
            ), 403

        if appointment.treatments:
            return render_template(
                'error_message.html',
                title='Action Not Allowed',
                message='Cannot delete an appointment that has treatments.',
                back_url=url_for('patient_detail', patient_id=appointment.patient_id)
            ), 403

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
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to delete appointment.',
            back_url=url_for('appointments')
        ), 500





@app.route('/appointments/<int:appointment_id>/edit', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    app.logger.info(f'Edit appointment page/request | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        if request.method == 'POST':

            # Only scheduled appointments can be edited.
            # "Done" must only happen through End Session.
            if appointment.status != 'Scheduled':
                return 'Cannot edit a closed or cancelled appointment.', 403

            appointment_data, appointment_error = parse_appointment_data(request.form)

            if appointment_error:
                return render_template(
                    'edit_appointment.html',
                    appointment=appointment,
                    mode='edit',
                    error_message=appointment_error,
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime
                ), 400

            new_status = request.form.get('status', '').strip()

            # In edit page, only Scheduled and Cancelled are allowed.
            # Done is not allowed here.
            if new_status not in {'Scheduled', 'Cancelled'}:
                return render_template(
                    'edit_appointment.html',
                    appointment=appointment,
                    mode='edit',
                    error_message='Invalid appointment status.',
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime
                ), 400

            appointment.appointment_date = appointment_data['appointment_date']
            appointment.reason = appointment_data['reason']
            appointment.status = new_status

            db.session.commit()

            app.logger.info(f'Appointment updated successfully | appointment_id={appointment.id}')
            return redirect(url_for('patient_detail', patient_id=appointment.patient_id))

        return render_template(
            'edit_appointment.html',
            appointment=appointment,
            mode='edit',
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime
        )

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to edit appointment | appointment_id={appointment_id}')
        return 'Failed to edit appointment', 500
    
@app.route('/appointments/<int:appointment_id>/view')
def view_appointment(appointment_id):
    app.logger.info(f'View appointment page opened | appointment_id={appointment_id}')

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        return render_template(
            'edit_appointment.html',
            appointment=appointment,
            mode='view',
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime
        )

    except Exception:
        app.logger.exception(f'Failed to view appointment | appointment_id={appointment_id}')
        return 'Failed to view appointment', 500


@app.route('/treatments/<int:treatment_id>/edit', methods=['GET', 'POST'])
def edit_treatment(treatment_id):
    app.logger.info(f'Edit treatment page/request | treatment_id={treatment_id}')

    try:
        treatment = Treatment.query.get_or_404(treatment_id)

        if treatment.appointment.status != 'Scheduled' and request.method == 'POST':
            return render_template(
                'error_message.html',
                title='Action Not Allowed',
                message='Cannot edit this treatment because the appointment session is closed or cancelled.',
                back_url=url_for('appointment_session', appointment_id=treatment.appointment_id)
            ), 403

        if request.method == 'POST':
            treatment.treatment_date = treatment.appointment.appointment_date

            procedure_type = request.form.get('procedure_type', '').strip()

            if procedure_type not in TREATMENT_PROCEDURE_TYPES:
                return render_template(
                    'edit_treatment.html',
                    treatment=treatment,
                    appointment=treatment.appointment,
                    patient=treatment.appointment.patient,
                    mode='edit',
                    treatment_prices=TREATMENT_PRICES,
                    error_message='Invalid treatment procedure type.'
                ), 400

            treatment.procedure_type = procedure_type
            treatment.tooth_number = request.form.get('tooth_number', '').strip()
            treatment.notes = request.form.get('notes', '').strip()

            treatment.total_cost = TREATMENT_PRICES[procedure_type]

            db.session.commit()

            app.logger.info(f'Treatment updated successfully | treatment_id={treatment.id}')

            return redirect(
                url_for(
                    'appointment_session',
                    appointment_id=treatment.appointment_id
                )
            )

        return render_template(
            'edit_treatment.html',
            treatment=treatment,
            appointment=treatment.appointment,
            patient=treatment.appointment.patient,
            mode='edit',
            treatment_prices=TREATMENT_PRICES
        )

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to edit treatment | treatment_id={treatment_id}')
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to edit treatment.',
            back_url=url_for('appointments')
        ), 500


@app.route('/treatments/<int:treatment_id>/view')
def view_treatment(treatment_id):
    app.logger.info(f'View treatment page opened | treatment_id={treatment_id}')

    try:
        treatment = Treatment.query.get_or_404(treatment_id)

        return render_template(
            'edit_treatment.html',
            treatment=treatment,
            appointment=treatment.appointment,
            patient=treatment.appointment.patient,
            mode='view',
            treatment_prices=TREATMENT_PRICES
        )

    except Exception:
        app.logger.exception(f'Failed to view treatment | treatment_id={treatment_id}')
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to view treatment.',
            back_url=url_for('appointments')
        ), 500


@app.route('/patients/<int:patient_id>/delete', methods=['GET', 'POST'])
def delete_patient(patient_id):
    app.logger.warning(f'Delete patient page/request | patient_id={patient_id}')

    try:
        patient = Patient.query.get_or_404(patient_id)

        if patient.appointments:
            return render_template(
                'error_message.html',
                title='Action Not Allowed',
                message='Cannot delete this patient because they have appointments linked to their medical history.',
                back_url=url_for('patient_detail', patient_id=patient.id)
            ), 403

        if request.method == 'POST':
            db.session.delete(patient)
            db.session.commit()

            app.logger.info(f'Patient deleted successfully | patient_id={patient_id}')
            return redirect(url_for('patients'))

        return render_template('delete_patient.html', patient=patient)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to delete patient | patient_id={patient_id}')
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to delete patient.',
            back_url=url_for('patients')
        ), 500
    


@app.route('/treatments/<int:treatment_id>/delete', methods=['GET', 'POST'])
def delete_treatment(treatment_id):
    app.logger.warning(f'Delete treatment page/request | treatment_id={treatment_id}')

    try:
        treatment = Treatment.query.get_or_404(treatment_id)
        appointment_id = treatment.appointment_id

        if treatment.appointment.status != 'Scheduled':
            return render_template(
                'error_message.html',
                title='Action Not Allowed',
                message='Cannot delete this treatment because the appointment session is closed or cancelled.',
                back_url=url_for('appointment_session', appointment_id=appointment_id)
            ), 403

        if request.method == 'POST':
            db.session.delete(treatment)
            db.session.commit()

            app.logger.info(f'Treatment deleted successfully | treatment_id={treatment_id}')
            return redirect(url_for('appointment_session', appointment_id=appointment_id))

        return render_template('delete_treatment.html', treatment=treatment)

    except Exception:
        db.session.rollback()
        app.logger.exception(f'Failed to delete treatment | treatment_id={treatment_id}')
        return render_template(
            'error_message.html',
            title='Error',
            message='Failed to delete treatment.',
            back_url=url_for('appointments')
        ), 500


if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Database tables created successfully or already exist')
        except Exception:
            app.logger.exception('Failed to create database tables')

    app.logger.info('Flask app is running')
    app.run(debug=True)
