import sys
import os
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api_key = "4UfwKdyMbmtW7yQxO5dpFZHVUoafFA"
to_number = "963958948727"

endpoints = [
    ("https://textpeak.commpeak.com/api/v1/streams", "GET"),
    ("https://textpeak.commpeak.com/api/v1/messages", "POST"),
    ("https://textpeak.commpeak.com/api/v1/streams/messages", "POST"),
    ("https://textpeak.commpeak.com/api/v1/streams/messages/send", "POST"),
    ("https://textpeak.commpeak.com/api/v1/sms/send", "POST")
]

for url, method in endpoints:
    print(f"\n--- Testing {method} {url} ---")
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
    }).encode("utf-8") if method == "POST" else None
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Success!", resp.read().decode("utf-8")[:300])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {body}")
    except Exception as e:
        print(f"Error: {e}")
