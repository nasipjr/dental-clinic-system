from datetime import datetime, time, timedelta

from flask import Blueprint, current_app, render_template

from models import db, Patient, Appointment, Treatment, Payment
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

        today_appointments = (
            Appointment.query
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .all()
        )
        today_checked_in = sum(1 for a in today_appointments if a.status == "Checked In")
        today_in_chair = sum(1 for a in today_appointments if a.status == "In Chair")
        today_done = sum(1 for a in today_appointments if a.status == "Done")
        today_scheduled = sum(1 for a in today_appointments if a.status == "Scheduled")

        from flask import g
        user = g.get("current_user")
        doctor_filter_id = user.id if (user and user.role == "doctor") else None

        scheduled_query = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .filter(Appointment.status.in_(["Scheduled", "Checked In", "In Chair"]))
        )
        if doctor_filter_id:
            scheduled_query = scheduled_query.filter(Appointment.doctor_id == doctor_filter_id)

        today_scheduled_appointments = scheduled_query.order_by(Appointment.appointment_date.asc()).all()

        done_query = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .filter(Appointment.status == "Done")
        )
        if doctor_filter_id:
            done_query = done_query.filter(Appointment.doctor_id == doctor_filter_id)

        today_done_appointments = done_query.order_by(Appointment.appointment_date.asc()).all()

        from models import Invoice
        total_revenue = sum(float(inv.total_amount) for inv in Invoice.query.join(Invoice.appointment).filter(Appointment.status != "Cancelled").all())
        total_paid = sum(float(pay.amount) for pay in Payment.query.all())

        total_remaining = total_revenue - total_paid
        total_outstanding = max(0.0, total_remaining)
        total_credit = max(0.0, -total_remaining)

        today_payments_sum = sum(float(pay.amount) for pay in Payment.query.filter(Payment.payment_date >= today_start, Payment.payment_date <= today_end).all())
        today_revenue_sum = sum(
            float(inv.total_amount)
            for inv in Invoice.query.join(Invoice.appointment).filter(
                Appointment.status != "Cancelled",
                Invoice.issue_date >= today_start,
                Invoice.issue_date <= today_end
            ).all()
        )

        pending_query = Appointment.query.join(Patient).filter(Appointment.status == "Pending")
        if doctor_filter_id:
            pending_query = pending_query.filter(Appointment.doctor_id == doctor_filter_id)
        pending_appointments = pending_query.order_by(Appointment.appointment_date.asc()).all()

        # Tomorrow's appointments query
        tomorrow = today + timedelta(days=1)
        tomorrow_start = datetime.combine(tomorrow, time.min)
        tomorrow_end = datetime.combine(tomorrow, time.max)
        tomorrow_query = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.appointment_date >= tomorrow_start)
            .filter(Appointment.appointment_date <= tomorrow_end)
            .filter(Appointment.status == "Scheduled")
        )
        if doctor_filter_id:
            tomorrow_query = tomorrow_query.filter(Appointment.doctor_id == doctor_filter_id)
        tomorrow_appointments = tomorrow_query.order_by(Appointment.appointment_date.asc()).all()

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
            tomorrow_appointments=tomorrow_appointments,
            today_payments_sum=today_payments_sum,
            today_revenue_sum=today_revenue_sum,
            pending_appointments=pending_appointments,
            today_checked_in=today_checked_in,
            today_in_chair=today_in_chair,
            today_done=today_done,
            today_scheduled=today_scheduled
        )

    except Exception:
        current_app.logger.exception("Error while loading home page")
        return "Error Loading MainPage", 500