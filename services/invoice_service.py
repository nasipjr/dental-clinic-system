from models import db, Invoice, PaymentAllocation, Treatment


def get_or_create_invoice_for_appointment(appointment):
    if appointment.invoice:
        return appointment.invoice

    inv = Invoice.query.filter_by(appointment_id=appointment.id).first()
    if inv:
        return inv

    invoice = Invoice(
        appointment_id=appointment.id,
        patient_id=appointment.patient_id,
        tax_rate=0.0
    )

    db.session.add(invoice)
    db.session.flush()

    return invoice


def remove_invoice_if_empty(appointment):
    inv = appointment.invoice or Invoice.query.filter_by(appointment_id=appointment.id).first()
    if not inv:
        return

    count = Treatment.query.filter_by(appointment_id=appointment.id).count()
    if count > 0:
        return

    PaymentAllocation.query.filter_by(invoice_id=inv.id).delete()
    db.session.delete(inv)
    db.session.flush()


def sync_invoice_for_appointment(appointment):
    count = Treatment.query.filter_by(appointment_id=appointment.id).count()
    if count > 0 or (appointment.treatments and len(appointment.treatments) > 0):
        return get_or_create_invoice_for_appointment(appointment)

    remove_invoice_if_empty(appointment)
    return None