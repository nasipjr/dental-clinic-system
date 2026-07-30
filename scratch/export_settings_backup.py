import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db
from models import SystemSetting, Patient

def main():
    app.app_context().push()

    settings_data = {}
    for s in SystemSetting.query.all():
        settings_data[s.key] = s.value

    patient_chats = []
    for p in Patient.query.filter(Patient.telegram_chat_id.isnot(None)).all():
        patient_chats.append({
            'id': p.id,
            'name': f"{p.first_name} {p.last_name}",
            'phone': p.phone,
            'telegram_chat_id': p.telegram_chat_id
        })

    backup_payload = {
        'system_settings': settings_data,
        'patient_telegram_chats': patient_chats
    }

    # 1. JSON Export
    json_path = 'notifications_and_settings_backup.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(backup_payload, f, ensure_ascii=False, indent=4)

    # 2. Text Export
    txt_path = 'notifications_and_settings_backup.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("====================================================================\n")
        f.write("    DENTAL CLINIC MS - NOTIFICATION TOKENS & SETTINGS BACKUP\n")
        f.write("====================================================================\n\n")
        
        f.write("[1. TELEGRAM BOT NOTIFICATIONS]\n")
        f.write(f"Telegram Bot Token: {settings_data.get('telegram_bot_token', '')}\n")
        f.write(f"Enable Telegram Notifications: {settings_data.get('notification_enable_telegram', '')}\n")
        f.write(f"24h Reminder Enabled: {settings_data.get('telegram_24h_enabled', '')}\n")
        f.write(f"2h Reminder Enabled: {settings_data.get('telegram_2h_enabled', '')}\n")
        f.write(f"Cancel Reminder Enabled: {settings_data.get('telegram_cancel_enabled', '')}\n")
        f.write(f"Reschedule Reminder Enabled: {settings_data.get('telegram_reschedule_enabled', '')}\n\n")

        f.write("[2. EASY SEND SMS PROVIDER]\n")
        f.write(f"SMS Username: {settings_data.get('easysendsms_username', '')}\n")
        f.write(f"SMS Password: {settings_data.get('easysendsms_password', '')}\n")
        f.write(f"SMS Sender Name: {settings_data.get('easysendsms_sender', '')}\n")
        f.write(f"Enable SMS Notifications: {settings_data.get('notification_enable_sms', '')}\n\n")

        f.write("[3. COMMPEAK SMS PROVIDER]\n")
        f.write(f"Commpeak API Key: {settings_data.get('commpeak_api_key', '')}\n")
        f.write(f"Commpeak Stream ID: {settings_data.get('commpeak_stream_id', '')}\n\n")

        f.write("[4. SMTP GMAIL NOTIFICATIONS]\n")
        f.write(f"SMTP Host: {settings_data.get('smtp_host', '')}\n")
        f.write(f"SMTP Port: {settings_data.get('smtp_port', '')}\n")
        f.write(f"SMTP User: {settings_data.get('smtp_user', '')}\n")
        f.write(f"SMTP Password: {settings_data.get('smtp_password', '')}\n")
        f.write(f"SMTP From Email: {settings_data.get('smtp_from_email', '')}\n")
        f.write(f"Enable Email Notifications: {settings_data.get('notification_enable_email', '')}\n\n")

        f.write("[5. CLINIC INFO & LICENSE KEY]\n")
        f.write(f"Clinic Name: {settings_data.get('clinic_name', '')}\n")
        f.write(f"Clinic Phone: {settings_data.get('clinic_phone', '')}\n")
        f.write(f"Clinic Email: {settings_data.get('clinic_email', '')}\n")
        f.write(f"Currency Symbol: {settings_data.get('currency_symbol', '')}\n")
        f.write(f"Anesthesia Needle Price: {settings_data.get('anesthesia_needle_price', '')}\n")
        f.write(f"License Key: {settings_data.get('active_license_key', '')}\n")
        f.write(f"License Type: {settings_data.get('license_type', '')}\n")
        f.write(f"License Expires At: {settings_data.get('license_expires_at', '')}\n")
        f.write(f"Developer WhatsApp: {settings_data.get('developer_whatsapp', '')}\n\n")

        if patient_chats:
            f.write("[6. PATIENT TELEGRAM CHAT IDS]\n")
            for pc in patient_chats:
                f.write(f"- Patient ID #{pc['id']}: {pc['name']} ({pc['phone']}) -> Chat ID: {pc['telegram_chat_id']}\n")
            f.write("\n")

        f.write("====================================================================\n")
        f.write("        END OF BACKUP FILE - ALL TOKENS SAFELY EXPORTED\n")
        f.write("====================================================================\n")

    print("SUCCESS: Exported settings backup to JSON and TXT files.")

if __name__ == '__main__':
    main()
