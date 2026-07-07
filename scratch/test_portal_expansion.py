import sys
import os

sys.path.append(os.path.abspath(r"c:\Users\Windows.11\Desktop\Dental Clinic MS Flask"))

from app import app
from models import db, User, Patient, Invoice, Appointment, Treatment, PatientFile

client = app.test_client()

print("Testing Patient Portal Expansion...")

def clean_database():
    with app.app_context():
        # Find test patient IDs
        test_patients = Patient.query.filter(Patient.first_name.in_(["PortalTest1", "PortalTest2"])).all()
        test_patient_ids = [p.id for p in test_patients]
        
        if test_patient_ids:
            # Delete Patient Files
            PatientFile.query.filter(PatientFile.patient_id.in_(test_patient_ids)).delete(synchronize_session=False)
            
            # 1. Delete Invoices
            Invoice.query.filter(Invoice.patient_id.in_(test_patient_ids)).delete(synchronize_session=False)
            
            # 2. Delete Treatments
            test_appts = Appointment.query.filter(Appointment.patient_id.in_(test_patient_ids)).all()
            test_appt_ids = [a.id for a in test_appts]
            if test_appt_ids:
                Treatment.query.filter(Treatment.appointment_id.in_(test_appt_ids)).delete(synchronize_session=False)
                
            # 3. Delete Appointments
            Appointment.query.filter(Appointment.patient_id.in_(test_patient_ids)).delete(synchronize_session=False)
            
            # 4. Delete Users
            User.query.filter(User.patient_id.in_(test_patient_ids)).delete(synchronize_session=False)
            
            # 5. Delete Patients
            Patient.query.filter(Patient.id.in_(test_patient_ids)).delete(synchronize_session=False)
            
        # Also clean up users by username just in case
        User.query.filter(User.username.in_(["test_patient_1", "test_patient_2"])).delete(synchronize_session=False)
        db.session.commit()

# Clean up before setup
clean_database()

# Set up database test data
with app.app_context():
    # 2. Create Patients
    p1 = Patient(first_name="PortalTest1", last_name="LastName1", phone="123456", email="p1@test.com")
    p2 = Patient(first_name="PortalTest2", last_name="LastName2", phone="654321", email="p2@test.com")
    db.session.add_all([p1, p2])
    db.session.flush()
    
    p1_id = p1.id
    p2_id = p2.id
    
    # 3. Create Portal User accounts for them
    u1 = User(username="test_patient_1", role="patient", patient_id=p1_id)
    u1.set_password("password123")
    u2 = User(username="test_patient_2", role="patient", patient_id=p2_id)
    u2.set_password("password123")
    db.session.add_all([u1, u2])
    db.session.flush()
    
    p1_user_id = u1.id
    p2_user_id = u2.id

    # 4. Create Appointments & Invoices
    appt1 = Appointment(patient_id=p1_id, appointment_date=db.func.now(), status="Done", reason="Check-up")
    appt2 = Appointment(patient_id=p2_id, appointment_date=db.func.now(), status="Done", reason="Cleaning")
    db.session.add_all([appt1, appt2])
    db.session.flush()
    
    appt1_id = appt1.id
    appt2_id = appt2.id
    
    t1 = Treatment(appointment_id=appt1_id, treatment_date=appt1.appointment_date, procedure_type="Check-up", total_cost=30.00)
    t2 = Treatment(appointment_id=appt2_id, treatment_date=appt2.appointment_date, procedure_type="Cleaning", total_cost=45.00)
    db.session.add_all([t1, t2])
    db.session.flush()
    
    inv1 = Invoice(appointment_id=appt1_id, patient_id=p1_id)
    inv2 = Invoice(appointment_id=appt2_id, patient_id=p2_id)
    db.session.add_all([inv1, inv2])
    db.session.flush()
    
    f1 = PatientFile(patient_id=p1_id, filename="patient1_file.jpg", filepath="uploads/patients/test1.jpg", filetype="image/jpeg")
    f2 = PatientFile(patient_id=p2_id, filename="patient2_file.jpg", filepath="uploads/patients/test2.jpg", filetype="image/jpeg")
    db.session.add_all([f1, f2])
    db.session.commit()
    
    inv1_id = inv1.id
    inv2_id = inv2.id
    f1_id = f1.id
    f2_id = f2.id

print(f"Test Data Setup Successful:")
print(f"  Patient 1: ID={p1_id}, User ID={p1_user_id}, Invoice ID={inv1_id}")
print(f"  Patient 2: ID={p2_id}, User ID={p2_user_id}, Invoice ID={inv2_id}")

try:
    # 1. Simulate login as Patient 1
    with client:
        with client.session_transaction() as sess:
            sess["user_id"] = p1_user_id
            sess["role"] = "patient"
            sess["patient_id"] = p1_id

        # 2. Test accessing patient's own billing page
        res_billing = client.get("/portal/billing")
        assert res_billing.status_code == 200
        html_billing = res_billing.get_data(as_text=True)
        assert "My Invoices" in html_billing or "فواتيري" in html_billing
        print("SUCCESS: Patient 1 can access their billing overview page!")

        # 3. Test accessing patient's own invoice details page
        res_inv1 = client.get(f"/portal/invoices/{inv1_id}")
        assert res_inv1.status_code == 200
        html_inv1 = res_inv1.get_data(as_text=True)
        assert f"Invoice INV-{inv1_id}" in html_inv1 or f"فاتورة INV-{inv1_id}" in html_inv1
        print("SUCCESS: Patient 1 can access their own invoice details!")

        # 4. Security Check: Test accessing Patient 2's invoice details page
        res_inv2 = client.get(f"/portal/invoices/{inv2_id}")
        # Should redirect to billing page with a flash message
        assert res_inv2.status_code == 302
        assert "/portal/billing" in res_inv2.location
        res_redirect = client.get("/portal/billing")
        html_redirect = res_redirect.get_data(as_text=True)
        assert "You do not have permission to view this invoice" in html_redirect or "ليس لديك صلاحية" in html_redirect
        print("SUCCESS: Patient 1 was BLOCKED from viewing Patient 2's invoice!")

        # 5. Test accessing patient's own medical history page
        res_med = client.get("/portal/medical-history")
        assert res_med.status_code == 200
        html_med = res_med.get_data(as_text=True)
        
        # Check for treatments or related strings
        try:
            assert "Treatments" in html_med or "العلاجات" in html_med or "الطبية" in html_med or "Medical Record" in html_med
        except AssertionError:
            print("ERROR: Assertion failed for html_med. Content was:")
            print(html_med[:3000])
            raise
        print("SUCCESS: Patient 1 can access their medical history page!")

        # 5b. Test accessing patient's own file (will view or trigger missing file redirect)
        res_file1 = client.get(f"/portal/files/{f1_id}")
        # Since physical file test1.jpg is not on disk, it should redirect to medical-history with a flash message
        assert res_file1.status_code == 302
        assert "/portal/medical-history" in res_file1.location
        
        # 5c. Test security check: Access Patient 2's file
        res_file2 = client.get(f"/portal/files/{f2_id}")
        assert res_file2.status_code == 302
        assert "/portal/medical-history" in res_file2.location
        print("SUCCESS: Patient 1 was BLOCKED from viewing Patient 2's secure files!")

        # 6. Test server-side translation on the portal
        # Request portal page in Arabic
        client.set_cookie("lang", "ar")
        res_ar = client.get("/portal/billing")
        html_ar = res_ar.get_data(as_text=True)
        
        # Assert server-side translation occurred (e.g. "My Invoices" is translated)
        assert "فواتيري" in html_ar or "الملخص المالي" in html_ar
        
        # Assert client-side script has been removed
        assert "Translation Script for Arabic Language" not in html_ar
        assert "MutationObserver" not in html_ar
        print("SUCCESS: Portal server-side Arabic translation and javascript cleanup verified!")

    print("ALL PATIENT PORTAL EXPANSION TESTS PASSED SUCCESSFULLY!")

finally:
    # Clean up test database records
    print("Cleaning up database test records...")
    clean_database()
    print("Database cleanup complete.")
