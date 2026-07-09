import sys
import os
import urllib.request
import urllib.error
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

token1 = "8e1e410449399bc048b0f38564af02b5c48a96396cf06f2194a5b146f27f04f05c71debd727e7d2471cbf5daf2cf0e1c4fc93d0344"
token2 = "4UfwKdyMbmtW7yQxO5dpFZHVUoafFA"

def test_headers(token, label):
    print(f"\n--- Testing {label} ---")
    url = "https://textpeak.commpeak.com/api/v1/streams"
    
    # Try 1: Authorization: <token>
    print("1. Trying: Authorization: <token>")
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Success with direct token!", resp.read().decode("utf-8")[:200])
            return
    except urllib.error.HTTPError as e:
        print(f"Direct token failed: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Direct token error: {e}")
        
    # Try 2: x-api-key: <token>
    print("2. Trying: x-api-key: <token>")
    headers = {
        "x-api-key": token,
        "Content-Type": "application/json"
    }
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Success with x-api-key!", resp.read().decode("utf-8")[:200])
            return
    except urllib.error.HTTPError as e:
        print(f"x-api-key failed: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"x-api-key error: {e}")

test_headers(token1, "Stream Token (token1)")
test_headers(token2, "Account/Other Token (token2)")
