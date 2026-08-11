import os
os.environ["TESTING"] = "true"

import unittest
from models import User

class PortalSecurityTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app, db
        from models import User
        with app.app_context():
            db.create_all()
            if not User.query.filter_by(role='admin').first():
                admin = User(id=1, username='admin', role='admin', first_name='Admin', last_name='User')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
    def test_user_password_hashing(self):
        user = User(username="patient_test", role="patient")
        user.set_password("secret123")

        # Ensure password_hash is populated and plain_password is NOT an attribute
        self.assertIsNotNone(user.password_hash)
        self.assertNotEqual(user.password_hash, "secret123")
        self.assertTrue(user.check_password("secret123"))
        self.assertFalse(user.check_password("wrongpassword"))
        self.assertFalse(hasattr(user, "plain_password"))

    def test_csrf_protection_validation(self):
        from app import app
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['TESTING'] = True
        with app.test_client() as client:
            # POST without valid CSRF token should be rejected with 400 Bad Request by Flask-WTF
            res = client.post("/login", data={"username": "admin", "password": "wrongpassword"})
            self.assertEqual(res.status_code, 400)

    def test_activation_page_rendering(self):
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            res = client.get("/activate")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"HWID", res.data)

    def test_archive_page_rendering(self):
        from app import app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        with app.test_client() as client:
            with app.app_context():
                admin = User.query.filter_by(role='admin').first()
                admin_id = admin.id if admin else 1
            with client.session_transaction() as sess:
                sess['user_id'] = admin_id
                sess['role'] = 'admin'
            res = client.get("/appointments/archive")
            self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
