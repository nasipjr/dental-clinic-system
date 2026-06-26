import sys
sys.path.append('.')
from app import app
from models import db, Appointment

with app.app_context():
    appts = Appointment.query.all()
    for appt in sorted(appts, key=lambda a: a.appointment_date):
        if appt.appointment_date.strftime('%Y-%m') == '2026-06':
            print(f"ID: {appt.id}, Date: {appt.appointment_date}, Patient: {appt.patient.first_name} {appt.patient.last_name}, Status: {appt.status}")
