import sys
import os
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api_key = "8e1e410449399bc048b0f38564af02b5c48a96396cf06f2194a5b146f27f04f05c71debd727e7d2471cbf5daf2cf0e1c4fc93d0344"
to_number = "963958948727"

endpoints = [
    "https://textpeak.commpeak.com/api/v1/streams/messages/send",
    "https://textpeak.commpeak.com/api/v1/streams/send",
    "https://textpeak.commpeak.com/api/v1/streams/1/messages",
    "https://textpeak.commpeak.com/api/v1/streams/ClinicReminders/messages",
    "https://textpeak.commpeak.com/api/v1/messages",
    "https://textpeak.commpeak.com/api/v1/sms/send"
]

for url in endpoints:
    print(f"\n--- Testing POST {url} ---")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = json.dumps({
        "stream_id": "Clinic Reminders",
        "streamId": "Clinic Reminders",
        "phone": to_number,
        "message": "Test from Dental Clinic",
        "text": "Test from Dental Clinic"
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Success!", resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {body}")
    except Exception as e:
        print(f"Error: {e}")
