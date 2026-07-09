import sys
import os
import urllib.request
import urllib.error
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

stream_token = "65959128dc1fd202542a36cc65600c98032826248369a6cb733fc628eee278a336b54f5929ad7bb56aae82f0d600afe0e975fe8ea8"
to_number = "963958948727"

url = "https://textpeak-streams.commpeak.com/simple_send"
headers = {
    "Authorization": stream_token,
    "Content-Type": "application/json; charset=UTF-8"
}

# Let's try sending with different sender names:
# 1. "DrClinic" (from database backup)
# 2. Empty string or None
# 3. "DEMO_SENDER" (from OTP example)

senders = ["DrClinic", "DEMO_SENDER", "Clinic"]

for sender in senders:
    print(f"\nTrying to send with sender='{sender}'...")
    payload = json.dumps({
        "messages": [
            {
                "internal_id": str(int(time.time())),
                "recipient_phone": to_number,
                "sender": sender,
                "message_content": "Dental Clinic reminder test. Please reply if received."
            }
        ]
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("SUCCESS!", resp.read().decode("utf-8"))
            break
    except urllib.error.HTTPError as e:
        print(f"Failed with HTTP {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")
