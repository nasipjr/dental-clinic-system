import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

file_path = "c:\\Users\\Windows.11\\Desktop\\Dental Clinic MS Flask\\utils\\notification_helper.py"

with open(file_path, "rb") as f:
    content_bytes = f.read()

# Let's search for "المريض" in the file bytes
search_str = "المريض".encode("utf-8")
if search_str in content_bytes:
    print("SUCCESS: 'المريض' is encoded in UTF-8 in the python file!")
else:
    print("WARNING: 'المريض' is NOT found in UTF-8 format in the python file!")
    # Let's print the line containing "المريض" as bytes
    lines = content_bytes.split(b"\n")
    for idx, line in enumerate(lines):
        if b"name" in line and b"{" in line:
            print(f"Line {idx + 1} bytes: {line}")
