import sys
import os
import urllib.request
import urllib.error
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

stream_token = "65959128dc1fd202542a36cc65600c98032826248369a6cb733fc628eee278a336b54f5929ad7bb56aae82f0d600afe0e975fe8ea8"
to_number = "963958948727"
url = "https://textpeak-streams.commpeak.com/simple_send/"
headers = {
    "Authorization": stream_token,
    "Content-Type": "application/json; charset=UTF-8"
}

# Test scenarios:
# 1. No sender key
# 2. Empty sender string
# 3. None sender
# 4. "DEMO_SENDER"

scenarios = [
    {"name": "No sender key", "payload": {
        "messages": [
            {
                "internal_id": str(int(time.time())) + "_1",
                "recipient_phone": to_number,
                "message_content": "Dental Clinic reminder test. Please reply if received."
            }
        ]
    }},
    {"name": "Empty sender string", "payload": {
        "messages": [
            {
                "internal_id": str(int(time.time())) + "_2",
                "recipient_phone": to_number,
                "sender": "",
                "message_content": "Dental Clinic reminder test. Please reply if received."
            }
        ]
    }},
    {"name": "DEMO_SENDER", "payload": {
        "messages": [
            {
                "internal_id": str(int(time.time())) + "_3",
                "recipient_phone": to_number,
                "sender": "DEMO_SENDER",
                "message_content": "Dental Clinic reminder test. Please reply if received."
            }
        ]
    }}
]

for scenario in scenarios:
    print(f"\n--- Testing Scenario: {scenario['name']} ---")
    payload_data = json.dumps(scenario["payload"]).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=payload_data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Response:", resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")
