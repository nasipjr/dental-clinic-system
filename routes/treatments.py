from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, session, jsonify

from models import db, Appointment, Treatment, ToothHistory, TreatmentPlanItem, Invoice
from services.invoice_service import sync_invoice_for_appointment
from services.payment_service import allocate_patient_payments_to_invoices
from utils.constants import TREATMENT_PRICES, TREATMENT_PROCEDURE_TYPES, get_equivalent_tooth_numbers
from utils.auth_helper import role_required, get_safe_redirect_url
from utils.settings_helper import get_setting, get_treatment_prices, get_treatment_details, get_anesthesia_types


treatments_bp = Blueprint("treatments", __name__)


@treatments_bp.route("/appointments/<int:appointment_id>/session")
@role_required("admin", "doctor")
def appointment_session(appointment_id):
    current_app.logger.info(f"Appointment session opened | appointment_id={appointment_id}")

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        from flask import session
        user_id = session.get("user_id")
        user_role = session.get("role")

        # Doctor users can only open session for their own appointments
        if user_role == "doctor" and appointment.doctor_id and appointment.doctor_id != user_id:
            return render_template(
                "error_message.html",
                title="Unauthorized",
                message="عفواً، لا يمكنك فتح جلسة علاج لموعد مخصص لطبيب آخر.",
                back_url=url_for("appointments.view_appointment", appointment_id=appointment.id),
            ), 403

        # Cancelled appointments redirect to view appointment read-only for non-admin users
        if user_role != "admin" and appointment.status == "Cancelled":
            return redirect(url_for("appointments.view_appointment", appointment_id=appointment.id))

        # Mark the session as opened so the auto-cancel job won't cancel it,
        # even if more than one hour has passed since the appointment time.
        if user_role in ("doctor", "admin") and user_id and not appointment.doctor_id:
            appointment.doctor_id = user_id

        from datetime import datetime
        now = datetime.now()

        # If opening a session for a scheduled appointment whose date is not today,
        # sync its appointment date to NOW so session, treatments, and appointments share the exact same date!
        if appointment.status == "Scheduled":
            if appointment.appointment_date and appointment.appointment_date.date() != now.date():
                appointment.appointment_date = now

            if appointment.session_opened_at is None:
                appointment.session_opened_at = now
            
        db.session.commit()

        treatments = (
            Treatment.query
            .filter_by(appointment_id=appointment.id)
            .order_by(Treatment.id.desc())
            .all()
        )

        previous_treatments = (
            Treatment.query
            .join(Appointment)
            .filter(
                Appointment.patient_id == appointment.patient_id,
                Appointment.status != "Cancelled",
                Treatment.appointment_id != appointment.id
            )
            .order_by(Treatment.treatment_date.desc(), Treatment.id.desc())
            .all()
        )

        total_cost_sum = appointment.invoice_total
        total_paid_sum = appointment.total_paid
        total_remaining_sum = appointment.balance
        credit_amount = appointment.credit

        tooth_histories = ToothHistory.query.filter_by(patient_id=appointment.patient_id).order_by(ToothHistory.created_at.desc()).all()
        tooth_history_dict = {}
        for th in tooth_histories:
            tn = str(th.tooth_number)
            if tn not in tooth_history_dict:
                tooth_history_dict[tn] = []
            tooth_history_dict[tn].append({
                "id": th.id,
                "procedure": th.procedure_type,
                "notes": th.notes or "",
                "history_date": th.history_date.strftime("%Y-%m-%d") if th.history_date else None,
                "created_at": th.created_at.strftime("%Y-%m-%d %I:%M %p") if th.created_at else (th.history_date.strftime("%Y-%m-%d") if th.history_date else "")
            })

        planned_items = TreatmentPlanItem.query.filter_by(patient_id=appointment.patient_id, status="Planned").order_by(TreatmentPlanItem.id.desc()).all()
        planned_teeth_dict = {}
        for pi in planned_items:
            tn = str(pi.tooth_number)
            if tn not in planned_teeth_dict:
                planned_teeth_dict[tn] = []
            planned_teeth_dict[tn].append({
                "id": pi.id,
                "procedure": pi.procedure_type,
                "cost": float(pi.estimated_cost or 0),
                "notes": pi.notes or "",
                "created_at": pi.created_at.strftime("%Y-%m-%d") if pi.created_at else ""
            })

        return render_template(
            "appointments/appointment_session.html",
            appointment=appointment,
            patient=appointment.patient,
            treatments=treatments,
            total_cost_sum=total_cost_sum,
            total_paid_sum=total_paid_sum,
            total_remaining_sum=total_remaining_sum,
            credit_amount=credit_amount,
            previous_treatments=previous_treatments,
            treatment_prices=get_treatment_prices(),
            treatment_details=get_treatment_details(),
            anesthesia_types=get_anesthesia_types(),
            treatment_procedure_types=list(TREATMENT_PROCEDURE_TYPES),
            tooth_history_dict=tooth_history_dict,
            planned_teeth_dict=planned_teeth_dict,
            anesthesia_needle_price=float(get_setting("anesthesia_needle_price", 50000)),
        )

    except Exception:
        current_app.logger.exception(
            f"Failed to open appointment session | appointment_id={appointment_id}"
        )
        is_ar = request.cookies.get("lang", "ar") != "en"
        return render_template(
            "error_message.html",
            title="خطأ في النظام" if is_ar else "System Error",
            message="فشل في فتح جلسة الموعد العلاجية." if is_ar else "Failed to open appointment session.",
            back_url=url_for("appointments.appointments"),
        ), 500



@treatments_bp.route("/appointments/<int:appointment_id>/treatments/add", methods=["GET", "POST"])
@role_required("admin", "doctor")
def add_treatment_to_appointment(appointment_id):
    current_app.logger.info(f"Add treatment to appointment | appointment_id={appointment_id}")

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status != "Scheduled":
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message="Cannot add treatment because this appointment session is closed or cancelled.",
                back_url=url_for("treatments.appointment_session", appointment_id=appointment.id),
            ), 403

        if request.method == "POST":
            from datetime import datetime
            now = datetime.now()
            treatment_date = now
            if appointment.appointment_date and appointment.appointment_date > now:
                appointment.appointment_date = now
            procedure_type = request.form.get("procedure_type", "").strip()

            if not procedure_type:
                return render_template(
                    "treatments/add_treatment.html",
                    appointment=appointment,
                    patient=appointment.patient,
                    treatment_prices=dict(TREATMENT_PRICES),
                    error_message="Treatment procedure type is required.",
                ), 400

            tooth_number = request.form.get("tooth_number", "").strip()
            if len(tooth_number) > 50:
                return render_template(
                    "treatments/add_treatment.html",
                    appointment=appointment,
                    patient=appointment.patient,
                    treatment_prices=dict(TREATMENT_PRICES),
                    error_message="Tooth number cannot exceed 50 characters.",
                ), 400

            notes = request.form.get("notes", "").strip()

            # Calculate cost multiplied by the number of teeth selected
            teeth_list = [t.strip() for t in tooth_number.split(',') if t.strip()]
            num_teeth = len(teeth_list) if teeth_list else 1

            # Check extraction rule (prior or clinic extraction)
            proc_lower = (procedure_type or "").lower()
            is_post_ext = "ما بعد القلع" in proc_lower or "post-extraction" in proc_lower or "post extraction" in proc_lower
            if not is_post_ext:
                for t in teeth_list:
                    check_teeth = get_equivalent_tooth_numbers(t)

                    has_prior_ext = ToothHistory.query.filter(
                        ToothHistory.patient_id == appointment.patient_id,
                        ToothHistory.tooth_number.in_(check_teeth),
                        (ToothHistory.procedure_type.ilike("%قلع%") | ToothHistory.procedure_type.ilike("%extract%"))
                    ).first()

                    has_clinic_ext = Treatment.query.join(Treatment.appointment).filter(
                        Appointment.patient_id == appointment.patient_id,
                        Appointment.status != "Cancelled",
                        Treatment.tooth_number.in_(check_teeth),
                        (Treatment.procedure_type.ilike("%قلع%") | Treatment.procedure_type.ilike("%extract%"))
                    ).first()

                    if has_prior_ext or has_clinic_ext:
                        err_msg = f"السن {t} مقلوع سابقاً أو في العيادة. لا يمكن إضافة معالجة عليه سوى (معالجة ما بعد القلع)." if request.cookies.get("lang") == "ar" else f"Tooth {t} is extracted. Only post-extraction care can be added."
                        return render_template(
                            "treatments/add_treatment.html",
                            appointment=appointment,
                            patient=appointment.patient,
                            treatment_prices=dict(TREATMENT_PRICES),
                            error_message=err_msg,
                        ), 400
            
            use_anesthesia = request.form.get("use_anesthesia") == "on"
            anesthesia_needles = int(request.form.get("anesthesia_needles", 0)) if use_anesthesia else 0
            anesthesia_type_val = request.form.get("anesthesia_type", "").strip() if use_anesthesia else None
            
            if use_anesthesia:
                needle_p = None
                if anesthesia_type_val:
                    for at in get_anesthesia_types():
                        if at.get("name") == anesthesia_type_val:
                            try:
                                needle_p = float(at.get("price", 50000))
                            except (ValueError, TypeError):
                                needle_p = 50000.0
                            break
                if needle_p is None:
                    needle_p = float(get_setting("anesthesia_needle_price", 50000))
                anesthesia_cost = anesthesia_needles * needle_p
            else:
                anesthesia_cost = 0.0
                
            custom_cost_str = request.form.get("custom_cost") or request.form.get("total_cost")
            if custom_cost_str is not None and str(custom_cost_str).strip() != "":
                try:
                    total_cost = float(str(custom_cost_str).strip().replace(",", ""))
                    if total_cost < 0:
                        total_cost = 0.0
                except ValueError:
                    unit_p = float(get_treatment_prices().get(procedure_type, TREATMENT_PRICES.get(procedure_type, 0.0)))
                    total_cost = (unit_p * num_teeth) + anesthesia_cost
            else:
                unit_p = float(get_treatment_prices().get(procedure_type, TREATMENT_PRICES.get(procedure_type, 0.0)))
                total_cost = (unit_p * num_teeth) + anesthesia_cost

            treating_doctor_id = None
            from flask import g
            if g.get("current_user") and g.current_user.role in ("doctor", "admin"):
                treating_doctor_id = g.current_user.id
            elif appointment.doctor_id:
                treating_doctor_id = appointment.doctor_id

            new_treatment = Treatment(
                appointment_id=appointment.id,
                treatment_date=treatment_date,
                procedure_type=procedure_type,
                tooth_number=tooth_number,
                notes=notes,
                total_cost=total_cost,
                use_anesthesia=use_anesthesia,
                anesthesia_needles=anesthesia_needles,
                anesthesia_cost=anesthesia_cost,
                anesthesia_type=anesthesia_type_val,
                doctor_id=treating_doctor_id,
            )

            db.session.add(new_treatment)
            if treating_doctor_id:
                appointment.doctor_id = treating_doctor_id
            db.session.flush()

            sync_invoice_for_appointment(appointment)
            allocate_patient_payments_to_invoices(appointment.patient_id)

            db.session.commit()

            current_app.logger.info(
                f"Treatment added successfully | treatment_id={new_treatment.id}, appointment_id={appointment.id}"
            )

            return redirect(
                url_for("treatments.appointment_session", appointment_id=appointment.id)
            )

        treatments = Treatment.query.filter_by(appointment_id=appointment.id).all()
        previous_treatments = (
            Treatment.query.join(Appointment)
            .filter(
                Appointment.patient_id == appointment.patient_id,
                Appointment.id != appointment.id,
            )
            .order_by(Treatment.treatment_date.desc(), Treatment.id.desc())
            .all()
        )

        return render_template(
            "treatments/add_treatment.html",
            appointment=appointment,
            patient=appointment.patient,
            treatments=treatments,
            previous_treatments=previous_treatments,
            treatment_prices=dict(TREATMENT_PRICES),
            anesthesia_needle_price=float(get_setting("anesthesia_needle_price", 50000)),
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            f"Failed to add treatment to appointment | appointment_id={appointment_id}"
        )
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to add treatment.",
            back_url=url_for("treatments.appointment_session", appointment_id=appointment_id),
        ), 500


@treatments_bp.route("/appointments/<int:appointment_id>/treatments/bulk-add", methods=["POST"])
@role_required("admin", "doctor")
def bulk_add_treatment(appointment_id):
    """AJAX endpoint: add one treatment covering multiple selected teeth at once."""
    import json
    from datetime import datetime

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status != "Scheduled":
            return jsonify({"success": False, "error": "الجلسة مغلقة أو ملغاة"}), 403

        data = request.get_json(force=True, silent=True) or {}

        procedure_type = (data.get("procedure_type") or "").strip()
        if not procedure_type:
            return jsonify({"success": False, "error": "يرجى اختيار نوع المعالجة"}), 400

        teeth_list = data.get("teeth", [])
        if not teeth_list or not isinstance(teeth_list, list):
            return jsonify({"success": False, "error": "يرجى اختيار سن واحد على الأقل"}), 400

        # Deduplicate & stringify
        teeth_list = [str(t).strip() for t in teeth_list if str(t).strip()]
        tooth_number = ", ".join(teeth_list)
        num_teeth = len(teeth_list)

        notes = (data.get("notes") or "").strip()

        # Anesthesia
        use_anesthesia = bool(data.get("use_anesthesia", False))
        anesthesia_needles = int(data.get("anesthesia_needles", 1)) if use_anesthesia else 0
        anesthesia_type_val = (data.get("anesthesia_type") or "").strip() if use_anesthesia else None

        if use_anesthesia:
            needle_p = None
            if anesthesia_type_val:
                for at in get_anesthesia_types():
                    if at.get("name") == anesthesia_type_val:
                        try:
                            needle_p = float(at.get("price", 50000))
                        except (ValueError, TypeError):
                            needle_p = 50000.0
                        break
            if needle_p is None:
                needle_p = float(get_setting("anesthesia_needle_price", 50000))
            anesthesia_cost = anesthesia_needles * needle_p
        else:
            anesthesia_cost = 0.0

        # Procedure base price & custom cost override
        custom_cost_val = data.get("custom_cost")
        if custom_cost_val is not None and str(custom_cost_val).strip() != "":
            try:
                total_cost = float(str(custom_cost_val).strip())
                if total_cost < 0:
                    total_cost = 0.0
            except ValueError:
                proc_price = float(get_treatment_prices().get(procedure_type, TREATMENT_PRICES.get(procedure_type, 0)))
                total_cost = (proc_price * num_teeth) + anesthesia_cost
        else:
            proc_price = float(get_treatment_prices().get(procedure_type, TREATMENT_PRICES.get(procedure_type, 0)))
            total_cost = (proc_price * num_teeth) + anesthesia_cost

        # Doctor
        from flask import g
        treating_doctor_id = None
        if g.get("current_user") and g.current_user.role in ("doctor", "admin"):
            treating_doctor_id = g.current_user.id
        elif appointment.doctor_id:
            treating_doctor_id = appointment.doctor_id

        now = datetime.now()
        if appointment.appointment_date and appointment.appointment_date > now:
            appointment.appointment_date = now

        new_treatment = Treatment(
            appointment_id=appointment.id,
            treatment_date=now,
            procedure_type=procedure_type,
            tooth_number=tooth_number,
            notes=notes,
            total_cost=total_cost,
            use_anesthesia=use_anesthesia,
            anesthesia_needles=anesthesia_needles,
            anesthesia_cost=anesthesia_cost,
            anesthesia_type=anesthesia_type_val,
            doctor_id=treating_doctor_id,
        )

        db.session.add(new_treatment)
        if treating_doctor_id:
            appointment.doctor_id = treating_doctor_id
        db.session.flush()

        sync_invoice_for_appointment(appointment)
        allocate_patient_payments_to_invoices(appointment.patient_id)
        db.session.commit()

        current_app.logger.info(
            f"Bulk treatment added | treatment_id={new_treatment.id}, teeth={tooth_number}, appointment_id={appointment.id}"
        )

        return jsonify({
            "success": True,
            "treatment_id": new_treatment.id,
            "teeth_count": num_teeth,
            "total_cost": total_cost,
            "redirect": url_for("treatments.appointment_session", appointment_id=appointment.id)
        })

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"bulk_add_treatment failed | appointment_id={appointment_id}")
        return jsonify({"success": False, "error": "حدث خطأ أثناء حفظ المعالجة"}), 500


@treatments_bp.route("/appointments/<int:appointment_id>/end-session", methods=["POST"])
@role_required("admin", "doctor")
def end_appointment_session(appointment_id):
    current_app.logger.info(f"End appointment session request | appointment_id={appointment_id}")
    is_ar = request.cookies.get("lang") == "ar"

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status != "Scheduled":
            if appointment.status == "Done":
                flash("تم إنهاء هذه الجلسة مسبقاً." if is_ar else "This session is already ended.", "info")
                return redirect(url_for("treatments.appointment_session", appointment_id=appointment.id))
            return render_template(
                "error_message.html",
                title="إجراء غير مسموح به" if is_ar else "Action Not Allowed",
                message="يمكن فقط إنهاء المواعيد المجدولة." if is_ar else "Only scheduled appointments can be ended.",
                back_url=url_for("treatments.appointment_session", appointment_id=appointment.id),
            ), 400

        from datetime import datetime
        now = datetime.now()

        from flask import g
        doc_id = None
        if g.get("current_user") and g.current_user.role in ("doctor", "admin"):
            doc_id = g.current_user.id
        elif appointment.doctor_id:
            doc_id = appointment.doctor_id

        # If no active treatments recorded today (e.g. only future plans or consultation),
        # automatically create a general clinical examination & consultation treatment (without specific tooth)
        existing_treatments_count = Treatment.query.filter_by(appointment_id=appointment.id).count()
        if existing_treatments_count == 0:
            current_prices = get_treatment_prices()
            consult_name = None
            for candidate in ["جلسة فحص و استشارة", "جلسة فحص واستشارة", "فحص دوري واستشارة", "فحص دوري", "Check-up", "Clinical Examination & Consultation"]:
                if candidate in current_prices:
                    consult_name = candidate
                    break
            if not consult_name:
                consult_name = "جلسة فحص و استشارة"

            exam_price = float(current_prices.get(consult_name, 50000))

            consultation_treatment = Treatment(
                appointment_id=appointment.id,
                treatment_date=appointment.appointment_date or now,
                procedure_type=consult_name,
                tooth_number=None,
                notes="جلسة فحص واستشارة سريرية وتحديد خطة العلاج" if is_ar else "Clinical Examination, Consultation & Treatment Planning",
                total_cost=exam_price,
                use_anesthesia=False,
                anesthesia_needles=0,
                anesthesia_cost=0.0,
                doctor_id=doc_id
            )
            db.session.add(consultation_treatment)
            db.session.flush()

        # Sync invoice for all treatments in the appointment
        sync_invoice_for_appointment(appointment)

        appointment.status = "Done"
        if appointment.appointment_date and appointment.appointment_date > now:
            appointment.appointment_date = now

        if doc_id:
            appointment.doctor_id = doc_id

        db.session.commit()

        current_app.logger.info(
            f"Appointment session ended successfully | appointment_id={appointment.id}"
        )
        flash("تم إنهاء الجلسة بنجاح وتوليد فاتورة الجلسة." if is_ar else "Session ended successfully with invoice generated.", "success")

        return redirect(
            url_for("treatments.appointment_session", appointment_id=appointment.id)
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            f"Failed to end appointment session | appointment_id={appointment_id}"
        )
        return render_template(
            "error_message.html",
            title="خطأ" if is_ar else "Error",
            message="فشل إنهاء جلسة الموعد." if is_ar else "Failed to end appointment session.",
            back_url=url_for("treatments.appointment_session", appointment_id=appointment_id),
        ), 500


@treatments_bp.route("/appointments/<int:appointment_id>/discard-quick-session", methods=["POST", "GET"])
@role_required("admin", "doctor", "receptionist")
def discard_quick_session(appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        patient_id = appointment.patient_id
        if not appointment.treatments and not appointment.invoice:
            db.session.delete(appointment)
            db.session.commit()
            flash("تم التراجع عن الجلسة السريعة بنجاح." if request.cookies.get("lang") == "ar" else "Quick session discarded.", "info")
        return redirect(url_for("patients.patient_detail", patient_id=patient_id))
    except Exception:
        db.session.rollback()
        return redirect(url_for("appointments.appointments"))


@treatments_bp.route("/appointments/<int:appointment_id>/reopen-session", methods=["POST"])
@role_required("admin")
def reopen_appointment_session(appointment_id):
    current_app.logger.info(f"Reopen appointment session request | appointment_id={appointment_id}")
    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status != "Done":
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message="Only completed appointments can be reopened.",
                back_url=url_for("treatments.appointment_session", appointment_id=appointment.id),
            ), 400

        appointment.status = "Scheduled"
        db.session.commit()

        current_app.logger.info(
            f"Appointment session reopened successfully | appointment_id={appointment.id}"
        )

        return redirect(
            url_for("treatments.appointment_session", appointment_id=appointment.id)
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            f"Failed to reopen appointment session | appointment_id={appointment_id}"
        )
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to reopen appointment session.",
            back_url=url_for("treatments.appointment_session", appointment_id=appointment_id),
        ), 500


@treatments_bp.route("/patients/<int:patient_id>/treatments/add")
@role_required("admin", "doctor")
def add_treatment(patient_id):
    current_app.logger.warning(
        f"Legacy add treatment route opened | patient_id={patient_id}"
    )

    return (
        "Treatments must be added from an appointment session.",
        400,
    )


@treatments_bp.route("/treatments/<int:treatment_id>/edit", methods=["GET", "POST"])
@role_required("admin", "doctor")
def edit_treatment(treatment_id):
    current_app.logger.info(f"Edit treatment page/request | treatment_id={treatment_id}")

    try:
        treatment = Treatment.query.get_or_404(treatment_id)

        if treatment.appointment.status in ("Cancelled", "ملغي") and request.method == "POST":
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message="Cannot edit this treatment because the appointment is cancelled.",
                back_url=url_for(
                    "treatments.appointment_session",
                    appointment_id=treatment.appointment_id,
                ),
            ), 403

        if request.method == "POST":
            delete_action = request.form.get("delete_action") == "1"
            if delete_action:
                appointment = treatment.appointment
                appointment_id = treatment.appointment_id
                patient_id = appointment.patient_id

                db.session.delete(treatment)
                db.session.flush()

                sync_invoice_for_appointment(appointment)
                allocate_patient_payments_to_invoices(patient_id)
                db.session.commit()

                current_app.logger.info(
                    f"Treatment deleted via edit form deselect | treatment_id={treatment_id}"
                )
                from flask import flash
                is_ar = request.cookies.get("lang", "ar") == "ar"
                flash("تم إلغاء وحذف المعالجة وتحديث الفاتورة بنجاح!" if is_ar else "Treatment deleted and invoice updated successfully!", "success")
                return redirect(
                    url_for(
                        "treatments.appointment_session",
                        appointment_id=appointment_id,
                    )
                )

            treatment.treatment_date = treatment.appointment.appointment_date

            procedure_type = request.form.get("procedure_type", "").strip()

            if procedure_type not in TREATMENT_PROCEDURE_TYPES:
                return render_template(
                    "treatments/edit_treatment.html",
                    treatment=treatment,
                    appointment=treatment.appointment,
                    patient=treatment.appointment.patient,
                    mode="edit",
                    treatment_prices=dict(TREATMENT_PRICES),
                    anesthesia_types=get_anesthesia_types(),
                    error_message="Invalid treatment procedure type.",
                ), 400

            tooth_number = request.form.get("tooth_number", "").strip()
            if len(tooth_number) > 50:
                return render_template(
                    "treatments/edit_treatment.html",
                    treatment=treatment,
                    appointment=treatment.appointment,
                    patient=treatment.appointment.patient,
                    mode="edit",
                    treatment_prices=dict(TREATMENT_PRICES),
                    anesthesia_types=get_anesthesia_types(),
                    error_message="Tooth number cannot exceed 50 characters.",
                ), 400

            treatment.procedure_type = procedure_type
            treatment.tooth_number = tooth_number
            treatment.notes = request.form.get("notes", "").strip()
            
            # Calculate cost multiplied by the number of teeth selected
            teeth_list = [t.strip() for t in tooth_number.split(',') if t.strip()]
            num_teeth = len(teeth_list) if teeth_list else 1
            
            use_anesthesia = request.form.get("use_anesthesia") == "on"
            anesthesia_needles = int(request.form.get("anesthesia_needles", 0)) if use_anesthesia else 0
            anesthesia_type_val = request.form.get("anesthesia_type", "").strip() if use_anesthesia else None
            
            if use_anesthesia:
                needle_p = None
                if anesthesia_type_val:
                    for at in get_anesthesia_types():
                        if at.get("name") == anesthesia_type_val:
                            try:
                                needle_p = float(at.get("price", 50000))
                            except (ValueError, TypeError):
                                needle_p = 50000.0
                            break
                if needle_p is None:
                    needle_p = float(get_setting("anesthesia_needle_price", 50000))
                anesthesia_cost = anesthesia_needles * needle_p
            else:
                anesthesia_cost = 0.0
                
            doctor_id_str = request.form.get("doctor_id")
            if doctor_id_str:
                try:
                    doc_id = int(doctor_id_str)
                    treatment.doctor_id = doc_id
                    treatment.appointment.doctor_id = doc_id
                except ValueError:
                    pass

            treatment.use_anesthesia = use_anesthesia
            treatment.anesthesia_needles = anesthesia_needles
            treatment.anesthesia_cost = anesthesia_cost
            treatment.anesthesia_type = anesthesia_type_val

            custom_cost_str = request.form.get("custom_cost") or request.form.get("total_cost")
            if custom_cost_str is not None and str(custom_cost_str).strip() != "":
                try:
                    total_cost = float(str(custom_cost_str).strip().replace(",", ""))
                    if total_cost < 0:
                        total_cost = 0.0
                except ValueError:
                    unit_p = float(get_treatment_prices().get(procedure_type, TREATMENT_PRICES.get(procedure_type, 0.0)))
                    total_cost = (unit_p * num_teeth) + anesthesia_cost
            else:
                unit_p = float(get_treatment_prices().get(procedure_type, TREATMENT_PRICES.get(procedure_type, 0.0)))
                total_cost = (unit_p * num_teeth) + anesthesia_cost

            treatment.total_cost = total_cost

            db.session.flush()

            sync_invoice_for_appointment(treatment.appointment)
            allocate_patient_payments_to_invoices(treatment.appointment.patient_id)

            db.session.commit()

            current_app.logger.info(
                f"Treatment updated successfully | treatment_id={treatment.id}"
            )

            return redirect(
                get_safe_redirect_url(
                    "treatments.appointment_session",
                    appointment_id=treatment.appointment_id,
                )
            )

        from models import User
        doctors = User.query.filter(User.role.in_(["doctor", "admin"])).all()

        treatments = Treatment.query.filter_by(appointment_id=treatment.appointment_id).all()
        previous_treatments = (
            Treatment.query.join(Appointment)
            .filter(
                Appointment.patient_id == treatment.appointment.patient_id,
                Appointment.id != treatment.appointment_id,
            )
            .order_by(Treatment.treatment_date.desc(), Treatment.id.desc())
            .all()
        )

        tooth_histories = ToothHistory.query.filter_by(patient_id=treatment.appointment.patient_id).order_by(ToothHistory.created_at.desc()).all()
        tooth_history_dict = {}
        for th in tooth_histories:
            tn = str(th.tooth_number)
            if tn not in tooth_history_dict:
                tooth_history_dict[tn] = []
            tooth_history_dict[tn].append({
                "id": th.id,
                "procedure": th.procedure_type,
                "notes": th.notes or "",
                "history_date": th.history_date.strftime("%Y-%m-%d") if th.history_date else None,
                "created_at": th.created_at.strftime("%Y-%m-%d %I:%M %p") if th.created_at else (th.history_date.strftime("%Y-%m-%d") if th.history_date else "")
            })

        return render_template(
            "treatments/edit_treatment.html",
            treatment=treatment,
            appointment=treatment.appointment,
            patient=treatment.appointment.patient,
            doctors=doctors,
            mode="edit",
            treatments=treatments,
            previous_treatments=previous_treatments,
            treatment_prices=dict(TREATMENT_PRICES),
            anesthesia_types=get_anesthesia_types(),
            tooth_history_dict=tooth_history_dict,
            anesthesia_needle_price=float(get_setting("anesthesia_needle_price", 50000)),
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to edit treatment | treatment_id={treatment_id}")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to edit treatment.",
            back_url=url_for("appointments.appointments"),
        ), 500


@treatments_bp.route("/treatments/<int:treatment_id>/view")
@role_required("admin", "doctor", "receptionist")
def view_treatment(treatment_id):
    current_app.logger.info(f"View treatment page opened | treatment_id={treatment_id}")

    try:
        treatment = Treatment.query.get_or_404(treatment_id)

        treatments = Treatment.query.filter_by(appointment_id=treatment.appointment_id).all()
        previous_treatments = (
            Treatment.query.join(Appointment)
            .filter(
                Appointment.patient_id == treatment.appointment.patient_id,
                Appointment.id != treatment.appointment_id,
            )
            .order_by(Treatment.treatment_date.desc(), Treatment.id.desc())
            .all()
        )

        return render_template(
            "treatments/edit_treatment.html",
            treatment=treatment,
            appointment=treatment.appointment,
            patient=treatment.appointment.patient,
            mode="view",
            treatments=treatments,
            previous_treatments=previous_treatments,
            treatment_prices=dict(TREATMENT_PRICES),
            anesthesia_types=get_anesthesia_types(),
            anesthesia_needle_price=float(get_setting("anesthesia_needle_price", 50000)),
        )

    except Exception:
        current_app.logger.exception(f"Failed to view treatment | treatment_id={treatment_id}")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to view treatment.",
            back_url=url_for("appointments.appointments"),
        ), 500


@treatments_bp.route("/treatments/<int:treatment_id>/delete", methods=["GET", "POST"])
@role_required("admin", "doctor")
def delete_treatment(treatment_id):
    current_app.logger.warning(f"Delete treatment page/request | treatment_id={treatment_id}")

    try:
        treatment = Treatment.query.get_or_404(treatment_id)
        appointment = treatment.appointment
        appointment_id = treatment.appointment_id
        patient_id = treatment.appointment.patient_id

        if treatment.appointment.status != "Scheduled":
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message="Cannot delete this treatment because the appointment session is closed or cancelled.",
                back_url=url_for("treatments.appointment_session", appointment_id=appointment_id),
            ), 403

        if request.method == "POST":
            db.session.delete(treatment)
            db.session.flush()

            sync_invoice_for_appointment(appointment)
            allocate_patient_payments_to_invoices(patient_id)

            db.session.commit()

            current_app.logger.info(
                f"Treatment deleted successfully | treatment_id={treatment_id}"
            )
            return redirect(
                get_safe_redirect_url("treatments.appointment_session", appointment_id=appointment_id)
            )

        return render_template("treatments/delete_treatment.html", treatment=treatment)

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to delete treatment | treatment_id={treatment_id}")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to delete treatment.",
            back_url=url_for("appointments.appointments"),
        ), 500


@treatments_bp.route("/appointments/<int:appointment_id>/revert-session", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def revert_session(appointment_id):
    current_app.logger.info(f"Reverting opened session | appointment_id={appointment_id}")
    is_ar = request.cookies.get('lang', 'ar') != 'en'

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        # Check if treatments were added during this session
        treatments_count = Treatment.query.filter_by(appointment_id=appointment.id).count()
        if treatments_count > 0:
            msg = "لا يمكن التراجع عن فتح الجلسة لأنها تحتوي على معالجات مسجلة. يرجى حذف المعالجات أولاً." if is_ar else "Cannot undo session start because treatments are already recorded. Delete treatments first."
            flash(msg, "warning")
            return redirect(url_for("treatments.appointment_session", appointment_id=appointment.id))

        patient_id = appointment.patient_id

        # If this was a Quick Session and has no treatments/invoice, DELETE it completely so no ghost appointment is left!
        if appointment.reason in ("جلسة جديدة سريعة", "Quick Session") and not appointment.invoice:
            db.session.delete(appointment)
            db.session.commit()
            msg = "تم التراجع عن الجلسة السريعة وإلغاؤها بالكامل بنجاح." if is_ar else "Quick session undone and completely removed."
            flash(msg, "info")
            return redirect(url_for("patients.patient_detail", patient_id=patient_id))

        # Reset session_opened_at and ensure status stays Scheduled
        appointment.session_opened_at = None
        appointment.status = "Scheduled"
        
        db.session.commit()

        msg = "تم التراجع عن فتح الجلسة وإعادة الموعد لحالة 'مجدول' بنجاح." if is_ar else "Session start undone. Appointment status returned to Scheduled."
        flash(msg, "success")
        target_url = request.referrer if (request.referrer and "/session" not in request.referrer) else url_for("patients.patient_detail", patient_id=patient_id)
        return redirect(target_url)

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to revert session for appointment_id={appointment_id}")
        msg = "حدث خطأ أثناء التراجع عن فتح الجلسة." if is_ar else "An error occurred while undoing session start."
        flash(msg, "danger")
        return redirect(url_for("appointments.appointments"))


@treatments_bp.route("/treatments/types/quick-add", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def quick_add_treatment_type():
    current_app.logger.info("Quick add treatment type requested")
    is_ar = request.cookies.get("lang") != "en" and session.get("lang") != "en"
    try:
        data = request.get_json(silent=True)
        if not data:
            data = request.form or {}
        name = (data.get("name") or "").strip()
        price_raw = str(data.get("price") or 0).strip().replace(",", "")
        duration_raw = str(data.get("duration") or 30).strip()
        category = (data.get("category") or "إجراءات عامة وأخرى").strip()

        if not name:
            msg = "يرجى كتابة اسم الإجراء." if is_ar else "Procedure name is required."
            return jsonify({"success": False, "message": msg}), 400

        try:
            price_val = float(price_raw) if '.' in price_raw else int(price_raw)
            if price_val < 0:
                price_val = 0
        except ValueError:
            price_val = 0

        try:
            duration_val = int(duration_raw)
            if duration_val <= 0:
                duration_val = 30
        except ValueError:
            duration_val = 30

        from utils.settings_helper import get_treatment_details, set_setting
        import json

        current_details = get_treatment_details()
        current_details[name] = {
            "price": price_val,
            "duration": duration_val,
            "active": True,
            "category": category
        }

        set_setting("treatment_prices", json.dumps(current_details, ensure_ascii=False))

        msg = "تمت إضافة الخدمة الجديدة بنجاح." if is_ar else "New service added successfully."
        return jsonify({
            "success": True,
            "message": msg,
            "service": {
                "name": name,
                "price": price_val,
                "duration": duration_val,
                "active": True,
                "category": category
            }
        })
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to quick add treatment type")
        msg = "حدث خطأ أثناء إضافة الخدمة." if is_ar else "Failed to add service."
        return jsonify({"success": False, "message": msg}), 500


@treatments_bp.route("/appointments/<int:appointment_id>/treatment-plans/<int:plan_id>/execute", methods=["POST"])
@role_required("admin", "doctor")
def execute_treatment_plan_item(appointment_id, plan_id):
    current_app.logger.info(f"Execute treatment plan item into session | appt_id={appointment_id}, plan_id={plan_id}")
    is_ar = request.cookies.get("lang", "ar") != "en"

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        if appointment.status != "Scheduled":
            flash("لا يمكن تنفيذ إجراء في جلسة مغلقة أو ملغاة." if is_ar else "Cannot execute plan in a closed session.", "danger")
            return redirect(url_for("treatments.appointment_session", appointment_id=appointment.id))

        plan_item = TreatmentPlanItem.query.filter_by(id=plan_id, patient_id=appointment.patient_id).first_or_404()

        from datetime import datetime
        now = datetime.now()

        # Check extraction rule
        proc_lower = (plan_item.procedure_type or "").lower()
        is_post_ext = "ما بعد القلع" in proc_lower or "post-extraction" in proc_lower or "post extraction" in proc_lower
        if not is_post_ext:
            check_teeth = get_equivalent_tooth_numbers(plan_item.tooth_number)

            has_ext = ToothHistory.query.filter(
                ToothHistory.patient_id == appointment.patient_id,
                ToothHistory.tooth_number.in_(check_teeth),
                (ToothHistory.procedure_type.ilike("%قلع%") | ToothHistory.procedure_type.ilike("%extract%"))
            ).first() or Treatment.query.join(Treatment.appointment).filter(
                Appointment.patient_id == appointment.patient_id,
                Appointment.status != "Cancelled",
                Treatment.tooth_number.in_(check_teeth),
                (Treatment.procedure_type.ilike("%قلع%") | Treatment.procedure_type.ilike("%extract%"))
            ).first()

            if has_ext:
                flash(f"السن {plan_item.tooth_number} مقلوع. لا يمكن تنفيذ أي معالجة عليه سوى (معالجة ما بعد القلع)." if is_ar else f"Tooth {plan_item.tooth_number} is extracted. Only post-extraction care can be added.", "danger")
                return redirect(url_for("treatments.appointment_session", appointment_id=appointment.id))

        final_cost = float(plan_item.estimated_cost or 0)
        if final_cost <= 0:
            prices = get_treatment_prices()
            final_cost = float(prices.get(plan_item.procedure_type, 0))

        from flask import session as flask_session
        user_id = flask_session.get("user_id")

        note_prefix = "تم التنفيذ من خطة العلاج المقترحة." if is_ar else "Executed from treatment plan."
        full_note = f"{note_prefix} {plan_item.notes or ''}".strip()

        new_treatment = Treatment(
            appointment_id=appointment.id,
            treatment_date=now,
            procedure_type=plan_item.procedure_type,
            tooth_number=plan_item.tooth_number,
            notes=full_note,
            total_cost=final_cost,
            doctor_id=user_id if flask_session.get("role") in ("doctor", "admin") else appointment.doctor_id
        )
        db.session.add(new_treatment)
        db.session.flush()

        # Mark plan item as Completed
        plan_item.status = "Completed"
        plan_item.completed_at = now
        plan_item.completed_treatment_id = new_treatment.id

        # Create/sync invoice
        if not appointment.invoice:
            invoice = Invoice(
                appointment_id=appointment.id,
                patient_id=appointment.patient_id,
                issue_date=now,
                discount=0.00,
                additional_charges=0.00,
                notes="Invoice generated from treatment session."
            )
            db.session.add(invoice)

        db.session.commit()

        flash("تم تحويل الإجراء المخطط وتنفيذه في جلسة اليوم بنجاح!" if is_ar else "Plan executed into today's session successfully!", "success")
        return redirect(url_for("treatments.appointment_session", appointment_id=appointment.id))

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to execute treatment plan item | id={plan_id}")
        flash("حدث خطأ أثناء تنفيذ خطة العلاج." if is_ar else "Failed to execute treatment plan.", "danger")
        return redirect(url_for("treatments.appointment_session", appointment_id=appointment_id))