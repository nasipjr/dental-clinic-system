from datetime import datetime

from flask import Blueprint, current_app, render_template, request, url_for

from models import Invoice


invoices_bp = Blueprint("invoices", __name__)


def get_invoices_context():
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")

    invoices = Invoice.query.all()

    if search_query:
        search_lower = search_query.lower()

        def matches_invoice(invoice):
            patient = invoice.patient
            appointment = invoice.appointment

            invoice_number = invoice.invoice_number.lower()
            appointment_date = (
                invoice.appointment_date.strftime("%Y-%m-%d %H:%M").lower()
                if invoice.appointment_date else ""
            )

            searchable_values = [
                invoice_number,
                str(invoice.id),
                str(invoice.appointment_id),
                patient.first_name or "",
                patient.last_name or "",
                patient.phone or "",
                appointment.status if appointment else "",
                appointment_date,
            ]

            return any(
                search_lower in str(value).lower()
                for value in searchable_values
            )

        invoices = [
            invoice
            for invoice in invoices
            if matches_invoice(invoice)
        ]

    sort_key_map = {
        "id": lambda invoice: invoice.id,
        "patient": lambda invoice: (
            invoice.patient.first_name or "",
            invoice.patient.last_name or "",
        ),
        "date": lambda invoice: invoice.appointment_date or datetime.min,
        "treatments": lambda invoice: invoice.treatments_count,
        "total": lambda invoice: invoice.total_amount,
        "payments": lambda invoice: invoice.total_paid,
        "outstanding": lambda invoice: invoice.outstanding_amount,
        "status": lambda invoice: invoice.status,
    }

    sort_key = sort_key_map.get(sort_by, sort_key_map["date"])
    reverse_order = order != "asc"

    invoices = sorted(
        invoices,
        key=sort_key,
        reverse=reverse_order,
    )

    return {
        "invoices": invoices,
        "search_query": search_query,
        "sort_by": sort_by,
        "order": order,
    }


@invoices_bp.route("/invoices")
def invoices():
    current_app.logger.info("Invoices page opened")

    try:
        context = get_invoices_context()
        return render_template("invoices/invoices.html", **context)

    except Exception:
        current_app.logger.exception("Failed to load invoices page")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load invoices.",
            back_url=url_for("dashboard.home"),
        ), 500


@invoices_bp.route("/invoices/table")
def invoices_table():
    current_app.logger.info("Invoices table partial requested")

    try:
        context = get_invoices_context()
        return render_template("partials/_invoices_table.html", **context)

    except Exception:
        current_app.logger.exception("Failed to load invoices table")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load invoices table.",
            back_url=url_for("dashboard.home"),
        ), 500


@invoices_bp.route("/invoices/<int:invoice_id>")
def view_invoice(invoice_id):
    current_app.logger.info(f"Invoice detail page opened | invoice_id={invoice_id}")

    try:
        invoice = Invoice.query.get_or_404(invoice_id)

        return render_template(
            "invoices/invoice_detail.html",
            invoice=invoice,
            appointment=invoice.appointment,
            patient=invoice.patient,
            treatments=invoice.treatments,
        )

    except Exception:
        current_app.logger.exception(
            f"Failed to load invoice detail | invoice_id={invoice_id}"
        )
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load invoice.",
            back_url=url_for("invoices.invoices"),
        ), 500