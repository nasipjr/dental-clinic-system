import sys
import os
import urllib.request
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, SystemSetting
from utils.settings_helper import set_setting

api_key = "8e1e410449399bc048b0f38564af02b5c48a96396cf06f2194a5b146f27f04f05c71debd727e7d2471cbf5daf2cf0e1c4fc93d0344"

with app.app_context():
    # 1. Save the API Key to database settings
    success_key = set_setting("commpeak_api_key", api_key)
    if not success_key:
        print("ERROR: Failed to save API Key to database settings.")
        sys.exit(1)
    print("1. Successfully saved API Key to database.")

    # 2. Call CommPeak API to get streams list
    url = "https://textpeak.commpeak.com/api/v1/streams"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
            # The API might return list of streams. Let's find "Clinic Reminders"
            print("2. Successfully connected to CommPeak API. Searching for 'Clinic Reminders'...")
            
            stream_id = None
            # If the response is a list or contains a list
            streams = data if isinstance(data, list) else data.get("result", [])
            if not isinstance(streams, list) and isinstance(data, dict):
                # Check other possible structures
                streams = data.get("data", [])
            
            if isinstance(streams, list):
                for s in streams:
                    name = s.get("name", "")
                    sid = s.get("id") or s.get("stream_id")
                    print(f"   Found Stream: Name='{name}', ID={sid}")
                    if name == "Clinic Reminders" or name == "ClinicReminders":
                        stream_id = sid
                        break
            
            if not stream_id and isinstance(data, dict):
                # Fallback if it is a dictionary of items
                for key, val in data.items():
                    if isinstance(val, dict):
                        name = val.get("name", "")
                        sid = val.get("id") or val.get("stream_id") or key
                        if name == "Clinic Reminders":
                            stream_id = sid
                            break

            if stream_id:
                # 3. Save the stream_id to database settings
                success_stream = set_setting("commpeak_stream_id", str(stream_id))
                if success_stream:
                    print(f"3. SUCCESS: Found and saved Stream ID: {stream_id}")
                else:
                    print(f"ERROR: Found Stream ID: {stream_id} but failed to save it to database.")
            else:
                print("WARNING: Could not find a stream named 'Clinic Reminders' in the API response.")
                # If we couldn't match, let's print the raw response to see
                print("Raw Response:", json.dumps(data, indent=2))

    except Exception as e:
        print(f"ERROR: API request failed: {e}")
        # Try to print more info if possible
        if 'urllib.error.HTTPError' in str(type(e)):
            print("HTTP Response Body:", e.read().decode("utf-8"))
