from datetime import datetime, time

from flask import Blueprint, current_app, render_template

from models import Patient, Appointment, Treatment, Payment
from utils.auth_helper import role_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@role_required("admin", "doctor", "receptionist")
def home():
    current_app.logger.info("Home page opened")

    try:
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        scheduled_appointments = Appointment.query.filter_by(status="Scheduled").count()
        done_appointments = Appointment.query.filter_by(status="Done").count()
        total_treatments = Treatment.query.count()

        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        today_scheduled_appointments = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .filter(Appointment.status == "Scheduled")
            .order_by(Appointment.appointment_date.asc())
            .all()
        )

        today_done_appointments = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .filter(Appointment.status == "Done")
            .order_by(Appointment.appointment_date.asc())
            .all()
        )

        all_treatments = Treatment.query.all()
        all_payments = Payment.query.all()

        total_revenue = sum(treatment.total_cost for treatment in all_treatments)
        total_paid = sum(payment.amount for payment in all_payments)
        total_remaining = total_revenue - total_paid
        total_outstanding = max(0.0, total_remaining)
        total_credit = max(0.0, -total_remaining)

        today_payments_sum = sum(payment.amount for payment in all_payments if payment.payment_date >= today_start and payment.payment_date <= today_end)
        today_revenue_sum = sum(t.total_cost for t in all_treatments if t.treatment_date >= today_start and t.treatment_date <= today_end)

        pending_appointments = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.status == "Pending")
            .order_by(Appointment.appointment_date.asc())
            .all()
        )

        return render_template(
            "dashboard/index.html",
            total_patients=total_patients,
            total_appointments=total_appointments,
            scheduled_appointments=scheduled_appointments,
            done_appointments=done_appointments,
            total_treatments=total_treatments,
            total_revenue=total_revenue,
            total_paid=total_paid,
            total_remaining=total_remaining,
            total_outstanding=total_outstanding,
            total_credit=total_credit,
            today_scheduled_appointments=today_scheduled_appointments,
            today_done_appointments=today_done_appointments,
            today_payments_sum=today_payments_sum,
            today_revenue_sum=today_revenue_sum,
            pending_appointments=pending_appointments,
        )

    except Exception:
        current_app.logger.exception("Error while loading home page")
        return "Error Loading MainPage", 500