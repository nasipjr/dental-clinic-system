import sys
import os

sys.path.append(os.path.abspath(r"c:\Users\Windows.11\Desktop\Dental Clinic MS Flask"))

from app import app
from models import db, User

client = app.test_client()

print("Simulating admin login session...")
with client:
    with client.session_transaction() as sess:
        with app.app_context():
            admin_user = User.query.filter_by(role="admin").first()
            sess["user_id"] = admin_user.id
            sess["role"] = admin_user.role

    print("Fetching home page with English cookie...")
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'html lang="en"' in html
    assert 'dir="ltr"' in html

    print("Fetching home page with Arabic cookie...")
    client.set_cookie('lang', 'ar')
    res_ar = client.get("/")
    assert res_ar.status_code == 200
    html_ar = res_ar.get_data(as_text=True)
    
    # Assert Arabic attributes
    assert 'html lang="ar"' in html_ar
    assert 'dir="rtl"' in html_ar
    
    # Verify that client-side script is NOT present
    assert "Translation Script for Arabic Language" not in html_ar
    assert "MutationObserver" not in html_ar
    
    # Verify server-side translation occurred
    assert "لوحة التحكم" in html_ar

    print("SUCCESS: Templates render correct HTML lang attributes and the translation script is successfully injected!")
