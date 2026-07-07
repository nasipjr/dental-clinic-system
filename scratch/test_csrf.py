import sys
import os
import re

sys.path.append(os.path.abspath(r"c:\Users\Windows.11\Desktop\Dental Clinic MS Flask"))

from app import app
from models import db, User

client = app.test_client()

print("Testing CSRF Protection...")

# 1. Test POST request without a CSRF token
# Try to login directly without getting the token first
data_no_csrf = {
    'username': 'admin',
    'password': 'admin123',
    'user_type': 'staff'
}
res = client.post("/login", data=data_no_csrf)
assert res.status_code == 403
assert b"CSRF Token missing or invalid" in res.data
print("SUCCESS: POST request without CSRF token was blocked with 403 Forbidden!")

# 2. Test GET request to login page (which should generate and inject CSRF token)
res_get = client.get("/login")
assert res_get.status_code == 200
html = res_get.get_data(as_text=True)

# Verify csrf_token is present in HTML form
match = re.search(r'name="csrf_token"\s+value="([a-f0-9]{64})"', html)
assert match is not None
csrf_token = match.group(1)
print(f"SUCCESS: CSRF token was successfully generated and injected: {csrf_token}")

# 3. Test POST request with the correct CSRF token
data_with_csrf = {
    'username': 'admin',
    'password': 'admin123',
    'user_type': 'staff',
    'csrf_token': csrf_token
}
res_post = client.post("/login", data=data_with_csrf)
# Login redirects to home (302) on success
assert res_post.status_code == 302
print("SUCCESS: POST request with correct CSRF token was accepted (Redirected successfully)!")
