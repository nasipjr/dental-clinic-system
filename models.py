from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)

    appointments = db.relationship("Appointment", backref="patient", lazy=False, cascade="all, delete-orphan")
    visits = db.relationship("Visit", backref="patient", lazy=True, cascade="all, delete-orphan")


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    appointment_date = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Scheduled")


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    visit_date = db.Column(db.String(50), nullable=False)
    procedure_type = db.Column(db.String(200))
    tooth_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    total_cost = db.Column(db.Float, default=0)
    paid_amount = db.Column(db.Float, default=0)
    @property
    def remaining_amount(self):
        return self.total_cost - self.paid_amount