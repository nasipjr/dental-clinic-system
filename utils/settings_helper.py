import json
from models import db, SystemSetting

DEFAULT_TREATMENT_DETAILS = {
    # 1. فحص وتشخيص (Diagnostic)
    "فحص دوري واستشارة": {"price": 25000, "duration": 20, "active": True, "category": "فحص وتشخيص"},
    "صورة بانورامية للأسنان": {"price": 50000, "duration": 20, "active": True, "category": "فحص وتشخيص"},
    "أشعة سينية (شعاعية)": {"price": 20000, "duration": 15, "active": True, "category": "فحص وتشخيص"},
    "كشف ألم طارئ": {"price": 60000, "duration": 30, "active": True, "category": "فحص وتشخيص"},
    "متابعة دورية": {"price": 20000, "duration": 15, "active": True, "category": "فحص وتشخيص"},

    # 2. حشوات ومعالجات تجميلية (Restorative & Cosmetic)
    "حشوة ضوئية كومبوزيت": {"price": 60000, "duration": 30, "active": True, "category": "حشوات ومعالجات تجميلية"},
    "تنظيف وتلميع الأسنان وتقليح": {"price": 50000, "duration": 30, "active": True, "category": "حشوات ومعالجات تجميلية"},
    "حشوة تجميلية": {"price": 200000, "duration": 30, "active": True, "category": "حشوات ومعالجات تجميلية"},
    "حشوة ضوئية كومبوزيت (سطح واحد)": {"price": 60000, "duration": 30, "active": True, "category": "حشوات ومعالجات تجميلية"},
    "حشوة ضوئية كومبوزيت (عدة سطوح)": {"price": 85000, "duration": 40, "active": True, "category": "حشوات ومعالجات تجميلية"},
    "حشوة أملغم ملغمية": {"price": 55000, "duration": 30, "active": True, "category": "حشوات ومعالجات تجميلية"},
    "تبييض الأسنان بالليزر/الضوء": {"price": 120000, "duration": 45, "active": True, "category": "حشوات ومعالجات تجميلية"},
    "عدسات فينير تجميلية": {"price": 250000, "duration": 45, "active": True, "category": "حشوات ومعالجات تجميلية"},

    # 3. علاج عصب وجذور (Endodontics)
    "جلسة سحب عصب وتنظيف قنوات": {"price": 200000, "duration": 45, "active": True, "category": "علاج عصب وجذور"},
    "حشو قنوات وحشو نهائي (عصب)": {"price": 150000, "duration": 45, "active": True, "category": "علاج عصب وجذور"},
    "إعادة علاج عصب سابق": {"price": 180000, "duration": 50, "active": True, "category": "علاج عصب وجذور"},
    "وتد فايبر مع حشوة بناء": {"price": 100000, "duration": 35, "active": True, "category": "علاج عصب وجذور"},

    # 4. جراحة وقلع (Oral Surgery)
    "قلع سن عادي": {"price": 80000, "duration": 30, "active": True, "category": "جراحة وقلع"},
    "معالجة ما بعد القلع": {"price": 30000, "duration": 20, "active": True, "category": "جراحة وقلع"},
    "قلع جراحي / ضرس عقل انحشاري": {"price": 180000, "duration": 45, "active": True, "category": "جراحة وقلع"},
    "زرع سن (زرعة تيتانيوم)": {"price": 450000, "duration": 60, "active": True, "category": "جراحة وقلع"},
    "طعوم عظمية ورفع جيب فكي": {"price": 350000, "duration": 60, "active": True, "category": "جراحة وقلع"},

    # 5. تعويضات وتيجان (Prosthodontics)
    "تاج زيركون / بورسلين": {"price": 200000, "duration": 45, "active": True, "category": "تعويضات وتيجان"},
    "جسر أسنان ثابت": {"price": 350000, "duration": 50, "active": True, "category": "تعويضات وتيجان"},
    "تاج إيماكس تجميلي": {"price": 230000, "duration": 45, "active": True, "category": "تعويضات وتيجان"},
    "طقم أسنان متحرك كاملاً": {"price": 350000, "duration": 50, "active": True, "category": "تعويضات وتيجان"},
    "طقم أسنان جزئي هيكلي": {"price": 250000, "duration": 40, "active": True, "category": "تعويضات وتيجان"},
    "طبعة أسنان وتأطير": {"price": 40000, "duration": 25, "active": True, "category": "تعويضات وتيجان"},

    # 6. تقويم أسنان (Orthodontics)
    "تركيب تقويم أسنان": {"price": 600000, "duration": 60, "active": True, "category": "تقويم أسنان"},
    "جلسة شد وتفقد تقويم": {"price": 35000, "duration": 20, "active": True, "category": "تقويم أسنان"},
    "فك تقويم وتثبيت": {"price": 120000, "duration": 40, "active": True, "category": "تقويم أسنان"},
    "تقويم شفاف (صينية)": {"price": 750000, "duration": 45, "active": True, "category": "تقويم أسنان"},

    # 7. أسنان أطفال (Pediatric Dentistry)
    "حشوة أطفال مخصصة": {"price": 45000, "duration": 25, "active": True, "category": "أسنان أطفال"},
    "بتر عصب أطفال (سحب عصب لببي)": {"price": 70000, "duration": 30, "active": True, "category": "أسنان أطفال"},
    "حافظ مسافة للأطفال": {"price": 80000, "duration": 30, "active": True, "category": "أسنان أطفال"},
    "تغليف ميازيب وقائي": {"price": 35000, "duration": 20, "active": True, "category": "أسنان أطفال"},

    # 8. إجراءات عامة وأخرى (General & Other Procedures)
    "تطبيق فلورايد وقائي": {"price": 30000, "duration": 15, "active": True, "category": "إجراءات عامة وأخرى"},
    "معالجة حساسيات الأسنان": {"price": 35000, "duration": 20, "active": True, "category": "إجراءات عامة وأخرى"},
    "واقي ليلي ضد الصرير": {"price": 100000, "duration": 30, "active": True, "category": "إجراءات عامة وأخرى"},
    "علاج التهابات اللثة": {"price": 60000, "duration": 30, "active": True, "category": "إجراءات عامة وأخرى"},
    "شهادة تقرير طبي": {"price": 25000, "duration": 15, "active": True, "category": "إجراءات عامة وأخرى"}
}

DEFAULT_TREATMENT_PRICES = {k: v["price"] for k, v in DEFAULT_TREATMENT_DETAILS.items()}

ARABIC_PROCEDURE_NAMES_MAP = {
    "فحص دوري": "فحص دوري واستشارة",
    "ألم طارئ": "كشف ألم طارئ",
    "متابعة": "متابعة دورية",
    "حشوة أسنان": "حشوة ضوئية كومبوزيت",
    "تنظيف وتلميع": "تنظيف وتلميع الأسنان وتقليح",
    "علاج عصب السن": "حشو قنوات وحشو نهائي (عصب)",
    "قلع سن": "قلع سن عادي",
    "تاج / جسر": "تاج زيركون / بورسلين",
    "تقويم الأسنان": "تركيب تقويم أسنان",
    "تبييض الأسنان": "تبييض الأسنان بالليزر/الضوء",
    "Check-up": "فحص دوري واستشارة",
    "Cleaning": "تنظيف وتلميع الأسنان وتقليح",
    "Filling": "حشوة ضوئية كومبوزيت",
    "Root Canal": "حشو قنوات وحشو نهائي (عصب)",
    "Extraction": "قلع سن عادي",
    "Post-Extraction Treatment": "معالجة ما بعد القلع",
    "Post-Extraction Care": "معالجة ما بعد القلع",
    "Crown / Bridge": "تاج زيركون / بورسلين",
    "Braces / Orthodontics": "تركيب تقويم أسنان",
    "Whitening": "تبييض الأسنان بالليزر/الضوء",
    "Emergency Pain": "كشف ألم طارئ",
    "Follow-up": "متابعة دورية",
}

DEFAULT_SETTINGS = {
    "clinic_name": "Clinic",
    "clinic_phone": "+963 958 948 727",
    "clinic_email": "kh.nasipdragon@gmail.com",
    "clinic_address": "Damascus, Syria",
    "developer_whatsapp": "963958948727",
    "currency_symbol": "$",
    "default_appointment_duration": "30",
    "auto_cancel_expired_minutes": "120",
    "auto_close_open_session_minutes": "120",
    "working_hours_start": "09:00",
    "working_hours_end": "19:00",
    "working_days": "0,1,2,3,4,5,6",
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
    "sms_24h_enabled": "true",
    "sms_2h_enabled": "true",
    "sms_24h_template": "تذكير من {clinic_name}: موعدك بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.",
    "sms_2h_template": "تذكير من {clinic_name}: موعدك بتاريخ {appointment_time}. يرجى الحضور في الوقت المحدد.",
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
    "tax_rate": "15",
    "clinic_vat_number": "",
    "booking_window_days": "60"
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
        db.session.expire_all()

        if has_app_context():
            if not hasattr(g, "system_settings_cache"):
                g.system_settings_cache = {}
            g.system_settings_cache[key] = str(value)

        return True
    except Exception:
        db.session.rollback()
        return False


def populate_default_settings():
    from models import db, SystemSetting
    try:
        for key, val in DEFAULT_SETTINGS.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                db.session.add(SystemSetting(key=key, value=val))
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False




DEFAULT_ANESTHESIA_TYPES = [
    {"name": "تخدير ارتشاحي (إبرة قصيرة)", "price": 50000},
    {"name": "تخدير حصري / ناصفي (إبرة طويلة)", "price": 60000},
    {"name": "تخدير موضعي (سطحي / جل)", "price": 25000},
    {"name": "تخدير خاص للأطفال", "price": 45000}
]

def get_currency_symbol():
    return get_setting("currency_symbol", "$")

def get_anesthesia_types():
    val = get_setting("anesthesia_types")
    if val:
        try:
            items = json.loads(val)
            if isinstance(items, list) and len(items) > 0:
                return items
        except Exception:
            pass
    base_price = float(get_setting("anesthesia_needle_price", 50000))
    types = [dict(item) for item in DEFAULT_ANESTHESIA_TYPES]
    if types:
        types[0]["price"] = base_price
    return types

def get_treatment_details():
    val = get_setting("treatment_prices")
    details_dict = {}
    if val:
        try:
            raw_dict = json.loads(val)
            if any(k in ARABIC_PROCEDURE_NAMES_MAP for k in raw_dict.keys()):
                updated_raw = {}
                for k, v in raw_dict.items():
                    new_k = ARABIC_PROCEDURE_NAMES_MAP.get(k, k)
                    updated_raw[new_k] = v
                raw_dict = updated_raw

            for name, val_item in raw_dict.items():
                default_info = DEFAULT_TREATMENT_DETAILS.get(name, {"price": 50000, "duration": 30, "active": True, "category": "عام"})
                if isinstance(val_item, dict):
                    details_dict[name] = {
                        "price": float(val_item.get("price", default_info["price"])),
                        "duration": int(val_item.get("duration", default_info["duration"])),
                        "active": bool(val_item.get("active", default_info["active"])),
                        "category": str(val_item.get("category", default_info["category"]))
                    }
                else:
                    details_dict[name] = {
                        "price": float(val_item),
                        "duration": int(default_info["duration"]),
                        "active": True,
                        "category": str(default_info["category"])
                    }
        except Exception:
            details_dict = DEFAULT_TREATMENT_DETAILS.copy()
    else:
        details_dict = DEFAULT_TREATMENT_DETAILS.copy()

    if "قلع سن عادي" not in details_dict and "قلع سن" not in details_dict:
        details_dict["قلع سن عادي"] = DEFAULT_TREATMENT_DETAILS["قلع سن عادي"].copy()
    if "معالجة ما بعد القلع" not in details_dict:
        details_dict["معالجة ما بعد القلع"] = DEFAULT_TREATMENT_DETAILS["معالجة ما بعد القلع"].copy()

    for proc_name, item in details_dict.items():
        if item.get("category") in ("جراحة", "عام") and proc_name in ("قلع سن عادي", "قلع سن", "معالجة ما بعد القلع"):
            item["category"] = "جراحة وقلع"
        elif item.get("category") == "جراحة":
            item["category"] = "جراحة وقلع"

    return details_dict

def get_treatment_prices():
    details = get_treatment_details()
    return {k: v["price"] for k, v in details.items()}
