from datetime import datetime
from sqlalchemy import func, or_

from flask import Blueprint, current_app, render_template, request, redirect, url_for

from models import db, Patient, Payment, PaymentAllocation
from services.payment_service import allocate_patient_payments_to_invoices
from utils.validators import parse_invoice_payment_amount
from utils.auth_helper import role_required


payments_bp = Blueprint("payments", __name__)


def get_payments_context():
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Payment.query.options(db.joinedload(Payment.patient)).join(Patient)

    if search_query:
        clean_search = search_query
        if search_query.lower().startswith("pay-"):
            clean_search = search_query[4:]

        filter_conds = [
            Patient.first_name.ilike(f"%{search_query}%"),
            Patient.last_name.ilike(f"%{search_query}%"),
            Patient.phone.ilike(f"%{search_query}%"),
            Payment.notes.ilike(f"%{search_query}%")
        ]

        try:
            payment_id_val = int(clean_search)
            filter_conds.append(Payment.id == payment_id_val)
        except ValueError:
            pass

        try:
            amount_val = float(search_query)
            filter_conds.append(Payment.amount == amount_val)
        except ValueError:
            pass

        query = query.filter(or_(*filter_conds))

    allocated_sum = (
        db.select(func.coalesce(func.sum(PaymentAllocation.amount), 0.0))
        .where(PaymentAllocation.payment_id == Payment.id)
        .scalar_subquery()
    )

    sort_columns = {
        "id": Payment.id,
        "date": Payment.payment_date,
        "patient": [Patient.first_name, Patient.last_name],
        "amount": Payment.amount,
        "allocated": allocated_sum,
        "credit": Payment.amount - allocated_sum,
    }

    sort_col = sort_columns.get(sort_by, Payment.payment_date)

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

    # ── Executive Manager Report & Stats for Payments ──
    total_payments_count = db.session.query(func.count(Payment.id)).scalar() or 0
    total_collected_cash = float(db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar() or 0.0)
    total_allocated_cash = float(db.session.query(func.coalesce(func.sum(PaymentAllocation.amount), 0.0)).scalar() or 0.0)
    total_unallocated_credit = max(0.0, total_collected_cash - total_allocated_cash)

    allocation_rate = float((total_allocated_cash / total_collected_cash * 100)) if total_collected_cash > 0 else 100.0
    avg_payment = float(total_collected_cash / total_payments_count) if total_payments_count > 0 else 0.0

    # Top 5 largest payments collected in clinic history
    top_payments = (
        Payment.query
        .options(db.joinedload(Payment.patient))
        .order_by(Payment.amount.desc())
        .limit(5)
        .all()
    )

    payment_stats = {
        "total_payments_count": total_payments_count,
        "total_collected_cash": float(total_collected_cash),
        "total_allocated_cash": float(total_allocated_cash),
        "total_unallocated_credit": float(total_unallocated_credit),
        "allocation_rate": allocation_rate,
        "avg_payment": avg_payment,
    }

    return {
        "payments": pagination.items,
        "pagination": pagination,
        "search_query": search_query,
        "sort_by": sort_by,
        "order": order,
        "payment_stats": payment_stats,
        "top_payments": top_payments,
        "per_page": per_page,
    }


@payments_bp.route("/payments")
@role_required("admin", "receptionist")
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
@role_required("admin", "receptionist")
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
@role_required("admin", "receptionist")
def add_patient_payment():
    current_app.logger.info("Add patient payment page/request")

    try:
        patients = Patient.query.order_by(
            Patient.first_name.asc(),
            Patient.last_name.asc(),
        ).all()

        selected_patient_id = request.args.get("patient_id", type=int)
        invoice_id = request.args.get("invoice_id", type=int)
        selected_patient = None

        if selected_patient_id:
            selected_patient = Patient.query.get(selected_patient_id)

        if request.method == "POST":
            patient_id = request.form.get("patient_id", type=int)
            payment_amount_raw = request.form.get("payment_amount", "")
            notes = request.form.get("notes", "").strip()
            invoice_id = request.form.get("invoice_id", type=int) or invoice_id

            patient = Patient.query.get(patient_id)

            if not patient:
                return render_template(
                    "payments/add_patient_payment.html",
                    patients=patients,
                    selected_patient_id=selected_patient_id,
                    selected_patient=selected_patient,
                    error_message="Please select a valid patient.",
                    invoice_id=invoice_id,
                ), 400

            payment_amount, payment_error = parse_invoice_payment_amount(payment_amount_raw)

            if payment_error:
                return render_template(
                    "payments/add_patient_payment.html",
                    patients=patients,
                    selected_patient_id=patient_id,
                    selected_patient=patient,
                    error_message=payment_error,
                    invoice_id=invoice_id,
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

            if invoice_id:
                return redirect(url_for("invoices.view_invoice", invoice_id=invoice_id))
            return redirect(url_for("payments.payments"))

        return render_template(
            "payments/add_patient_payment.html",
            patients=patients,
            selected_patient_id=selected_patient_id,
            selected_patient=selected_patient,
            invoice_id=invoice_id,
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


@payments_bp.route("/payments/<int:payment_id>")
@role_required("admin", "receptionist")
def view_payment(payment_id):
    current_app.logger.info(f"Payment detail page opened | payment_id={payment_id}")
    try:
        payment = Payment.query.get_or_404(payment_id)
        return render_template(
            "payments/payment_detail.html",
            payment=payment,
            patient=payment.patient,
            allocations=payment.allocations,
            current_lang=request.cookies.get('lang', 'en')
        )
    except Exception:
        current_app.logger.exception(
            f"Failed to load payment detail | payment_id={payment_id}"
        )
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load payment details.",
            back_url=url_for("payments.payments"),
        ), 500


@payments_bp.route("/payments/quick-settle/<int:patient_id>", methods=["POST"])
@role_required("admin", "receptionist")
def quick_settle_patient_debt(patient_id):
    """Instantly record a payment for a patient to settle their total remaining debt."""
    from models import db, Patient, Payment, Invoice, Appointment
    from services.payment_service import allocate_patient_payments_to_invoices
    from utils.settings_helper import get_setting
    from sqlalchemy import func, case
    is_ar = request.cookies.get("lang", "ar") != "en"

    try:
        patient = Patient.query.get_or_404(patient_id)

        req_amount_raw = request.form.get("amount", "")
        if req_amount_raw:
            try:
                outstanding = max(0.0, round(float(req_amount_raw), 2))
            except ValueError:
                outstanding = 0.0
        else:
            outstanding = 0.0

        if outstanding <= 0:
            subtotal_sub = func.coalesce(Invoice.subtotal, 0.0)
            discount_amt_sub = case(
                (Invoice.discount_type == 'percentage', subtotal_sub * (func.coalesce(Invoice.discount_value, 0.0) / 100.0)),
                else_=func.coalesce(Invoice.discount_value, 0.0)
            )
            net_total_sub = case(
                (subtotal_sub - discount_amt_sub + func.coalesce(Invoice.additional_charges, 0.0) > 0,
                 subtotal_sub - discount_amt_sub + func.coalesce(Invoice.additional_charges, 0.0)),
                else_=0.0
            )

            invoiced = float(
                db.session.query(func.coalesce(func.sum(net_total_sub), 0.0))
                .join(Appointment, Invoice.appointment_id == Appointment.id)
                .filter(Invoice.patient_id == patient_id, Appointment.status != "Cancelled")
                .scalar() or 0.0
            )

            paid = float(
                db.session.query(func.coalesce(func.sum(Payment.amount), 0.0))
                .filter(Payment.patient_id == patient_id)
                .scalar() or 0.0
            )

            outstanding = max(0.0, round(invoiced - paid, 2))

        if outstanding <= 0:
            msg = "لا توجد ديون متبقية على هذا المريض لتسديدها." if is_ar else "No outstanding debt found for this patient."
            return {"success": False, "message": msg}, 400

        full_name = f"{patient.first_name or ''} {patient.last_name or ''}".strip() or f"Patient #{patient_id}"
        currency = get_setting("currency_symbol", "ل.س")

        new_payment = Payment(
            patient_id=patient.id,
            amount=outstanding,
            notes=f"تسديد كامل الدين تلقائياً للمريض ({full_name})" if is_ar else f"Full quick debt settlement for ({full_name})"
        )
        db.session.add(new_payment)
        db.session.flush()

        allocate_patient_payments_to_invoices(patient.id)
        db.session.commit()

        msg = (f"تم التسديد السريع لدين المريض ({full_name}) بمبلغ ({outstanding:,.0f} {currency}) وتوثيقه بسجل المدفوعات بنجاح!"
               if is_ar else
               f"Successfully settled debt of ({outstanding:,.0f} {currency}) for patient ({full_name})!")

        return {"success": True, "message": msg, "amount": outstanding, "patient_id": patient_id}

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Failed quick debt settlement for patient_id={patient_id}: {e}")
        msg = f"حدث خطأ أثناء التسديد السريع للدين: {str(e)}" if is_ar else f"Failed to process quick debt settlement: {str(e)}"
        return {"success": False, "message": msg}, 500
