import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import SystemSetting
from utils.notification_helper import format_notification_template

with app.app_context():
    template = SystemSetting.query.filter_by(key="telegram_2h_template").first().value
    print("Template from DB:", repr(template))
    
    patient_name = "نسيب جبارة"
    formatted_date = "03:15 AM 09-07-2026"
    clinic_name = "Clinic"
    
    result = format_notification_template(template, patient_name, formatted_date, clinic_name)
    print("Formatted result:", repr(result))
