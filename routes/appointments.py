from flask import Blueprint, current_app, render_template, request, redirect, url_for, jsonify, flash, session
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload, selectinload

from models import db, Patient, Appointment, User
from utils.validators import (
    get_appointment_datetime_limits,
    parse_appointment_data,
    check_appointment_conflict,
    booking_lock,
)
from utils.auth_helper import role_required, get_safe_redirect_url
from utils.constants import TREATMENT_PRICES


appointments_bp = Blueprint("appointments", __name__)



def cancel_expired_appointments():
    try:
        from utils.settings_helper import get_setting
        from datetime import time
        minutes_str = get_setting("auto_cancel_expired_minutes", "60")
        try:
            minutes = int(minutes_str)
        except (ValueError, TypeError):
            minutes = 60

        now = datetime.now()
        today_start = datetime.combine(now.date(), time.min)

        # Auto-close open sessions (In Chair or Checked In) left open for longer than auto_close_open_session_minutes
        close_minutes_str = get_setting("auto_close_open_session_minutes", "120")
        try:
            close_minutes = int(close_minutes_str)
        except (ValueError, TypeError):
            close_minutes = 120

        if close_minutes > 0:
            session_cutoff = now - timedelta(minutes=close_minutes)
            open_sessions = Appointment.query.filter(
                Appointment.status == "Scheduled",
                Appointment.session_opened_at != None,
                Appointment.appointment_date <= now
            ).all()

            auto_closed = 0
            for appt in open_sessions:
                ref_time = appt.session_opened_at or appt.appointment_date
                if ref_time and ref_time <= session_cutoff:
                    if appt.treatments:
                        appt.status = "Done"
                    else:
                        appt.status = "Cancelled"
                    auto_closed += 1
            if auto_closed > 0:
                db.session.commit()
                current_app.logger.info(f"Auto-closed {auto_closed} open sessions inactive for over {close_minutes} minutes.")
        else:
            # If set to 0 (disabled for same day), auto-close sessions from previous days
            past_active = Appointment.query.filter(
                Appointment.status == "Scheduled",
                Appointment.appointment_date < today_start
            ).all()
            if past_active:
                for appt in past_active:
                    if appt.treatments:
                        appt.status = "Done"
                    else:
                        appt.status = "Cancelled"
                db.session.commit()

        if minutes <= 0:
            return  # Auto-cancel is disabled

        cutoff_time = now - timedelta(minutes=minutes)
        expired = Appointment.query.filter(
            Appointment.status == "Scheduled",
            Appointment.appointment_date < cutoff_time,
            Appointment.session_opened_at == None,  # noqa: E711 – skip if session was opened
        ).all()
        if expired:
            cancelled_count = 0
            for appt in expired:
                if not appt.treatments:
                    appt.status = "Cancelled"
                    cancelled_count += 1
            if cancelled_count > 0:
                db.session.commit()
                current_app.logger.info(f"Auto-cancelled {cancelled_count} expired appointments (cutoff: {minutes} mins).")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to auto-cancel expired appointments")


def schedule_expired_appointments_cleanup(app, interval_seconds=900):
    """Starts a background daemon thread that periodically cancels expired scheduled appointments."""
    import threading
    import time

    def run_cleanup_loop():
        time.sleep(10)
        while True:
            with app.app_context():
                cancel_expired_appointments()
            time.sleep(interval_seconds)

    thread = threading.Thread(target=run_cleanup_loop, daemon=True)
    thread.start()



def get_appointments_context():
    cancel_expired_appointments()
    search_query = request.args.get("search", "")
    status_filter = request.args.get("status", "")
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Auto-assign doctor to unassigned appointments ONLY if there is exactly 1 doctor in the clinic
    try:
        all_docs = User.query.filter(User.role.in_(["admin", "doctor"])).all()
        if len(all_docs) == 1:
            admin_doc = all_docs[0]
            unassigned = Appointment.query.filter(Appointment.doctor_id == None).all()
            if unassigned:
                for appt in unassigned:
                    appt.doctor_id = admin_doc.id
                db.session.commit()
    except Exception:
        db.session.rollback()

    query = Appointment.query.join(Patient).options(
        joinedload(Appointment.patient),
        joinedload(Appointment.doctor),
        joinedload(Appointment.invoice)
    )

    if search_query:
        query = query.filter(
            (Patient.first_name.ilike(f"%{search_query}%")) |
            (Patient.last_name.ilike(f"%{search_query}%")) |
            ((Patient.first_name + " " + Patient.last_name).ilike(f"%{search_query}%"))
        )

    doctor_filter = request.args.get("doctor_id", "")
    if doctor_filter:
        try:
            query = query.filter(Appointment.doctor_id == int(doctor_filter))
        except ValueError:
            pass

    query = query.filter(Appointment.status == "Scheduled")

    date_filter = request.args.get("date_filter", "").strip().lower()

    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    today_end = today_start + timedelta(days=1)
    tomorrow_end = today_start + timedelta(days=2)

    base_active = Appointment.query.filter(Appointment.status == "Scheduled")
    today_count = base_active.filter(
        Appointment.appointment_date >= today_start,
        Appointment.appointment_date < today_end
    ).count()

    tomorrow_count = base_active.filter(
        Appointment.appointment_date >= today_end,
        Appointment.appointment_date < tomorrow_end
    ).count()

    all_count = base_active.count()

    # Default to today if not specified, unless today has 0 and all has items
    if not date_filter:
        date_filter = "today" if today_count > 0 else "all"

    if date_filter == "today":
        query = query.filter(
            Appointment.appointment_date >= today_start,
            Appointment.appointment_date < today_end
        )
    elif date_filter == "tomorrow":
        query = query.filter(
            Appointment.appointment_date >= today_end,
            Appointment.appointment_date < tomorrow_end
        )

    sort_columns = {
        "id": Appointment.id,
        "patient": Patient.first_name,
        "date": Appointment.appointment_date,
        "status": Appointment.status,
        "reason": Appointment.reason,
    }

    if sort_by == "doctor":
        query = query.outerjoin(User, Appointment.doctor_id == User.id)
        sort_column = User.first_name
    else:
        sort_column = sort_columns.get(sort_by, Appointment.appointment_date)

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    has_cancelled = Appointment.query.filter(Appointment.status == "Cancelled").first() is not None

    # ── Executive Manager Report & Stats for Appointments ──
    all_appts = Appointment.query.filter(Appointment.status != "Pending").all()
    total_appts_count = len(all_appts)

    completed_count = sum(1 for appt in all_appts if appt.status == "Done")
    scheduled_count = sum(1 for appt in all_appts if appt.status == "Scheduled")
    cancelled_count = sum(1 for appt in all_appts if appt.status == "Cancelled")

    active_count = scheduled_count

    completion_rate = float((completed_count / total_appts_count * 100)) if total_appts_count > 0 else 100.0
    cancellation_rate = float((cancelled_count / total_appts_count * 100)) if total_appts_count > 0 else 0.0

    # Top 5 upcoming active appointments
    upcoming_list = [appt for appt in all_appts if appt.status == "Scheduled" and appt.appointment_date and appt.appointment_date >= now]
    top_upcoming_appointments = sorted(upcoming_list, key=lambda appt: appt.appointment_date)[:5]

    appointment_stats = {
        "all_count": total_appts_count,
        "total_appts_count": total_appts_count,
        "completed_count": completed_count,
        "active_count": active_count,
        "cancelled_count": cancelled_count,
        "completion_rate": round(completion_rate, 1),
        "cancellation_rate": round(cancellation_rate, 1),
    }

    today_appts = [appt for appt in all_appts if appt.appointment_date and today_start <= appt.appointment_date < today_end]
    today_stats = {
        "all_count": today_count,
        "active_count": sum(1 for appt in today_appts if appt.status == "Scheduled"),
        "completed_count": sum(1 for appt in today_appts if appt.status == "Done"),
        "cancelled_count": sum(1 for appt in today_appts if appt.status == "Cancelled"),
    }

    tomorrow_appts = [appt for appt in all_appts if appt.appointment_date and today_end <= appt.appointment_date < tomorrow_end]
    tomorrow_stats = {
        "all_count": tomorrow_count,
        "active_count": sum(1 for appt in tomorrow_appts if appt.status == "Scheduled"),
        "completed_count": sum(1 for appt in tomorrow_appts if appt.status == "Done"),
        "cancelled_count": sum(1 for appt in tomorrow_appts if appt.status == "Cancelled"),
    }

    # Fetch doctors for the doctor filter dropdown
    doctors_list = User.query.filter(User.role.in_(["admin", "doctor"])).order_by(User.first_name.asc()).all()

    return {
        "appointments": pagination.items,
        "pagination": pagination,
        "search_query": search_query,
        "status_filter": status_filter,
        "sort_by": sort_by,
        "order": order,
        "has_cancelled": has_cancelled,
        "date_filter": date_filter,
        "today_count": today_count,
        "tomorrow_count": tomorrow_count,
        "all_count": all_count,
        "appointment_stats": appointment_stats,
        "today_stats": today_stats,
        "tomorrow_stats": tomorrow_stats,
        "top_upcoming_appointments": top_upcoming_appointments,
        "doctors_list": doctors_list,
        "doctor_filter": doctor_filter,
        "per_page": per_page,
    }


@appointments_bp.route("/appointments")
@role_required("admin", "doctor", "receptionist")
def appointments():
    current_app.logger.info("Appointments page opened")

    try:
        tab = request.args.get("tab", "").strip()
        context = get_appointments_context()
        
        if tab == "pending":
            pending_appointments = Appointment.query.filter_by(status="Pending").order_by(Appointment.appointment_date.asc()).all()
            context["show_pending"] = True
            context["pending_appointments"] = pending_appointments
        else:
            context["show_pending"] = False

        return render_template("appointments/appointments.html", **context)

    except Exception:
        current_app.logger.exception("Error while loading appointments page")
        return "Error Loading AppointmentsPage", 500
    
@appointments_bp.route("/appointments/table")
@role_required("admin", "doctor", "receptionist")
def appointments_table():
    current_app.logger.info("Appointments table partial requested")

    try:
        context = get_appointments_context()
        return render_template("partials/_appointments_table.html", **context)

    except Exception:
        current_app.logger.exception("Error while loading appointments table")
        return "Error Loading AppointmentsTable", 500


@appointments_bp.route("/appointments/add", methods=["GET", "POST"])
@role_required("admin", "receptionist", "doctor")
def add_appointment_direct():
    current_app.logger.info("Direct add appointment page/request")
    try:
        from models import User
        doctors = User.query.filter(User.role.in_(["admin", "doctor"])).all()
        patients = Patient.query.order_by(Patient.first_name.asc(), Patient.last_name.asc()).all()
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()
        
        prefilled_date = request.args.get("date", "")
        if prefilled_date:
            prefilled_date = prefilled_date.replace("T", " ")

        if request.method == "POST":
            patient_id = request.form.get("patient_id")
            if not patient_id:
                return render_template(
                    "appointments/add_appointment.html",
                    patients=patients,
                    doctors=doctors,
                    treatment_prices=dict(TREATMENT_PRICES),
                    error_message="Patient ID is required.",
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                    prefilled_date=prefilled_date,
                ), 400

            patient = Patient.query.get_or_404(patient_id)
            appointment_data, appointment_error = parse_appointment_data(request.form)

            if appointment_error:
                return render_template(
                    "appointments/add_appointment.html",
                    patients=patients,
                    doctors=doctors,
                    treatment_prices=dict(TREATMENT_PRICES),
                    error_message=appointment_error,
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                    prefilled_date=prefilled_date,
                ), 400

            with booking_lock:
                conflict = check_appointment_conflict(
                    appointment_data["appointment_date"],
                    doctor_id=appointment_data.get("doctor_id")
                )
                if conflict:
                    lang = request.cookies.get("lang", "en")
                    if lang == "ar":
                        err_msg = f"تعارض في الموعد: يوجد موعد آخر مجدول في هذا الوقت ({conflict.appointment_date.strftime('%Y-%m-%d %I:%M %p')} للمريض {conflict.patient.first_name} {conflict.patient.last_name})."
                    else:
                        err_msg = f"Conflict: There is another scheduled appointment at this time ({conflict.appointment_date.strftime('%Y-%m-%d %I:%M %p')} for patient {conflict.patient.first_name} {conflict.patient.last_name})."
                    return render_template(
                        "appointments/add_appointment.html",
                        patients=patients,
                        doctors=doctors,
                        treatment_prices=dict(TREATMENT_PRICES),
                        error_message=err_msg,
                        appointment_min_datetime=appointment_min_datetime,
                        appointment_max_datetime=appointment_max_datetime,
                        prefilled_date=prefilled_date,
                    ), 400

                new_appointment = Appointment(
                    patient_id=patient.id,
                    appointment_date=appointment_data["appointment_date"],
                    reason=appointment_data["reason"],
                    doctor_id=appointment_data.get("doctor_id"),
                    status="Scheduled",
                )

                db.session.add(new_appointment)
                db.session.commit()

            current_app.logger.info(
                f"Appointment added successfully | appointment_id={new_appointment.id}, patient_id={patient.id}"
            )

            return redirect(get_safe_redirect_url("appointments.appointments"))

        next_url = request.args.get("next") or request.referrer or ""
        if any(k in next_url for k in ["/add", "/edit", "/delete"]):
            next_url = ""

        return render_template(
            "appointments/add_appointment.html",
            patients=patients,
            doctors=doctors,
            treatment_prices=dict(TREATMENT_PRICES),
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime,
            prefilled_date=prefilled_date,
            next_url=next_url,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to direct add appointment")
        return "Error Loading AppointmentInfo", 500


@appointments_bp.route("/patients/<int:patient_id>/appointments/add", methods=["GET", "POST"])
@role_required("admin", "receptionist", "doctor")
def add_appointment(patient_id):
    current_app.logger.info(f"Add appointment page/request | patient_id={patient_id}")

    try:
        from models import User
        doctors = User.query.filter(User.role.in_(["admin", "doctor"])).all()
        patient = Patient.query.get_or_404(patient_id)
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        if request.method == "POST":
            appointment_data, appointment_error = parse_appointment_data(request.form)

            if appointment_error:
                return render_template(
                    "appointments/add_appointment.html",
                    patient=patient,
                    doctors=doctors,
                    treatment_prices=dict(TREATMENT_PRICES),
                    error_message=appointment_error,
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                ), 400

            with booking_lock:
                conflict = check_appointment_conflict(
                    appointment_data["appointment_date"],
                    doctor_id=appointment_data.get("doctor_id")
                )
                if conflict:
                    lang = request.cookies.get("lang", "en")
                    if lang == "ar":
                        err_msg = f"تعارض في الموعد: يوجد موعد آخر مجدول في هذا الوقت ({conflict.appointment_date.strftime('%Y-%m-%d %I:%M %p')} للمريض {conflict.patient.first_name} {conflict.patient.last_name})."
                    else:
                        err_msg = f"Conflict: There is another scheduled appointment at this time ({conflict.appointment_date.strftime('%Y-%m-%d %I:%M %p')} for patient {conflict.patient.first_name} {conflict.patient.last_name})."
                    return render_template(
                        "appointments/add_appointment.html",
                        patient=patient,
                        doctors=doctors,
                        treatment_prices=dict(TREATMENT_PRICES),
                        error_message=err_msg,
                        appointment_min_datetime=appointment_min_datetime,
                        appointment_max_datetime=appointment_max_datetime,
                    ), 400

                new_appointment = Appointment(
                    patient_id=patient.id,
                    appointment_date=appointment_data["appointment_date"],
                    reason=appointment_data["reason"],
                    doctor_id=appointment_data.get("doctor_id"),
                    status="Scheduled",
                )


                db.session.add(new_appointment)
                db.session.commit()

            current_app.logger.info(
                f"Appointment added successfully | appointment_id={new_appointment.id}, patient_id={patient.id}"
            )

            return redirect(get_safe_redirect_url("patients.patient_detail", patient_id=patient.id))

        next_url = request.args.get("next") or request.referrer or ""
        if any(k in next_url for k in ["/add", "/edit", "/delete"]):
            next_url = ""

        return render_template(
            "appointments/add_appointment.html",
            patient=patient,
            doctors=doctors,
            treatment_prices=dict(TREATMENT_PRICES),
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime,
            next_url=next_url,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to add appointment | patient_id={patient_id}")
        return "Error Loading AppointmentInfo", 500


@appointments_bp.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
@role_required("admin", "receptionist", "doctor")
def edit_appointment(appointment_id):
    current_app.logger.info(f"Edit appointment page/request | appointment_id={appointment_id}")

    try:
        from models import User
        doctors = User.query.filter(User.role.in_(["admin", "doctor"])).all()
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        from flask import session
        user_id = session.get("user_id")
        user_role = session.get("role")

        if user_role == "doctor" and appointment.doctor_id and appointment.doctor_id != user_id:
            return render_template(
                "error_message.html",
                title="Unauthorized",
                message="عفواً، لا يمكنك تعديل موعد خاص بطبيب آخر.",
                back_url=url_for("appointments.view_appointment", appointment_id=appointment.id),
            ), 403

        if request.method == "POST":
            if user_role != "admin" and appointment.status != "Scheduled":
                return "Cannot edit a closed or cancelled appointment.", 403

            appointment_data, appointment_error = parse_appointment_data(request.form)

            if appointment_error:
                return render_template(
                    "appointments/edit_appointment.html",
                    appointment=appointment,
                    doctors=doctors,
                    treatment_prices=dict(TREATMENT_PRICES),
                    mode="edit",
                    error_message=appointment_error,
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                ), 400

            new_status = request.form.get("status", "").strip()

            if new_status not in {"Scheduled", "Cancelled"}:
                return render_template(
                    "appointments/edit_appointment.html",
                    appointment=appointment,
                    doctors=doctors,
                    treatment_prices=dict(TREATMENT_PRICES),
                    mode="edit",
                    error_message="Invalid appointment status.",
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                ), 400

            with booking_lock:
                if new_status == "Scheduled":
                    conflict = check_appointment_conflict(
                        appointment_data["appointment_date"],
                        current_appointment_id=appointment.id,
                        doctor_id=appointment_data.get("doctor_id")
                    )
                    if conflict:
                        lang = request.cookies.get("lang", "en")
                        if lang == "ar":
                            err_msg = f"تعارض في الموعد: يوجد موعد آخر مجدول في هذا الوقت ({conflict.appointment_date.strftime('%Y-%m-%d %I:%M %p')} للمريض {conflict.patient.first_name} {conflict.patient.last_name})."
                        else:
                            err_msg = f"Conflict: There is another scheduled appointment at this time ({conflict.appointment_date.strftime('%Y-%m-%d %I:%M %p')} for patient {conflict.patient.first_name} {conflict.patient.last_name})."
                        return render_template(
                            "appointments/edit_appointment.html",
                            appointment=appointment,
                            doctors=doctors,
                            treatment_prices=dict(TREATMENT_PRICES),
                            mode="edit",
                            error_message=err_msg,
                            appointment_min_datetime=appointment_min_datetime,
                            appointment_max_datetime=appointment_max_datetime,
                        ), 400

                old_date = appointment.appointment_date
                new_date = appointment_data["appointment_date"]
                time_edited = (old_date != new_date)

                appointment.appointment_date = new_date
                appointment.reason = appointment_data["reason"]
                appointment.doctor_id = appointment_data.get("doctor_id")
                appointment.status = new_status


                db.session.commit()

            from services.notification_service import notify_appointment_cancellation, notify_appointment_reschedule
            if new_status == "Cancelled":
                notify_appointment_cancellation(appointment)
            elif time_edited and new_status == "Scheduled":
                notify_appointment_reschedule(appointment)

            current_app.logger.info(
                f"Appointment updated successfully | appointment_id={appointment.id}"
            )

            return redirect(get_safe_redirect_url("appointments.appointments"))

        next_url = request.args.get("next") or request.referrer or ""
        if any(k in next_url for k in ["/add", "/edit", "/delete"]):
            next_url = ""

        return render_template(
            "appointments/edit_appointment.html",
            appointment=appointment,
            doctors=doctors,
            treatment_prices=dict(TREATMENT_PRICES),
            mode="edit",
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime,
            next_url=next_url,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to edit appointment | appointment_id={appointment_id}")
        return "Failed to edit appointment", 500


@appointments_bp.route("/appointments/<int:appointment_id>/view")
@role_required("admin", "doctor", "receptionist")
def view_appointment(appointment_id):
    current_app.logger.info(f"View appointment page opened | appointment_id={appointment_id}")

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        from models import User
        from utils.constants import TREATMENT_PRICES
        doctors = User.query.filter_by(role="doctor").all()
        return render_template(
            "appointments/edit_appointment.html",
            appointment=appointment,
            doctors=doctors,
            treatment_prices=dict(TREATMENT_PRICES),
            mode="view",
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime,
        )

    except Exception:
        current_app.logger.exception(f"Failed to view appointment | appointment_id={appointment_id}")
        return "Failed to view appointment", 500


@appointments_bp.route("/appointments/<int:appointment_id>/delete", methods=["GET", "POST"])
@role_required("admin", "receptionist")
def delete_appointment(appointment_id):
    current_app.logger.warning(f"Delete appointment page/request | appointment_id={appointment_id}")

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        lang = request.cookies.get("lang", "en")

        if appointment.status == "Done":
            err_title = "الإجراء غير مسموح به" if lang == "ar" else "Action Not Allowed"
            err_msg = "لا يمكن حذف موعد مكتمل لأنه قد يحتوي على سجلات طبية أو مالية مهمة." if lang == "ar" else "Cannot delete a completed appointment because it may contain important medical or payment history."
            return render_template(
                "error_message.html",
                title=err_title,
                message=err_msg,
                back_url=url_for("patients.patient_detail", patient_id=appointment.patient_id),
            ), 403

        if appointment.treatments:
            err_title = "الإجراء غير مسموح به" if lang == "ar" else "Action Not Allowed"
            err_msg = "لا يمكن حذف موعد يحتوي على معالجات مسجلة." if lang == "ar" else "Cannot delete an appointment that has treatments."
            return render_template(
                "error_message.html",
                title=err_title,
                message=err_msg,
                back_url=url_for("patients.patient_detail", patient_id=appointment.patient_id),
            ), 403

        if request.method == "POST":
            patient_id = appointment.patient_id
            appointment.status = "Deleted"
            db.session.flush()

            from services.payment_service import allocate_patient_payments_to_invoices
            allocate_patient_payments_to_invoices(patient_id)
            db.session.commit()

            current_app.logger.info(
                f"Appointment deleted successfully | appointment_id={appointment_id}"
            )

            return redirect(get_safe_redirect_url("appointments.appointments"))

        next_url = request.args.get("next") or request.referrer or ""
        if any(k in next_url for k in ["/add", "/edit", "/delete"]):
            next_url = ""

        return render_template("appointments/delete_appointment.html", appointment=appointment, next_url=next_url)

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to delete appointment | appointment_id={appointment_id}")

        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to delete appointment.",
            back_url=url_for("appointments.appointments"),
        ), 500


@appointments_bp.route("/appointments/<int:appointment_id>/quick-cancel", methods=["POST"])
@role_required("admin", "receptionist")
def quick_cancel(appointment_id):
    current_app.logger.info(f"Quick cancel appointment | id={appointment_id}")
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        if appointment.status != "Scheduled":
            return jsonify({"success": False, "message": "Only scheduled appointments can be cancelled."}), 400

        appointment.status = "Cancelled"
        db.session.commit()

        from services.notification_service import notify_appointment_cancellation
        notify_appointment_cancellation(appointment)

        return jsonify({"success": True, "message": "Appointment cancelled successfully."})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to quick cancel appointment")
        return jsonify({"success": False, "message": "Internal server error."}), 500


@appointments_bp.route("/appointments/<int:appointment_id>/quick-done", methods=["POST"])
@role_required("admin", "receptionist")
def quick_done(appointment_id):
    current_app.logger.info(f"Quick done appointment | id={appointment_id}")
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        if appointment.status != "Scheduled":
            return jsonify({"success": False, "message": "Only scheduled appointments can be marked as Done."}), 400

        appointment.status = "Done"
        now = datetime.now()
        if appointment.appointment_date and appointment.appointment_date > now:
            appointment.appointment_date = now

        from services.invoice_service import sync_invoice_for_appointment
        sync_invoice_for_appointment(appointment)
        db.session.commit()
        return jsonify({"success": True, "message": "Appointment completed successfully."})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to quick complete appointment")
        return jsonify({"success": False, "message": "Internal server error."}), 500


@appointments_bp.route("/appointments/booked-slots")
@role_required("admin", "doctor", "receptionist")
def booked_slots():
    try:
        exclude_id = request.args.get("exclude_id", type=int)
        query = Appointment.query.filter(Appointment.status == "Scheduled")
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)

        scheduled = query.all()
        slots = [appt.appointment_date.strftime('%Y-%m-%d %I:%M %p') for appt in scheduled]
        return jsonify(slots)
    except Exception:
        return jsonify([]), 500


@appointments_bp.route("/calendar")
@role_required("admin", "doctor", "receptionist")
def calendar():
    current_app.logger.info("Calendar page opened")
    try:
        from utils.settings_helper import get_setting
        working_days = get_setting("working_days", "0,1,2,3,4,6")
        working_days_list = [int(d) for d in working_days.split(",") if d.strip().isdigit()]
        return render_template("appointments/calendar.html", working_days_list=working_days_list)
    except Exception as e:
        current_app.logger.exception(f"Failed to load calendar page: {e}")
        return f"Error loading calendar page: {str(e)}", 500


@appointments_bp.route("/appointments/events")
@role_required("admin", "doctor", "receptionist")
def appointment_events():
    current_app.logger.info("Appointment events requested")
    try:
        cancel_expired_appointments()
        from utils.settings_helper import get_setting
        try:
            duration = int(get_setting("default_appointment_duration", "30"))
        except ValueError:
            duration = 30
        from flask import session
        user_id = session.get("user_id")
        user_role = session.get("role")

        appointments = Appointment.query.all()
        events = []
        for appt in appointments:
            if appt.status == "Done":
                color = "#16a34a"
            elif appt.status == "Cancelled":
                color = "#e11d48"
            else:
                color = "#0284c7"

            start_iso = appt.appointment_date.isoformat()
            end_iso = (appt.appointment_date + timedelta(minutes=duration)).isoformat()

            is_closed = bool(appt.status in ("Done", "Cancelled"))
            is_admin = (user_role == "admin")

            # Admin can open any session.
            # Doctor can open session for their assigned appointments if not Cancelled (even if Done)
            can_open_session = (
                is_admin or (
                    user_role == "doctor" and appt.doctor_id == user_id and appt.status != "Cancelled"
                )
            )

            can_edit = (
                not is_closed and appt.status not in ("Done", "Cancelled") and (
                    is_admin or user_role == "receptionist" or (user_role == "doctor" and appt.doctor_id == user_id)
                )
            )

            can_remind = (
                not is_closed and appt.status == "Scheduled" and
                (user_role in ("admin", "receptionist") or (user_role == "doctor" and appt.doctor_id == user_id)) and
                bool(appt.patient and appt.patient.phone and appt.patient.phone.strip() and appt.patient.phone != "No phone")
            )

            events.append({
                "id": appt.id,
                "title": f"{appt.patient.first_name} {appt.patient.last_name} ({appt.reason or 'N/A'})",
                "start": start_iso,
                "end": end_iso,
                "color": color,
                "extendedProps": {
                    "patientName": f"{appt.patient.first_name} {appt.patient.last_name}",
                    "patientUrl": url_for("patients.patient_detail", patient_id=appt.patient_id),
                    "phone": appt.patient.phone or "No phone",
                    "reason": appt.reason or "No reason",
                    "status": appt.status,
                    "id": appt.id,
                    "isClosed": is_closed,
                    "canOpenSession": can_open_session,
                    "canEdit": can_edit,
                    "canRemind": can_remind,
                    "sessionUrl": url_for("treatments.appointment_session", appointment_id=appt.id) if can_open_session else None,
                    "viewUrl": url_for("appointments.view_appointment", appointment_id=appt.id),
                    "editUrl": url_for("appointments.edit_appointment", appointment_id=appt.id) if can_edit else None
                }
            })
        return jsonify(events)
    except Exception:
        current_app.logger.exception("Failed to fetch appointment events")
        return jsonify([]), 500


@appointments_bp.route("/appointments/delete-all-cancelled", methods=["POST"])
@role_required("admin", "receptionist")
def delete_all_cancelled():
    current_app.logger.warning("Delete all cancelled appointments requested")
    try:
        cancelled_appointments = Appointment.query.filter(Appointment.status == "Cancelled").all()
        count = len(cancelled_appointments)
        for appt in cancelled_appointments:
            db.session.delete(appt)
        db.session.commit()
        current_app.logger.info(f"Successfully deleted {count} cancelled appointments")
        return redirect(url_for("appointments.appointments"))
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to delete all cancelled appointments")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to delete cancelled appointments.",
            back_url=url_for("appointments.appointments"),
        ), 500


def cleanup_expired_pending_appointments():
    """
    Automatically cancels any pending appointment request if the requested appointment date
    is less than lead_minutes away (default: 120 minutes = 2 hours before appointment time)
    or is already in the past.
    """
    try:
        from utils.settings_helper import get_setting
        lead_mins_str = get_setting("auto_cancel_expired_minutes", "120")
        try:
            lead_mins = int(lead_mins_str)
            if lead_mins < 0:
                lead_mins = 120
        except ValueError:
            lead_mins = 120

        now = datetime.now()
        # Cutoff: any pending appointment scheduled at or before (now + lead_mins) is considered expired/past-due
        cutoff = now + timedelta(minutes=lead_mins)

        expired_appts = Appointment.query.filter(
            Appointment.status == "Pending",
            Appointment.appointment_date <= cutoff
        ).all()

        count = len(expired_appts)
        if count > 0:
            lead_hours = round(lead_mins / 60.0, 1)
            for appt in expired_appts:
                appt.status = "Cancelled"
                note_suffix = f" [تم الإلغاء تلقائياً لعدم التأكيد قبل الموعد بـ {lead_hours} ساعة]"
                appt.reason = (appt.reason or "") + note_suffix
            db.session.commit()
            current_app.logger.info(f"Auto-cleaned {count} pending appointment requests within {lead_mins} minutes cutoff")
        return count
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error in cleanup_expired_pending_appointments")
        return 0


@appointments_bp.route("/appointments/cleanup-expired", methods=["POST"])
@role_required("admin", "receptionist")
def cleanup_expired_route():
    count = cleanup_expired_pending_appointments()
    is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
    msg = f"تم إلغاء وتنظيف {count} طلب حجز منتهي الصلاحية تلقائياً." if is_ar else f"Auto-cleaned {count} expired booking requests."
    return jsonify({"success": True, "message": msg, "cleaned_count": count})


@appointments_bp.route("/appointments/pending")
@role_required("admin", "doctor", "receptionist")
def pending_appointments():
    current_app.logger.info("Pending appointments page opened")
    try:
        # Auto clean expired pending requests before displaying
        cleanup_expired_pending_appointments()

        now = datetime.now()
        pending = (
            Appointment.query
            .join(Patient)
            .filter(Appointment.status == "Pending")
            .order_by(Appointment.appointment_date.asc())
            .all()
        )
        return render_template("appointments/pending_appointments.html", pending_appointments=pending, now=now)
    except Exception:
        current_app.logger.exception("Error while loading pending appointments page")
        return "Error Loading Pending Appointments Page", 500


@appointments_bp.route("/appointments/<int:appointment_id>/confirm", methods=["POST"])
@role_required("admin", "receptionist")
def confirm_appointment(appointment_id):
    current_app.logger.info(f"Confirming appointment request | id={appointment_id}")
    try:
        appt = Appointment.query.get_or_404(appointment_id)
        if appt.status != "Pending":
            is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
            return jsonify({"success": False, "message": "يمكن تأكيد المواعيد قيد التثبيت فقط." if is_ar else "Only pending appointments can be confirmed."}), 400
        
        appt.status = "Scheduled"
        db.session.commit()
        is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
        return jsonify({"success": True, "message": "تم تأكيد طلب الموعد بنجاح." if is_ar else "Appointment confirmed successfully."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to confirm appointment request")
        is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
        return jsonify({"success": False, "message": "حدث خطأ في النظام أثناء التأكيد." if is_ar else "Internal server error."}), 500


@appointments_bp.route("/appointments/<int:appointment_id>/decline", methods=["POST"])
@role_required("admin", "receptionist")
def decline_appointment(appointment_id):
    current_app.logger.info(f"Declining appointment request | id={appointment_id}")
    try:
        appt = Appointment.query.get_or_404(appointment_id)
        if appt.status != "Pending":
            is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
            return jsonify({"success": False, "message": "يمكن رفض المواعيد قيد التثبيت فقط." if is_ar else "Only pending appointments can be declined."}), 400
        
        appt.status = "Rejected"
        db.session.commit()

        try:
            from services.notification_service import notify_appointment_cancellation
            notify_appointment_cancellation(appt)
        except Exception as e:
            current_app.logger.error(f"Failed to send cancellation notification: {e}")

        is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
        return jsonify({"success": True, "message": "تم رفض طلب الموعد بنجاح." if is_ar else "Appointment request declined."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to decline appointment request")
        is_ar = request.cookies.get("lang") == "ar" or session.get("lang") == "ar"
        return jsonify({"success": False, "message": "حدث خطأ في النظام أثناء الرفض." if is_ar else "Internal server error."}), 500


@appointments_bp.route("/appointments/<int:appointment_id>/reschedule", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def reschedule_appointment(appointment_id):
    current_app.logger.info(f"Rescheduling appointment request | id={appointment_id}")
    try:
        appt = Appointment.query.get_or_404(appointment_id)
        if appt.status != "Scheduled":
            return jsonify({"success": False, "message": "Only scheduled appointments can be rescheduled."}), 400
        
        data = request.get_json() or {}
        new_start_str = data.get("start")
        if not new_start_str:
            return jsonify({"success": False, "message": "Missing start time parameter."}), 400
            
        try:
            if "+" in new_start_str:
                new_start_str = new_start_str.split("+")[0]
            elif "Z" in new_start_str:
                new_start_str = new_start_str.replace("Z", "")
            
            if "T" in new_start_str:
                new_date = datetime.fromisoformat(new_start_str)
            else:
                new_date = datetime.strptime(new_start_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"success": False, "message": "Invalid date format."}), 400
            
        # Check conflicts
        conflict = check_appointment_conflict(new_date, appt.id)
        if conflict:
            lang = request.cookies.get('lang', 'en')
            msg = "هذا الوقت محجوز مسبقاً لموعد آخر." if lang == 'ar' else "This time slot is already booked for another appointment."
            return jsonify({"success": False, "message": msg}), 409
            
        appt.appointment_date = new_date
        db.session.commit()

        from services.notification_service import notify_appointment_reschedule
        notify_appointment_reschedule(appt)
        
        return jsonify({"success": True, "message": "Appointment rescheduled successfully."})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to reschedule appointment")
        return jsonify({"success": False, "message": "Failed to reschedule appointment."}), 500


@appointments_bp.route("/appointments/<int:appointment_id>/update-status", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def update_appointment_status(appointment_id):
    current_app.logger.info(f"Updating appointment status | id={appointment_id}")
    try:
        appt = Appointment.query.get_or_404(appointment_id)
        data = request.get_json() or {}
        new_status = data.get("status")
        
        valid_statuses = ["Scheduled", "Done", "Cancelled"]
        if new_status not in valid_statuses:
            return jsonify({"success": False, "message": "Invalid status."}), 400

        appt.status = new_status
        db.session.commit()

        if new_status == "Cancelled":
            from services.notification_service import notify_appointment_cancellation
            notify_appointment_cancellation(appt)
        
        return jsonify({"success": True, "message": "Status updated successfully.", "new_status": new_status})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to update appointment status")
        return jsonify({"success": False, "message": "Failed to update status."}), 500


@appointments_bp.route("/appointments/today-statuses", methods=["GET"])
@role_required("admin", "doctor", "receptionist")
def get_today_statuses():
    current_app.logger.info("Auto-refresh status check requested")
    try:
        from datetime import datetime, time
        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)
        
        appointments = (
            Appointment.query
            .filter(Appointment.appointment_date >= today_start)
            .filter(Appointment.appointment_date <= today_end)
            .all()
        )
        
        statuses = {str(a.id): a.status for a in appointments}
        return jsonify({"success": True, "statuses": statuses})
    except Exception:
        current_app.logger.exception("Failed to get today statuses")
        return jsonify({"success": False, "statuses": {}}), 500


def get_archive_context():
    from sqlalchemy.orm import joinedload
    search_query = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    sort_by = request.args.get("sort", "date").strip()
    order = request.args.get("order", "desc").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = (
        Appointment.query
        .filter(Appointment.status.in_(["Done", "Cancelled"]))
        .options(
            joinedload(Appointment.patient),
            joinedload(Appointment.doctor)
        )
    )

    if search_query:
        query = query.join(Patient).filter(
            (Patient.first_name.ilike(f"%{search_query}%")) |
            (Patient.last_name.ilike(f"%{search_query}%"))
        )

    if status_filter in ["Done", "Cancelled"]:
        query = query.filter(Appointment.status == status_filter)

    sort_columns = {
        "date": Appointment.appointment_date,
        "status": Appointment.status,
        "reason": Appointment.reason,
    }

    if sort_by == "patient":
        if not search_query:
            query = query.join(Patient)
        sort_column = Patient.first_name
    elif sort_by == "doctor":
        query = query.outerjoin(User, Appointment.doctor_id == User.id)
        sort_column = User.first_name
    else:
        sort_column = sort_columns.get(sort_by, Appointment.appointment_date)

    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    archived_count = Appointment.query.filter(Appointment.status.in_(["Done", "Cancelled"])).count()

    return {
        "pagination": pagination,
        "archived_appointments": pagination.items,
        "archived_count": archived_count,
        "search_query": search_query,
        "status_filter": status_filter,
        "sort_by": sort_by,
        "order": order,
        "now": datetime.now(),
        "current_lang": request.cookies.get("lang", "ar"),
        "per_page": per_page
    }


@appointments_bp.route("/appointments/archive", methods=["GET"])
@role_required("admin", "doctor", "receptionist")
def appointments_archive():
    """Renders the Archived, Cancelled & Deleted Appointments page."""
    current_app.logger.info("Appointments archive page requested")
    try:
        context = get_archive_context()
        return render_template("appointments/archive.html", **context)
    except Exception:
        current_app.logger.exception("Failed to load appointments archive")
        flash("فشل في تحميل أرشيف المواعيد." if request.cookies.get("lang","ar")!="en" else "Failed to load appointments archive.", "danger")
        return redirect(url_for("appointments.appointments"))


@appointments_bp.route("/appointments/archive/table", methods=["GET"])
@role_required("admin", "doctor", "receptionist")
def archive_table():
    """Renders the Archive table partial for AJAX sorting and pagination."""
    current_app.logger.info("Appointments archive table partial requested")
    try:
        context = get_archive_context()
        return render_template("partials/_archive_table.html", **context)
    except Exception:
        current_app.logger.exception("Failed to load archive table partial")
        return "Failed to load archive table", 500


@appointments_bp.route("/appointments/<int:appointment_id>/restore", methods=["POST"])
@role_required("admin", "doctor", "receptionist")
def restore_appointment(appointment_id):
    """Restores an archived/cancelled/deleted appointment back to Scheduled status ONLY if it is in the future."""
    is_ar = request.cookies.get("lang", "ar") != "en"
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    try:
        appt = Appointment.query.get_or_404(appointment_id)
        
        # Enforce Rule: Only future appointments can be restored
        if appt.appointment_date and appt.appointment_date < datetime.now():
            msg = "لا يمكن استعادة موعد انتهى تاريخه الزمني. يمكن استعادة المواعيد المستقبلية فقط." if is_ar else "Cannot restore an appointment with a past date. Only future appointments can be restored."
            if is_ajax:
                return {"success": False, "message": msg}, 400
            flash(msg, "warning")
            return redirect(url_for("appointments.appointments_archive"))

        appt.status = "Scheduled"
        db.session.commit()

        try:
            from services.notification_service import notify_appointment_restoration
            notify_appointment_restoration(appt)
        except Exception as ne:
            current_app.logger.error(f"Failed to send restoration notification: {ne}")

        patient_name = f"{appt.patient.first_name} {appt.patient.last_name}" if appt.patient else ""
        msg = f"تمت استعادة الموعد وإعادته إلى الجدول بنجاح للمريض ({patient_name})." if is_ar else f"Appointment restored successfully for ({patient_name})."
        current_app.logger.info(f"Appointment id={appointment_id} restored to Scheduled")
        if is_ajax:
            return {"success": True, "message": msg}
        flash(msg, "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to restore appointment id={appointment_id}")
        msg = "فشل في استعادة الموعد." if is_ar else "Failed to restore appointment."
        if is_ajax:
            return {"success": False, "message": msg}, 500
        flash(msg, "danger")

    return redirect(url_for("appointments.appointments_archive"))


@appointments_bp.route("/appointments/<int:appointment_id>/permanent-delete", methods=["POST"])
@role_required("admin", "receptionist")
def permanent_delete_appointment(appointment_id):
    """Permanently deletes a cancelled appointment record."""
    is_ar = request.cookies.get("lang", "ar") != "en"
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    try:
        appt = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appt)
        db.session.commit()

        msg = "تم حذف الموعد نهائياً من قاعدة البيانات." if is_ar else "Appointment permanently deleted."
        current_app.logger.info(f"Appointment id={appointment_id} permanently deleted")
        if is_ajax:
            return {"success": True, "message": msg}
        flash(msg, "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to permanently delete appointment id={appointment_id}")
        msg = "فشل في حذف الموعد." if is_ar else "Failed to delete appointment."
        if is_ajax:
            return {"success": False, "message": msg}, 500
        flash(msg, "danger")

    return redirect(url_for("appointments.appointments_archive"))


@appointments_bp.route("/appointments/archive/restore-all", methods=["POST"])
@role_required("admin", "receptionist")
def restore_all_archived_appointments():
    """Restores all future archived/cancelled/deleted appointments back to Scheduled status."""
    is_ar = request.cookies.get("lang", "ar") != "en"
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    try:
        now = datetime.now()
        restorable = Appointment.query.filter(
            Appointment.status.in_(["Cancelled", "Deleted"]),
            Appointment.appointment_date >= now
        ).all()

        count = len(restorable)
        if count == 0:
            msg = "لا توجد مواعيد مستقبلية قابلة للاستعادة حالياً في الأرشيف." if is_ar else "No future restorable appointments found in archive."
            if is_ajax:
                return {"success": False, "message": msg}, 400
            flash(msg, "warning")
            return redirect(url_for("appointments.appointments_archive"))

        for appt in restorable:
            appt.status = "Scheduled"
            try:
                from services.notification_service import notify_appointment_restoration
                notify_appointment_restoration(appt)
            except Exception:
                pass

        db.session.commit()
        msg = f"تمت استعادة {count} موعد مستقبلي وإعادتها إلى الجدول بنجاح!" if is_ar else f"Successfully restored {count} future appointments!"
        current_app.logger.info(f"Restored all {count} future archived appointments")

        if is_ajax:
            return {"success": True, "message": msg, "restored_count": count}
        flash(msg, "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to restore all archived appointments")
        msg = f"حدث خطأ أثناء استعادة المواعيد: {str(e)}" if is_ar else f"Error restoring appointments: {str(e)}"
        if is_ajax:
            return {"success": False, "message": msg}, 500
        flash(msg, "danger")

    return redirect(url_for("appointments.appointments_archive"))


@appointments_bp.route("/appointments/archive/permanent-delete-all", methods=["POST"])
@role_required("admin", "receptionist")
def permanent_delete_all_archived_appointments():
    """Permanently deletes all archived (Cancelled/Deleted) appointments."""
    is_ar = request.cookies.get("lang", "ar") != "en"
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    try:
        archived = Appointment.query.filter(
            Appointment.status.in_(["Cancelled", "Deleted"])
        ).all()

        count = len(archived)
        if count == 0:
            msg = "لا توجد مواعيد مؤرشفة لحذفها نهائياً." if is_ar else "No archived appointments found to delete."
            if is_ajax:
                return {"success": False, "message": msg}, 400
            flash(msg, "warning")
            return redirect(url_for("appointments.appointments_archive"))

        for appt in archived:
            db.session.delete(appt)

        db.session.commit()
        msg = f"تم الحذف النهائي لجميع المواعيد المؤرشفة ({count} موعد) من قاعدة البيانات بنجاح." if is_ar else f"Permanently deleted all {count} archived appointments."
        current_app.logger.info(f"Permanently deleted all {count} archived appointments")

        if is_ajax:
            return {"success": True, "message": msg, "deleted_count": count}
        flash(msg, "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to permanent delete all archived appointments")
        msg = f"حدث خطأ أثناء الحذف النهائي للمواعيد: {str(e)}" if is_ar else f"Error permanently deleting appointments: {str(e)}"
        if is_ajax:
            return {"success": False, "message": msg}, 500
        flash(msg, "danger")

    return redirect(url_for("appointments.appointments_archive"))



