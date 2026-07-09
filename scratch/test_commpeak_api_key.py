import sys
import os
import urllib.request
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from utils.settings_helper import set_setting

api_key = "4UfwKdyMbmtW7yQxO5dpFZHVUoafFA"

with app.app_context():
    print(f"Connecting to CommPeak API using token: {api_key}...")
    
    url = "https://textpeak.commpeak.com/api/v1/streams"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("\nSUCCESS! Fetched streams:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Save the api key to database settings
            set_setting("commpeak_api_key", api_key)
            print("Successfully saved API Key to database.")
            
    except Exception as e:
        print(f"Failed: {e}")
        if 'urllib.error.HTTPError' in str(type(e)):
            print("HTTP Response Body:", e.read().decode("utf-8"))
