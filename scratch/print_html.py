import sys
import os
from io import BytesIO

sys.path.append(os.path.abspath(r"c:\Users\Windows.11\Desktop\Dental Clinic MS Flask"))

from app import app
from models import db, User, Patient

client = app.test_client()

with client:
    with client.session_transaction() as sess:
        with app.app_context():
            admin_user = User.query.filter_by(role="admin").first()
            sess["user_id"] = admin_user.id
            sess["role"] = admin_user.role
            patient = Patient.query.first()
            patient_id = patient.id

    data = {
        'file': (BytesIO(b"<h1>Malicious HTML</h1>"), 'test.html'),
        'notes': 'Test unsafe upload'
    }
    res = client.post(f"/patients/{patient_id}/files/upload", data=data, content_type='multipart/form-data')
    res_redirect = client.get(f"/patients/{patient_id}")
    html = res_redirect.get_data(as_text=True)
    
    with open("scratch/output.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML saved to scratch/output.html")
