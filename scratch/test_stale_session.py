import sys
import os

sys.path.append(os.path.abspath(r"c:\Users\Windows.11\Desktop\Dental Clinic MS Flask"))

from app import app
from models import db, User

print("Testing Stale Session Bug...")

# 1. Create a temporary user in the database
with app.app_context():
    # Make sure to clean up any existing temp_staff
    User.query.filter_by(username="temp_staff").delete()
    db.session.commit()
    
    # Create temp user
    temp_user = User(
        username="temp_staff",
        password_hash="dummy_hash", # Not logging in with credentials, just session
        role="receptionist"
    )
    db.session.add(temp_user)
    db.session.commit()
    temp_user_id = temp_user.id
    print(f"Created temporary user ID: {temp_user_id}")

client = app.test_client()

# 2. Simulate login session
with client:
    with client.session_transaction() as sess:
        sess["user_id"] = temp_user_id
        sess["role"] = "receptionist"

    # 3. Access a protected staff page while user exists in DB
    res = client.get("/patients")
    # Should render the patients list page (200 OK)
    assert res.status_code == 200
    print("SUCCESS: Logged in user can access /patients!")

    # 4. Delete the temporary user from database to simulate deletion while session is active
    with app.app_context():
        User.query.filter_by(id=temp_user_id).delete()
        db.session.commit()
    print(f"Deleted user ID: {temp_user_id} from database.")

    # 5. Access the protected staff page again
    # Since CSRF doesn't block GET, we can do a simple GET request
    res_after = client.get("/patients")
    # Should redirect to login page (302)
    assert res_after.status_code == 302
    assert "/login" in res_after.location
    print("SUCCESS: Access after deletion redirects to login!")

    # 6. Check that session is cleared
    with client.session_transaction() as sess_after:
        assert "user_id" not in sess_after
    print("SUCCESS: Session was cleared automatically!")

    # 7. Check for the flash message
    res_login = client.get("/login")
    html = res_login.get_data(as_text=True)
    assert "Your account has been deleted or deactivated." in html
    print("SUCCESS: Flashed account deletion message is displayed!")
