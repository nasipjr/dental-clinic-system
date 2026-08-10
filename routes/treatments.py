from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash

from models import db, Appointment, Treatment, ToothHistory
from services.invoice_service import sync_invoice_for_appointment
from services.payment_service import allocate_patient_payments_to_invoices
from utils.constants import TREATMENT_PRICES, TREATMENT_PROCEDURE_TYPES
from utils.auth_helper import role_required, get_safe_redirect_url
from utils.settings_helper import get_setting


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

        if appointment.status == "Scheduled" and appointment.session_opened_at is None:
            from datetime import datetime
            appointment.session_opened_at = datetime.now()
            
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
            treatment_prices=dict(TREATMENT_PRICES),
            treatment_procedure_types=list(TREATMENT_PROCEDURE_TYPES),
            tooth_history_dict=tooth_history_dict,
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

            if procedure_type not in TREATMENT_PROCEDURE_TYPES:
                return render_template(
                    "treatments/add_treatment.html",
                    appointment=appointment,
                    patient=appointment.patient,
                    treatment_prices=dict(TREATMENT_PRICES),
                    error_message="Invalid treatment procedure type.",
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
                univ_to_fdi = {
                    '1': '18', '2': '17', '3': '16', '4': '15', '5': '14', '6': '13', '7': '12', '8': '11',
                    '9': '21', '10': '22', '11': '23', '12': '24', '13': '25', '14': '26', '15': '27', '16': '28',
                    '17': '38', '18': '37', '19': '36', '20': '35', '21': '34', '22': '33', '23': '32', '24': '31',
                    '25': '41', '26': '42', '27': '43', '28': '44', '29': '45', '30': '46', '31': '47', '32': '48'
                }
                fdi_to_univ = {v: k for k, v in univ_to_fdi.items()}

                for t in teeth_list:
                    check_teeth = [t]
                    if t in univ_to_fdi:
                        check_teeth.append(univ_to_fdi[t])
                    if t in fdi_to_univ:
                        check_teeth.append(fdi_to_univ[t])

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
            
            if use_anesthesia:
                needle_p = float(get_setting("anesthesia_needle_price", 50000))
                anesthesia_cost = anesthesia_needles * needle_p
            else:
                anesthesia_cost = 0.0
                
            custom_cost_str = request.form.get("custom_cost")
            if custom_cost_str is not None and custom_cost_str.strip() != "":
                try:
                    total_cost = float(custom_cost_str.strip())
                    if total_cost < 0:
                        total_cost = 0.0
                except ValueError:
                    total_cost = (TREATMENT_PRICES[procedure_type] * num_teeth) + anesthesia_cost
            else:
                total_cost = (TREATMENT_PRICES[procedure_type] * num_teeth) + anesthesia_cost

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


@treatments_bp.route("/appointments/<int:appointment_id>/end-session", methods=["POST"])
@role_required("admin", "doctor")
def end_appointment_session(appointment_id):
    current_app.logger.info(f"End appointment session request | appointment_id={appointment_id}")

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status != "Scheduled":
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message="Only scheduled appointments can be ended.",
                back_url=url_for("treatments.appointment_session", appointment_id=appointment.id),
            ), 400

        appointment.status = "Done"
        from datetime import datetime
        now = datetime.now()
        if appointment.appointment_date and appointment.appointment_date > now:
            appointment.appointment_date = now

        from flask import g
        if g.get("current_user") and g.current_user.role in ("doctor", "admin"):
            appointment.doctor_id = g.current_user.id
        db.session.commit()

        current_app.logger.info(
            f"Appointment session ended successfully | appointment_id={appointment.id}"
        )

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
            title="Error",
            message="Failed to end appointment session.",
            back_url=url_for("treatments.appointment_session", appointment_id=appointment_id),
        ), 500


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
            
            if use_anesthesia:
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

            custom_cost_str = request.form.get("custom_cost")
            if custom_cost_str is not None and custom_cost_str.strip() != "":
                try:
                    total_cost = float(custom_cost_str.strip())
                    if total_cost < 0:
                        total_cost = 0.0
                except ValueError:
                    total_cost = (TREATMENT_PRICES[procedure_type] * num_teeth) + anesthesia_cost
            else:
                total_cost = (TREATMENT_PRICES[procedure_type] * num_teeth) + anesthesia_cost

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

        # Reset session_opened_at and ensure status stays Scheduled
        appointment.session_opened_at = None
        appointment.status = "Scheduled"
        
        db.session.commit()

        msg = "تم التراجع عن فتح الجلسة وإعادة الموعد لحالة 'مجدول' بنجاح." if is_ar else "Session start undone. Appointment status returned to Scheduled."
        flash(msg, "success")
        target_url = request.referrer if (request.referrer and "/session" not in request.referrer) else url_for("appointments.appointments")
        return redirect(target_url)

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to revert session for appointment_id={appointment_id}")
        msg = "حدث خطأ أثناء التراجع عن فتح الجلسة." if is_ar else "An error occurred while undoing session start."
        flash(msg, "danger")
        return redirect(url_for("appointments.appointments"))