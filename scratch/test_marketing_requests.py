import sys
import os
import requests
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

stream_token = "65959128dc1fd202542a36cc65600c98032826248369a6cb733fc628eee278a336b54f5929ad7bb56aae82f0d600afe0e975fe8ea8"
to_number = "963958948727"

url = "https://textpeak-streams.commpeak.com/simple_send"
headers = {
    "Authorization": stream_token,
    "Content-Type": "application/json; charset=UTF-8"
}

payload = {
    "messages": [
        {
            "internal_id": str(int(time.time())),
            "recipient_phone": to_number,
            "sender": "DrClinic",
            "message_content": "Dental Clinic reminder test. Please reply if received."
        }
    ]
}

try:
    print("Sending POST request via requests...")
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    print("History (redirects):", response.history)
    for r in response.history:
        print(f"Redirected from {r.url} to {response.url} via status {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
