from datetime import datetime
from decimal import Decimal
from models import db, Patient, Appointment, Treatment, Invoice, Payment, PaymentAllocation

def test_invoice_calculations(app):
    with app.app_context():
        patient = Patient(
            first_name="Khaled",
            last_name="Nasser",
            gender="Male",
            date_of_birth=datetime(1995, 1, 1).date()
        )
        db.session.add(patient)
        db.session.commit()

        appointment = Appointment(
            patient_id=patient.id,
            appointment_date=datetime.now(),
            reason="Checkup",
            status="Completed"
        )
        db.session.add(appointment)
        db.session.commit()

        treatment1 = Treatment(
            appointment_id=appointment.id,
            treatment_date=datetime.now(),
            procedure_type="Filling",
            total_cost=Decimal("100.00")
        )
        treatment2 = Treatment(
            appointment_id=appointment.id,
            treatment_date=datetime.now(),
            procedure_type="Cleaning",
            total_cost=Decimal("50.00")
        )
        db.session.add_all([treatment1, treatment2])
        db.session.commit()

        invoice = Invoice(
            appointment_id=appointment.id,
            patient_id=patient.id,
            discount=Decimal("10.00"),
            discount_type="percentage"
        )
        db.session.add(invoice)
        db.session.commit()

        # Subtotal: 150.00, Discount 10%: 15.00, Total: 135.00
        assert invoice.subtotal == Decimal("150.00")
        assert invoice.discount_amount == Decimal("15.00")
        assert invoice.total_amount == Decimal("135.00")
        assert invoice.status == "Unpaid"


def test_direct_invoice_payment_allocation(app):
    with app.app_context():
        from services.payment_service import allocate_patient_payments_to_invoices

        patient = Patient(
            first_name="Sami",
            last_name="Ahmad",
            gender="Male"
        )
        db.session.add(patient)
        db.session.commit()

        # Create Old Appointment & Invoice #1 ($50 total)
        appt1 = Appointment(patient_id=patient.id, appointment_date=datetime(2025, 1, 1), status="Completed")
        db.session.add(appt1)
        db.session.commit()
        t1 = Treatment(appointment_id=appt1.id, treatment_date=datetime.now(), procedure_type="Procedure 1", total_cost=Decimal("50.00"))
        db.session.add(t1)
        db.session.commit()
        inv1 = Invoice(appointment_id=appt1.id, patient_id=patient.id)
        db.session.add(inv1)
        db.session.commit()

        # Create New Appointment & Invoice #2 ($100 total)
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

        # Invoice #2 must be FULLY PAID ($100 total, $100 paid)
        assert inv2.status == "Paid"
        assert inv2.total_paid == Decimal("100.00")

        # Invoice #1 must remain UNPAID ($50 total, $0 paid)
        assert inv1.status == "Unpaid"
        assert inv1.total_paid == Decimal("0.00")
