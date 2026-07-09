import sys
import os
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

stream_token = "8e1e410449399bc048b0f38564af02b5c48a96396cf06f2194a5b146f27f04f05c71debd727e7d2471cbf5daf2cf0e1c4fc93d0344"
api_key = "4UfwKdyMbmtW7yQxO5dpFZHVUoafFA"
to_number = "963958948727"

# Endpoints on textpeak-streams.commpeak.com
endpoints = [
    ("https://textpeak-streams.commpeak.com/v1/messages", "POST", stream_token),
    ("https://textpeak-streams.commpeak.com/api/v1/messages", "POST", stream_token),
    ("https://textpeak-streams.commpeak.com/messages", "POST", stream_token),
    ("https://textpeak-streams.commpeak.com/v1/streams", "GET", stream_token),
    ("https://textpeak-streams.commpeak.com/api/v1/streams", "GET", stream_token),
    # Also test the API key on these
    ("https://textpeak-streams.commpeak.com/v1/messages", "POST", api_key),
    ("https://textpeak-streams.commpeak.com/api/v1/messages", "POST", api_key),
]

for url, method, token in endpoints:
    print(f"\n--- Testing {method} {url} with token={token[:10]}... ---")
    headers = {
        "Authorization": token,  # Try direct first
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = json.dumps({
        "phone": to_number,
        "message": "Test from Dental Clinic Streams API",
        "text": "Test from Dental Clinic Streams API"
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
        
    # Try with Bearer
    print(f"Trying with Bearer header...")
    headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Success with Bearer!", resp.read().decode("utf-8")[:300])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code} (Bearer): {body}")
    except Exception as e:
        print(f"Error: {e}")
