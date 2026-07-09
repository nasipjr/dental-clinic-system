import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import NotificationLog

with app.app_context():
    logs = NotificationLog.query.order_by(NotificationLog.sent_at.desc()).limit(15).all()
    print(f"{'ID':<5} | {'Type':<15} | {'Channel':<10} | {'Recipient':<20} | {'Sent At':<20} | {'Status':<10}")
    print("-" * 90)
    for log in logs:
        print(f"{log.id:<5} | {log.type:<15} | {log.channel:<10} | {log.recipient:<20} | {str(log.sent_at):<20} | {log.status:<10}")
