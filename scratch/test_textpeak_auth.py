import sys
import os
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api_key = "4UfwKdyMbmtW7yQxO5dpFZHVUoafFA"
endpoints = [
    "https://textpeak.commpeak.com/api/v1/auth",
    "https://textpeak.commpeak.com/api/v1/auth/login",
    "https://textpeak.commpeak.com/api/v1/login",
    "https://textpeak.commpeak.com/api/v1/tokens",
    "https://textpeak.commpeak.com/api/auth",
    "https://textpeak.commpeak.com/api/auth/login",
]

payloads = [
    {"api_key": api_key},
    {"api_token": api_key},
    {"token": api_key},
    {"key": api_key}
]

for url in endpoints:
    for payload in payloads:
        print(f"\n--- Testing POST {url} with payload {list(payload.keys())[0]} ---")
        headers = {
            "Content-Type": "application/json"
        }
        encoded_payload = json.dumps(payload).encode("utf-8")
        try:
            req = urllib.request.Request(url, data=encoded_payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                print("SUCCESS!", resp.read().decode("utf-8")[:300])
                sys.exit(0)
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}")
        except Exception as e:
            print(f"Error: {e}")
