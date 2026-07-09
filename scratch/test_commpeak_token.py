import sys
import os
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api_key = "8e1e410449399bc048b0f38564af02b5c48a96396cf06f2194a5b146f27f04f05c71debd727e7d2471cbf5daf2cf0e1c4fc93d0344"
to_number = "963958948727"

def try_send(stream_id_val):
    print(f"\n--- Trying send with stream_id='{stream_id_val}' ---")
    url = "https://textpeak.commpeak.com/api/v1/streams/messages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = json.dumps({
        "stream_id": stream_id_val,
        "phone": to_number,
        "message": "Test message from Clinic Reminders"
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Success!", resp.read().decode("utf-8"))
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"Failed with HTTP {e.code}: {body}")
    except Exception as e:
        print(f"Failed with error: {e}")
    return False

# Try empty stream_id
try_send("")
# Try stream name
try_send("Clinic Reminders")
# Try stream name without spaces
try_send("ClinicReminders")
