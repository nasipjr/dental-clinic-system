import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Appointment, Patient, NotificationLog
from services.notification_service import notify_appointment_cancellation, notify_appointment_reschedule

with app.app_context():
    print("Finding a scheduled appointment to test...")
    # Find any scheduled appointment
    appt = Appointment.query.filter_by(status="Scheduled").first()
    if not appt:
        print("No Scheduled appointments found, trying to find any appointment...")
        appt = Appointment.query.first()
        
    if not appt:
        print("No appointments found in the database. Please make sure there is dummy data.")
        sys.exit(1)
        
    patient = appt.patient
    print(f"Testing with Appointment ID {appt.id} for patient {patient.first_name} {patient.last_name}")
    
    # Temporarily enable settings for testing
    from utils.settings_helper import set_setting, get_setting
    set_setting("notification_enable_sms", "true")
    set_setting("notification_enable_telegram", "true")
    set_setting("notification_enable_email", "true")
    set_setting("sms_cancel_enabled", "true")
    set_setting("telegram_cancel_enabled", "true")
    set_setting("email_cancel_enabled", "true")
    
    # Save original values of phone/email/telegram just in case, but let's make sure they are set
    orig_phone = patient.phone
    orig_email = patient.email
    orig_tg = getattr(patient, "telegram_chat_id", None)
    
    if not patient.phone:
        patient.phone = "+963958948727"
    if not patient.email:
        patient.email = "test@example.com"
    if not getattr(patient, "telegram_chat_id", None):
        patient.telegram_chat_id = 123456789
        
    db.session.commit()

    print("\nSynchronous debug of settings and flags:")
    sms_enabled = get_setting("notification_enable_sms", "false").lower() == "true"
    telegram_enabled = get_setting("notification_enable_telegram", "false").lower() == "true"
    email_enabled = get_setting("notification_enable_email", "false").lower() == "true"
    cancel_email_enabled = get_setting("email_cancel_enabled", "true").lower() == "true"
    print(f"sms_enabled: {sms_enabled}")
    print(f"telegram_enabled: {telegram_enabled}")
    print(f"email_enabled: {email_enabled}")
    print(f"cancel_email_enabled: {cancel_email_enabled}")
    print(f"patient.email: {patient.email}")

    print("\n1. Testing Cancellation Notification...")
    # Clean previous test logs
    NotificationLog.query.filter_by(appointment_id=appt.id).delete()
    db.session.commit()
    
    notify_appointment_cancellation(appt)
    
    # Wait for the background thread to finish
    import time
    print("Waiting for background thread to run...")
    time.sleep(10)
    
    db.session.rollback()
    logs = NotificationLog.query.filter_by(appointment_id=appt.id).all()
    print(f"Found {len(logs)} notification logs:")
    for log in logs:
        print(f" - Channel: {log.channel}, Type: {log.type}, Status: {log.status}, Error: {log.error_message}")
        
    print("\n2. Testing Reschedule Notification...")
    # Clean logs again
    NotificationLog.query.filter_by(appointment_id=appt.id).delete()
    db.session.commit()
    
    notify_appointment_reschedule(appt)
    
    print("Waiting for background thread to run...")
    time.sleep(10)
    
    db.session.rollback()
    logs = NotificationLog.query.filter_by(appointment_id=appt.id).all()
    print(f"Found {len(logs)} notification logs:")
    for log in logs:
        print(f" - Channel: {log.channel}, Type: {log.type}, Status: {log.status}, Error: {log.error_message}")
        
    # Revert patient changes
    patient.phone = orig_phone
    patient.email = orig_email
    patient.telegram_chat_id = orig_tg
    db.session.commit()
    
    print("\nTest complete!")
