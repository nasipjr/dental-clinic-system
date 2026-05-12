from models import db, Appointment, Payment, PaymentAllocation


def allocate_patient_payments_to_invoices(patient_id):
    payments = (
        Payment.query
        .filter_by(patient_id=patient_id)
        .order_by(Payment.payment_date.asc(), Payment.id.asc())
        .all()
    )

    appointments = (
        Appointment.query
        .filter_by(patient_id=patient_id)
        .order_by(Appointment.appointment_date.asc(), Appointment.id.asc())
        .all()
    )

    for payment in payments:
        PaymentAllocation.query.filter_by(payment_id=payment.id).delete()

    db.session.flush()

    for payment in payments:
        remaining_payment_amount = float(payment.amount or 0)

        if remaining_payment_amount <= 0:
            continue

        for appointment in appointments:
            invoice_total = float(appointment.invoice_total or 0)

            if invoice_total <= 0:
                continue

            allocated_to_appointment = sum(
                float(allocation.amount or 0)
                for allocation in PaymentAllocation.query.filter_by(
                    appointment_id=appointment.id
                ).all()
            )

            outstanding_amount = invoice_total - allocated_to_appointment

            if outstanding_amount <= 0:
                continue

            allocation_amount = min(remaining_payment_amount, outstanding_amount)

            allocation = PaymentAllocation(
                payment_id=payment.id,
                appointment_id=appointment.id,
                amount=allocation_amount,
            )

            db.session.add(allocation)
            remaining_payment_amount -= allocation_amount

            if remaining_payment_amount <= 0:
                break

    db.session.flush()