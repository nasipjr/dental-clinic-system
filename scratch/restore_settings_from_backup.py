import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db
from models import SystemSetting

def restore_settings():
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notifications_and_settings_backup.json')
    if not os.path.exists(json_path):
        print("Error: Backup file not found!")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    settings_dict = data.get('system_settings', {})
    
    with app.app_context():
        for key, val in settings_dict.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = str(val) if val is not None else ""
            else:
                setting = SystemSetting(key=key, value=str(val) if val is not None else "")
                db.session.add(setting)
        
        db.session.commit()
        print("SUCCESS: All tokens and notification settings successfully restored into the new database!")

if __name__ == '__main__':
    restore_settings()
