from datetime import datetime

from flask import Blueprint, current_app, render_template, request, url_for

from models import Appointment, Treatment


invoices_bp = Blueprint("invoices", __name__)


@invoices_bp.route("/invoices")
def invoices():
    current_app.logger.info("Invoices page opened")

    try:
        search_query = request.args.get("search", "").strip()
        sort_by = request.args.get("sort", "date")
        order = request.args.get("order", "desc")

        invoice_appointments = (
            Appointment.query
            .join(Treatment)
            .distinct()
            .all()
        )

        if search_query:
            search_lower = search_query.lower()

            def matches_invoice(appointment):
                patient = appointment.patient
                invoice_number = f"inv-{appointment.id}".lower()
                appointment_date = (
                    appointment.appointment_date.strftime("%Y-%m-%d %H:%M").lower()
                    if appointment.appointment_date else ""
                )

                searchable_values = [
                    invoice_number,
                    str(appointment.id),
                    patient.first_name or "",
                    patient.last_name or "",
                    patient.phone or "",
                    appointment.status or "",
                    appointment_date,
                ]

                return any(
                    search_lower in str(value).lower()
                    for value in searchable_values
                )

            invoice_appointments = [
                appointment
                for appointment in invoice_appointments
                if matches_invoice(appointment)
            ]

        sort_key_map = {
            "id": lambda appointment: appointment.id,
            "patient": lambda appointment: (
                appointment.patient.first_name or "",
                appointment.patient.last_name or "",
            ),
            "date": lambda appointment: appointment.appointment_date or datetime.min,
            "treatments": lambda appointment: appointment.treatments_count,
            "total": lambda appointment: appointment.invoice_total,
            "payments": lambda appointment: appointment.total_paid,
            "outstanding": lambda appointment: appointment.balance,
            "status": lambda appointment: appointment.invoice_status,
        }

        sort_key = sort_key_map.get(sort_by, sort_key_map["date"])
        reverse_order = order != "asc"

        invoice_appointments = sorted(
            invoice_appointments,
            key=sort_key,
            reverse=reverse_order,
        )

        return render_template(
            "invoices/invoices.html",
            invoice_appointments=invoice_appointments,
            search_query=search_query,
            sort_by=sort_by,
            order=order,
        )

    except Exception:
        current_app.logger.exception("Failed to load invoices page")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load invoices.",
            back_url=url_for("dashboard.home"),
        ), 500


@invoices_bp.route("/invoices/<int:appointment_id>")
def view_invoice(appointment_id):
    current_app.logger.info(
        f"Invoice detail page opened | appointment_id={appointment_id}"
    )

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if not appointment.has_invoice:
            return render_template(
                "error_message.html",
                title="No Invoice Available",
                message="This appointment has no treatments, so there is no invoice to view.",
                back_url=url_for("invoices.invoices"),
            ), 400

        return render_template(
            "invoices/invoice_detail.html",
            appointment=appointment,
            patient=appointment.patient,
            treatments=appointment.treatments,
        )

    except Exception:
        current_app.logger.exception(
            f"Failed to load invoice detail | appointment_id={appointment_id}"
        )
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load invoice.",
            back_url=url_for("invoices.invoices"),
        ), 500