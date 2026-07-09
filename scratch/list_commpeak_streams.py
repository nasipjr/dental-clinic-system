import sys
import os
import urllib.request
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from utils.settings_helper import get_setting

with app.app_context():
    api_key = get_setting("commpeak_api_key", "").strip()
    
    if not api_key:
        print("ERROR: CommPeak API key is not configured in settings yet. Please save it first.")
        sys.exit(1)
        
    print(f"Connecting to CommPeak API using token: {api_key[:10]}...")
    
    url = "https://textpeak.commpeak.com/api/v1/streams"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("\nSuccessfully fetched streams list:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"API Request failed: {e}")
