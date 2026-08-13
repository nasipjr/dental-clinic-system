from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class Patient(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(20))
    first_name = db.Column(db.String(100), nullable=False, index=True)
    last_name = db.Column(db.String(100), nullable=False, index=True)

    preferred_first_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))

    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(120), index=True)

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
    telegram_chat_id = db.Column(db.String(50), nullable=True)
    reminders_enabled = db.Column(db.Boolean, default=True, nullable=False)
    primary_doctor_id = db.Column(db.Integer, db.ForeignKey("user.id", use_alter=True, name="fk_patient_primary_doctor"), nullable=True)
    primary_doctor = db.relationship("User", foreign_keys=[primary_doctor_id], backref="primary_patients")

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

    invoices = db.relationship(
        "Invoice",
        backref="patient",
        lazy=True,
        cascade="all, delete-orphan"
    )

    files = db.relationship(
        "PatientFile",
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
            invoice.appointment
            for invoice in self.invoices
            if invoice.appointment is not None
        ]

    @property
    def total_invoice_amount(self):
        from decimal import Decimal
        return sum((Decimal(str(invoice.total_amount or 0)) for invoice in self.invoices), Decimal('0.00'))

    @property
    def total_payments_amount(self):
        from decimal import Decimal
        return sum((Decimal(str(payment.amount or 0)) for payment in self.payments), Decimal('0.00'))

    @property
    def total_allocated_amount(self):
        from decimal import Decimal
        return sum((Decimal(str(payment.allocated_amount or 0)) for payment in self.payments), Decimal('0.00'))

    @property
    def outstanding_amount(self):
        from decimal import Decimal
        balance = self.total_invoice_amount - self.total_payments_amount
        return max(balance, Decimal('0.00'))

    @property
    def credit_amount(self):
        from decimal import Decimal
        credit = self.total_payments_amount - self.total_invoice_amount
        return max(credit, Decimal('0.00'))

    @property
    def balance_amount(self):
        return self.total_invoice_amount - self.total_payments_amount


class Appointment(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    appointment_date = db.Column(db.DateTime, nullable=False, index=True)
    duration = db.Column(db.Integer, nullable=False, default=30)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Scheduled", index=True)
    session_opened_at = db.Column(db.DateTime, nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True, index=True)

    __table_args__ = (
        db.Index("idx_appt_date_status", "appointment_date", "status"),
    )
    doctor = db.relationship("User", foreign_keys=[doctor_id], backref="doctor_appointments")

    treatments = db.relationship(
        "Treatment",
        backref="appointment",
        lazy=True,
        cascade="all, delete-orphan"
    )

    invoice = db.relationship(
        "Invoice",
        backref="appointment",
        lazy=True,
        uselist=False,
        cascade="all, delete-orphan"
    )

    @property
    def attending_doctor(self):
        if self.treatments:
            for t in reversed(self.treatments):
                if t.doctor:
                    return t.doctor
        return self.doctor

    @property
    def invoice_total(self):
        if self.invoice:
            return self.invoice.total_amount

        return sum(treatment.total_cost for treatment in self.treatments)

    @property
    def total_paid(self):
        if self.invoice:
            return self.invoice.total_paid

        return 0

    @property
    def outstanding_amount(self):
        if self.invoice:
            return self.invoice.outstanding_amount

        total = self.invoice_total

        if total > 0:
            return total

        return 0

    @property
    def balance(self):
        if self.invoice:
            return self.invoice.balance

        return self.invoice_total

    @property
    def credit(self):
        if self.invoice:
            return self.invoice.credit

        return 0

    @property
    def treatments_count(self):
        return len(self.treatments)

    @property
    def has_invoice(self):
        return self.invoice is not None

    @property
    def invoice_status(self):
        if self.invoice:
            return self.invoice.status

        return "No Invoice"

    @property
    def payment_allocations(self):
        if self.invoice:
            return self.invoice.payment_allocations

        return []


class Treatment(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointment.id", ondelete="CASCADE"),
        nullable=False
    )

    treatment_date = db.Column(db.DateTime, nullable=False)
    procedure_type = db.Column(db.String(200))
    tooth_number = db.Column(db.String(50))
    notes = db.Column(db.Text)

    total_cost = db.Column(db.Numeric(10, 2), default=0.00)

    use_anesthesia = db.Column(db.Boolean, default=False, nullable=False)
    anesthesia_needles = db.Column(db.Integer, default=0, nullable=False)
    anesthesia_cost = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    anesthesia_type = db.Column(db.String(150), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    doctor = db.relationship("User", foreign_keys=[doctor_id], backref="doctor_treatments")

    salary_expense_id = db.Column(db.Integer, db.ForeignKey("expense.id", ondelete="SET NULL"), nullable=True)
    salary_expense = db.relationship("Expense", foreign_keys=[salary_expense_id], backref=db.backref("deducted_treatments", lazy="dynamic"))

    @property
    def procedure_cost(self):
        if self.use_anesthesia and self.anesthesia_cost and self.anesthesia_cost > 0:
            cost = (self.total_cost or 0) - self.anesthesia_cost
            return max(cost, 0)
        return self.total_cost or 0

    @property
    def patient(self):
        return self.appointment.patient

    @property
    def patient_id(self):
        return self.appointment.patient_id


class ToothHistory(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id", ondelete="CASCADE"),
        nullable=False
    )
    tooth_number = db.Column(db.String(50), nullable=False)
    procedure_type = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    history_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    patient = db.relationship("Patient", backref=db.backref("tooth_histories", cascade="all, delete-orphan"))


class Invoice(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointment.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id", ondelete="CASCADE"),
        nullable=False
    )

    issue_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    discount = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    discount_type = db.Column(db.String(20), default="value", nullable=False)
    additional_charges = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    payment_allocations = db.relationship(
        "PaymentAllocation",
        backref="invoice",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def invoice_number(self):
        return f"INV-{self.id}"

    @property
    def treatments(self):
        if not self.appointment:
            return []

        return self.appointment.treatments

    @property
    def appointment_date(self):
        if not self.appointment:
            return None

        return self.appointment.appointment_date

    @property
    def subtotal(self):
        from decimal import Decimal
        return sum((Decimal(str(treatment.total_cost or 0)) for treatment in self.treatments), Decimal('0.00'))

    @property
    def discount_amount(self):
        from decimal import Decimal
        sub = Decimal(str(self.subtotal or 0))
        disc = Decimal(str(self.discount or 0))
        if self.discount_type == "percentage":
            return (sub * disc / Decimal('100.00')).quantize(Decimal('0.01'))
        return disc

    @property
    def additional_charges_amount(self):
        from decimal import Decimal
        return Decimal(str(self.additional_charges or 0))

    @property
    def tax_amount(self):
        from decimal import Decimal
        return Decimal('0.00')

    @property
    def total_amount(self):
        from decimal import Decimal
        sub = Decimal(str(self.subtotal or 0))
        disc_amt = Decimal(str(self.discount_amount or 0))
        add_charges = Decimal(str(self.additional_charges_amount or 0))
        net = max(sub - disc_amt + add_charges, Decimal('0.00'))
        return net

    @property
    def total_paid(self):
        from decimal import Decimal
        return sum((Decimal(str(allocation.amount or 0)) for allocation in self.payment_allocations), Decimal('0.00'))

    @property
    def outstanding_amount(self):
        from decimal import Decimal
        balance = Decimal(str(self.total_amount)) - Decimal(str(self.total_paid))
        return max(balance, Decimal('0.00'))

    @property
    def balance(self):
        from decimal import Decimal
        return Decimal(str(self.total_amount)) - Decimal(str(self.total_paid))

    @property
    def credit(self):
        from decimal import Decimal
        credit = Decimal(str(self.total_paid)) - Decimal(str(self.total_amount))
        return max(credit, Decimal('0.00'))

    @property
    def treatments_count(self):
        return len(self.treatments)

    @property
    def status(self):
        if self.total_paid <= 0:
            return "Unpaid"

        if self.total_paid < self.total_amount:
            return "Partially Paid"

        if self.total_paid == self.total_amount:
            return "Paid"

        return "Credit"


class Payment(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id", ondelete="CASCADE"),
        nullable=False
    )

    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoice.id", ondelete="SET NULL"),
        nullable=True
    )

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    notes = db.Column(db.Text)

    invoice = db.relationship("Invoice", foreign_keys=[invoice_id], backref="direct_payments")

    allocations = db.relationship(
        "PaymentAllocation",
        backref="payment",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def allocated_amount(self):
        from decimal import Decimal
        return sum((Decimal(str(allocation.amount or 0)) for allocation in self.allocations), Decimal('0.00'))

    @property
    def unallocated_amount(self):
        from decimal import Decimal
        unallocated = Decimal(str(self.amount or 0)) - Decimal(str(self.allocated_amount or 0))
        return max(unallocated, Decimal('0.00'))


class PaymentAllocation(db.Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    id = db.Column(db.Integer, primary_key=True)

    payment_id = db.Column(
        db.Integer,
        db.ForeignKey("payment.id", ondelete="CASCADE"),
        nullable=False
    )

    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoice.id", ondelete="CASCADE"),
        nullable=False
    )

    amount = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def appointment(self):
        return self.invoice.appointment

    @property
    def appointment_id(self):
        return self.invoice.appointment_id

    @property
    def patient(self):
        return self.invoice.patient

    @property
    def patient_id(self):
        return self.invoice.patient_id


class SystemSetting(db.Model):
    __tablename__ = "system_setting"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="receptionist", nullable=False)  # 'admin', 'doctor', 'receptionist', 'patient'
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id", ondelete="CASCADE", use_alter=True, name="fk_user_patient"), nullable=True)
    patient = db.relationship("Patient", foreign_keys=[patient_id], backref=db.backref("user", uselist=False, cascade="all, delete-orphan"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    @property
    def display_name(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        if full_name:
            if self.role in ("doctor", "admin"):
                return f"د. {full_name}" if not full_name.startswith("د.") else full_name
            return full_name
        return self.username


class PatientFile(db.Model):
    __tablename__ = "patient_file"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id", ondelete="CASCADE"),
        nullable=False
    )
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    filetype = db.Column(db.String(100))
    upload_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    notes = db.Column(db.Text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class NotificationLog(db.Model):
    __tablename__ = "notification_log"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointment.id", ondelete="CASCADE"),
        nullable=False
    )
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id", ondelete="CASCADE"),
        nullable=False
    )
    type = db.Column(db.String(50), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    status = db.Column(db.String(20), default="sent", nullable=False)
    error_message = db.Column(db.Text)

    appointment = db.relationship(
        "Appointment",
        backref=db.backref("notifications", cascade="all, delete-orphan")
    )
    patient = db.relationship(
        "Patient",
        backref=db.backref("notifications", cascade="all, delete-orphan")
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Expense(db.Model):
    __tablename__ = "expense"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)  # e.g., "Materials", "Rent", "Salaries", "Other"
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, default=datetime.now, nullable=False)
    notes = db.Column(db.Text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class StaffSalary(db.Model):
    """Stores salary configuration per staff member (receptionist or doctor)."""
    __tablename__ = "staff_salary"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True  # One salary config per user
    )
    # "fixed" → fixed monthly amount; "percentage" → % of total invoiced by that doctor
    salary_type = db.Column(db.String(20), nullable=False, default="fixed")
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    deduction_day = db.Column(db.Integer, nullable=False, default=1)  # 1–28
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.Text, nullable=True)
    last_deducted_month = db.Column(db.String(7), nullable=True)  # "YYYY-MM" of last auto-deduction
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    user = db.relationship("User", backref=db.backref("salary_config", uselist=False, cascade="all, delete-orphan"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


