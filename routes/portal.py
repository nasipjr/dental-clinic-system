from functools import wraps
from datetime import datetime, timedelta, time
import json
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, jsonify
from models import db, Patient, Appointment, User, Invoice, Payment, PatientFile
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
            "advance_date": "لا يمكن حجز موعد قبل أكثر من {days} يوماً.",
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
            "advance_date": "Appointment cannot be booked more than {days} days in advance.",
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
        
        # Verify the patient still exists in the database (e.g. in case database was cleared/reseeded)
        patient_id = session.get("patient_id")
        patient = Patient.query.get(patient_id)
        if not patient:
            session.clear()
            flash_message("login_required", "danger")
            return redirect(url_for("portal.login"))
            
        return f(*args, **kwargs)
    return decorated_function


@portal_bp.route("/login", methods=["GET", "POST"])
def login():
    return redirect(url_for("auth.login"))


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

        appt_date_raw_normalized = appt_date_raw.replace('ص', 'AM').replace('م', 'PM').strip()
        try:
            appointment_date = datetime.strptime(appt_date_raw_normalized, "%Y-%m-%dT%H:%M")
        except ValueError:
            try:
                appointment_date = datetime.strptime(appt_date_raw_normalized, "%Y-%m-%d %H:%M")
            except ValueError:
                try:
                    appointment_date = datetime.strptime(appt_date_raw_normalized, "%Y-%m-%d %I:%M %p")
                except ValueError:
                    flash_message("invalid_date_format", "danger")
                    return redirect(url_for("portal.book_appointment"))

        # Time limits check
        try:
            booking_window_days = int(get_setting("booking_window_days", "30"))
        except ValueError:
            booking_window_days = 30
        now = datetime.now().replace(second=0, microsecond=0)
        max_date = now + timedelta(days=booking_window_days)

        if appointment_date < now:
            flash_message("past_date", "danger")
            return redirect(url_for("portal.book_appointment"))

        if appointment_date > max_date:
            flash_message("advance_date", "danger", days=booking_window_days)
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
    try:
        booking_window_days = int(get_setting("booking_window_days", "30"))
    except ValueError:
        booking_window_days = 30
    now = datetime.now()
    max_date = now + timedelta(days=booking_window_days)
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
        # Get all occupied slots in the next dynamic days
        try:
            booking_window_days = int(get_setting("booking_window_days", "30"))
        except ValueError:
            booking_window_days = 30
        now = datetime.now()
        limit_date = now + timedelta(days=booking_window_days)
        
        occupied = Appointment.query.filter(
            Appointment.status.in_(["Scheduled", "Pending", "Done"]),
            Appointment.appointment_date >= now.date(),
            Appointment.appointment_date <= limit_date
        ).all()
        
        slots = [appt.appointment_date.strftime('%Y-%m-%d %I:%M %p') for appt in occupied]
        return jsonify(slots)
    except Exception:
        return jsonify([]), 500


@portal_bp.route("/events")
@patient_login_required
def portal_events():
    try:
        # Get all occupied slots in the next dynamic days
        try:
            booking_window_days = int(get_setting("booking_window_days", "30"))
        except ValueError:
            booking_window_days = 30
        now = datetime.now()
        limit_date = now + timedelta(days=booking_window_days)
        
        occupied = Appointment.query.filter(
            Appointment.status.in_(["Scheduled", "Pending", "Done"]),
            Appointment.appointment_date >= now.date(),
            Appointment.appointment_date <= limit_date
        ).all()
        
        try:
            duration = int(get_setting("default_appointment_duration", "30"))
        except ValueError:
            duration = 30
            
        events = []
        for appt in occupied:
            start_iso = appt.appointment_date.isoformat()
            end_iso = (appt.appointment_date + timedelta(minutes=duration)).isoformat()
            
            events.append({
                "title": "Reserved",
                "start": start_iso,
                "end": end_iso,
                "color": "#6c757d",  # Muted grey color for occupied slot
                "classNames": ["fc-event-reserved"],
                "extendedProps": {
                    "status": "Reserved"
                }
            })
            
        return jsonify(events)
    except Exception:
        current_app.logger.exception("Failed to fetch portal calendar events")
        return jsonify([]), 500


@portal_bp.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
@patient_login_required
def cancel_appointment(appointment_id):
    patient_id = session.get("patient_id")
    appointment = Appointment.query.filter_by(id=appointment_id, patient_id=patient_id).first_or_404()
    
    lang = request.cookies.get('lang', 'en')
    
    if appointment.status not in ["Scheduled", "Pending"]:
        deny_msg = {
            "ar": "لا يمكنك إلغاء المواعيد المكتملة أو الملغاة بالفعل.",
            "en": "You cannot cancel appointments that are already completed or cancelled."
        }.get(lang, "You cannot cancel this appointment.")
        flash(deny_msg, "danger")
        return redirect(url_for("portal.dashboard"))
    
    try:
        old_status = appointment.status
        appointment.status = "Cancelled"
        db.session.commit()
        
        current_app.logger.info(f"Appointment {appointment.id} cancelled by patient {patient_id}")
        
        # Notify patient through services
        from services.notification_service import notify_appointment_cancellation
        notify_appointment_cancellation(appointment)
        
        success_msg = {
            "ar": "تم إلغاء الموعد بنجاح وتم إشعار العيادة.",
            "en": "Appointment cancelled successfully and the clinic has been notified."
        }.get(lang, "Appointment cancelled successfully.")
        flash(success_msg, "success")
        
        # Send Email Notification to the Clinic/Doctor
        clinic_email = get_setting("clinic_email", "")
        if clinic_email:
            from utils.notification_helper import send_smtp_email
            patient = appointment.patient
            formatted_date = appointment.appointment_date.strftime('%Y-%m-%d %I:%M %p')
            
            subject = f"Appointment Cancelled - Patient: {patient.first_name} {patient.last_name}"
            body = (
                f"Dear Doctor,\n\n"
                f"This is an automated notification to inform you that the following appointment has been cancelled by the patient:\n\n"
                f"Patient Name: {patient.first_name} {patient.last_name}\n"
                f"Phone: {patient.phone or 'N/A'}\n"
                f"Appointment Date/Time: {formatted_date}\n"
                f"Reason for appointment: {appointment.reason}\n"
                f"Previous Status: {old_status}\n\n"
                f"This time slot is now open and available for booking on the calendar.\n\n"
                f"Best regards,\nDental Clinic Management System"
            )
            
            import threading
            app = current_app._get_current_object()
            def send_email_async(app_context):
                with app_context:
                    try:
                        send_smtp_email(clinic_email, subject, body)
                    except Exception as ex:
                        app.logger.error(f"Failed to send cancellation notification email to doctor: {ex}")
            
            threading.Thread(target=send_email_async, args=(app.app_context(),), daemon=True).start()
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Failed to cancel appointment {appointment_id}: {e}")
        error_msg = {
            "ar": "حدث خطأ أثناء إلغاء الموعد. يرجى المحاولة مرة أخرى.",
            "en": "An error occurred while cancelling the appointment. Please try again."
        }.get(lang, "An error occurred.")
        flash(error_msg, "danger")
        
    return redirect(url_for("portal.dashboard"))


@portal_bp.route("/billing")
@patient_login_required
def billing():
    patient_id = session.get("patient_id")
    patient = Patient.query.get_or_404(patient_id)
    invoices = Invoice.query.filter_by(patient_id=patient_id).order_by(Invoice.issue_date.desc()).all()
    payments = Payment.query.filter_by(patient_id=patient_id).order_by(Payment.payment_date.desc()).all()
    
    return render_template(
        "portal/billing.html",
        patient=patient,
        invoices=invoices,
        payments=payments
    )


@portal_bp.route("/invoices/<int:invoice_id>")
@patient_login_required
def view_invoice(invoice_id):
    patient_id = session.get("patient_id")
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Security check: verify this invoice belongs to the patient
    if invoice.patient_id != patient_id:
        flash("You do not have permission to view this invoice.", "danger")
        return redirect(url_for("portal.billing"))
        
    return render_template(
        "portal/invoice_detail.html",
        invoice=invoice,
        appointment=invoice.appointment,
        patient=invoice.patient,
        treatments=invoice.treatments
    )


@portal_bp.route("/medical-history")
@patient_login_required
def medical_history():
    patient_id = session.get("patient_id")
    patient = Patient.query.get_or_404(patient_id)
    
    treatments = sorted(patient.treatments, key=lambda t: t.treatment_date, reverse=True)
    files = sorted(patient.files, key=lambda f: f.upload_date, reverse=True)
    
    return render_template(
        "portal/medical_history.html",
        patient=patient,
        treatments=treatments,
        patient_files=files
    )


@portal_bp.route("/logout-confirm")
@patient_login_required
def logout_confirm():
    return render_template("portal/logout_confirm.html")


@portal_bp.route("/files/<int:file_id>")
@patient_login_required
def view_file(file_id):
    import os
    from flask import send_from_directory
    
    patient_file = PatientFile.query.get_or_404(file_id)
    if patient_file.patient_id != session.get("patient_id"):
        flash("Unauthorized access." if request.cookies.get('lang', 'en') == 'en' else "وصول غير مصرح به.", "danger")
        return redirect(url_for("portal.medical_history"))
        
    disk_path = os.path.join(current_app.static_folder, patient_file.filepath)
    if not os.path.exists(disk_path):
        flash("File not found on server." if request.cookies.get('lang', 'en') == 'en' else "الملف غير موجود على الخادم.", "danger")
        return redirect(url_for("portal.medical_history"))
        
    return send_from_directory(
        os.path.join(current_app.static_folder, "uploads", "patients"),
        os.path.basename(patient_file.filepath)
    )


@portal_bp.route("/files/<int:file_id>/download")
@patient_login_required
def download_file(file_id):
    import os
    from flask import send_from_directory
    
    patient_file = PatientFile.query.get_or_404(file_id)
    if patient_file.patient_id != session.get("patient_id"):
        flash("Unauthorized access." if request.cookies.get('lang', 'en') == 'en' else "وصول غير مصرح به.", "danger")
        return redirect(url_for("portal.medical_history"))
        
    disk_path = os.path.join(current_app.static_folder, patient_file.filepath)
    if not os.path.exists(disk_path):
        flash("File not found on server." if request.cookies.get('lang', 'en') == 'en' else "الملف غير موجود على الخادم.", "danger")
        return redirect(url_for("portal.medical_history"))
        
    return send_from_directory(
        os.path.join(current_app.static_folder, "uploads", "patients"),
        os.path.basename(patient_file.filepath),
        as_attachment=True,
        download_name=patient_file.filename
    )
