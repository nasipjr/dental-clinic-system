from datetime import datetime

from flask import Blueprint, current_app, render_template, request, redirect, url_for

from models import db, Patient, Appointment, Treatment, Invoice, Payment
from services.invoice_service import sync_invoice_for_appointment
from services.payment_service import allocate_patient_payments_to_invoices
from utils.constants import TREATMENT_PRICES, TREATMENT_PROCEDURE_TYPES


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
        
@invoices_bp.route("/invoices/add", methods=["GET", "POST"])
def add_invoice():
    current_app.logger.info("Add manual invoice page/request")

    try:
        patients = (
            Patient.query
            .order_by(Patient.first_name.asc(), Patient.last_name.asc())
            .all()
        )

        default_visit_datetime = datetime.now().replace(second=0, microsecond=0)

        if request.method == "POST":
            patient_id = request.form.get("patient_id", type=int)
            appointment_date_raw = request.form.get("appointment_date", "").strip()

            procedure_types = request.form.getlist("procedure_type")
            tooth_numbers = request.form.getlist("tooth_number")
            notes_list = request.form.getlist("notes")

            payment_option = request.form.get("payment_option", "no_payment").strip()
            custom_payment_amount_raw = request.form.get("custom_payment_amount", "").strip()

            patient = Patient.query.get(patient_id)

            if not patient:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=TREATMENT_PRICES,
                    default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                    error_message="Please select a valid patient.",
                ), 400

            if not appointment_date_raw:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=TREATMENT_PRICES,
                    default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                    error_message="Visit date is required.",
                ), 400

            try:
                appointment_date = datetime.strptime(appointment_date_raw, "%Y-%m-%dT%H:%M")
            except ValueError:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=TREATMENT_PRICES,
                    default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                    error_message="Visit date must be valid.",
                ), 400

            invoice_items = []

            for index, procedure_type in enumerate(procedure_types):
                procedure_type = procedure_type.strip()

                if not procedure_type:
                    continue

                if procedure_type not in TREATMENT_PROCEDURE_TYPES:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=TREATMENT_PRICES,
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Invalid treatment procedure type.",
                    ), 400

                tooth_number = tooth_numbers[index].strip() if index < len(tooth_numbers) else ""
                notes = notes_list[index].strip() if index < len(notes_list) else ""

                invoice_items.append({
                    "procedure_type": procedure_type,
                    "tooth_number": tooth_number,
                    "notes": notes,
                    "total_cost": TREATMENT_PRICES[procedure_type],
                })

            if not invoice_items:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=TREATMENT_PRICES,
                    default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                    error_message="Please add at least one invoice item.",
                ), 400

            appointment = Appointment(
                patient_id=patient.id,
                appointment_date=appointment_date,
                reason="Manual",
                status="Done",
            )

            db.session.add(appointment)
            db.session.flush()

            for item in invoice_items:
                treatment = Treatment(
                    appointment_id=appointment.id,
                    treatment_date=appointment.appointment_date,
                    procedure_type=item["procedure_type"],
                    tooth_number=item["tooth_number"],
                    notes=item["notes"],
                    total_cost=item["total_cost"],
                )

                db.session.add(treatment)

            db.session.flush()

            invoice = sync_invoice_for_appointment(appointment)
            invoice_total = invoice.total_amount

            if payment_option not in {"no_payment", "full_price", "custom_amount"}:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=TREATMENT_PRICES,
                    default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                    error_message="Invalid payment option.",
                ), 400

            payment_amount = 0

            if payment_option == "full_price":
                payment_amount = invoice_total

            elif payment_option == "custom_amount":
                if not custom_payment_amount_raw:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=TREATMENT_PRICES,
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Custom payment amount is required.",
                    ), 400

                try:
                    payment_amount = float(custom_payment_amount_raw)
                except ValueError:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=TREATMENT_PRICES,
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Custom payment amount must be a valid number.",
                    ), 400

                if payment_amount <= 0:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=TREATMENT_PRICES,
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Custom payment amount must be greater than 0.",
                    ), 400

                if payment_amount > invoice_total:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=TREATMENT_PRICES,
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Custom payment amount cannot be greater than invoice total.",
                    ), 400

            if payment_amount > 0:
                payment = Payment(
                    patient_id=patient.id,
                    amount=payment_amount,
                    notes=f"Manual invoice payment for {invoice.invoice_number}",
                )

                db.session.add(payment)
                db.session.flush()

            allocate_patient_payments_to_invoices(patient.id)

            db.session.commit()

            current_app.logger.info(
                f"Manual invoice created successfully | invoice_id={invoice.id}, patient_id={patient.id}"
            )

            return redirect(url_for("invoices.view_invoice", invoice_id=invoice.id))

        return render_template(
            "invoices/add_invoice.html",
            patients=patients,
            treatment_prices=TREATMENT_PRICES,
            default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to create manual invoice")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to create manual invoice.",
            back_url=url_for("invoices.invoices"),
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