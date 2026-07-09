import threading
from flask import current_app
from models import db, Appointment, Patient
from utils.settings_helper import get_setting
from utils.notification_helper import (
    send_commpeak_sms,
    send_telegram_message,
    send_smtp_email,
    format_notification_template,
    _log_notification
)

def send_patient_notifications_async(app, appointment_id, patient_id, action_type):
    """
    Background worker to send SMS, Telegram, and/or Email to the patient.
    action_type can be 'cancel' or 'reschedule'.
    """
    with app.app_context():
        try:
            appointment = Appointment.query.get(appointment_id)
            patient = Patient.query.get(patient_id)
            if not appointment or not patient:
                app.logger.error(f"Async notifications failed: appointment_id={appointment_id} or patient_id={patient_id} not found")
                return

            # Check if reminders are enabled for this patient specifically
            if not getattr(patient, "reminders_enabled", True):
                app.logger.info(f"Notifications disabled for patient {patient_id}")
                return

            clinic_name = get_setting("clinic_name", "Clinic")
            formatted_date = appointment.appointment_date.strftime("%Y-%m-%d %I:%M %p")
            patient_full_name = f"{patient.first_name} {patient.last_name}".strip()

            sms_enabled = get_setting("notification_enable_sms", "false").lower() == "true"
            telegram_enabled = get_setting("notification_enable_telegram", "false").lower() == "true"
            email_enabled = get_setting("notification_enable_email", "false").lower() == "true"

            if action_type == 'cancel':
                # Check cancellation notifications specifically
                cancel_sms_enabled = get_setting("sms_cancel_enabled", "true").lower() == "true"
                cancel_telegram_enabled = get_setting("telegram_cancel_enabled", "true").lower() == "true"
                cancel_email_enabled = get_setting("email_cancel_enabled", "true").lower() == "true"

                # 1. SMS
                if sms_enabled and cancel_sms_enabled and patient.phone:
                    template = get_setting("sms_cancel_template", "تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {appointment_time}.")
                    body = format_notification_template(template, patient_full_name, formatted_date, clinic_name)
                    success, msg = send_commpeak_sms(patient.phone, body)
                    _log_notification(appointment, patient, "sms_cancel", "sms", patient.phone, success, msg)

                # 2. Telegram
                telegram_chat_id = getattr(patient, "telegram_chat_id", None)
                if telegram_enabled and cancel_telegram_enabled and telegram_chat_id:
                    template = get_setting("telegram_cancel_template", "تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {appointment_time}. نتمنى لكم السلامة.")
                    body = format_notification_template(template, patient_full_name, formatted_date, clinic_name)
                    success, msg = send_telegram_message(telegram_chat_id, body)
                    _log_notification(appointment, patient, "telegram_cancel", "telegram", str(telegram_chat_id), success, msg)

                # 3. Email
                if email_enabled and cancel_email_enabled and patient.email:
                    subject_template = get_setting("email_cancel_subject", "إلغاء الموعد - {clinic_name}")
                    body_template = get_setting("email_cancel_template", "عزيزي {patient_name}،\n\nنود إعلامكم بأنه تم إلغاء موعدكم المحدد بتاريخ {appointment_time}.\n\nنتمنى لكم السلامة.\n\nمع تحيات،\n{clinic_name}")
                    
                    subject = format_notification_template(subject_template, patient_full_name, formatted_date, clinic_name)
                    body = format_notification_template(body_template, patient_full_name, formatted_date, clinic_name)
                    success, msg = send_smtp_email(patient.email, subject, body)
                    _log_notification(appointment, patient, "email_cancel", "email", patient.email, success, msg)

            elif action_type == 'reschedule':
                # Check reschedule notifications specifically
                reschedule_sms_enabled = get_setting("sms_reschedule_enabled", "true").lower() == "true"
                reschedule_telegram_enabled = get_setting("telegram_reschedule_enabled", "true").lower() == "true"
                reschedule_email_enabled = get_setting("email_reschedule_enabled", "true").lower() == "true"

                # 1. SMS
                if sms_enabled and reschedule_sms_enabled and patient.phone:
                    template = get_setting("sms_reschedule_template", "تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.")
                    body = format_notification_template(template, patient_full_name, formatted_date, clinic_name)
                    success, msg = send_commpeak_sms(patient.phone, body)
                    _log_notification(appointment, patient, "sms_reschedule", "sms", patient.phone, success, msg)

                # 2. Telegram
                telegram_chat_id = getattr(patient, "telegram_chat_id", None)
                if telegram_enabled and reschedule_telegram_enabled and telegram_chat_id:
                    template = get_setting("telegram_reschedule_template", "تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.")
                    body = format_notification_template(template, patient_full_name, formatted_date, clinic_name)
                    success, msg = send_telegram_message(telegram_chat_id, body)
                    _log_notification(appointment, patient, "telegram_reschedule", "telegram", str(telegram_chat_id), success, msg)

                # 3. Email
                if email_enabled and reschedule_email_enabled and patient.email:
                    subject_template = get_setting("email_reschedule_subject", "تعديل موعدك لدى {clinic_name}")
                    body_template = get_setting("email_reschedule_template", "عزيزي {patient_name}،\n\nنود إعلامكم بأنه تم تعديل موعدكم ليصبح بتاريخ {appointment_time}.\n\nيرجى الحضور في الوقت المحدد.\n\nمع تحيات،\n{clinic_name}")
                    
                    subject = format_notification_template(subject_template, patient_full_name, formatted_date, clinic_name)
                    body = format_notification_template(body_template, patient_full_name, formatted_date, clinic_name)
                    success, msg = send_smtp_email(patient.email, subject, body)
                    _log_notification(appointment, patient, "email_reschedule", "email", patient.email, success, msg)

        except Exception as e:
            app.logger.error(f"Error in send_patient_notifications_async: {e}")


def notify_appointment_cancellation(appointment):
    """
    Trigger cancellation notifications for patient in a background thread.
    """
    try:
        app = current_app._get_current_object()
        threading.Thread(
            target=send_patient_notifications_async,
            args=(app, appointment.id, appointment.patient_id, 'cancel'),
            daemon=True
        ).start()
    except Exception as e:
        # Fallback if outside application context during initialization or test
        pass


def notify_appointment_reschedule(appointment):
    """
    Trigger reschedule/edit time notifications for patient in a background thread.
    """
    try:
        app = current_app._get_current_object()
        threading.Thread(
            target=send_patient_notifications_async,
            args=(app, appointment.id, appointment.patient_id, 'reschedule'),
            daemon=True
        ).start()
    except Exception as e:
        pass
