import sys
import os
from io import BytesIO

sys.path.append(os.path.abspath(r"c:\Users\Windows.11\Desktop\Dental Clinic MS Flask"))

from app import app
from models import db, User, Patient

client = app.test_client()

print("Simulating admin login session...")
with client:
    with client.session_transaction() as sess:
        with app.app_context():
            admin_user = User.query.filter_by(role="admin").first()
            sess["user_id"] = admin_user.id
            sess["role"] = admin_user.role
            
            # Find a patient
            patient = Patient.query.first()
            if not patient:
                print("No patient found in database to run test.")
                sys.exit(1)
            patient_id = patient.id

    print(f"Testing file upload for patient ID: {patient_id}")
    
    # Fetch patient detail page first to get CSRF token
    res_get = client.get(f"/patients/{patient_id}")
    html_get = res_get.get_data(as_text=True)
    import re
    match = re.search(r'name="csrf_token"\s+value="([a-f0-9]{64})"', html_get)
    csrf_token = match.group(1) if match else None

    # 1. Test uploading a disallowed file extension (.html)
    data = {
        'file': (BytesIO(b"<h1>Malicious HTML</h1>"), 'test.html'),
        'notes': 'Test unsafe upload',
        'csrf_token': csrf_token
    }
    res = client.post(f"/patients/{patient_id}/files/upload", data=data, content_type='multipart/form-data')
    assert res.status_code == 302
    res_redirect = client.get(f"/patients/{patient_id}")
    html = res_redirect.get_data(as_text=True)
    assert "Invalid file type" in html or "نوع الملف غير صالح" in html
    print("SUCCESS: Unsafe .html file upload was blocked!")

    # 2. Test uploading an allowed file extension (.png)
    data_safe = {
        'file': (BytesIO(b"dummy image data"), 'test.png'),
        'notes': 'Test safe upload',
        'csrf_token': csrf_token
    }
    res_safe = client.post(f"/patients/{patient_id}/files/upload", data=data_safe, content_type='multipart/form-data')
    assert res_safe.status_code == 302
    res_redirect_safe = client.get(f"/patients/{patient_id}")
    html_safe = res_redirect_safe.get_data(as_text=True)
    assert "File uploaded successfully" in html_safe or "تم رفع الملف بنجاح" in html_safe
    print("SUCCESS: Safe .png file upload was accepted!")
