from datetime import datetime, timedelta, time

from utils.constants import APPOINTMENT_REASONS, PATIENT_GENDERS


def parse_treatment_money(total_cost_raw, paid_amount_raw):
    total_cost_raw = str(total_cost_raw or "").strip()
    paid_amount_raw = str(paid_amount_raw or "").strip()

    try:
        total_cost = float(total_cost_raw) if total_cost_raw else 0
        paid_amount = float(paid_amount_raw) if paid_amount_raw else 0
    except ValueError:
        return None, None, "Total cost and paid amount must be valid numbers."

    if total_cost < 0:
        return None, None, "Total cost cannot be negative."

    if paid_amount < 0:
        return None, None, "Paid amount cannot be negative."

    if paid_amount > total_cost:
        return None, None, "Paid amount cannot be greater than total cost."

    return total_cost, paid_amount, None


def parse_patient_data(form):
    first_name = form.get("first_name", "").strip()
    last_name = form.get("last_name", "").strip()
    gender = form.get("gender", "").strip()
    date_of_birth_raw = form.get("date_of_birth", "").strip()

    if not first_name:
        return None, "First name is required."

    if not last_name:
        return None, "Last name is required."

    if not gender:
        return None, "Gender is required."

    if gender not in PATIENT_GENDERS:
        return None, "Invalid gender value."

    if not date_of_birth_raw:
        return None, "Date of birth is required."

    try:
        date_of_birth = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
    except ValueError:
        return None, "Date of birth must be a valid date."

    patient_data = {
        "title": form.get("title"),
        "first_name": first_name,
        "last_name": last_name,
        "preferred_first_name": form.get("preferred_first_name"),
        "date_of_birth": date_of_birth,
        "gender": gender,
        "phone": form.get("phone"),
        "email": form.get("email"),
        "address": form.get("address"),
        "city": form.get("city"),
        "state": form.get("state"),
        "post_code": form.get("post_code"),
        "country": form.get("country"),
        "notes": form.get("notes"),
        "medical_information": form.get("medical_information"),
        "appointment_notes": form.get("appointment_notes"),
        "occupation": form.get("occupation"),
        "emergency_contact": form.get("emergency_contact"),
        "medicare_number": form.get("medicare_number"),
    }

    return patient_data, None


def parse_appointment_data(form):
    appointment_date_raw = form.get("appointment_date", "").strip()
    reason = form.get("reason", "").strip()

    if not appointment_date_raw:
        return None, "Appointment date and time is required."

    try:
        appointment_date = datetime.strptime(appointment_date_raw, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None, "Appointment date and time must be valid."

    now = datetime.now().replace(second=0, microsecond=0)
    max_appointment_date = now + timedelta(days=30)

    clinic_start_time = time(8, 0)
    clinic_end_time = time(18, 0)

    if appointment_date < now:
        return None, "Appointment date and time cannot be in the past."

    if appointment_date > max_appointment_date:
        return None, "Appointment date cannot be more than 30 days from today."

    if appointment_date.time() < clinic_start_time or appointment_date.time() > clinic_end_time:
        return None, "Appointment time must be between 08:00 and 18:00."

    if not reason:
        return None, "Appointment reason is required."

    if reason not in APPOINTMENT_REASONS:
        return None, "Invalid appointment reason."

    appointment_data = {
        "appointment_date": appointment_date,
        "reason": reason,
    }

    return appointment_data, None


def get_appointment_datetime_limits():
    now = datetime.now().replace(second=0, microsecond=0)
    max_appointment_date = now + timedelta(days=30)

    return (
        now.strftime("%Y-%m-%dT%H:%M"),
        max_appointment_date.strftime("%Y-%m-%dT%H:%M"),
    )


def parse_payment_amount(payment_amount_raw, remaining_amount):
    payment_amount_raw = str(payment_amount_raw or "").strip()

    if not payment_amount_raw:
        return None, "Payment amount is required."

    try:
        payment_amount = float(payment_amount_raw)
    except ValueError:
        return None, "Payment amount must be a valid number."

    if payment_amount <= 0:
        return None, "Payment amount must be greater than 0."

    if payment_amount > remaining_amount:
        return None, "Payment amount cannot be greater than the remaining amount."

    return payment_amount, None


def parse_invoice_payment_amount(payment_amount_raw):
    payment_amount_raw = str(payment_amount_raw or "").strip()

    if not payment_amount_raw:
        return None, "Payment amount is required."

    try:
        payment_amount = float(payment_amount_raw)
    except ValueError:
        return None, "Payment amount must be a valid number."

    if payment_amount <= 0:
        return None, "Payment amount must be greater than 0."

    return payment_amount, None