from flask_sqlalchemy import SQLAlchemy

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

    @property
    def treatments(self):
        patient_treatments = []

        for appointment in self.appointments:
            patient_treatments.extend(appointment.treatments)

        return patient_treatments


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
    paid_amount = db.Column(db.Float, default=0)

    @property
    def patient(self):
        return self.appointment.patient

    @property
    def patient_id(self):
        return self.appointment.patient_id

    @property
    def remaining_amount(self):
        return self.total_cost - self.paid_amount