from flask import Blueprint, current_app, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta

from models import db, Patient, Appointment
from utils.validators import (
    get_appointment_datetime_limits,
    parse_appointment_data,
    check_appointment_conflict,
)


appointments_bp = Blueprint("appointments", __name__)


@appointments_bp.before_app_request
def auto_cancel_expired_appointments():
    if request.endpoint and "static" not in request.endpoint:
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            expired = Appointment.query.filter(
                Appointment.status == "Scheduled",
                Appointment.appointment_date < one_hour_ago
            ).all()
            if expired:
                for appt in expired:
                    appt.status = "Cancelled"
                db.session.commit()
                current_app.logger.info(f"Auto-cancelled {len(expired)} expired appointments.")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Failed to auto-cancel expired appointments")


def get_appointments_context():
    search_query = request.args.get("search", "")
    status_filter = request.args.get("status", "")
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = Appointment.query.join(Patient)

    if search_query:
        query = query.filter(
            (Patient.first_name.ilike(f"%{search_query}%")) |
            (Patient.last_name.ilike(f"%{search_query}%"))
        )

    if status_filter:
        query = query.filter(Appointment.status == status_filter)

    sort_columns = {
        "id": Appointment.id,
        "patient": Patient.first_name,
        "date": Appointment.appointment_date,
        "status": Appointment.status,
        "reason": Appointment.reason,
    }

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

    return {
        "appointments": pagination.items,
        "pagination": pagination,
        "search_query": search_query,
        "status_filter": status_filter,
        "sort_by": sort_by,
        "order": order,
    }


@appointments_bp.route("/appointments")
def appointments():
    current_app.logger.info("Appointments page opened")

    try:
        context = get_appointments_context()
        return render_template("appointments/appointments.html", **context)

    except Exception:
        current_app.logger.exception("Error while loading appointments page")
        return "Error Loading AppointmentsPage", 500
    
@appointments_bp.route("/appointments/table")
def appointments_table():
    current_app.logger.info("Appointments table partial requested")

    try:
        context = get_appointments_context()
        return render_template("partials/_appointments_table.html", **context)

    except Exception:
        current_app.logger.exception("Error while loading appointments table")
        return "Error Loading AppointmentsTable", 500


@appointments_bp.route("/appointments/add", methods=["GET", "POST"])
def add_appointment_direct():
    current_app.logger.info("Direct add appointment page/request")
    try:
        patients = Patient.query.order_by(Patient.first_name.asc(), Patient.last_name.asc()).all()
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        if request.method == "POST":
            patient_id = request.form.get("patient_id")
            if not patient_id:
                return "Patient ID is required.", 400

            patient = Patient.query.get_or_404(patient_id)
            appointment_data, appointment_error = parse_appointment_data(request.form)

            if appointment_error:
                return render_template(
                    "appointments/add_appointment.html",
                    patients=patients,
                    error_message=appointment_error,
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                ), 400

            conflict = check_appointment_conflict(appointment_data["appointment_date"])
            if conflict:
                return render_template(
                    "appointments/add_appointment.html",
                    patients=patients,
                    error_message=f"Conflict: There is another scheduled appointment at this time ({conflict.appointment_date.strftime('%Y-%m-%d %H:%M')} for patient {conflict.patient.first_name} {conflict.patient.last_name}).",
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                ), 400

            new_appointment = Appointment(
                patient_id=patient.id,
                appointment_date=appointment_data["appointment_date"],
                reason=appointment_data["reason"],
                status="Scheduled",
            )

            db.session.add(new_appointment)
            db.session.commit()

            current_app.logger.info(
                f"Appointment added successfully | appointment_id={new_appointment.id}, patient_id={patient.id}"
            )

            return redirect(url_for("appointments.appointments"))

        return render_template(
            "appointments/add_appointment.html",
            patients=patients,
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to direct add appointment")
        return "Error Loading AppointmentInfo", 500


@appointments_bp.route("/patients/<int:patient_id>/appointments/add", methods=["GET", "POST"])

def add_appointment(patient_id):
    current_app.logger.info(f"Add appointment page/request | patient_id={patient_id}")

    try:
        patient = Patient.query.get_or_404(patient_id)
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        if request.method == "POST":
            appointment_data, appointment_error = parse_appointment_data(request.form)

            if appointment_error:
                return render_template(
                    "appointments/add_appointment.html",
                    patient=patient,
                    error_message=appointment_error,
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                ), 400

            conflict = check_appointment_conflict(appointment_data["appointment_date"])
            if conflict:
                return render_template(
                    "appointments/add_appointment.html",
                    patient=patient,
                    error_message=f"Conflict: There is another scheduled appointment at this time ({conflict.appointment_date.strftime('%Y-%m-%d %H:%M')} for patient {conflict.patient.first_name} {conflict.patient.last_name}).",
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                ), 400

            new_appointment = Appointment(
                patient_id=patient.id,
                appointment_date=appointment_data["appointment_date"],
                reason=appointment_data["reason"],
                status="Scheduled",
            )


            db.session.add(new_appointment)
            db.session.commit()

            current_app.logger.info(
                f"Appointment added successfully | appointment_id={new_appointment.id}, patient_id={patient.id}"
            )

            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        return render_template(
            "appointments/add_appointment.html",
            patient=patient,
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to add appointment | patient_id={patient_id}")
        return "Error Loading AppointmentInfo", 500


@appointments_bp.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    current_app.logger.info(f"Edit appointment page/request | appointment_id={appointment_id}")

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        if request.method == "POST":
            if appointment.status != "Scheduled":
                return "Cannot edit a closed or cancelled appointment.", 403

            appointment_data, appointment_error = parse_appointment_data(request.form)

            if appointment_error:
                return render_template(
                    "appointments/edit_appointment.html",
                    appointment=appointment,
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
                    mode="edit",
                    error_message="Invalid appointment status.",
                    appointment_min_datetime=appointment_min_datetime,
                    appointment_max_datetime=appointment_max_datetime,
                ), 400

            if new_status == "Scheduled":
                conflict = check_appointment_conflict(
                    appointment_data["appointment_date"],
                    current_appointment_id=appointment.id
                )
                if conflict:
                    return render_template(
                        "appointments/edit_appointment.html",
                        appointment=appointment,
                        mode="edit",
                        error_message=f"Conflict: There is another scheduled appointment at this time ({conflict.appointment_date.strftime('%Y-%m-%d %H:%M')} for patient {conflict.patient.first_name} {conflict.patient.last_name}).",
                        appointment_min_datetime=appointment_min_datetime,
                        appointment_max_datetime=appointment_max_datetime,
                    ), 400

            appointment.appointment_date = appointment_data["appointment_date"]
            appointment.reason = appointment_data["reason"]
            appointment.status = new_status


            db.session.commit()

            current_app.logger.info(
                f"Appointment updated successfully | appointment_id={appointment.id}"
            )

            return redirect(url_for("patients.patient_detail", patient_id=appointment.patient_id))

        return render_template(
            "appointments/edit_appointment.html",
            appointment=appointment,
            mode="edit",
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime,
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to edit appointment | appointment_id={appointment_id}")
        return "Failed to edit appointment", 500


@appointments_bp.route("/appointments/<int:appointment_id>/view")
def view_appointment(appointment_id):
    current_app.logger.info(f"View appointment page opened | appointment_id={appointment_id}")

    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment_min_datetime, appointment_max_datetime = get_appointment_datetime_limits()

        return render_template(
            "appointments/edit_appointment.html",
            appointment=appointment,
            mode="view",
            appointment_min_datetime=appointment_min_datetime,
            appointment_max_datetime=appointment_max_datetime,
        )

    except Exception:
        current_app.logger.exception(f"Failed to view appointment | appointment_id={appointment_id}")
        return "Failed to view appointment", 500


@appointments_bp.route("/appointments/<int:appointment_id>/delete", methods=["GET", "POST"])
def delete_appointment(appointment_id):
    current_app.logger.warning(f"Delete appointment page/request | appointment_id={appointment_id}")

    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.status == "Done":
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message=(
                    "Cannot delete a completed appointment because it may contain "
                    "important medical or payment history."
                ),
                back_url=url_for("patients.patient_detail", patient_id=appointment.patient_id),
            ), 403

        if appointment.treatments:
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message="Cannot delete an appointment that has treatments.",
                back_url=url_for("patients.patient_detail", patient_id=appointment.patient_id),
            ), 403

        if request.method == "POST":
            patient_id = appointment.patient_id
            db.session.delete(appointment)
            db.session.commit()

            current_app.logger.info(
                f"Appointment deleted successfully | appointment_id={appointment_id}"
            )

            return redirect(url_for("patients.patient_detail", patient_id=patient_id))

        return render_template("appointments/delete_appointment.html", appointment=appointment)

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
def quick_cancel(appointment_id):
    current_app.logger.info(f"Quick cancel appointment | id={appointment_id}")
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        if appointment.status != "Scheduled":
            return jsonify({"success": False, "message": "Only scheduled appointments can be cancelled."}), 400

        appointment.status = "Cancelled"
        db.session.commit()
        return jsonify({"success": True, "message": "Appointment cancelled successfully."})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to quick cancel appointment")
        return jsonify({"success": False, "message": "Internal server error."}), 500


@appointments_bp.route("/appointments/<int:appointment_id>/quick-done", methods=["POST"])
def quick_done(appointment_id):
    current_app.logger.info(f"Quick done appointment | id={appointment_id}")
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        if appointment.status != "Scheduled":
            return jsonify({"success": False, "message": "Only scheduled appointments can be marked as Done."}), 400

        appointment.status = "Done"
        from services.invoice_service import sync_invoice_for_appointment
        sync_invoice_for_appointment(appointment)
        db.session.commit()
        return jsonify({"success": True, "message": "Appointment completed successfully."})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to quick complete appointment")
        return jsonify({"success": False, "message": "Internal server error."}), 500


@appointments_bp.route("/appointments/booked-slots")
def booked_slots():
    try:
        exclude_id = request.args.get("exclude_id", type=int)
        query = Appointment.query.filter(Appointment.status == "Scheduled")
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)

        scheduled = query.all()
        slots = [appt.appointment_date.strftime("%Y-%m-%d %H:%M") for appt in scheduled]
        return jsonify(slots)
    except Exception:
        return jsonify([]), 500


@appointments_bp.route("/calendar")
def calendar():
    current_app.logger.info("Calendar page opened")
    try:
        return render_template("appointments/calendar.html")
    except Exception:
        current_app.logger.exception("Failed to load calendar page")
        return "Error loading calendar page", 500


@appointments_bp.route("/appointments/events")
def appointment_events():
    current_app.logger.info("Appointment events requested")
    try:
        appointments = Appointment.query.all()
        events = []
        for appt in appointments:
            if appt.status == "Done":
                color = "#0d9488"
            elif appt.status == "Cancelled":
                color = "#e11d48"
            else:
                color = "#0284c7"

            start_iso = appt.appointment_date.isoformat()
            end_iso = (appt.appointment_date + timedelta(minutes=30)).isoformat()

            events.append({
                "id": appt.id,
                "title": f"{appt.patient.first_name} {appt.patient.last_name} ({appt.reason or 'N/A'})",
                "start": start_iso,
                "end": end_iso,
                "color": color,
                "extendedProps": {
                    "patientName": f"{appt.patient.first_name} {appt.patient.last_name}",
                    "phone": appt.patient.phone or "No phone",
                    "reason": appt.reason or "No reason",
                    "status": appt.status,
                    "id": appt.id,
                    "sessionUrl": url_for("treatments.appointment_session", appointment_id=appt.id),
                    "viewUrl": url_for("appointments.view_appointment", appointment_id=appt.id),
                    "editUrl": url_for("appointments.edit_appointment", appointment_id=appt.id) if appt.status == "Scheduled" else None
                }
            })
        return jsonify(events)
    except Exception:
        current_app.logger.exception("Failed to fetch appointment events")
        return jsonify([]), 500

