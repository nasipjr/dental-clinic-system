import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, NotificationLog
from utils.notification_helper import process_reminders

print("Deleting last 1 hour of notification logs to allow re-triggering...")
with app.app_context():
    one_hour_ago = datetime.now() - timedelta(hours=1)
    deleted = NotificationLog.query.filter(NotificationLog.sent_at >= one_hour_ago).delete()
    db.session.commit()
    print(f"Deleted {deleted} log entries from the last hour.")

print("Manually running process_reminders to test template formatting...")
with app.app_context():
    try:
        process_reminders(app)
        print("process_reminders executed successfully!")
    except Exception as e:
        print(f"Error during manual process_reminders: {e}")
