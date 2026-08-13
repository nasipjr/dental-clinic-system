from decimal import Decimal
from models import db, Appointment, Invoice, Payment, PaymentAllocation


def allocate_patient_payments_to_invoices(patient_id):
    payments = (
        Payment.query
        .filter_by(patient_id=patient_id)
        .order_by(Payment.payment_date.asc(), Payment.id.asc())
        .all()
    )

    invoices = (
        Invoice.query
        .join(Invoice.appointment)
        .filter(Invoice.patient_id == patient_id)
        .order_by(Appointment.appointment_date.asc(), Invoice.id.asc())
        .all()
    )

    payment_ids = [p.id for p in payments]
    if payment_ids:
        PaymentAllocation.query.filter(PaymentAllocation.payment_id.in_(payment_ids)).delete(synchronize_session=False)

    db.session.flush()

    invoice_map = {invoice.id: invoice for invoice in invoices}
    invoice_allocated = {invoice.id: Decimal('0.00') for invoice in invoices}
    payment_remaining_map = {payment.id: Decimal(str(payment.amount or 0)) for payment in payments}

    # Phase 1: Targeted Allocations
    # If a payment has payment.invoice_id set and that invoice belongs to this patient,
    # allocate directly to that invoice first up to its total amount.
    for payment in payments:
        if not payment.invoice_id or payment.invoice_id not in invoice_map:
            continue

        target_invoice = invoice_map[payment.invoice_id]
        invoice_total = Decimal(str(target_invoice.total_amount or 0))
        rem_payment = payment_remaining_map[payment.id]

        if invoice_total <= Decimal('0.00') or rem_payment <= Decimal('0.00'):
            continue

        allocated_to_invoice = invoice_allocated[target_invoice.id]
        outstanding = invoice_total - allocated_to_invoice

        if outstanding > Decimal('0.00'):
            allocation_amount = min(rem_payment, outstanding)
            allocation = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=target_invoice.id,
                amount=allocation_amount,
            )
            db.session.add(allocation)
            invoice_allocated[target_invoice.id] += allocation_amount
            payment_remaining_map[payment.id] -= allocation_amount

    # Phase 2: General & Surplus Allocations (FIFO for remaining amounts across remaining outstanding invoices)
    for payment in payments:
        remaining_payment_amount = payment_remaining_map[payment.id]
        if remaining_payment_amount <= Decimal('0.00'):
            continue

        for invoice in invoices:
            invoice_total = Decimal(str(invoice.total_amount or 0))
            if invoice_total <= Decimal('0.00'):
                continue

            allocated_to_invoice = invoice_allocated[invoice.id]
            outstanding_amount = invoice_total - allocated_to_invoice

            if outstanding_amount <= Decimal('0.00'):
                continue

            allocation_amount = min(remaining_payment_amount, outstanding_amount)

            allocation = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=invoice.id,
                amount=allocation_amount,
            )

            db.session.add(allocation)
            invoice_allocated[invoice.id] += allocation_amount
            remaining_payment_amount -= allocation_amount
            payment_remaining_map[payment.id] = remaining_payment_amount

            if remaining_payment_amount <= Decimal('0.00'):
                break

    db.session.flush()