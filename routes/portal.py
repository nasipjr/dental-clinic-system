from functools import wraps
from datetime import datetime, timedelta, time
import json
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, jsonify
from models import db, Patient, Appointment, User
from utils.settings_helper import get_setting

portal_bp = Blueprint("portal", __name__, url_prefix="/portal")

def patient_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "patient":
            flash("Please log in to access the patient portal.", "danger")
            return redirect(url_for("portal.login"))
        return f(*args, **kwargs)
    return decorated_function


@portal_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session and session.get("role") == "patient":
        return redirect(url_for("portal.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("portal/login.html")

        user = User.query.filter_by(username=username, role="patient").first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role
            session["patient_id"] = user.patient_id
            session.permanent = True
            flash(f"Welcome to your portal, {user.first_name or user.username}!", "success")
            return redirect(url_for("portal.dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("portal/login.html")


@portal_bp.route("/register", methods=["GET", "POST"])
def register():
    flash("Public registration is disabled. Please contact the clinic staff to set up your account.", "danger")
    return redirect(url_for("portal.login"))


@portal_bp.route("/logout")
def logout():
    session.clear()
    flash("You have logged out of the portal.", "success")
    return redirect(url_for("portal.login"))


@portal_bp.route("/dashboard")
@patient_login_required
def dashboard():
    patient_id = session.get("patient_id")
    patient = Patient.query.get_or_404(patient_id)
    
    # Fetch patient appointments ordered by date
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).all()
    
    from utils.constants import APPOINTMENT_REASONS
    
    return render_template(
        "portal/dashboard.html",
        patient=patient,
        appointments=appointments,
        reasons=list(APPOINTMENT_REASONS)
    )


@portal_bp.route("/book", methods=["GET", "POST"])
@patient_login_required
def book_appointment():
    patient_id = session.get("patient_id")
    patient = Patient.query.get_or_404(patient_id)

    if request.method == "POST":
        appt_date_raw = request.form.get("appointment_date", "").strip()
        reason = request.form.get("reason", "").strip()

        if not appt_date_raw or not reason:
            flash("All fields are required.", "danger")
            return redirect(url_for("portal.book_appointment"))

        try:
            appointment_date = datetime.strptime(appt_date_raw, "%Y-%m-%dT%H:%M")
        except ValueError:
            try:
                appointment_date = datetime.strptime(appt_date_raw, "%Y-%m-%d %H:%M")
            except ValueError:
                flash("Invalid appointment date and time format.", "danger")
                return redirect(url_for("portal.book_appointment"))

        # Time limits check
        now = datetime.now().replace(second=0, microsecond=0)
        max_date = now + timedelta(days=30)

        if appointment_date < now:
            flash("Appointment cannot be booked in the past.", "danger")
            return redirect(url_for("portal.book_appointment"))

        if appointment_date > max_date:
            flash("Appointment cannot be booked more than 30 days in advance.", "danger")
            return redirect(url_for("portal.book_appointment"))

        # Working hours and working days checks
        working_days = get_setting("working_days", "0,1,2,3,4,6")
        working_days_list = [d.strip() for d in working_days.split(",") if d.strip()]
        day_str = appointment_date.strftime("%w")

        if day_str not in working_days_list:
            flash("Clinic is closed on this day.", "danger")
            return redirect(url_for("portal.book_appointment"))

        start_str = get_setting("working_hours_start", "09:00")
        end_str = get_setting("working_hours_end", "17:00")

        try:
            sh, sm = map(int, start_str.split(':'))
            start_time = time(sh, sm)
        except Exception:
            start_time = time(9, 0)

        try:
            eh, em = map(int, end_str.split(':'))
            end_time = time(eh, em)
        except Exception:
            end_time = time(17, 0)

        appt_time = appointment_date.time()
        if appt_time < start_time or appt_time > end_time:
            flash(f"Appointment time must be between {start_str} and {end_str}.", "danger")
            return redirect(url_for("portal.book_appointment"))

        # Check conflict
        from utils.validators import check_appointment_conflict
        conflict = check_appointment_conflict(appointment_date)
        if conflict:
            flash("Selected slot is no longer available. Please select another time.", "danger")
            return redirect(url_for("portal.book_appointment"))

        try:
            new_appt = Appointment(
                patient_id=patient.id,
                appointment_date=appointment_date,
                reason=reason,
                status="Pending" # Pending approval
            )
            db.session.add(new_appt)
            db.session.commit()
            flash("Appointment request submitted successfully! Pending staff confirmation.", "success")
            return redirect(url_for("portal.dashboard"))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to submit appointment request: {e}")
            flash("Failed to submit request. Please try again.", "danger")
            return redirect(url_for("portal.book_appointment"))

    # Limits for input
    now = datetime.now()
    max_date = now + timedelta(days=30)
    min_datetime_str = now.strftime("%Y-%m-%dT%H:%M")
    max_datetime_str = max_date.strftime("%Y-%m-%dT%H:%M")

    # Fetch default reasons
    from utils.constants import APPOINTMENT_REASONS

    return render_template(
        "portal/book.html",
        patient=patient,
        reasons=list(APPOINTMENT_REASONS),
        min_datetime=min_datetime_str,
        max_datetime=max_datetime_str
    )


@portal_bp.route("/booked-slots")
@patient_login_required
def booked_slots():
    try:
        # Get all occupied slots in the next 30 days
        now = datetime.now()
        limit_date = now + timedelta(days=30)
        
        occupied = Appointment.query.filter(
            Appointment.status.in_(["Scheduled", "Pending", "Done"]),
            Appointment.appointment_date >= now.date(),
            Appointment.appointment_date <= limit_date
        ).all()
        
        slots = [appt.appointment_date.strftime("%Y-%m-%d %H:%M") for appt in occupied]
        return jsonify(slots)
    except Exception:
        return jsonify([]), 500


@portal_bp.route("/events")
@patient_login_required
def portal_events():
    try:
        # Get all occupied slots in the next 30 days
        now = datetime.now()
        limit_date = now + timedelta(days=30)
        
        occupied = Appointment.query.filter(
            Appointment.status.in_(["Scheduled", "Pending", "Done"]),
            Appointment.appointment_date >= now.date(),
            Appointment.appointment_date <= limit_date
        ).all()
        
        events = []
        for appt in occupied:
            start_iso = appt.appointment_date.isoformat()
            end_iso = (appt.appointment_date + timedelta(minutes=30)).isoformat()
            
            events.append({
                "title": "Reserved",
                "start": start_iso,
                "end": end_iso,
                "color": "#6c757d",  # Muted grey color for occupied slot
                "extendedProps": {
                    "status": "Reserved"
                }
            })
            
        return jsonify(events)
    except Exception:
        current_app.logger.exception("Failed to fetch portal calendar events")
        return jsonify([]), 500
