from datetime import datetime
from sqlalchemy import func, or_

from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash

from models import db, Patient, Appointment, Treatment, Invoice, Payment, PaymentAllocation
from services.invoice_service import sync_invoice_for_appointment
from services.payment_service import allocate_patient_payments_to_invoices
from utils.constants import TREATMENT_PRICES, TREATMENT_PROCEDURE_TYPES
from utils.auth_helper import role_required


invoices_bp = Blueprint("invoices", __name__)


def get_invoices_context():
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Invoice.query.options(
        db.joinedload(Invoice.patient),
        db.joinedload(Invoice.appointment)
    ).join(Invoice.patient).join(Invoice.appointment)

    if search_query:
        clean_search = search_query
        if search_query.lower().startswith("inv-"):
            clean_search = search_query[4:]

        filter_conds = [
            Patient.first_name.ilike(f"%{search_query}%"),
            Patient.last_name.ilike(f"%{search_query}%"),
            (Patient.first_name + " " + Patient.last_name).ilike(f"%{search_query}%"),
            Patient.phone.ilike(f"%{search_query}%"),
            Appointment.status.ilike(f"%{search_query}%")
        ]

        try:
            invoice_id_val = int(clean_search)
            filter_conds.append(Invoice.id == invoice_id_val)
        except ValueError:
            pass

        try:
            appt_id_val = int(search_query)
            filter_conds.append(Invoice.appointment_id == appt_id_val)
        except ValueError:
            pass

        query = query.filter(or_(*filter_conds))

    treatments_count_sub = (
        db.select(func.count(Treatment.id))
        .where(Treatment.appointment_id == Invoice.appointment_id)
        .scalar_subquery()
    )

    total_amount_sub = (
        db.select(func.coalesce(func.sum(Treatment.total_cost), 0.0))
        .where(Treatment.appointment_id == Invoice.appointment_id)
        .scalar_subquery()
    )

    total_paid_sub = (
        db.select(func.coalesce(func.sum(PaymentAllocation.amount), 0.0))
        .where(PaymentAllocation.invoice_id == Invoice.id)
        .scalar_subquery()
    )

    discount_amt_sub = db.case(
        (Invoice.discount_type == "percentage", total_amount_sub * func.coalesce(Invoice.discount, 0.0) / 100.0),
        else_=func.coalesce(Invoice.discount, 0.0)
    )

    net_total_sub = (
        total_amount_sub - discount_amt_sub + func.coalesce(Invoice.additional_charges, 0.0)
    )

    outstanding_sub = db.case(
        (net_total_sub - total_paid_sub > 0, net_total_sub - total_paid_sub),
        else_=0.0
    )

    if status_filter:
        if status_filter in ("Paid", "مدفوع"):
            query = query.filter(total_paid_sub >= net_total_sub, net_total_sub > 0)
        elif status_filter in ("Partially Paid", "Partial", "Partially", "جزئي"):
            query = query.filter(total_paid_sub > 0.001, total_paid_sub < net_total_sub)
        elif status_filter in ("Unpaid", "غير مدفوع"):
            query = query.filter(or_(total_paid_sub <= 0.001, total_paid_sub.is_(None)))

    sort_columns = {
        "id": Invoice.id,
        "patient": [Patient.first_name, Patient.last_name],
        "date": Appointment.appointment_date,
        "treatments": treatments_count_sub,
        "total": total_amount_sub,
        "payments": total_paid_sub,
        "outstanding": outstanding_sub,
        "status": outstanding_sub,
    }

    sort_col = sort_columns.get(sort_by, Appointment.appointment_date)

    if isinstance(sort_col, list):
        if order == "asc":
            query = query.order_by(*(c.asc() for c in sort_col))
        else:
            query = query.order_by(*(c.desc() for c in sort_col))
    else:
        if order == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    # ── Executive Manager Report & Stats ──
    from decimal import Decimal

    inv_summary_tuples = db.session.query(
        Invoice.id,
        net_total_sub.label("net_total"),
        total_paid_sub.label("total_paid"),
        outstanding_sub.label("outstanding")
    ).all()

    total_invoices_count = len(inv_summary_tuples)
    total_billed = Decimal('0.00')
    total_collected = Decimal('0.00')
    total_outstanding = Decimal('0.00')

    unpaid_count = 0
    paid_count = 0
    partial_count = 0
    unpaid_count_strict = 0

    for _, net_t, paid_t, out_t in inv_summary_tuples:
        net_val = Decimal(str(net_t or 0))
        paid_val = Decimal(str(paid_t or 0))
        out_val = Decimal(str(out_t or 0))

        total_billed += net_val
        total_collected += paid_val
        total_outstanding += out_val

        if out_val > Decimal('0.00'):
            unpaid_count += 1

        if paid_val <= Decimal('0.001'):
            unpaid_count_strict += 1
        elif paid_val < net_val:
            partial_count += 1
        else:
            paid_count += 1

    collection_rate = (total_collected / total_billed * Decimal('100.00')).quantize(Decimal('0.01')) if total_billed > Decimal('0.00') else Decimal('100.00')
    avg_invoice = (total_billed / Decimal(str(total_invoices_count))).quantize(Decimal('0.01')) if total_invoices_count > 0 else Decimal('0.00')

    # Top 5 largest unpaid / partially paid invoices
    top_unpaid_invoices = (
        Invoice.query
        .options(db.joinedload(Invoice.patient), db.joinedload(Invoice.appointment))
        .filter(outstanding_sub > 0)
        .order_by(outstanding_sub.desc())
        .limit(5)
        .all()
    )

    invoice_stats = {
        "total_invoices_count": total_invoices_count,
        "total_billed": total_billed,
        "total_collected": total_collected,
        "total_outstanding": total_outstanding,
        "unpaid_count": unpaid_count,
        "collection_rate": collection_rate,
        "avg_invoice": avg_invoice,
    }

    status_counts = {
        "all": total_invoices_count,
        "paid": paid_count,
        "partial": partial_count,
        "unpaid": unpaid_count_strict,
    }

    return {
        "invoices": pagination.items,
        "pagination": pagination,
        "search_query": search_query,
        "status_filter": status_filter,
        "status_counts": status_counts,
        "sort_by": sort_by,
        "order": order,
        "invoice_stats": invoice_stats,
        "per_page": per_page,
        "top_unpaid_invoices": top_unpaid_invoices,
    }


@invoices_bp.route("/invoices")
@role_required("admin", "doctor", "receptionist")
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
@role_required("admin", "doctor", "receptionist")
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
@role_required("admin", "receptionist")
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

            patient = db.session.get(Patient, patient_id)

            if not patient:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=dict(TREATMENT_PRICES),
                    default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                    error_message="Please select a valid patient.",
                ), 400

            if not appointment_date_raw:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=dict(TREATMENT_PRICES),
                    default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                    error_message="Visit date is required.",
                ), 400

            appointment_date_raw_normalized = appointment_date_raw.replace('ص', 'AM').replace('م', 'PM').strip()
            try:
                appointment_date = datetime.strptime(appointment_date_raw_normalized, "%Y-%m-%dT%H:%M")
            except ValueError:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=dict(TREATMENT_PRICES),
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
                        treatment_prices=dict(TREATMENT_PRICES),
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Invalid treatment procedure type.",
                    ), 400

                tooth_number = tooth_numbers[index].strip() if index < len(tooth_numbers) else ""
                if len(tooth_number) > 50:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=dict(TREATMENT_PRICES),
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Tooth number cannot exceed 50 characters.",
                    ), 400
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
                    treatment_prices=dict(TREATMENT_PRICES),
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
            
            discount_type = request.form.get("discount_type", "value").strip()
            if discount_type not in {"value", "percentage"}:
                discount_type = "value"
                
            discount_val = 0.0
            discount_raw = request.form.get("discount", "0").strip()
            if discount_raw:
                try:
                    discount_val = float(discount_raw)
                    if discount_val < 0:
                        discount_val = 0.0
                except ValueError:
                    pass
            
            if discount_type == "percentage" and discount_val > 100.0:
                discount_val = 100.0
            elif discount_type == "value" and discount_val > float(invoice.subtotal):
                discount_val = float(invoice.subtotal)
                
            from decimal import Decimal
            invoice.discount = Decimal(str(discount_val))
            invoice.discount_type = discount_type
            db.session.flush()

            invoice_total = invoice.total_amount

            if payment_option not in {"no_payment", "full_price", "custom_amount"}:
                return render_template(
                    "invoices/add_invoice.html",
                    patients=patients,
                    treatment_prices=dict(TREATMENT_PRICES),
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
                        treatment_prices=dict(TREATMENT_PRICES),
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Custom payment amount is required.",
                    ), 400

                try:
                    payment_amount = float(custom_payment_amount_raw)
                except ValueError:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=dict(TREATMENT_PRICES),
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Custom payment amount must be a valid number.",
                    ), 400

                if payment_amount <= 0:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=dict(TREATMENT_PRICES),
                        default_visit_datetime=default_visit_datetime.strftime("%Y-%m-%dT%H:%M"),
                        error_message="Custom payment amount must be greater than 0.",
                    ), 400

                if payment_amount > invoice_total:
                    return render_template(
                        "invoices/add_invoice.html",
                        patients=patients,
                        treatment_prices=dict(TREATMENT_PRICES),
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
            treatment_prices=dict(TREATMENT_PRICES),
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
@role_required("admin", "doctor", "receptionist")
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


def make_invoice_json_data(invoice, is_ar, message):
    from utils.settings_helper import get_currency_symbol
    currency = get_currency_symbol()
    disc_label = f"({invoice.discount:,.0f}%)" if invoice.discount_type == "percentage" else ""
    return {
        "success": True,
        "message": message,
        "subtotal": float(invoice.subtotal),
        "subtotal_formatted": f"{invoice.subtotal:,.0f}",
        "discount": float(invoice.discount),
        "discount_type": invoice.discount_type,
        "discount_label": disc_label,
        "discount_amount": float(invoice.discount_amount),
        "discount_amount_formatted": f"{invoice.discount_amount:,.0f}",
        "additional_charges": float(invoice.additional_charges),
        "additional_charges_amount": float(invoice.additional_charges_amount),
        "additional_charges_amount_formatted": f"{invoice.additional_charges_amount:,.0f}",
        "total_amount": float(invoice.total_amount),
        "total_amount_formatted": f"{invoice.total_amount:,.0f}",
        "total_paid": float(invoice.total_paid),
        "total_paid_formatted": f"{invoice.total_paid:,.0f}",
        "outstanding_amount": float(invoice.outstanding_amount),
        "outstanding_amount_formatted": f"{invoice.outstanding_amount:,.0f}",
        "credit": float(invoice.credit),
        "credit_formatted": f"{invoice.credit:,.0f}",
        "status": invoice.status,
        "currency": currency,
        "notes": invoice.notes or "",
    }


@invoices_bp.route("/invoices/<int:invoice_id>/discount", methods=["POST"])
@role_required("admin", "receptionist")
def update_invoice_discount(invoice_id):
    current_app.logger.info(f"Update discount request | invoice_id={invoice_id}")
    is_ar = request.cookies.get("lang", "ar") == "ar"
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json or "application/json" in request.headers.get("Accept", "")

    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        
        discount_type = request.form.get("discount_type", "value").strip()
        if discount_type not in {"value", "percentage"}:
            discount_type = "value"
            
        discount_raw = request.form.get("discount", "0").strip()
        discount_val = 0.0
        if discount_raw:
            try:
                discount_val = float(discount_raw)
                if discount_val < 0:
                    discount_val = 0.0
            except ValueError:
                err_msg = "قيمة الخصم غير صحيحة." if is_ar else "Invalid discount amount."
                if is_ajax:
                    return {"success": False, "message": err_msg}, 400
                flash(err_msg, "danger")
                redirect_url = request.referrer or url_for("invoices.view_invoice", invoice_id=invoice_id)
                return redirect(redirect_url)
        
        if discount_type == "percentage" and discount_val > 100.0:
            err_msg = "لا يمكن أن تتجاوز نسبة الخصم 100%." if is_ar else "Discount percentage cannot exceed 100%."
            if is_ajax:
                return {"success": False, "message": err_msg}, 400
            flash(err_msg, "danger")
            redirect_url = request.referrer or url_for("invoices.view_invoice", invoice_id=invoice_id)
            return redirect(redirect_url)
        elif discount_type == "value" and discount_val > float(invoice.subtotal):
            err_msg = "لا يمكن أن يتجاوز الخصم المجموع الفرعي." if is_ar else "Discount cannot exceed the subtotal."
            if is_ajax:
                return {"success": False, "message": err_msg}, 400
            flash(err_msg, "danger")
            redirect_url = request.referrer or url_for("invoices.view_invoice", invoice_id=invoice_id)
            return redirect(redirect_url)
            
        from decimal import Decimal
        invoice.discount = Decimal(str(discount_val))
        invoice.discount_type = discount_type
        db.session.flush()
        
        # Recalculate allocations for the patient since invoice total has changed
        allocate_patient_payments_to_invoices(invoice.patient_id)
        db.session.commit()
        
        succ_msg = "تم تحديث الخصم بنجاح!" if is_ar else "Discount updated successfully!"
        if is_ajax:
            return make_invoice_json_data(invoice, is_ar, succ_msg)
        flash(succ_msg, "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to update discount for invoice {invoice_id}")
        err_msg = "فشل في تحديث الخصم." if is_ar else "Failed to update discount."
        if is_ajax:
            return {"success": False, "message": err_msg}, 500
        flash(err_msg, "danger")
        
    redirect_url = request.referrer or url_for("invoices.view_invoice", invoice_id=invoice_id)
    return redirect(redirect_url)


@invoices_bp.route("/invoices/<int:invoice_id>/additional-charges", methods=["POST"])
@role_required("admin", "receptionist")
def update_invoice_additional_charges(invoice_id):
    current_app.logger.info(f"Update additional charges request | invoice_id={invoice_id}")
    is_ar = request.cookies.get("lang", "ar") == "ar"
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json or "application/json" in request.headers.get("Accept", "")

    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        
        charges_raw = request.form.get("additional_charges", "0").strip()
        charges_val = 0.0
        if charges_raw:
            try:
                charges_val = float(charges_raw)
                if charges_val < 0:
                    charges_val = 0.0
            except ValueError:
                err_msg = "قيمة التكاليف الإضافية غير صحيحة." if is_ar else "Invalid additional charges amount."
                if is_ajax:
                    return {"success": False, "message": err_msg}, 400
                flash(err_msg, "danger")
                redirect_url = request.referrer or url_for("invoices.view_invoice", invoice_id=invoice_id)
                return redirect(redirect_url)
            
        from decimal import Decimal
        invoice.additional_charges = Decimal(str(charges_val))
        db.session.flush()
        
        # Recalculate allocations for the patient since invoice total has changed
        allocate_patient_payments_to_invoices(invoice.patient_id)
        db.session.commit()
        
        succ_msg = "تم تحديث التكاليف الإضافية بنجاح!" if is_ar else "Additional charges updated successfully!"
        if is_ajax:
            return make_invoice_json_data(invoice, is_ar, succ_msg)
        flash(succ_msg, "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to update additional charges for invoice {invoice_id}")
        err_msg = "فشل في تحديث التكاليف الإضافية." if is_ar else "Failed to update additional charges."
        if is_ajax:
            return {"success": False, "message": err_msg}, 500
        flash(err_msg, "danger")
        
    redirect_url = request.referrer or url_for("invoices.view_invoice", invoice_id=invoice_id)
    return redirect(redirect_url)


@invoices_bp.route("/invoices/<int:invoice_id>/notes", methods=["POST"])
@role_required("admin", "receptionist")
def update_invoice_notes(invoice_id):
    current_app.logger.info(f"Update invoice notes request | invoice_id={invoice_id}")
    is_ar = request.cookies.get("lang", "ar") == "ar"
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json or "application/json" in request.headers.get("Accept", "")

    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        notes = request.form.get("notes", "").strip()
        invoice.notes = notes
        db.session.commit()
        
        succ_msg = "تم تحديث ملاحظات الفاتورة بنجاح!" if is_ar else "Invoice notes updated successfully!"
        if is_ajax:
            return make_invoice_json_data(invoice, is_ar, succ_msg)
        flash(succ_msg, "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to update notes for invoice {invoice_id}")
        err_msg = "فشل في تحديث ملاحظات الفاتورة." if is_ar else "Failed to update invoice notes."
        if is_ajax:
            return {"success": False, "message": err_msg}, 500
        flash(err_msg, "danger")
        
    redirect_url = request.referrer or url_for("invoices.view_invoice", invoice_id=invoice_id)
    return redirect(redirect_url)

