from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload

from models import db, Patient, Appointment, Treatment, Payment, Invoice, PatientFile, ToothHistory, User
from utils.validators import parse_patient_data
from utils.auth_helper import role_required, get_safe_redirect_url
from utils.constants import TREATMENT_PROCEDURE_TYPES


patients_bp = Blueprint("patients", __name__)


def get_patients_context():
    search_query = request.args.get("search", "")
    sort_by = request.args.get("sort", "id")
    order = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Patient.query

    if search_query:
        query = query.filter(
            (Patient.first_name.ilike(f"%{search_query}%")) |
            (Patient.last_name.ilike(f"%{search_query}%")) |
            (Patient.phone.ilike(f"%{search_query}%")) |
            (Patient.email.ilike(f"%{search_query}%")) |
            (Patient.city.ilike(f"%{search_query}%"))
        )

    sort_columns = {
        "id": Patient.id,
        "first_name": Patient.first_name,
        "last_name": Patient.last_name,
        "phone": Patient.phone,
        "email": Patient.email,
        "city": Patient.city,
        "date_of_birth": Patient.date_of_birth,
    }

    sort_column = sort_columns.get(sort_by, Patient.id)

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    return {
        "patients": pagination.items,
        "pagination": pagination,
        "search_query": search_query,
        "sort_by": sort_by,
        "order": order,
    }


def get_patient_payments_context(patient_or_id):
    if isinstance(patient_or_id, Patient):
        patient = patient_or_id
    else:
        patient = Patient.query.get_or_404(patient_or_id)

    payment_sort = request.args.get("payment_sort", "date")
    payment_order = request.args.get("payment_order", "desc")

    patient_payments = Payment.query.filter_by(patient_id=patient.id).all()

    sort_key_map = {
        "id": lambda payment: payment.id,
        "date": lambda payment: payment.payment_date,
        "amount": lambda payment: payment.amount,
        "allocated": lambda payment: payment.allocated_amount,
        "credit": lambda payment: payment.unallocated_amount,
    }

    sort_key = sort_key_map.get(payment_sort, sort_key_map["date"])

    patient_payments = sorted(
        patient_payments,
        key=sort_key,
        reverse=payment_order != "asc",
    )

    return {
        "patient": patient,
        "patient_payments": patient_payments,
        "payment_sort": payment_sort,
        "payment_order": payment_order,
    }


def get_patient_invoices_context(patient_or_id):
    if isinstance(patient_or_id, Patient):
        patient = patient_or_id
    else:
        patient = Patient.query.get_or_404(patient_or_id)

    invoice_sort = request.args.get("invoice_sort", "date")
    invoice_order = request.args.get("invoice_order", "desc")

    patient_invoices = (
        Invoice.query
        .filter_by(patient_id=patient.id)
        .options(joinedload(Invoice.appointment), joinedload(Invoice.patient))
        .all()
    )

    sort_key_map = {
        "id": lambda invoice: invoice.id,
        "date": lambda invoice: invoice.appointment_date,
        "patient": lambda invoice: (invoice.patient.first_name, invoice.patient.last_name),
        "treatments": lambda invoice: invoice.treatments_count,
        "total": lambda invoice: invoice.total_amount,
        "payments": lambda invoice: invoice.total_paid,
        "outstanding": lambda invoice: invoice.balance,
        "status": lambda invoice: invoice.status,
    }

    sort_key = sort_key_map.get(invoice_sort, sort_key_map["date"])

    patient_invoices = sorted(
        patient_invoices,
        key=sort_key,
        reverse=invoice_order != "asc",
    )

    return {
        "patient": patient,
        "invoices": patient_invoices,
        "invoice_sort": invoice_sort,
        "invoice_order": invoice_order,
    }


@patients_bp.route("/patients")
@role_required("admin", "doctor", "receptionist")
def patients():
    current_app.logger.info("Patients page opened")

    try:
        context = get_patients_context()
        return render_template("patients/patients.html", **context)

    except Exception:
        current_app.logger.exception("Error while loading patients page")
        return "Error Loading PatientsPage", 500


@patients_bp.route("/patients/table")
@role_required("admin", "doctor", "receptionist")
def patients_table():
    current_app.logger.info("Patients table partial requested")

    try:
        context = get_patients_context()
        return render_template("partials/_patients_table.html", **context)

    except Exception:
        current_app.logger.exception("Error while loading patients table")
        return "Error Loading PatientsTable", 500


@patients_bp.route("/patients/check-duplicate", methods=["GET"])
@role_required("admin", "receptionist", "doctor")
def check_duplicate_patient():
    """AJAX endpoint: returns existing patients with same first+last name (case-insensitive)."""
    first_name = request.args.get("first_name", "").strip()
    last_name = request.args.get("last_name", "").strip()
    exclude_id = request.args.get("exclude_id", None, type=int)

    if not first_name or not last_name:
        return jsonify({"duplicates": []})

    query = Patient.query.filter(
        func.lower(Patient.first_name) == first_name.lower(),
        func.lower(Patient.last_name) == last_name.lower()
    )
    if exclude_id:
        query = query.filter(Patient.id != exclude_id)

    matches = query.all()
    result = [
        {
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "phone": p.phone or "",
            "date_of_birth": str(p.date_of_birth) if p.date_of_birth else "",
            "url": url_for("patients.patient_detail", patient_id=p.id)
        }
        for p in matches
    ]
    return jsonify({"duplicates": result})


@patients_bp.route("/patients/add", methods=["GET", "POST"])
@role_required("admin", "receptionist")
def add_patient():
    all_patients = Patient.query.order_by(Patient.first_name, Patient.last_name).all()

    if request.method == "POST":
        patient_data, patient_error = parse_patient_data(request.form)

        if patient_error:
            return render_template(
                "patients/add_patient.html",
                error_message=patient_error,
                all_patients=all_patients,
            ), 400

        # --- Duplicate Name Check ---
        force_save = request.form.get("force_save") == "1"
        if not force_save:
            first_name = patient_data.get("first_name", "").strip()
            last_name = patient_data.get("last_name", "").strip()
            duplicates = Patient.query.filter(
                func.lower(Patient.first_name) == first_name.lower(),
                func.lower(Patient.last_name) == last_name.lower()
            ).all()
            if duplicates:
                current_app.logger.warning(
                    f"Duplicate patient attempt: '{first_name} {last_name}' | matches={[p.id for p in duplicates]}"
                )
                return render_template(
                    "patients/add_patient.html",
                    duplicate_warning=True,
                    duplicate_patients=duplicates,
                    form_data=request.form,
                    all_patients=all_patients,
                ), 200
        # --- End Duplicate Check ---

        try:
            new_patient = Patient(**patient_data)

            db.session.add(new_patient)
            db.session.commit()

            current_app.logger.info(f"New patient added | id={new_patient.id} name='{new_patient.first_name} {new_patient.last_name}'")
            return redirect(url_for("patients.patients"))
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Failed to add patient")
            return render_template(
                "patients/add_patient.html",
                error_message="Failed to save patient database record. Please try again.",
                all_patients=all_patients,
            ), 500

    return render_template("patients/add_patient.html", all_patients=all_patients)


@patients_bp.route("/patients/<int:patient_id>")
@role_required("admin", "doctor", "receptionist")
def patient_detail(patient_id):
    current_app.logger.info(f"Patient detail page opened | patient_id={patient_id}")

    try:
        from utils.notification_helper import get_bot_username
        patient = (
            Patient.query
            .options(
                selectinload(Patient.files),
                selectinload(Patient.invoices),
                selectinload(Patient.payments)
            )
            .get_or_404(patient_id)
        )

        appointment_sort = request.args.get("appointment_sort", "date")
        appointment_order = request.args.get("appointment_order", "desc")

        treatment_sort = request.args.get("treatment_sort", "date")
        treatment_order = request.args.get("treatment_order", "desc")

        payment_context = get_patient_payments_context(patient)
        invoice_context = get_patient_invoices_context(patient)

        active_tab = request.args.get("tab", "appointments")

        appointment_sort_columns = {
            "id": Appointment.id,
            "date": Appointment.appointment_date,
            "reason": Appointment.reason,
            "status": Appointment.status,
        }

        appointments_query = (
            Appointment.query
            .filter_by(patient_id=patient.id)
            .options(
                selectinload(Appointment.treatments),
                joinedload(Appointment.invoice),
                joinedload(Appointment.doctor)
            )
        )

        if appointment_sort == "doctor":
            appointments_query = appointments_query.outerjoin(User, Appointment.doctor_id == User.id)
            if appointment_order == "asc":
                appointments_query = appointments_query.order_by(User.first_name.asc())
            else:
                appointments_query = appointments_query.order_by(User.first_name.desc())
        else:
            appointment_sort_column = appointment_sort_columns.get(
                appointment_sort,
                Appointment.appointment_date,
            )
            if appointment_order == "asc":
                appointments_query = appointments_query.order_by(appointment_sort_column.asc())
            else:
                appointments_query = appointments_query.order_by(appointment_sort_column.desc())

        patient_appointments = appointments_query.all()

        treatment_sort_columns = {
            "id": Treatment.id,
            "date": Treatment.treatment_date,
            "procedure_type": Treatment.procedure_type,
            "tooth_number": Treatment.tooth_number,
        }

        treatments_query = (
            Treatment.query
            .join(Appointment)
            .filter(Appointment.patient_id == patient.id)
            .options(joinedload(Treatment.doctor), joinedload(Treatment.appointment))
        )

        if treatment_sort == "doctor":
            treatments_query = treatments_query.outerjoin(User, Treatment.doctor_id == User.id)
            if treatment_order == "asc":
                treatments_query = treatments_query.order_by(User.first_name.asc())
            else:
                treatments_query = treatments_query.order_by(User.first_name.desc())
        else:
            treatment_sort_column = treatment_sort_columns.get(
                treatment_sort,
                Treatment.treatment_date,
            )
            if treatment_order == "asc":
                treatments_query = treatments_query.order_by(treatment_sort_column.asc())
            else:
                treatments_query = treatments_query.order_by(treatment_sort_column.desc())

        patient_treatments = treatments_query.all()
        
        patient_invoices = (
                Invoice.query
                .filter_by(patient_id=patient.id)
                .join(Invoice.appointment)
                .options(joinedload(Invoice.appointment), joinedload(Invoice.patient))
                .order_by(Appointment.appointment_date.desc(), Invoice.id.desc())
                .all()
            )

        total_cost_sum = patient.total_invoice_amount
        total_paid_sum = patient.total_payments_amount
        total_remaining_sum = patient.outstanding_amount
        credit_amount = patient.credit_amount

        patient_files = sorted(patient.files, key=lambda f: f.upload_date, reverse=True)

        # Build Ledger Entries
        def to_date_only(d):
            if d is None:
                return None
            if hasattr(d, "hour") and hasattr(d, "date") and callable(d.date):
                return d.date()
            return d

        ledger_entries = []
        invoices = Invoice.query.join(Invoice.appointment).filter(
            Appointment.patient_id == patient.id,
            Appointment.status != "Cancelled"
        ).options(joinedload(Invoice.appointment).selectinload(Appointment.treatments)).all()
        for inv in invoices:
            desc_items = [t.procedure_type for t in inv.appointment.treatments if t.procedure_type]
            desc_str = ", ".join(desc_items) if desc_items else (inv.appointment.reason or "Dental Session")
            inv_date = to_date_only(inv.issue_date)
            ledger_entries.append({
                "id": inv.id,
                "date": inv_date,
                "type": "invoice",
                "ref": inv.invoice_number,
                "description": desc_str,
                "debit": float(inv.total_amount),
                "credit": 0.0,
            })

        payments = Payment.query.filter_by(patient_id=patient.id).all()
        for pay in payments:
            pay_date = to_date_only(pay.payment_date)
            ledger_entries.append({
                "id": pay.id,
                "date": pay_date,
                "type": "payment",
                "ref": f"PAY-{pay.id:04d}",
                "description": pay.notes or ("Payment received" if request.cookies.get('lang') != 'ar' else "دفعة نقدية مستلمة"),
                "debit": 0.0,
                "credit": float(pay.amount),
            })

        # Sort chronologically
        ledger_entries.sort(key=lambda x: (x["date"], 0 if x["type"] == "invoice" else 1))

        # Calculate running balance
        running_bal = 0.0
        for entry in ledger_entries:
            running_bal += entry["debit"] - entry["credit"]
            entry["balance"] = running_bal

        # Tooth Pre-existing History / Diagnostic Notes
        from collections import defaultdict
        tooth_histories = ToothHistory.query.filter_by(patient_id=patient.id).order_by(ToothHistory.created_at.desc()).all()
        tooth_history_dict = defaultdict(list)
        for th in tooth_histories:
            tooth_history_dict[str(th.tooth_number)].append({
                "id": th.id,
                "procedure": th.procedure_type,
                "notes": th.notes or "",
                "history_date": th.history_date.strftime("%Y-%m-%d") if th.history_date else None,
                "created_at": th.created_at.strftime("%Y-%m-%d %I:%M %p") if th.created_at else (th.history_date.strftime("%Y-%m-%d") if th.history_date else "")
            })

        return render_template(
            "patients/patient_detail.html",
            patient=patient,
            patient_appointments=patient_appointments,
            patient_treatments=patient_treatments,
            patient_payments=payment_context["patient_payments"],
            invoices=invoice_context["invoices"],
            patient_files=patient_files,
            total_cost_sum=total_cost_sum,
            total_paid_sum=total_paid_sum,
            total_remaining_sum=total_remaining_sum,
            credit_amount=credit_amount,
            appointment_sort=appointment_sort,
            appointment_order=appointment_order,
            treatment_sort=treatment_sort,
            treatment_order=treatment_order,
            payment_sort=payment_context["payment_sort"],
            payment_order=payment_context["payment_order"],
            invoice_sort=invoice_context["invoice_sort"],
            invoice_order=invoice_context["invoice_order"],
            active_tab=active_tab,
            ledger_entries=ledger_entries,
            tooth_history_dict=tooth_history_dict,
            treatment_procedure_types=list(TREATMENT_PROCEDURE_TYPES),
            bot_username=get_bot_username()
        )

    except Exception:
        current_app.logger.exception(
            f"Error while loading patient detail | patient_id={patient_id}"
        )
        return "Error Loading PatientsInfo", 500


@patients_bp.route("/patients/<int:patient_id>/tooth-history/add", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def add_tooth_history(patient_id):
    import re
    patient = Patient.query.get_or_404(patient_id)
    tooth_number = request.form.get("tooth_number")
    procedure_type = request.form.get("procedure_type")
    notes = request.form.get("notes", "").strip()

    appointment_id = request.form.get("appointment_id") or request.args.get("appointment_id")
    if not appointment_id and request.referrer:
        match = re.search(r'/appointments/(\d+)/session', request.referrer)
        if match:
            appointment_id = match.group(1)

    if not tooth_number or not procedure_type:
        flash("يرجى اختيار السن ونوع الإجراء السريري." if request.cookies.get("lang") == "ar" else "Please specify tooth number and procedure type.", "danger")
        if appointment_id:
            return redirect(url_for("treatments.appointment_session", appointment_id=appointment_id))
        return redirect(url_for("patients.patient_detail", patient_id=patient_id, active_tab="chart"))

    history_date_str = request.form.get("history_date", "").strip()
    history_date_val = None
    if history_date_str:
        try:
            from datetime import datetime
            parsed_date = datetime.strptime(history_date_str, "%Y-%m-%d").date()
            if parsed_date > datetime.now().date():
                flash("لا يمكن اختيار تاريخ مستقبلي لمعالجة تاريخية سابقة!" if request.cookies.get("lang") == "ar" else "Cannot select a future date for prior tooth history!", "danger")
                if appointment_id:
                    return redirect(url_for("treatments.appointment_session", appointment_id=appointment_id))
                return redirect(url_for("patients.patient_detail", patient_id=patient_id, active_tab="chart"))
            history_date_val = parsed_date
        except ValueError:
            history_date_val = None

    th = ToothHistory(
        patient_id=patient.id,
        tooth_number=str(tooth_number),
        procedure_type=procedure_type,
        notes=notes,
        history_date=history_date_val
    )
    db.session.add(th)
    db.session.commit()

    flash("تم تسجيل السابقة المرضية بنجاح." if request.cookies.get("lang") == "ar" else "Tooth pre-existing condition recorded successfully.", "success")
    if appointment_id:
        return redirect(url_for("treatments.appointment_session", appointment_id=appointment_id))
    return redirect(url_for("patients.patient_detail", patient_id=patient_id, active_tab="chart"))


@patients_bp.route("/patients/<int:patient_id>/tooth-history/<int:history_id>/delete", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def delete_tooth_history(patient_id, history_id):
    import re
    patient = Patient.query.get_or_404(patient_id)
    th = ToothHistory.query.filter_by(id=history_id, patient_id=patient.id).first_or_404()
    db.session.delete(th)
    db.session.commit()

    appointment_id = request.form.get("appointment_id") or request.args.get("appointment_id")
    if not appointment_id and request.referrer:
        match = re.search(r'/appointments/(\d+)/session', request.referrer)
        if match:
            appointment_id = match.group(1)

    flash("تم حذف السابقة المرضية بنجاح." if request.cookies.get("lang") == "ar" else "Tooth condition record deleted successfully.", "success")
    if appointment_id:
        return redirect(url_for("treatments.appointment_session", appointment_id=appointment_id))
    return redirect(url_for("patients.patient_detail", patient_id=patient_id, active_tab="chart"))


@patients_bp.route("/patients/<int:patient_id>/tooth-history/<int:history_id>/edit", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def edit_tooth_history(patient_id, history_id):
    import re
    patient = Patient.query.get_or_404(patient_id)
    th = ToothHistory.query.filter_by(id=history_id, patient_id=patient.id).first_or_404()

    procedure_type = request.form.get("procedure_type", "").strip()
    notes = request.form.get("notes", "").strip()
    history_date_str = request.form.get("history_date", "").strip()

    if procedure_type:
        th.procedure_type = procedure_type
    th.notes = notes

    if history_date_str:
        try:
            from datetime import datetime
            parsed_date = datetime.strptime(history_date_str, "%Y-%m-%d").date()
            if parsed_date > datetime.now().date():
                appointment_id = request.form.get("appointment_id") or request.args.get("appointment_id")
                flash("لا يمكن اختيار تاريخ مستقبلي لمعالجة تاريخية سابقة!" if request.cookies.get("lang") == "ar" else "Cannot select a future date for prior tooth history!", "danger")
                if appointment_id:
                    return redirect(url_for("treatments.appointment_session", appointment_id=appointment_id))
                return redirect(url_for("patients.patient_detail", patient_id=patient_id, active_tab="chart"))
            th.history_date = parsed_date
        except ValueError:
            th.history_date = None
    else:
        th.history_date = None

    db.session.commit()

    appointment_id = request.form.get("appointment_id") or request.args.get("appointment_id")
    if not appointment_id and request.referrer:
        match = re.search(r'/appointments/(\d+)/session', request.referrer)
        if match:
            appointment_id = match.group(1)

    flash("تم تحديث السابقة المرضية بنجاح." if request.cookies.get("lang") == "ar" else "Tooth condition record updated successfully.", "success")
    if appointment_id:
        return redirect(url_for("treatments.appointment_session", appointment_id=appointment_id))
    return redirect(url_for("patients.patient_detail", patient_id=patient_id, active_tab="chart"))


@patients_bp.route("/patients/<int:patient_id>/ledger/print")
@role_required("admin", "doctor", "receptionist")
def patient_ledger_print(patient_id):
    current_app.logger.info(f"Printing patient ledger | patient_id={patient_id}")
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        def to_date_only(d):
            if d is None:
                return None
            if hasattr(d, "hour") and hasattr(d, "date") and callable(d.date):
                return d.date()
            return d

        ledger_entries = []
        invoices = Invoice.query.join(Invoice.appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.status != "Cancelled"
        ).all()
        
        for inv in invoices:
            desc_items = [t.procedure_type for t in inv.appointment.treatments if t.procedure_type]
            desc_str = ", ".join(desc_items) if desc_items else (inv.appointment.reason or "Dental Session")
            inv_date = to_date_only(inv.issue_date)
            ledger_entries.append({
                "id": inv.id,
                "date": inv_date,
                "type": "invoice",
                "ref": inv.invoice_number,
                "description": desc_str,
                "debit": Decimal(str(inv.total_amount or 0)),
                "credit": Decimal('0.00'),
            })
            
        payments = Payment.query.filter_by(patient_id=patient_id).all()
        for pay in payments:
            pay_date = to_date_only(pay.payment_date)
            ledger_entries.append({
                "id": pay.id,
                "date": pay_date,
                "type": "payment",
                "ref": f"PAY-{pay.id:04d}",
                "description": pay.notes or ("Payment received" if request.cookies.get('lang') != 'ar' else "دفعة نقدية مستلمة"),
                "debit": Decimal('0.00'),
                "credit": Decimal(str(pay.amount or 0)),
            })
            
        ledger_entries.sort(key=lambda x: (x["date"], 0 if x["type"] == "invoice" else 1))
        
        from decimal import Decimal
        running_bal = Decimal('0.00')
        for entry in ledger_entries:
            running_bal += entry["debit"] - entry["credit"]
            entry["balance"] = running_bal
            
        from utils.settings_helper import get_setting
        clinic_name = get_setting("clinic_name", "Dental Clinic")
        currency_symbol = get_setting("currency_symbol", "S.P")
        
        from datetime import datetime
        return render_template(
            "patients/patient_ledger_print.html",
            patient=patient,
            entries=ledger_entries,
            clinic_name=clinic_name,
            currency_symbol=currency_symbol,
            now=datetime.now(),
            current_lang=request.cookies.get('lang', 'en')
        )
    except Exception:
        current_app.logger.exception(f"Failed to print ledger for patient {patient_id}")
        return "Failed to print ledger", 500


@patients_bp.route("/patients/<int:patient_id>/payments-table")
@role_required("admin", "doctor", "receptionist")
def patient_payments_table(patient_id):
    context = get_patient_payments_context(patient_id)

    return render_template(
        "partials/_patient_payments_table.html",
        **context,
    )


@patients_bp.route("/patients/<int:patient_id>/invoices-table")
@role_required("admin", "doctor", "receptionist")
def patient_invoices_table(patient_id):
    context = get_patient_invoices_context(patient_id)

    return render_template(
        "partials/_patient_invoices_table.html",
        **context,
    )


@patients_bp.route("/patients/<int:patient_id>/appointments-table")
@role_required("admin", "doctor", "receptionist")
def patient_appointments_table(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    appointment_sort = request.args.get("appointment_sort", "date")
    appointment_order = request.args.get("appointment_order", "desc")

    sort_columns = {
        "id": Appointment.id,
        "date": Appointment.appointment_date,
        "reason": Appointment.reason,
        "status": Appointment.status,
    }

    query = Appointment.query.filter_by(patient_id=patient.id)

    if appointment_sort == "doctor":
        query = query.outerjoin(User, Appointment.doctor_id == User.id)
        if appointment_order == "asc":
            query = query.order_by(User.first_name.asc())
        else:
            query = query.order_by(User.first_name.desc())
    else:
        sort_column = sort_columns.get(appointment_sort, Appointment.appointment_date)
        if appointment_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

    patient_appointments = query.all()

    return render_template(
        "partials/_patient_appointments_table.html",
        patient=patient,
        patient_appointments=patient_appointments,
        appointment_sort=appointment_sort,
        appointment_order=appointment_order,
    )


@patients_bp.route("/patients/<int:patient_id>/treatments-table")
@role_required("admin", "doctor", "receptionist")
def patient_treatments_table(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    treatment_sort = request.args.get("treatment_sort", "date")
    treatment_order = request.args.get("treatment_order", "desc")

    sort_columns = {
        "id": Treatment.id,
        "date": Treatment.treatment_date,
        "procedure_type": Treatment.procedure_type,
        "tooth_number": Treatment.tooth_number,
    }

    query = (
        Treatment.query
        .join(Appointment)
        .filter(Appointment.patient_id == patient.id)
    )

    if treatment_sort == "doctor":
        query = query.outerjoin(User, Treatment.doctor_id == User.id)
        if treatment_order == "asc":
            query = query.order_by(User.first_name.asc())
        else:
            query = query.order_by(User.first_name.desc())
    else:
        sort_column = sort_columns.get(treatment_sort, Treatment.treatment_date)
        if treatment_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

    patient_treatments = query.all()

    return render_template(
        "partials/_patient_treatments_table.html",
        patient=patient,
        patient_treatments=patient_treatments,
        treatment_sort=treatment_sort,
        treatment_order=treatment_order,
    )


@patients_bp.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
@role_required("admin", "doctor", "receptionist")
def edit_patient(patient_id):
    current_app.logger.info(f"Edit patient page/request | patient_id={patient_id}")

    try:
        patient = Patient.query.get_or_404(patient_id)
        all_patients = Patient.query.filter(Patient.id != patient_id).order_by(Patient.first_name, Patient.last_name).all()

        if request.method == "POST":
            patient_data, patient_error = parse_patient_data(request.form)

            if patient_error:
                return render_template(
                    "patients/edit_patient.html",
                    patient=patient,
                    mode="edit",
                    error_message=patient_error,
                    all_patients=all_patients,
                ), 400

            # --- Duplicate Name Check (exclude current patient) ---
            force_save = request.form.get("force_save") == "1"
            if not force_save:
                first_name = patient_data.get("first_name", "").strip()
                last_name = patient_data.get("last_name", "").strip()
                duplicates = Patient.query.filter(
                    func.lower(Patient.first_name) == first_name.lower(),
                    func.lower(Patient.last_name) == last_name.lower(),
                    Patient.id != patient_id
                ).all()
                if duplicates:
                    current_app.logger.warning(
                        f"Duplicate name on edit: '{first_name} {last_name}' | existing={[p.id for p in duplicates]}"
                    )
                    return render_template(
                        "patients/edit_patient.html",
                        patient=patient,
                        mode="edit",
                        duplicate_warning=True,
                        duplicate_patients=duplicates,
                        all_patients=all_patients,
                    ), 200
            # --- End Duplicate Check ---

            for field, value in patient_data.items():
                setattr(patient, field, value)

            db.session.commit()

            current_app.logger.info(
                f"Patient updated successfully | patient_id={patient.id}"
            )
            return redirect(get_safe_redirect_url("patients.patient_detail", patient_id=patient.id))

        next_url = request.args.get("next") or request.referrer or ""
        if any(k in next_url for k in ["/edit", "/delete"]):
            next_url = ""

        return render_template(
            "patients/edit_patient.html",
            patient=patient,
            mode="edit",
            all_patients=all_patients,
            next_url=next_url,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to edit patient | patient_id={patient_id}")
        return "Failed to edit patient", 500


@patients_bp.route("/patients/<int:patient_id>/view")
@role_required("admin", "doctor", "receptionist")
def view_patient(patient_id):
    current_app.logger.info(f"View patient page opened | patient_id={patient_id}")

    try:
        patient = Patient.query.get_or_404(patient_id)

        return render_template(
            "patients/edit_patient.html",
            patient=patient,
            mode="view",
        )

    except Exception:
        current_app.logger.exception(f"Failed to view patient | patient_id={patient_id}")
        return "Failed to view patient", 500


@patients_bp.route("/patients/<int:patient_id>/delete", methods=["GET", "POST"])
@role_required("admin")
def delete_patient(patient_id):
    current_app.logger.warning(f"Delete patient page/request | patient_id={patient_id}")

    try:
        patient = Patient.query.get_or_404(patient_id)

        if patient.appointments:
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message=(
                    "Cannot delete this patient because they have appointments "
                    "linked to their medical history."
                ),
                back_url=url_for("patients.patient_detail", patient_id=patient.id),
            ), 403

        if request.method == "POST":
            import os
            for patient_file in patient.files:
                disk_path = os.path.join(current_app.static_folder, patient_file.filepath)
                if os.path.exists(disk_path):
                    try:
                        os.remove(disk_path)
                    except Exception:
                        current_app.logger.exception(f"Failed to remove file from disk during patient delete: {disk_path}")
            
            db.session.delete(patient)
            db.session.commit()

            current_app.logger.info(
                f"Patient deleted successfully | patient_id={patient_id}"
            )
            return redirect(url_for("patients.patients"))

        return render_template("patients/delete_patient.html", patient=patient)

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to delete patient | patient_id={patient_id}")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to delete patient.",
            back_url=url_for("patients.patients"),
        ), 500


@patients_bp.route("/patients/<int:patient_id>/portal/create", methods=["POST"])
@role_required("admin", "receptionist")
def create_portal_account(patient_id):
    current_app.logger.info(f"Creating patient portal account for patient_id={patient_id}")
    try:
        patient = Patient.query.get_or_404(patient_id)
        if patient.user:
            flash("Patient already has a portal account.", "warning")
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        is_ar = request.cookies.get('lang', 'ar') != 'en'

        if len(username) > 80:
            msg = "اسم المستخدم لا يمكن أن يتجاوز 80 حرفاً." if is_ar else "Username cannot exceed 80 characters."
            flash(msg, "danger")
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        if len(password) < 6:
            msg = "كلمة السر يجب أن تكون 6 أحرف على الأقل." if is_ar else "Password must be at least 6 characters."
            flash(msg, "danger")
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        from models import User
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            msg = "اسم المستخدم موجود مسبقاً، يرجى اختيار اسم آخر." if is_ar else "Username already exists. Please choose a different one."
            flash(msg, "danger")
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        new_user = User(
            username=username,
            role="patient",
            first_name=patient.first_name,
            last_name=patient.last_name,
            patient_id=patient.id
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Send Telegram notification if patient has a linked telegram chat
        telegram_sent = False
        if getattr(patient, "telegram_chat_id", None):
            try:
                from utils.notification_helper import send_telegram_message
                from utils.settings_helper import get_setting
                clinic_name = get_setting("clinic_name", "العيادة")
                patient_name = f"{patient.first_name} {patient.last_name}"
                msg_text = (
                    f"🎉 *مرحباً بك في بوابة المرضى الإلكترونية*\n\n"
                    f"مرحباً *{patient_name}*،\n"
                    f"تم إنشاء حساب جديد لك في بوابة {clinic_name}.\n\n"
                    f"👤 *اسم المستخدم:* `{username}`\n"
                    f"🔑 *كلمة المرور:* `{password}`\n\n"
                    f"⚠️ _يرجى الحفاظ على كلمة المرور وعدم مشاركتها مع أحد._"
                )
                success, _ = send_telegram_message(patient.telegram_chat_id, msg_text)
                if success:
                    telegram_sent = True
            except Exception as e:
                current_app.logger.error(f"Failed to send telegram account creation alert: {e}")

        if is_ar:
            if telegram_sent:
                flash(f"تم إنشاء حساب البوابة الإلكترونية للمريض: {patient.first_name} وإرسال بيانات الدخول إلى حسابه على التلغرام.", "success")
            else:
                flash(f"تم إنشاء حساب البوابة الإلكترونية بنجاح للمريض: {patient.first_name}. اسم المستخدم: {username} | كلمة المرور: {password}", "success")
        else:
            if telegram_sent:
                flash(f"Portal account created successfully for patient: {patient.first_name}. Credentials sent via Telegram.", "success")
            else:
                flash(f"Portal account created successfully for patient: {patient.first_name}. Username: {username} | Password: {password}", "success")
        return redirect(url_for("patients.patient_detail", patient_id=patient.id))

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to create portal account for patient_id={patient_id}")
        msg = "فشل إنشاء حساب البوابة بسبب خطأ في قاعدة البيانات." if is_ar else "Failed to create portal account due to a database error."
        flash(msg, "danger")
        return redirect(url_for("patients.patient_detail", patient_id=patient_id))


@patients_bp.route("/patients/<int:patient_id>/portal/reset_password", methods=["POST"])
@role_required("admin", "receptionist", "doctor")
def reset_portal_account_password(patient_id):
    current_app.logger.info(f"Resetting patient portal password for patient_id={patient_id}")
    is_ar = request.cookies.get('lang', 'ar') != 'en'
    try:
        patient = Patient.query.get_or_404(patient_id)
        if not patient.user:
            msg = "المريض ليس لديه حساب بوابة إلكترونية." if is_ar else "Patient does not have a portal account."
            flash(msg, "warning")
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        new_password = request.form.get("password", "").strip()
        if not new_password or len(new_password) < 6:
            msg = "كلمة السر يجب أن تكون 6 أحرف على الأقل." if is_ar else "Password must be at least 6 characters."
            flash(msg, "danger")
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        patient.user.set_password(new_password)
        db.session.commit()

        # Send Telegram notification if patient has a linked telegram chat
        telegram_sent = False
        if getattr(patient, "telegram_chat_id", None):
            try:
                from utils.notification_helper import send_telegram_message
                from utils.settings_helper import get_setting
                clinic_name = get_setting("clinic_name", "العيادة")
                patient_name = f"{patient.first_name} {patient.last_name}"
                msg_text = (
                    f"🔐 *تنبيه أمان - بوابة المرضى*\n\n"
                    f"مرحباً *{patient_name}*،\n"
                    f"تم تحديث بيانات الدخول الخاصة بحسابك في بوابة {clinic_name} بنجاح.\n\n"
                    f"👤 *اسم المستخدم:* `{patient.user.username}`\n"
                    f"🔑 *كلمة المرور الجديدة:* `{new_password}`\n\n"
                    f"⚠️ _يرجى الحفاظ على كلمة المرور وعدم مشاركتها مع أحد._"
                )
                success, _ = send_telegram_message(patient.telegram_chat_id, msg_text)
                if success:
                    telegram_sent = True
            except Exception as e:
                current_app.logger.error(f"Failed to send telegram password reset alert: {e}")

        if is_ar:
            if telegram_sent:
                msg = f"تم تحديث كلمة المرور للمريض ({patient.first_name}) بنجاح وإرسال الإشعار عبر التلغرام."
            else:
                msg = f"تم تحديث كلمة المرور للمريض ({patient.first_name}) بنجاح. كلمة المرور الجديدة: {new_password}"
        else:
            if telegram_sent:
                msg = f"Password updated for patient ({patient.first_name}) and notification sent via Telegram."
            else:
                msg = f"Password updated for patient ({patient.first_name}). New password: {new_password}"

        flash(msg, "success")
        return redirect(url_for("patients.patient_detail", patient_id=patient.id))

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to reset portal password for patient_id={patient_id}")
        msg = "فشل تغيير كلمة المرور بسبب خطأ في قاعدة البيانات." if is_ar else "Failed to reset portal password due to database error."
        flash(msg, "danger")
        return redirect(url_for("patients.patient_detail", patient_id=patient_id))


@patients_bp.route("/patients/<int:patient_id>/portal/delete", methods=["POST"])
@role_required("admin", "receptionist")
def delete_portal_account(patient_id):
    current_app.logger.warning(f"Deleting patient portal account for patient_id={patient_id}")
    is_ar = request.cookies.get('lang', 'ar') != 'en'
    try:
        patient = Patient.query.get_or_404(patient_id)
        if not patient.user:
            msg = "المريض ليس لديه حساب بوابة إلكترونية." if is_ar else "Patient does not have a portal account."
            flash(msg, "warning")
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        db.session.delete(patient.user)
        db.session.commit()

        msg = "تم حذف حساب البوابة الإلكترونية للمريض بنجاح." if is_ar else "Portal account access deleted successfully."
        flash(msg, "success")
        return redirect(url_for("patients.patient_detail", patient_id=patient.id))

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to delete portal account for patient_id={patient_id}")
        msg = "فشل حذف حساب البوابة الإلكترونية." if is_ar else "Failed to delete portal account."
        flash(msg, "danger")
        return redirect(url_for("patients.patient_detail", patient_id=patient_id))


@patients_bp.route("/patients/<int:patient_id>/files/upload", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def upload_patient_file(patient_id):
    import os
    import uuid
    from werkzeug.utils import secure_filename
    
    patient = Patient.query.get_or_404(patient_id)
    
    if "file" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("patients.patient_detail", patient_id=patient_id, tab="files"))
        
    file = request.files["file"]
    notes = request.form.get("notes", "").strip()
    
    if file.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for("patients.patient_detail", patient_id=patient_id, tab="files"))
        
    if file:
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt'}
        if file_ext not in ALLOWED_EXTENSIONS:
            flash("Invalid file type. Only images, PDFs, documents, spreadsheets, and text files are allowed.", "danger")
            return redirect(url_for("patients.patient_detail", patient_id=patient_id, tab="files"))
            
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        upload_dir = os.path.join(current_app.static_folder, "uploads", "patients")
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, unique_filename)
        file.save(filepath)
        
        relative_path = f"uploads/patients/{unique_filename}"
        
        new_file = PatientFile(
            patient_id=patient_id,
            filename=filename,
            filepath=relative_path,
            filetype=file.content_type,
            notes=notes
        )
        
        try:
            db.session.add(new_file)
            db.session.commit()
            flash("File uploaded successfully.", "success")
        except Exception:
            db.session.rollback()
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass
            current_app.logger.exception("Failed to save PatientFile to database")
            flash("Failed to save file metadata to database.", "danger")
            
        return redirect(url_for("patients.patient_detail", patient_id=patient_id, tab="files"))


@patients_bp.route("/patients/<int:patient_id>/files/<int:file_id>/delete", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def delete_patient_file(patient_id, file_id):
    import os
    
    patient = Patient.query.get_or_404(patient_id)
    patient_file = PatientFile.query.get_or_404(file_id)
    
    if patient_file.patient_id != patient.id:
        flash("Unauthorized operation.", "danger")
        return redirect(url_for("patients.patient_detail", patient_id=patient_id, tab="files"))
        
    disk_path = os.path.join(current_app.static_folder, patient_file.filepath)
    if os.path.exists(disk_path):
        try:
            os.remove(disk_path)
        except Exception:
            current_app.logger.exception(f"Failed to remove file from disk: {disk_path}")
            
    try:
        db.session.delete(patient_file)
        db.session.commit()
        flash("File deleted successfully.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to delete PatientFile from database")
        flash("Failed to delete file from database.", "danger")
        
    return redirect(url_for("patients.patient_detail", patient_id=patient_id, tab="files"))


@patients_bp.route("/api/patients/<int:patient_id>/fdi-chart", methods=["GET"])
@role_required("admin", "doctor", "receptionist")
def get_patient_fdi_chart_api(patient_id):
    """Returns compact JSON of patient tooth history and clinic treatments for dynamic FDI chart loading."""
    from collections import defaultdict
    patient = Patient.query.get_or_404(patient_id)

    tooth_histories = ToothHistory.query.filter_by(patient_id=patient.id).order_by(ToothHistory.created_at.desc()).all()
    history_dict = defaultdict(list)
    for th in tooth_histories:
        history_dict[str(th.tooth_number)].append({
            "id": th.id,
            "procedure": th.procedure_type,
            "notes": th.notes or "",
            "history_date": th.history_date.strftime("%Y-%m-%d") if th.history_date else None,
            "created_at": th.created_at.strftime("%Y-%m-%d %I:%M %p") if th.created_at else (th.history_date.strftime("%Y-%m-%d") if th.history_date else "")
        })

    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient.id,
        Appointment.status != "Cancelled"
    ).all()

    treatments_dict = defaultdict(list)
    for tr in treatments:
        if tr.tooth_number:
            treatments_dict[str(tr.tooth_number)].append({
                "id": tr.id,
                "procedure": tr.procedure_type,
                "notes": tr.notes or "",
                "date": tr.treatment_date.strftime("%Y-%m-%d") if tr.treatment_date else "",
                "cost": float(tr.total_cost or 0)
            })

    return jsonify({
        "success": True,
        "patient_id": patient.id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "tooth_history": dict(history_dict),
        "clinic_treatments": dict(treatments_dict)
    })
