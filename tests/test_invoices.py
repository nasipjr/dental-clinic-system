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
