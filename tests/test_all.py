import os
os.environ["TESTING"] = "true"

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
    @classmethod
    def setUpClass(cls):
        from app import app, db
        from models import User
        from utils.settings_helper import populate_default_settings
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        with app.app_context():
            db.drop_all()
            db.create_all()
            populate_default_settings()
            admin = User(id=1, username='admin', role='admin', first_name='Admin', last_name='User')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        from app import app, db
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_parse_treatment_money(self):
        total, paid, err = parse_treatment_money(100, 50)
        self.assertIsNone(err)
        self.assertEqual(total, Decimal('100.00'))
        self.assertEqual(paid, Decimal('50.00'))

        total, paid, err = parse_treatment_money(-10, 0)
        self.assertIsNone(total)
        self.assertIn("cannot be negative", err)

    def test_parse_patient_data(self):
        form = {
            "first_name": "Sami",
            "last_name": "Karim",
            "gender": "Male",
            "date_of_birth": "1988-11-20",
            "phone": "+963958948727"
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
        for rel_name in ["appointments", "payments", "invoices", "files", "tooth_histories"]:
            rel = getattr(Patient, rel_name).property
            self.assertTrue(rel.cascade.delete_orphan)

    def test_tooth_history_model(self):
        from models import ToothHistory
        th = ToothHistory(patient_id=1, tooth_number="21", procedure_type="قلع سن (سابق)", notes="تم القلع خارج العيادة")
        self.assertEqual(th.tooth_number, "21")
        self.assertEqual(th.procedure_type, "قلع سن (سابق)")

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

    def test_tooth_history_redirect_to_appointment_session(self):
        from app import app, db
        from models import Patient, Appointment, ToothHistory
        with app.app_context():
            p = Patient.query.first()
            if not p:
                p = Patient(first_name="TestHistory", last_name="Patient", phone="0511111111")
                db.session.add(p)
                db.session.commit()
            apt = Appointment.query.filter_by(patient_id=p.id).first()
            if not apt:
                apt = Appointment(patient_id=p.id, appointment_date=datetime.now(), status="Scheduled")
                db.session.add(apt)
                db.session.commit()
            patient_id = p.id
            appointment_id = apt.id

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['role'] = 'admin'
                sess['csrf_token'] = 'test_csrf'
            
            # Post adding tooth history with appointment_id
            resp = client.post(f'/patients/{patient_id}/tooth-history/add', data={
                'tooth_number': '11',
                'procedure_type': 'حشوة أسنان (سابقة)',
                'notes': 'Test prior history note',
                'appointment_id': str(appointment_id),
                'csrf_token': 'test_csrf'
            })
            self.assertEqual(resp.status_code, 302)
            self.assertIn(f'/appointments/{appointment_id}/session', resp.location)

            # Test delete with appointment_id
            with app.app_context():
                th = ToothHistory.query.filter_by(patient_id=patient_id, tooth_number='11').first()
                th_id = th.id if th else None

            if th_id:
                resp_del = client.post(f'/patients/{patient_id}/tooth-history/{th_id}/delete', data={
                    'appointment_id': str(appointment_id),
                    'csrf_token': 'test_csrf'
                })
                self.assertEqual(resp_del.status_code, 302)
                self.assertIn(f'/appointments/{appointment_id}/session', resp_del.location)

    def test_manual_backup_restore_upload(self):
        import io
        import tempfile
        import os
        import sqlite3
        from app import app, db
        from models import User

        # Ensure admin user exists with admin / admin123
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', role='admin', first_name='Admin', last_name='User')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()

            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            is_mysql = db_uri.startswith('mysql')

        if is_mysql:
            upload_filename = "valid_backup.sql"
            upload_content = b"-- MySQL dump\nSELECT 1;\n"
        else:
            upload_filename = "valid_backup.db"
            tmp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
            tmp_db_path = tmp_db.name
            tmp_db.close()
            try:
                with sqlite3.connect(tmp_db_path) as conn:
                    conn.execute("CREATE TABLE dummy_restore_test (id INT PRIMARY KEY);")
                    conn.execute("INSERT INTO dummy_restore_test VALUES (100);")
                    conn.commit()
                with open(tmp_db_path, "rb") as f:
                    upload_content = f.read()
            finally:
                if os.path.exists(tmp_db_path):
                    try: os.remove(tmp_db_path)
                    except Exception: pass

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['role'] = 'admin'

            # Test upload invalid format extension (.txt)
            resp_invalid = client.post('/settings/restore-backup', data={
                'backup_filename': '__upload__',
                'admin_username': 'admin',
                'admin_password': 'admin123',
                'manual_backup_file': (io.BytesIO(b"dummy text"), "bad_file.txt")
            })
            self.assertEqual(resp_invalid.status_code, 302)

            # Test valid upload for current DB engine
            resp_valid = client.post('/settings/restore-backup', data={
                'backup_filename': '__upload__',
                'admin_username': 'admin',
                'admin_password': 'admin123',
                'manual_backup_file': (io.BytesIO(upload_content), upload_filename)
            }, content_type='multipart/form-data')
            self.assertEqual(resp_valid.status_code, 302)
            self.assertIn('/settings#tab-backups', resp_valid.location)

            # Cleanup test backup files created during unit test execution
            with app.app_context():
                try:
                    db.session.remove()
                    db.engine.dispose()
                except Exception:
                    pass
            backup_dir = os.path.join(app.root_path, 'backups')
            if os.path.exists(backup_dir):
                for fname in os.listdir(backup_dir):
                    if fname.startswith('backup_uploaded_'):
                        try:
                            os.remove(os.path.join(backup_dir, fname))
                        except Exception:
                            pass

    def test_reset_clinic_operational(self):
        from app import app, db
        from models import User

        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', role='admin', first_name='Admin', last_name='User')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
            admin_id = admin.id

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = admin_id
                sess['role'] = 'admin'

            resp = client.post('/settings/reset-clinic', data={
                'admin_username': 'admin',
                'admin_password': 'admin123'
            })
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/settings', resp.location)

    def test_factory_reset_clinic(self):
        from app import app, db
        from models import User

        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', role='admin', first_name='Admin', last_name='User')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
            admin_id = admin.id

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = admin_id
                sess['role'] = 'admin'

            resp = client.post('/settings/factory-reset', data={
                'admin_username': 'admin',
                'admin_password': 'admin123'
            })
            # Factory reset clears session and redirects to login
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/login', resp.location)

        with app.app_context():
            # Verify admin user exists with admin / admin123
            default_admin = User.query.filter_by(username='admin').first()
            self.assertIsNotNone(default_admin)
            self.assertTrue(default_admin.check_password('admin123'))
            self.assertEqual(default_admin.role, 'admin')

    def test_direct_invoice_payment_allocation(self):
        from app import app, db
        from models import Patient, Appointment, Treatment, Invoice, Payment
        from services.payment_service import allocate_patient_payments_to_invoices

        with app.app_context():
            patient = Patient(
                first_name="Sami",
                last_name="Ahmad",
                gender="Male"
            )
            db.session.add(patient)
            db.session.commit()

            # Old Appointment & Invoice #1 ($50 total)
            appt1 = Appointment(patient_id=patient.id, appointment_date=datetime(2025, 1, 1), status="Completed")
            db.session.add(appt1)
            db.session.commit()
            t1 = Treatment(appointment_id=appt1.id, treatment_date=datetime.now(), procedure_type="Procedure 1", total_cost=Decimal("50.00"))
            db.session.add(t1)
            db.session.commit()
            inv1 = Invoice(appointment_id=appt1.id, patient_id=patient.id)
            db.session.add(inv1)
            db.session.commit()

            # New Appointment & Invoice #2 ($100 total)
            appt2 = Appointment(patient_id=patient.id, appointment_date=datetime(2025, 2, 1), status="Completed")
            db.session.add(appt2)
            db.session.commit()
            t2 = Treatment(appointment_id=appt2.id, treatment_date=datetime.now(), procedure_type="Procedure 2", total_cost=Decimal("100.00"))
            db.session.add(t2)
            db.session.commit()
            inv2 = Invoice(appointment_id=appt2.id, patient_id=patient.id)
            db.session.add(inv2)
            db.session.commit()

            # Pay $100 specifically targeted for Invoice #2
            payment = Payment(patient_id=patient.id, invoice_id=inv2.id, amount=Decimal("100.00"))
            db.session.add(payment)
            db.session.commit()

            allocate_patient_payments_to_invoices(patient.id)
            db.session.commit()

            # Invoice #2 must be Paid ($100 total, $100 paid)
            self.assertEqual(inv2.status, "Paid")
            self.assertEqual(inv2.total_paid, Decimal("100.00"))

            # Invoice #1 must remain Unpaid ($50 total, $0 paid)
            self.assertEqual(inv1.status, "Unpaid")
            self.assertEqual(inv1.total_paid, Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()




