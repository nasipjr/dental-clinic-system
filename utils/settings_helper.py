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
    "currency_symbol": "$",
    "default_appointment_duration": "30",
    "working_hours_start": "09:00",
    "working_hours_end": "17:00",
    "working_days": "0,1,2,3,4,6",
    "treatment_prices": json.dumps(DEFAULT_TREATMENT_PRICES)
}

def get_setting(key, default=None):
    try:
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting is not None:
            return setting.value
    except Exception:
        pass
    if default is not None:
        return default
    return DEFAULT_SETTINGS.get(key, None)

def set_setting(key, value):
    try:
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
        else:
            setting = SystemSetting(key=key, value=str(value))
            db.session.add(setting)
        db.session.commit()
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
