import sys
import os
import urllib.request
import urllib.error
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

stream_token = "65959128dc1fd202542a36cc65600c98032826248369a6cb733fc628eee278a336b54f5929ad7bb56aae82f0d600afe0e975fe8ea8"
to_number = "963958948727"

# Added the trailing slash!
url = "https://textpeak-streams.commpeak.com/simple_send/"
headers = {
    "Authorization": stream_token,
    "Content-Type": "application/json; charset=UTF-8"
}

payload = json.dumps({
    "messages": [
        {
            "internal_id": str(int(time.time())),
            "recipient_phone": to_number,
            "sender": "DrClinic",
            "message_content": "Dental Clinic reminder test. Please reply if received."
        }
    ]
}).encode("utf-8")

try:
    print(f"Sending request directly to trailing slash URL: {url}")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Success! Response Code:", resp.getcode())
        print("Body:", resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print("Headers:", e.headers)
    print("Body:", e.read().decode("utf-8"))
except Exception as e:
    print(f"Error: {e}")
