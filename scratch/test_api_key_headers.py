import sys
import os
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api_key = "4UfwKdyMbmtW7yQxO5dpFZHVUoafFA"
url = "https://textpeak.commpeak.com/api/v1/streams/1/messages"  # 1 is dummy stream_id
to_number = "963958948727"

headers_to_test = [
    {"Authorization": f"Bearer {api_key}"},
    {"Authorization": api_key},
    {"Authorization": f"Token {api_key}"},
    {"Authorization": f"Key {api_key}"},
    {"x-api-key": api_key},
    {"Api-Token": api_key},
    {"token": api_key},
    {"key": api_key}
]

for headers in headers_to_test:
    header_name = list(headers.keys())[0]
    header_val = headers[header_name]
    print(f"\n--- Testing with Header {header_name}: {header_val[:15]}... ---")
    
    payload = json.dumps({
        "phone": to_number,
        "message": "Test message"
    }).encode("utf-8")
    
    full_headers = {
        "Content-Type": "application/json"
    }
    full_headers.update(headers)
    
    try:
        req = urllib.request.Request(url, data=payload, headers=full_headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Success!", resp.read().decode("utf-8")[:200])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {body}")
    except Exception as e:
        print(f"Error: {e}")
