from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(20))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    preferred_first_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))

    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))

    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    post_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

    notes = db.Column(db.Text)
    medical_information = db.Column(db.Text)
    appointment_notes = db.Column(db.Text)

    occupation = db.Column(db.String(150))
    emergency_contact = db.Column(db.String(150))
    medicare_number = db.Column(db.String(100))

    appointments = db.relationship(
        "Appointment",
        backref="patient",
        lazy=True,
        cascade="all, delete-orphan"
    )

    payments = db.relationship(
        "Payment",
        backref="patient",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def treatments(self):
        patient_treatments = []

        for appointment in self.appointments:
            patient_treatments.extend(appointment.treatments)

        return patient_treatments

    @property
    def invoice_appointments(self):
        return [
            appointment
            for appointment in self.appointments
            if appointment.has_invoice
        ]

    @property
    def total_invoice_amount(self):
        return sum(
            appointment.invoice_total
            for appointment in self.invoice_appointments
        )

    @property
    def total_payments_amount(self):
        return sum(payment.amount for payment in self.payments)

    @property
    def total_allocated_amount(self):
        return sum(payment.allocated_amount for payment in self.payments)

    @property
    def outstanding_amount(self):
        balance = self.total_invoice_amount - self.total_payments_amount

        if balance > 0:
            return balance

        return 0

    @property
    def credit_amount(self):
        credit = self.total_payments_amount - self.total_invoice_amount

        if credit > 0:
            return credit

        return 0

    @property
    def balance_amount(self):
        return self.total_invoice_amount - self.total_payments_amount


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    appointment_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Scheduled")

    treatments = db.relationship(
        "Treatment",
        backref="appointment",
        lazy=True,
        cascade="all, delete-orphan"
    )

    payment_allocations = db.relationship(
        "PaymentAllocation",
        backref="appointment",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def invoice_total(self):
        return sum(treatment.total_cost for treatment in self.treatments)

    @property
    def total_paid(self):
        return sum(allocation.amount for allocation in self.payment_allocations)

    @property
    def outstanding_amount(self):
        balance = self.invoice_total - self.total_paid

        if balance > 0:
            return balance

        return 0

    @property
    def balance(self):
        return self.invoice_total - self.total_paid

    @property
    def credit(self):
        credit = self.total_paid - self.invoice_total

        if credit > 0:
            return credit

        return 0

    @property
    def treatments_count(self):
        return len(self.treatments)

    @property
    def has_invoice(self):
        return self.treatments_count > 0

    @property
    def invoice_status(self):
        if not self.has_invoice:
            return "No Invoice"

        if self.total_paid <= 0:
            return "Unpaid"

        if self.total_paid < self.invoice_total:
            return "Partially Paid"

        if self.total_paid == self.invoice_total:
            return "Paid"

        return "Credit"


class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointment.id"),
        nullable=False
    )

    treatment_date = db.Column(db.DateTime, nullable=False)
    procedure_type = db.Column(db.String(200))
    tooth_number = db.Column(db.String(50))
    notes = db.Column(db.Text)

    total_cost = db.Column(db.Float, default=0)

    @property
    def patient(self):
        return self.appointment.patient

    @property
    def patient_id(self):
        return self.appointment.patient_id


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    notes = db.Column(db.Text)

    allocations = db.relationship(
        "PaymentAllocation",
        backref="payment",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def allocated_amount(self):
        return sum(allocation.amount for allocation in self.allocations)

    @property
    def unallocated_amount(self):
        unallocated = self.amount - self.allocated_amount

        if unallocated > 0:
            return unallocated

        return 0


class PaymentAllocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    payment_id = db.Column(
        db.Integer,
        db.ForeignKey("payment.id"),
        nullable=False
    )

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointment.id"),
        nullable=False
    )

    amount = db.Column(db.Float, nullable=False)