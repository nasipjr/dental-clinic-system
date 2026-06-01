from datetime import datetime

from flask import Blueprint, current_app, render_template, request, redirect, url_for

from models import db, Patient, Payment
from services.payment_service import allocate_patient_payments_to_invoices
from utils.validators import parse_invoice_payment_amount


payments_bp = Blueprint("payments", __name__)


def get_payments_context():
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")

    all_payments = (
        Payment.query
        .join(Patient)
        .all()
    )

    if search_query:
        search_lower = search_query.lower()

        def matches_payment(payment):
            patient = payment.patient
            payment_number = f"pay-{payment.id}".lower()
            payment_date = (
                payment.payment_date.strftime("%Y-%m-%d %H:%M").lower()
                if payment.payment_date else ""
            )

            searchable_values = [
                payment_number,
                str(payment.id),
                patient.first_name or "",
                patient.last_name or "",
                patient.phone or "",
                str(payment.amount),
                str(payment.allocated_amount),
                str(payment.unallocated_amount),
                payment.notes or "",
                payment_date,
            ]

            return any(
                search_lower in str(value).lower()
                for value in searchable_values
            )

        all_payments = [
            payment
            for payment in all_payments
            if matches_payment(payment)
        ]

    sort_key_map = {
        "id": lambda payment: payment.id,
        "date": lambda payment: payment.payment_date or datetime.min,
        "patient": lambda payment: (
            payment.patient.first_name or "",
            payment.patient.last_name or "",
        ),
        "amount": lambda payment: payment.amount,
        "allocated": lambda payment: payment.allocated_amount,
        "credit": lambda payment: payment.unallocated_amount,
    }

    sort_key = sort_key_map.get(sort_by, sort_key_map["date"])
    reverse_order = order != "asc"

    all_payments = sorted(
        all_payments,
        key=sort_key,
        reverse=reverse_order,
    )

    return {
        "payments": all_payments,
        "search_query": search_query,
        "sort_by": sort_by,
        "order": order,
    }


@payments_bp.route("/payments")
def payments():
    current_app.logger.info("Payments page opened")

    try:
        context = get_payments_context()
        return render_template("payments/payments.html", **context)

    except Exception:
        current_app.logger.exception("Failed to load payments page")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load payments.",
            back_url=url_for("dashboard.home"),
        ), 500


@payments_bp.route("/payments/table")
def payments_table():
    current_app.logger.info("Payments table partial requested")

    try:
        context = get_payments_context()
        return render_template("partials/_payments_table.html", **context)

    except Exception:
        current_app.logger.exception("Failed to load payments table")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load payments table.",
            back_url=url_for("dashboard.home"),
        ), 500


@payments_bp.route("/payments/add", methods=["GET", "POST"])
def add_patient_payment():
    current_app.logger.info("Add patient payment page/request")

    try:
        patients = Patient.query.order_by(
            Patient.first_name.asc(),
            Patient.last_name.asc(),
        ).all()

        selected_patient_id = request.args.get("patient_id", type=int)
        selected_patient = None

        if selected_patient_id:
            selected_patient = Patient.query.get(selected_patient_id)

        if request.method == "POST":
            patient_id = request.form.get("patient_id", type=int)
            payment_amount_raw = request.form.get("payment_amount", "")
            notes = request.form.get("notes", "").strip()

            patient = Patient.query.get(patient_id)

            if not patient:
                return render_template(
                    "payments/add_patient_payment.html",
                    patients=patients,
                    selected_patient_id=selected_patient_id,
                    selected_patient=selected_patient,
                    error_message="Please select a valid patient.",
                ), 400

            payment_amount, payment_error = parse_invoice_payment_amount(payment_amount_raw)

            if payment_error:
                return render_template(
                    "payments/add_patient_payment.html",
                    patients=patients,
                    selected_patient_id=patient_id,
                    selected_patient=patient,
                    error_message=payment_error,
                ), 400

            new_payment = Payment(
                patient_id=patient.id,
                amount=payment_amount,
                notes=notes,
            )

            db.session.add(new_payment)
            db.session.flush()

            allocate_patient_payments_to_invoices(patient.id)

            db.session.commit()

            current_app.logger.info(
                f"Patient payment added successfully | patient_id={patient.id}, "
                f"payment_id={new_payment.id}, amount={payment_amount}"
            )

            return redirect(url_for("payments.payments"))

        return render_template(
            "payments/add_patient_payment.html",
            patients=patients,
            selected_patient_id=selected_patient_id,
            selected_patient=selected_patient,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to add patient payment")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to add payment.",
            back_url=url_for("payments.payments"),
        ), 500
