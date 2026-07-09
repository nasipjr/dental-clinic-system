import os
import threading
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from flask import current_app
from models import db, Appointment, Patient, NotificationLog
from utils.settings_helper import get_setting


# ─────────────────────────────────────────────
#  Telegram Bot
# ─────────────────────────────────────────────
def send_telegram_message(chat_id, body, bot_token=None):
    """Send a message via Telegram Bot API to a specific chat_id."""
    if bot_token is None:
        bot_token = get_setting("telegram_bot_token", "")

    if not bot_token:
        current_app.logger.info(f"[MOCK TELEGRAM] chat_id={chat_id} | Body: {body}")
        return True, "Mock Sent (Bot token not configured)"

    if not chat_id:
        return False, "No Telegram chat_id provided for this patient"

    try:
        import urllib.request
        import urllib.parse
        import json

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": body,
            "parse_mode": "HTML"
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if result.get("ok"):
            msg_id = result.get("result", {}).get("message_id", "?")
            return True, f"Sent message_id={msg_id}"
        else:
            err = result.get("description", "Unknown error")
            current_app.logger.error(f"Telegram API error: {err}")
            return False, err

    except Exception as e:
        current_app.logger.error(f"Telegram message sending failed: {e}")
        return False, str(e)


# ─────────────────────────────────────────────
#  CommPeak — SMS Gateway (TextPeak Streams API)
# ─────────────────────────────────────────────
def send_commpeak_sms(to_number, body, api_key=None, stream_id=None):
    """Send SMS via CommPeak TextPeak Streams API (simple_send endpoint)."""
    if api_key is None:
        api_key = get_setting("commpeak_api_key", "")

    if not api_key:
        current_app.logger.info(f"[MOCK SMS] To: {to_number} | Body: {body}")
        return True, "Mock Sent (CommPeak credentials not configured)"

    try:
        import urllib.request
        import urllib.parse
        import urllib.error
        import json
        import time

        # Clean number to ensure E.164 digits format (remove '+' for compatibility)
        cleaned_number = to_number.replace("+", "").strip()

        # The simple_send endpoint with trailing slash to prevent HTTP 307 redirect issues
        url = "https://textpeak-streams.commpeak.com/simple_send/"
        
        headers = {
            "Authorization": api_key,  # Direct stream token authorization
            "Content-Type": "application/json; charset=utf-8"
        }
        
        payload = json.dumps({
            "messages": [
                {
                    "internal_id": str(int(time.time())),
                    "recipient_phone": cleaned_number,
                    "message_content": body
                }
            ]
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result_data = json.loads(resp.read().decode("utf-8"))
            if result_data.get("status") is True:
                return True, f"Sent: {result_data}"
            else:
                err_details = ""
                messages = result_data.get("messages", [])
                if messages:
                    err_details = messages[0].get("details") or messages[0].get("error")
                return False, f"CommPeak Error: {err_details or result_data}"

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        current_app.logger.error(f"CommPeak API error: {e.code} - {err_msg}")
        return False, f"API Error {e.code}: {err_msg}"
    except Exception as e:
        current_app.logger.error(f"CommPeak sending failed: {e}")
        return False, str(e)


# ─────────────────────────────────────────────
#  SMTP Email (Gmail or any SMTP server)
# ─────────────────────────────────────────────
def send_smtp_email(to_email, subject, body, smtp_host=None, smtp_port=None, smtp_user=None, smtp_password=None, from_email=None):
    """Send an email via SMTP (Gmail App Password recommended)."""
    if smtp_host is None:
        smtp_host = get_setting("smtp_host", "smtp.gmail.com")
    if smtp_port is None:
        smtp_port = get_setting("smtp_port", "587")
    if smtp_user is None:
        smtp_user = get_setting("smtp_user", "")
    if smtp_password is None:
        smtp_password = get_setting("smtp_password", "")
    if from_email is None:
        from_email = get_setting("smtp_from_email", "")

    if not smtp_user or not smtp_password or not from_email:
        current_app.logger.info(
            f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {body}"
        )
        return True, "Mock Sent (SMTP credentials not configured)"

    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"]    = from_email
        msg["To"]      = to_email

        # 'with' ensures connection is always closed even on error
        with smtplib.SMTP(smtp_host, int(smtp_port), timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, [to_email], msg.as_string())

        return True, "Email sent successfully"

    except Exception as e:
        current_app.logger.error(f"SMTP Email sending failed: {e}")
        return False, str(e)


def format_notification_template(template_str, patient_name, formatted_date, clinic_name):
    """Replace English and Arabic placeholders with actual values."""
    if not template_str:
        return ""
    return template_str.replace("{patient_name}", patient_name)\
                       .replace("{المريض_name}", patient_name)\
                       .replace("{اسم_المريض}", patient_name)\
                       .replace("{appointment_time}", formatted_date)\
                       .replace("{الموعد_الوقت}", formatted_date)\
                       .replace("{وقت_الموعد}", formatted_date)\
                       .replace("{clinic_name}", clinic_name)\
                       .replace("{اسم_العيادة}", clinic_name)


# ─────────────────────────────────────────────
#  Core reminder logic
# ─────────────────────────────────────────────
def process_reminders(app):
    now        = datetime.now()
    end_window = now + timedelta(hours=25)

    sms_enabled      = get_setting("notification_enable_sms",      "false").lower() == "true"
    telegram_enabled = get_setting("notification_enable_telegram",  "false").lower() == "true"
    email_enabled    = get_setting("notification_enable_email",     "false").lower() == "true"

    if not (sms_enabled or telegram_enabled or email_enabled):
        return

    appointments = Appointment.query.filter(
        Appointment.status == "Scheduled",
        Appointment.appointment_date >= now,
        Appointment.appointment_date <= end_window
    ).all()

    clinic_name = get_setting("clinic_name", "Clinic")

    for appt in appointments:
        time_to_appt  = appt.appointment_date - now
        hours_to_appt = time_to_appt.total_seconds() / 3600.0

        patient = appt.patient
        if not patient:
            continue

        # 24-hour reminder (between 22 and 25 hours out)
        if 22.0 <= hours_to_appt <= 25.0:
            trigger_reminder(
                appt, patient, "24h",
                sms_enabled, telegram_enabled, email_enabled, clinic_name
            )
        # 2-hour reminder (between 1.5 and 2.5 hours out)
        elif 1.5 <= hours_to_appt <= 2.5:
            trigger_reminder(
                appt, patient, "2h",
                sms_enabled, telegram_enabled, email_enabled, clinic_name
            )


def trigger_reminder(appt, patient, type_label,
                     sms_enabled, telegram_enabled, email_enabled, clinic_name):
    # Check if reminders are enabled for this patient specifically
    if not getattr(patient, "reminders_enabled", True):
        return

    formatted_date = appt.appointment_date.strftime("%Y-%m-%d %I:%M %p")

    # ── SMS via CommPeak ──────────────────────────────────────────────────
    if sms_enabled and patient.phone:
        timing_enabled = True
        template = ""
        if type_label == "24h":
            timing_enabled = get_setting("sms_24h_enabled", "true").lower() == "true"
            template = get_setting("sms_24h_template", "")
        elif type_label == "2h":
            timing_enabled = get_setting("sms_2h_enabled", "true").lower() == "true"
            template = get_setting("sms_2h_template", "")

        if timing_enabled and template:
            type_key = f"sms_{type_label}"
            existing = NotificationLog.query.filter_by(
                appointment_id=appt.id, type=type_key
            ).first()
            if not existing:
                patient_full_name = f"{patient.first_name} {patient.last_name}".strip()
                body = format_notification_template(template, patient_full_name, formatted_date, clinic_name)
                success, msg = send_commpeak_sms(patient.phone, body)
                _log_notification(appt, patient, type_key, "sms", patient.phone, success, msg)

    # ── Telegram Bot ─────────────────────────────────────────────────────
    if telegram_enabled:
        telegram_chat_id = getattr(patient, "telegram_chat_id", None)
        if telegram_chat_id:
            timing_enabled = True
            template = ""
            if type_label == "24h":
                timing_enabled = get_setting("telegram_24h_enabled", "true").lower() == "true"
                template = get_setting("telegram_24h_template", "")
            elif type_label == "2h":
                timing_enabled = get_setting("telegram_2h_enabled", "true").lower() == "true"
                template = get_setting("telegram_2h_template", "")

            if timing_enabled and template:
                type_key = f"telegram_{type_label}"
                existing = NotificationLog.query.filter_by(
                    appointment_id=appt.id, type=type_key
                ).first()
                if not existing:
                    patient_full_name = f"{patient.first_name} {patient.last_name}".strip()
                    body = format_notification_template(template, patient_full_name, formatted_date, clinic_name)
                    success, msg = send_telegram_message(telegram_chat_id, body)
                    _log_notification(
                        appt, patient, type_key, "telegram", str(telegram_chat_id), success, msg
                    )

    # ── Email via SMTP ────────────────────────────────────────────────────
    if email_enabled and patient.email:
        timing_enabled = True
        template_subject = ""
        template_body = ""
        if type_label == "24h":
            timing_enabled = get_setting("email_24h_enabled", "true").lower() == "true"
            template_subject = get_setting("email_24h_subject", "")
            template_body = get_setting("email_24h_template", "")
        elif type_label == "2h":
            timing_enabled = get_setting("email_2h_enabled", "true").lower() == "true"
            template_subject = get_setting("email_2h_subject", "")
            template_body = get_setting("email_2h_template", "")

        if timing_enabled and template_subject and template_body:
            type_key = f"email_{type_label}"
            existing = NotificationLog.query.filter_by(
                appointment_id=appt.id, type=type_key
            ).first()
            if not existing:
                patient_full_name = f"{patient.first_name} {patient.last_name}".strip()
                subject = format_notification_template(template_subject, patient_full_name, formatted_date, clinic_name)
                body = format_notification_template(template_body, patient_full_name, formatted_date, clinic_name)
                success, msg = send_smtp_email(patient.email, subject, body)
                _log_notification(
                    appt, patient, type_key, "email", patient.email, success, msg
                )


def _log_notification(appt, patient, type_key, channel, recipient, success, msg):
    """Helper: create and commit a NotificationLog entry."""
    try:
        log = NotificationLog(
            appointment_id=appt.id,
            patient_id=patient.id,
            type=type_key,
            channel=channel,
            recipient=recipient,
            status="sent" if success else "failed",
            error_message=msg if not success else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to log notification: {e}")


# ─────────────────────────────────────────────
#  Background scheduler thread
# ─────────────────────────────────────────────
def schedule_appointment_reminders(app):
    def run_reminder_loop():
        # Wait a bit for app startup
        time.sleep(15)
        while True:
            with app.app_context():
                try:
                    process_reminders(app)
                except Exception as e:
                    app.logger.error(
                        f"Failed to execute appointment reminders process: {e}"
                    )
            # Check every 5 minutes
            time.sleep(300)

    thread = threading.Thread(target=run_reminder_loop, daemon=True)
    thread.start()


# ─────────────────────────────────────────────
#  Telegram Bot Polling Listener & Auto-Register
# ─────────────────────────────────────────────
def start_telegram_bot_listener(app):
    """Starts a background thread to poll Telegram updates and auto-register patient chat IDs."""
    def run_polling_loop():
        # Wait a bit for app startup
        time.sleep(10)
        last_update_id = 0

        while True:
            with app.app_context():
                bot_token = get_setting("telegram_bot_token", "")
                clinic_name = get_setting("clinic_name", "العيادة")

            if not bot_token:
                time.sleep(10)
                continue

            try:
                import urllib.request
                import urllib.parse
                import json

                url = f"https://api.telegram.org/bot{bot_token}/getUpdates?timeout=30&limit=10"
                if last_update_id > 0:
                    url += f"&offset={last_update_id + 1}"

                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=35) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                if data.get("ok"):
                    for update in data.get("result", []):
                        last_update_id = update["update_id"]
                        process_telegram_update(app, update, bot_token, clinic_name)

            except Exception:
                # Silently catch networking errors or server restarts
                pass

            time.sleep(2)

    thread = threading.Thread(target=run_polling_loop, daemon=True)
    thread.start()


def process_telegram_update(app, update, bot_token, clinic_name):
    """Process a single incoming Telegram Bot update (start commands and contact sharing)."""
    import urllib.request
    import urllib.parse
    import json
    from models import db, Patient

    message = update.get("message")
    if not message:
        return

    chat = message.get("chat")
    chat_id = chat.get("id")

    # 1. User shared contact (phone number)
    contact = message.get("contact")
    if contact:
        user_id = message.get("from", {}).get("id")
        contact_user_id = contact.get("user_id")

        if contact_user_id and contact_user_id != user_id:
            reply_text = "❌ عذراً، يجب مشاركة رقم هاتفك الشخصي الخاص بك من خلال الضغط على الزر المتاح."
            _send_telegram_bot_reply(bot_token, chat_id, reply_text)
            return

        phone = contact.get("phone_number", "").strip()
        clean_phone = phone.replace("+", "").strip()

        with app.app_context():
            # Query match by last 9 digits of phone suffix to support Syrian formats (e.g. 9xxxxxxxx or 09xxxxxxxx)
            suffix = clean_phone[-9:] if len(clean_phone) >= 9 else clean_phone
            patient = Patient.query.filter(Patient.phone.like(f"%{suffix}")).first()

            if patient:
                patient.telegram_chat_id = chat_id
                db.session.commit()

                reply_text = (
                    f"✅ <b>تم تفعيل التذكيرات بنجاح!</b>\n\n"
                    f"مرحباً بك <b>{patient.first_name} {patient.last_name}</b> في نظام تذكير المواعيد لـ <b>{clinic_name}</b>.\n"
                    f"ستصلك رسائل التذكير التلقائية هنا مجاناً."
                )
                reply_markup = {"remove_keyboard": True}
                _send_telegram_bot_reply(bot_token, chat_id, reply_text, reply_markup)
            else:
                reply_text = (
                    f"❌ لم نجد رقم الهاتف <b>+{clean_phone}</b> مسجلاً في عيادتنا.\n\n"
                    f"يرجى طلب تسجيل رقم هاتفك هذا من السكرتيرة في العيادة أولاً لتتمكن من تفعيل الخدمة."
                )
                _send_telegram_bot_reply(bot_token, chat_id, reply_text)
        return

    # 2. Regular message / start
    text = message.get("text", "").strip()
    if text:
        reply_text = (
            f"👋 مرحباً بك في بوت التذكيرات لـ <b>{clinic_name}</b>!\n\n"
            f"لتفعيل خدمة التذكير التلقائي بالمواعيد عبر تيليغرام مجاناً، يرجى الضغط على الزر أدناه لمشاركة رقم هاتفك المعتمد لدينا في العيادة."
        )
        reply_markup = {
            "keyboard": [
                [
                    {
                        "text": "📱 مشاركة رقم الهاتف لتفعيل التذكيرات",
                        "request_contact": True
                    }
                ]
            ],
            "one_time_keyboard": True,
            "resize_keyboard": True
        }
        _send_telegram_bot_reply(bot_token, chat_id, reply_text, reply_markup)


def _send_telegram_bot_reply(bot_token, chat_id, text, reply_markup=None):
    """Helper to send outbound responses from the bot."""
    import urllib.request
    import urllib.parse
    import json

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
    except Exception:
        pass


_bot_username_cache = None

def get_bot_username():
    """Retrieve and cache the bot username from Telegram API to generate dynamic links."""
    global _bot_username_cache
    if _bot_username_cache:
        return _bot_username_cache

    token = get_setting("telegram_bot_token", "")
    if not token:
        return None

    import urllib.request
    import json
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                username = data["result"].get("username")
                _bot_username_cache = username
                return username
    except Exception:
        pass
    return None
