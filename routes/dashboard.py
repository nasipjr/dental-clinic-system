from datetime import datetime, time, timedelta

from flask import Blueprint, current_app, render_template
from sqlalchemy.orm import joinedload

from models import db, Patient, Appointment, Treatment, Payment
from utils.auth_helper import role_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@role_required("admin", "doctor", "receptionist")
def home():
    current_app.logger.info("Home page opened")

    try:
        from routes.appointments import cancel_expired_appointments
        cancel_expired_appointments()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        scheduled_appointments = Appointment.query.filter_by(status="Scheduled").count()
        done_appointments = Appointment.query.filter_by(status="Done").count()
        cancelled_appointments = Appointment.query.filter_by(status="Cancelled").count()
        total_treatments = Treatment.query.count()

        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        from sqlalchemy import func
        from models import Invoice

        today_status_rows = (
            db.session.query(Appointment.status, func.count(Appointment.id))
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .group_by(Appointment.status)
            .all()
        )
        status_dict = dict(today_status_rows)
        today_done = status_dict.get("Done", 0)
        today_scheduled = status_dict.get("Scheduled", 0)

        from flask import g
        user = g.get("current_user")
        doctor_filter_id = user.id if (user and user.role == "doctor") else None

        scheduled_query = (
            Appointment.query
            .join(Patient)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor),
                joinedload(Appointment.invoice)
            )
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .filter(Appointment.status == "Scheduled")
        )
        if doctor_filter_id:
            scheduled_query = scheduled_query.filter(Appointment.doctor_id == doctor_filter_id)

        today_scheduled_appointments = scheduled_query.order_by(Appointment.appointment_date.asc()).all()

        done_query = (
            Appointment.query
            .join(Patient)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor),
                joinedload(Appointment.invoice)
            )
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .filter(Appointment.status == "Done")
        )
        if doctor_filter_id:
            done_query = done_query.filter(Appointment.doctor_id == doctor_filter_id)

        today_done_appointments = done_query.order_by(Appointment.appointment_date.asc()).all()

        # ─── Per-patient financial breakdown (CRITICAL: never net credit against debt) ───
        subtotal_sub = (
            db.select(func.coalesce(func.sum(Treatment.total_cost), 0.0))
            .where(Treatment.appointment_id == Invoice.appointment_id)
            .scalar_subquery()
        )

        discount_amt_sub = db.case(
            (Invoice.discount_type == "percentage", subtotal_sub * func.coalesce(Invoice.discount, 0.0) / 100.0),
            else_=func.coalesce(Invoice.discount, 0.0)
        )

        net_total_sub = db.case(
            (subtotal_sub - discount_amt_sub + func.coalesce(Invoice.additional_charges, 0.0) > 0,
             subtotal_sub - discount_amt_sub + func.coalesce(Invoice.additional_charges, 0.0)),
            else_=0.0
        )

        patient_invoiced_rows = db.session.query(
            func.coalesce(Invoice.patient_id, Appointment.patient_id),
            func.coalesce(func.sum(net_total_sub), 0.0)
        ).join(Appointment, Invoice.appointment_id == Appointment.id).filter(
            Appointment.status != "Cancelled"
        ).group_by(func.coalesce(Invoice.patient_id, Appointment.patient_id)).all()

        patient_invoiced = {p_id: float(tot) for p_id, tot in patient_invoiced_rows if p_id}

        patient_payments_rows = db.session.query(
            Payment.patient_id,
            func.coalesce(func.sum(Payment.amount), 0.0)
        ).group_by(Payment.patient_id).all()

        patient_paid = {p_id: float(tot) for p_id, tot in patient_payments_rows if p_id}

        # Per-patient balance — positives = debt owed to clinic, negatives = clinic credit
        all_patient_ids = set(list(patient_invoiced.keys()) + list(patient_paid.keys()))
        total_outstanding = 0.0  # total owed TO the clinic (debts)
        total_credit = 0.0       # total owed BY the clinic (overpayments)
        for pid in all_patient_ids:
            balance = patient_invoiced.get(pid, 0.0) - patient_paid.get(pid, 0.0)
            if balance > 0:
                total_outstanding += balance   # patient owes clinic
            elif balance < 0:
                total_credit += abs(balance)   # clinic owes patient

        total_revenue = sum(patient_invoiced.values())
        total_paid = sum(patient_paid.values())
        total_remaining = total_outstanding - total_credit  # net for display widget only
        collection_rate = round((total_paid / total_revenue * 100), 1) if total_revenue > 0 else 100.0

        today_payments_sum = float(
            db.session.query(func.coalesce(func.sum(Payment.amount), 0.0))
            .filter(Payment.payment_date >= today_start, Payment.payment_date <= today_end)
            .scalar() or 0.0
        )
        today_revenue_sum = float(
            db.session.query(func.coalesce(func.sum(net_total_sub), 0.0))
            .join(Appointment, Invoice.appointment_id == Appointment.id)
            .filter(
                Appointment.status != "Cancelled",
                Invoice.issue_date >= today_start,
                Invoice.issue_date <= today_end
            )
            .scalar() or 0.0
        )

        from routes.appointments import cleanup_expired_pending_appointments
        cleanup_expired_pending_appointments()

        pending_query = (
            Appointment.query
            .join(Patient)
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor)
            )
            .filter(Appointment.status == "Pending")
        )
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
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor)
            )
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
            cancelled_appointments=cancelled_appointments,
            total_treatments=total_treatments,
            total_revenue=total_revenue,
            total_paid=total_paid,
            total_remaining=total_remaining,
            total_outstanding=total_outstanding,
            total_credit=total_credit,
            collection_rate=collection_rate,
            today_scheduled_appointments=today_scheduled_appointments,
            today_done_appointments=today_done_appointments,
            tomorrow_appointments=tomorrow_appointments,
            today_payments_sum=today_payments_sum,
            today_revenue_sum=today_revenue_sum,
            pending_appointments=pending_appointments,
            today_done=today_done,
            today_scheduled=today_scheduled
        )

    except Exception:
        current_app.logger.exception("Error while loading home page")
        return "Error Loading MainPage", 500