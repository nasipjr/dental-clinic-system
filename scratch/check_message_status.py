import sys
import os
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

stream_token = "65959128dc1fd202542a36cc65600c98032826248369a6cb733fc628eee278a336b54f5929ad7bb56aae82f0d600afe0e975fe8ea8"
message_uuid = "fc2ce00b-f373-4665-bfc5-7868aadafe19"

url = "https://textpeak-streams.commpeak.com/messages_status/"
headers = {
    "Authorization": stream_token,
    "Content-Type": "application/json; charset=UTF-8"
}

payload = json.dumps({
    "message_uuids": [message_uuid]
}).encode("utf-8")

try:
    print(f"Checking status for message {message_uuid}...")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Success! Status Response:")
        print(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(f"HTTPError {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
