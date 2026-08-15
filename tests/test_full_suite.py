import os
os.environ["TESTING"] = "true"

import unittest
from datetime import datetime, date, timedelta, time
from decimal import Decimal
import json

from app import app, db
from models import (
    User, Patient, Appointment, Treatment, ToothHistory,
    TreatmentPlanItem, Invoice, Payment, PaymentAllocation,
    Expense, StaffSalary, PatientFile, NotificationLog
)
from utils.settings_helper import populate_default_settings, set_setting, get_setting, get_treatment_prices
from utils.license_helper import generate_license_key, verify_license_key


class ComprehensiveAppTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
            populate_default_settings()

            # Seed Admin
            cls.admin = User(username="admin", role="admin", first_name="Admin", last_name="System")
            cls.admin.set_password("admin123")
            db.session.add(cls.admin)

            # Seed Doctor
            cls.doctor = User(username="dr_sami", role="doctor", first_name="سامي", last_name="الأحمد")
            cls.doctor.set_password("doc123")
            db.session.add(cls.doctor)

            # Seed Receptionist
            cls.receptionist = User(username="reception", role="receptionist", first_name="سارة", last_name="خالد")
            cls.receptionist.set_password("rec123")
            db.session.add(cls.receptionist)

            # Seed Patient User
            cls.patient = Patient(
                first_name="عمرو",
                last_name="دياب",
                gender="Male",
                phone="+963911223344",
                email="amr@test.com",
                date_of_birth=date(1990, 5, 15)
            )
            db.session.add(cls.patient)
            db.session.flush()

            cls.patient_user = User(
                username="amr_diab",
                role="patient",
                first_name="عمرو",
                last_name="دياب",
                patient_id=cls.patient.id
            )
            cls.patient_user.set_password("patient123")
            db.session.add(cls.patient_user)
            db.session.commit()

            cls.admin_id = cls.admin.id
            cls.doctor_id = cls.doctor.id
            cls.receptionist_id = cls.receptionist.id
            cls.patient_id = cls.patient.id
            cls.patient_user_id = cls.patient_user.id

    def login_as(self, role="admin"):
        with self.client.session_transaction() as sess:
            if role == "admin":
                sess["user_id"] = self.admin_id
                sess["role"] = "admin"
            elif role == "doctor":
                sess["user_id"] = self.doctor_id
                sess["role"] = "doctor"
            elif role == "receptionist":
                sess["user_id"] = self.receptionist_id
                sess["role"] = "receptionist"
            elif role == "patient":
                sess["user_id"] = self.patient_user_id
                sess["role"] = "patient"
                sess["patient_id"] = self.patient_id

    def logout(self):
        with self.client.session_transaction() as sess:
            sess.clear()

    # ==========================================
    # 1. AUTHENTICATION & ACCESS CONTROL TESTS
    # ==========================================
    def test_01_unauthenticated_redirect(self):
        self.logout()
        res = self.client.get("/")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login", res.headers["Location"])

    def test_02_login_flow(self):
        self.logout()
        # Invalid password
        res = self.client.post("/login", data={"username": "admin", "password": "wrongpassword", "user_type": "staff"})
        self.assertEqual(res.status_code, 200)

        # Successful Admin login
        res = self.client.post("/login", data={"username": "admin", "password": "admin123", "user_type": "staff"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"admin", res.data.lower())

    def test_03_role_restrictions(self):
        # Receptionist trying to access admin settings -> should be redirected
        self.login_as("receptionist")
        res = self.client.get("/settings")
        self.assertEqual(res.status_code, 302)

        # Admin accessing settings -> 200 OK
        self.login_as("admin")
        res = self.client.get("/settings")
        self.assertEqual(res.status_code, 200)

    # ==========================================
    # 2. PATIENT CRUD & VALIDATIONS
    # ==========================================
    def test_04_patient_lifecycle(self):
        self.login_as("receptionist")
        # Create Patient
        res = self.client.post("/patients/add", data={
            "first_name": "ياسين",
            "last_name": "حمزة",
            "gender": "Male",
            "date_of_birth": "1995-02-10",
            "phone": "+963988776655",
            "email": "yassin@test.com",
            "occupation": "مهندس",
            "city": "دمشق"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            p = Patient.query.filter_by(phone="+963988776655").first()
            self.assertIsNotNone(p)
            self.assertEqual(p.first_name, "ياسين")
            p_id = p.id

        # View Patient Detail
        res = self.client.get(f"/patients/{p_id}")
        self.assertEqual(res.status_code, 200)

        # Edit Patient
        res = self.client.post(f"/patients/{p_id}/edit", data={
            "first_name": "ياسين",
            "last_name": "حمزة المعدل",
            "gender": "Male",
            "date_of_birth": "1995-02-10",
            "phone": "+963988776655",
            "email": "yassin@test.com"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            p = db.session.get(Patient, p_id)
            self.assertEqual(p.last_name, "حمزة المعدل")

    # ==========================================
    # 3. APPOINTMENTS & SCHEDULING
    # ==========================================
    def test_05_appointment_creation_and_status(self):
        self.login_as("doctor")
        with app.app_context():
            set_setting("working_days", "0,1,2,3,4,5,6")
            set_setting("working_hours_start", "08:00")
            set_setting("working_hours_end", "20:00")
            prices = get_treatment_prices()
            first_proc = list(prices.keys())[0] if prices else "فحص واستشارة"

        appt_time = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)

        res = self.client.post("/appointments/add", data={
            "patient_id": self.patient_id,
            "appointment_date": appt_time.strftime("%Y-%m-%d %H:%M"),
            "doctor_id": self.doctor_id,
            "reason": first_proc,
            "custom_reason": "",
            "duration": 30
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            appt = Appointment.query.filter_by(patient_id=self.patient_id).first()
            self.assertIsNotNone(appt)
            self.assertEqual(appt.status, "Scheduled")
            appt_id = appt.id

        # Update status to Done
        res = self.client.post(f"/appointments/{appt_id}/update-status", data={"status": "Done"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            appt = db.session.get(Appointment, appt_id)
            self.assertEqual(appt.status, "Done")
            # Reset to Scheduled for treatment addition
            appt.status = "Scheduled"
            db.session.commit()

    # ==========================================
    # 4. TREATMENTS & ODONTOGRAM & INVOICES
    # ==========================================
    def test_06_treatment_and_financial_flow(self):
        self.login_as("doctor")
        with app.app_context():
            appt = Appointment.query.filter_by(patient_id=self.patient_id).first()
            appt_id = appt.id

        # Add treatment with anesthesia
        res = self.client.post(f"/appointments/{appt_id}/treatments/add", data={
            "procedure_type": "قلع سن جراحي",
            "tooth_number": "18",
            "total_cost": "150000",
            "use_anesthesia": "on",
            "anesthesia_needles": "2",
            "anesthesia_cost": "30000",
            "notes": "قلع سن العقل العلوي الأيمن"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            t = Treatment.query.filter_by(appointment_id=appt_id).first()
            self.assertIsNotNone(t)
            self.assertEqual(t.total_cost, Decimal("150000.00"))
            self.assertEqual(t.procedure_cost, Decimal("50000.00"))

            # Check invoice creation
            inv = Invoice.query.filter_by(appointment_id=appt_id).first()
            self.assertIsNotNone(inv)
            self.assertEqual(inv.total_amount, Decimal("150000.00"))
            self.assertEqual(inv.status, "Unpaid")
            inv_id = inv.id

        # Record payment
        self.login_as("receptionist")
        res = self.client.post(f"/payments/add", data={
            "patient_id": self.patient_id,
            "invoice_id": inv_id,
            "amount": "150000",
            "payment_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "notes": "سداد نقدي كامل"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            inv = db.session.get(Invoice, inv_id)
            self.assertEqual(inv.status, "Paid")
            self.assertEqual(inv.total_paid, Decimal("150000.00"))
            self.assertEqual(inv.outstanding_amount, Decimal("0.00"))

    # ==========================================
    # 5. PATIENT PORTAL
    # ==========================================
    def test_07_patient_portal_flow(self):
        self.login_as("patient")
        # Access portal dashboard
        res = self.client.get("/portal/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"portal", res.data.lower())

        # Access portal billing
        res = self.client.get("/portal/billing")
        self.assertEqual(res.status_code, 200)

        # Access portal medical history
        res = self.client.get("/portal/medical-history")
        self.assertEqual(res.status_code, 200)

    # ==========================================
    # 6. REPORTS & DASHBOARD METRICS
    # ==========================================
    def test_08_reports_and_analytics(self):
        self.login_as("admin")
        # Dashboard
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

        # Financial Report
        res = self.client.get("/reports")
        self.assertEqual(res.status_code, 200)

        # Doctor Revenue Share Report
        res = self.client.get("/reports/doctor-revenue-share")
        self.assertEqual(res.status_code, 200)

        # Doctor Appointments Report
        res = self.client.get("/reports/doctor-appointments")
        self.assertEqual(res.status_code, 200)

    # ==========================================
    # 7. STAFF SALARY & EXPENSE DEDUCTIONS
    # ==========================================
    def test_09_staff_salary_configuration(self):
        self.login_as("admin")
        # Configure doctor salary
        res = self.client.post("/settings/salary/save", data={
            "user_id": self.doctor_id,
            "salary_type": "percentage",
            "amount": "40.0",
            "deduction_day": "1",
            "is_active": "on",
            "notes": "نسبة 40% من معالجات الطبيب"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            ss = StaffSalary.query.filter_by(user_id=self.doctor_id).first()
            self.assertIsNotNone(ss)
            self.assertEqual(ss.salary_type, "percentage")
            self.assertEqual(ss.amount, Decimal("40.00"))

    # ==========================================
    # 8. LICENSE VERIFICATION & CRYPTOGRAPHY
    # ==========================================
    def test_10_licensing_system(self):
        key = generate_license_key(days=365, license_type="annual")
        self.assertTrue(key.startswith("DCMS-"))
        is_valid, data = verify_license_key(key)
        self.assertTrue(is_valid)
        self.assertEqual(data["license_type"], "annual")
        self.assertGreaterEqual(data["days_remaining"], 364)

        # Tampered key should fail
        tampered_key = key[:-4] + "XXXX"
        is_valid_t, _ = verify_license_key(tampered_key)
        self.assertFalse(is_valid_t)


if __name__ == "__main__":
    unittest.main()
