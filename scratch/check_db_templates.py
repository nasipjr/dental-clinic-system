import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import SystemSetting

with app.app_context():
    settings = SystemSetting.query.all()
    for s in settings:
        if 'template' in s.key or 'subject' in s.key:
            print(f"Key: {s.key}")
            print(f"  Value (str) : {s.value}")
            print(f"  Value (repr): {repr(s.value)}")
            print(f"  Value (bytes): {s.value.encode('utf-8') if s.value else None}")
            print("-" * 50)
