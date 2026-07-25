import unittest
from datetime import datetime
from decimal import Decimal

from utils.validators import (
    parse_treatment_money,
    parse_patient_data,
    parse_payment_amount,
)
from utils.license_helper import generate_license_key, verify_license_key


class DentalClinicTestCase(unittest.TestCase):
    def test_parse_treatment_money(self):
        total, paid, err = parse_treatment_money(100, 50)
        self.assertIsNone(err)
        self.assertEqual(total, 100.0)
        self.assertEqual(paid, 50.0)

        total, paid, err = parse_treatment_money(-10, 0)
        self.assertIsNone(total)
        self.assertIn("cannot be negative", err)

    def test_parse_patient_data(self):
        form = {
            "first_name": "Sami",
            "last_name": "Karim",
            "gender": "Male",
            "date_of_birth": "1988-11-20"
        }
        data, err = parse_patient_data(form)
        self.assertIsNone(err)
        self.assertEqual(data["first_name"], "Sami")

    def test_license_key_generation_and_verification(self):
        key = generate_license_key(days=30, license_type="trial")
        self.assertTrue(key.startswith("DCMS-"))
        is_valid, data = verify_license_key(key)
        self.assertTrue(is_valid)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["license_type"], "trial")
        self.assertGreaterEqual(data["days_remaining"], 29)

    def test_payment_validation(self):
        amount, err = parse_payment_amount("150.00", 200.00)
        self.assertIsNone(err)
        self.assertEqual(amount, 150.0)

        amount, err = parse_payment_amount("250.00", 200.00)
        self.assertIsNone(amount)
        self.assertIn("cannot be greater than", err)

    def test_expense_numeric_type(self):
        from models import Expense
        from sqlalchemy import Numeric
        amount_col_type = Expense.amount.type
        self.assertIsInstance(amount_col_type, Numeric)

    def test_cascade_delete_orphan_rules(self):
        from models import Patient
        for rel_name in ["appointments", "payments", "invoices", "files"]:
            rel = getattr(Patient, rel_name).property
            self.assertTrue(rel.cascade.delete_orphan)

    def test_fast_translation(self):
        from utils.translator import translate_html, fast_translate_text
        html = '<div class="content"><p>Patients</p><p>Appointments</p></div>'
        translated = translate_html(html)
        self.assertIn("المرضى", translated)
        self.assertIn("المواعيد", translated)
        self.assertEqual(fast_translate_text("Patients"), "المرضى")

    def test_sqlite_backup_api(self):
        import sqlite3
        import tempfile
        import os
        f1 = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        f2 = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        src_path = f1.name
        dst_path = f2.name
        f1.close()
        f2.close()
        try:
            with sqlite3.connect(src_path) as conn:
                conn.execute("CREATE TABLE test (id INT, val TEXT)")
                conn.execute("INSERT INTO test VALUES (1, 'demo')")
                conn.commit()
            with sqlite3.connect(src_path) as src_conn, sqlite3.connect(dst_path) as dst_conn:
                src_conn.backup(dst_conn)
            with sqlite3.connect(dst_path) as check_conn:
                row = check_conn.execute("SELECT val FROM test WHERE id=1").fetchone()
                self.assertEqual(row[0], 'demo')
        finally:
            if os.path.exists(src_path):
                try: os.remove(src_path)
                except Exception: pass
            if os.path.exists(dst_path):
                try: os.remove(dst_path)
                except Exception: pass

    def test_sqlite_wal_mode(self):
        from app import app, db
        with app.app_context():
            if db.engine.name == "sqlite":
                from sqlalchemy import text
                result = db.session.execute(text("PRAGMA journal_mode;")).scalar()
                self.assertEqual(str(result).lower(), "wal")


    def test_appointment_date_filter_tabs(self):
        from app import app
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['role'] = 'admin'
            response = client.get('/appointments?date_filter=today')
            self.assertEqual(response.status_code, 200)
    def test_portal_dashboard_pagination(self):
        from app import app, db
        from models import Patient
        with app.app_context():
            p = Patient.query.first()
            if not p:
                p = Patient(first_name="Test", last_name="Patient", phone="0500000000")
                db.session.add(p)
                db.session.commit()
            pid = p.id
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 999
                sess['role'] = 'patient'
                sess['patient_id'] = pid
            response = client.get('/portal/dashboard?page=1')
            self.assertEqual(response.status_code, 200)
            
            response_ajax = client.get('/portal/dashboard?page=1&ajax=1', headers={'X-Requested-With': 'XMLHttpRequest'})
            self.assertEqual(response_ajax.status_code, 200)
            json_data = response_ajax.get_json()
            self.assertEqual(json_data['status'], 'success')
            response_book = client.get('/portal/book')
            self.assertEqual(response_book.status_code, 200)


if __name__ == "__main__":
    unittest.main()




