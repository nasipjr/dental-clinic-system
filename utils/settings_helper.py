import json
from models import db, SystemSetting

DEFAULT_TREATMENT_PRICES = {
    "Check-up": 25000,
    "Cleaning": 50000,
    "Filling": 75000,
    "Root Canal": 150000,
    "Extraction": 80000,
    "Crown / Bridge": 200000,
    "Braces / Orthodontics": 300000,
    "Whitening": 120000,
    "Emergency Pain": 60000,
    "Follow-up": 20000
}

DEFAULT_SETTINGS = {
    "clinic_name": "Clinic",
    "clinic_phone": "+963 958 948 727",
    "clinic_email": "kh.nasipdragon@gmail.com",
    "clinic_address": "Damascus, Syria",
    "developer_whatsapp": "963958948727",
    "currency_symbol": "$",
    "default_appointment_duration": "30",
    "working_hours_start": "09:00",
    "working_hours_end": "17:00",
    "working_days": "0,1,2,3,4,6",
    "treatment_prices": json.dumps(DEFAULT_TREATMENT_PRICES),
    "anesthesia_needle_price": "50000",
    # ── Notification channels ──────────────────────────────────
    "notification_enable_sms": "false",       # CommPeak
    "notification_enable_telegram": "false",  # Telegram Bot
    "notification_enable_email": "false",     # SMTP
    # ── Telegram Bot credentials ───────────────────────────────
    "telegram_bot_token": "",
    "telegram_24h_enabled": "true",
    "telegram_2h_enabled": "true",
    "telegram_24h_template": "تذكير موعد من {clinic_name}: مرحباً {patient_name}، نود تذكيركم بموعدكم غداً بتاريخ {appointment_time}. نتمنى لكم السلامة.",
    "telegram_2h_template": "تذكير موعد من {clinic_name}: مرحباً {patient_name}، نود تذكيركم بموعدكم اليوم بعد ساعتين في تمام الساعة {appointment_time}. بانتظاركم.",
    # ── CommPeak credentials (Streams SMS gateway) ─────────────
    "commpeak_api_key": "",
    "commpeak_stream_id": "",
    # ── SMTP Email credentials ─────────────────────────────────
    "smtp_host": "smtp.gmail.com",
    "smtp_port": "587",
    "smtp_user": "",
    "smtp_password": "",
    "smtp_from_email": "",
    "email_24h_enabled": "true",
    "email_2h_enabled": "true",
    "email_24h_subject": "تذكير بموعدك لدى {clinic_name}",
    "email_24h_template": "عزيزي {patient_name}،\n\nهذا تذكير بموعدك لدى {clinic_name} غداً بتاريخ {appointment_time}.\n\nنتمنى لكم السلامة.\n\nمع تحيات،\n{clinic_name}",
    "email_2h_subject": "تذكير بموعدك لدى {clinic_name}",
    "email_2h_template": "عزيزي {patient_name}،\n\nهذا تذكير بموعدك لدى {clinic_name} اليوم بعد ساعتين في تمام الساعة {appointment_time}.\n\nبانتظاركم.\n\nمع تحيات،\n{clinic_name}",
    # ── SMS reminder templates ─────────────────────────────────
    "sms_24h_enabled": "true",
    "sms_2h_enabled": "true",
    "sms_24h_template": "تذكير من {clinic_name}: موعدك بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.",
    "sms_2h_template": "تذكير من {clinic_name}: موعدك بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.",
    # ── Cancel and Reschedule notifications ────────────────────
    "sms_cancel_enabled": "true",
    "sms_reschedule_enabled": "true",
    "telegram_cancel_enabled": "true",
    "telegram_reschedule_enabled": "true",
    "email_cancel_enabled": "true",
    "email_reschedule_enabled": "true",
    "sms_cancel_template": "تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {appointment_time}.",
    "sms_reschedule_template": "تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.",
    "telegram_cancel_template": "تنبيه من {clinic_name}: تم إلغاء موعدك المحدد بتاريخ {appointment_time}. نتمنى لكم السلامة.",
    "telegram_reschedule_template": "تنبيه من {clinic_name}: تم تعديل موعدك ليصبح بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.",
    "email_cancel_subject": "إلغاء الموعد - {clinic_name}",
    "email_cancel_template": "عزيزي {patient_name}،\n\nنود إعلامكم بأنه تم إلغاء موعدكم المحدد بتاريخ {appointment_time}.\n\nنتمنى لكم السلامة.\n\nمع تحيات،\n{clinic_name}",
    "email_reschedule_subject": "تعديل موعدك لدى {clinic_name}",
    "email_reschedule_template": "عزيزي {patient_name}،\n\nنود إعلامكم بأنه تم تعديل موعدكم ليصبح بتاريخ {appointment_time}.\n\nيرجى الحضور في الوقت المحدد.\n\nمع تحيات،\n{clinic_name}",
    # ── Billing ───────────────────────────────────────────────
    "tax_rate": "15",
    "clinic_vat_number": "",
    "booking_window_days": "30"
}

from flask import g, has_app_context

def get_setting(key, default=None):
    if has_app_context():
        if not hasattr(g, "system_settings_cache"):
            g.system_settings_cache = {}
        if key in g.system_settings_cache:
            return g.system_settings_cache[key]

    val = None
    try:
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting is not None:
            val = setting.value
    except Exception:
        pass

    if val is None:
        if default is not None:
            val = default
        else:
            val = DEFAULT_SETTINGS.get(key, None)

    if has_app_context():
        g.system_settings_cache[key] = val

    return val

def set_setting(key, value):
    try:
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
        else:
            setting = SystemSetting(key=key, value=str(value))
            db.session.add(setting)
        db.session.commit()

        if has_app_context():
            if not hasattr(g, "system_settings_cache"):
                g.system_settings_cache = {}
            g.system_settings_cache[key] = str(value)

        return True
    except Exception:
        db.session.rollback()
        return False

def get_currency_symbol():
    return get_setting("currency_symbol", "$")

def get_treatment_prices():
    val = get_setting("treatment_prices")
    if val:
        try:
            return json.loads(val)
        except Exception:
            pass
    return DEFAULT_TREATMENT_PRICES
