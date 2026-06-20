from functools import wraps
from datetime import datetime, timedelta, time
import json
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, jsonify
from models import db, Patient, Appointment, User
from utils.settings_helper import get_setting

portal_bp = Blueprint("portal", __name__, url_prefix="/portal")

def flash_message(key, category="danger", **kwargs):
    lang = request.cookies.get('lang', 'en')
    translations = {
        "ar": {
            "login_required": "يرجى تسجيل الدخول للوصول إلى بوابة المرضى.",
            "fields_required": "يرجى إدخال اسم المستخدم وكلمة المرور.",
            "welcome": "مرحباً بك في بوابتك الخاصة، {name}!",
            "invalid_credentials": "اسم المستخدم أو كلمة المرور غير صالحة.",
            "registration_disabled": "التسجيل العام معطل. يرجى التواصل مع موظفي العيادة لإنشاء حسابك.",
            "logged_out": "لقد قمت بتسجيل الخروج من البوابة بنجاح.",
            "all_fields_required": "جميع الحقول مطلوبة.",
            "invalid_date_format": "تنسيق تاريخ ووقت الموعد غير صالح.",
            "past_date": "لا يمكن حجز موعد في الماضي.",
            "advance_date": "لا يمكن حجز موعد قبل أكثر من 30 يوماً.",
            "clinic_closed": "العيادة مغلقة في هذا اليوم.",
            "time_limit": "يجب أن يكون وقت الموعد بين {start} و {end}.",
            "slot_unavailable": "الوقت المحدد لم يعد متاحاً. يرجى اختيار وقت آخر.",
            "booking_success": "تم تقديم طلب الموعد بنجاح! بانتظار تأكيد الموظفين.",
            "booking_failed": "فشل تقديم الطلب. يرجى المحاولة مرة أخرى."
        },
        "en": {
            "login_required": "Please log in to access the patient portal.",
            "fields_required": "Please enter both username and password.",
            "welcome": "Welcome to your portal, {name}!",
            "invalid_credentials": "Invalid username or password.",
            "registration_disabled": "Public registration is disabled. Please contact the clinic staff to set up your account.",
            "logged_out": "You have logged out of the portal.",
            "all_fields_required": "All fields are required.",
            "invalid_date_format": "Invalid appointment date and time format.",
            "past_date": "Appointment cannot be booked in the past.",
            "advance_date": "Appointment cannot be booked more than 30 days in advance.",
            "clinic_closed": "Clinic is closed on this day.",
            "time_limit": "Appointment time must be between {start} and {end}.",
            "slot_unavailable": "Selected slot is no longer available. Please select another time.",
            "booking_success": "Appointment request submitted successfully! Pending staff confirmation.",
            "booking_failed": "Failed to submit request. Please try again."
        }
    }
    msg_tpl = translations.get(lang, translations["en"]).get(key, key)
    flash(msg_tpl.format(**kwargs), category)


def patient_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "patient":
            flash_message("login_required", "danger")
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
            flash_message("fields_required", "danger")
            return render_template("portal/login.html")

        user = User.query.filter_by(username=username, role="patient").first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role
            session["patient_id"] = user.patient_id
            session.permanent = True
            flash_message("welcome", "success", name=(user.first_name or user.username))
            return redirect(url_for("portal.dashboard"))
        else:
            flash_message("invalid_credentials", "danger")

    return render_template("portal/login.html")


@portal_bp.route("/register", methods=["GET", "POST"])
def register():
    flash_message("registration_disabled", "danger")
    return redirect(url_for("portal.login"))


@portal_bp.route("/logout")
def logout():
    session.clear()
    flash_message("logged_out", "success")
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
            flash_message("all_fields_required", "danger")
            return redirect(url_for("portal.book_appointment"))

        try:
            appointment_date = datetime.strptime(appt_date_raw, "%Y-%m-%dT%H:%M")
        except ValueError:
            try:
                appointment_date = datetime.strptime(appt_date_raw, "%Y-%m-%d %H:%M")
            except ValueError:
                flash_message("invalid_date_format", "danger")
                return redirect(url_for("portal.book_appointment"))

        # Time limits check
        now = datetime.now().replace(second=0, microsecond=0)
        max_date = now + timedelta(days=30)

        if appointment_date < now:
            flash_message("past_date", "danger")
            return redirect(url_for("portal.book_appointment"))

        if appointment_date > max_date:
            flash_message("advance_date", "danger")
            return redirect(url_for("portal.book_appointment"))

        # Working hours and working days checks
        working_days = get_setting("working_days", "0,1,2,3,4,6")
        working_days_list = [d.strip() for d in working_days.split(",") if d.strip()]
        day_str = appointment_date.strftime("%w")

        if day_str not in working_days_list:
            flash_message("clinic_closed", "danger")
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
            flash_message("time_limit", "danger", start=start_str, end=end_str)
            return redirect(url_for("portal.book_appointment"))

        # Check conflict
        from utils.validators import check_appointment_conflict, booking_lock
        with booking_lock:
            conflict = check_appointment_conflict(appointment_date)
            if conflict:
                flash_message("slot_unavailable", "danger")
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
                flash_message("booking_success", "success")
                return redirect(url_for("portal.dashboard"))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Failed to submit appointment request: {e}")
                flash_message("booking_failed", "danger")
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
