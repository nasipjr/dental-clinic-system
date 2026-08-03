import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from utils.settings_helper import get_setting, set_setting, get_treatment_prices, DEFAULT_SETTINGS
from utils.auth_helper import role_required

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings", methods=["GET", "POST"])
@role_required("admin")
def settings_page():
    if request.method == "POST":
        current_app.logger.info("Updating system settings")
        try:
            # 1. Update general, calendar, and billing settings
            for key in ["clinic_name", "clinic_phone", "clinic_email", "clinic_address", 
                        "working_hours_start", "working_hours_end", "default_appointment_duration", 
                        "auto_cancel_expired_minutes",
                        "currency_symbol", "booking_window_days", "anesthesia_needle_price"]:
                val = request.form.get(key, "").strip()
                if key == "booking_window_days":
                    try:
                        ival = int(val)
                        if ival <= 0:
                            raise ValueError
                    except ValueError:
                        flash("Booking window days must be a positive integer.", "danger")
                        return redirect(url_for("settings.settings_page") + "#tab-calendar")
                if key == "anesthesia_needle_price":
                    try:
                        fval = float(val)
                        if fval < 0:
                            raise ValueError
                    except ValueError:
                        flash("Anesthesia needle price must be a non-negative number.", "danger")
                        return redirect(url_for("settings.settings_page") + "#tab-treatments")
                set_setting(key, val)

            # 1b. Update notification provider credentials and templates
            for key in ["telegram_bot_token", "telegram_24h_template", "telegram_2h_template",
                        "telegram_cancel_template", "telegram_reschedule_template",
                        "commpeak_api_key", "commpeak_stream_id",
                        "sms_24h_template", "sms_2h_template",
                        "sms_cancel_template", "sms_reschedule_template",
                        "smtp_host", "smtp_port", "smtp_user", "smtp_password", "smtp_from_email",
                        "email_24h_subject", "email_24h_template", "email_2h_subject", "email_2h_template",
                        "email_cancel_subject", "email_cancel_template", "email_reschedule_subject", "email_reschedule_template"]:
                val = request.form.get(key, "").strip()
                set_setting(key, val)

            sms_enabled      = "true" if request.form.get("notification_enable_sms")      else "false"
            telegram_enabled = "true" if request.form.get("notification_enable_telegram") else "false"
            email_enabled    = "true" if request.form.get("notification_enable_email")    else "false"
            set_setting("notification_enable_sms",      sms_enabled)
            set_setting("notification_enable_telegram", telegram_enabled)
            set_setting("notification_enable_email",    email_enabled)

            telegram_24h_enabled = "true" if request.form.get("telegram_24h_enabled") else "false"
            telegram_2h_enabled  = "true" if request.form.get("telegram_2h_enabled")  else "false"
            set_setting("telegram_24h_enabled", telegram_24h_enabled)
            set_setting("telegram_2h_enabled",  telegram_2h_enabled)

            email_24h_enabled = "true" if request.form.get("email_24h_enabled") else "false"
            email_2h_enabled  = "true" if request.form.get("email_2h_enabled")  else "false"
            set_setting("email_24h_enabled", email_24h_enabled)
            set_setting("email_2h_enabled",  email_2h_enabled)

            sms_24h_enabled = "true" if request.form.get("sms_24h_enabled") else "false"
            sms_2h_enabled  = "true" if request.form.get("sms_2h_enabled")  else "false"
            set_setting("sms_24h_enabled", sms_24h_enabled)
            set_setting("sms_2h_enabled",  sms_2h_enabled)

            sms_cancel_enabled = "true" if request.form.get("sms_cancel_enabled") else "false"
            sms_reschedule_enabled = "true" if request.form.get("sms_reschedule_enabled") else "false"
            set_setting("sms_cancel_enabled", sms_cancel_enabled)
            set_setting("sms_reschedule_enabled", sms_reschedule_enabled)

            telegram_cancel_enabled = "true" if request.form.get("telegram_cancel_enabled") else "false"
            telegram_reschedule_enabled = "true" if request.form.get("telegram_reschedule_enabled") else "false"
            set_setting("telegram_cancel_enabled", telegram_cancel_enabled)
            set_setting("telegram_reschedule_enabled", telegram_reschedule_enabled)

            email_cancel_enabled = "true" if request.form.get("email_cancel_enabled") else "false"
            email_reschedule_enabled = "true" if request.form.get("email_reschedule_enabled") else "false"
            set_setting("email_cancel_enabled", email_cancel_enabled)
            set_setting("email_reschedule_enabled", email_reschedule_enabled)
            
            # Save working days checklist as a comma-separated string
            working_days_list = request.form.getlist("working_days")
            set_setting("working_days", ",".join(working_days_list))
            
            # 2. Update treatment prices (only if present in request to prevent clearing on partial form submissions)
            if "procedure_names[]" in request.form:
                names = request.form.getlist("procedure_names[]")
                prices = request.form.getlist("procedure_prices[]")
                
                treatment_dict = {}
                for name, price in zip(names, prices):
                    name = name.strip()
                    if name:
                        if len(name) > 200:
                            flash("Procedure name cannot exceed 200 characters.", "danger")
                            return redirect(url_for("settings.settings_page") + "#tab-treatments")
                        try:
                            # Convert price to number
                            price_clean = price.strip().replace(",", "")
                            price_val = float(price_clean) if '.' in price_clean else int(price_clean)
                            if price_val < 0:
                                price_val = 0
                        except ValueError:
                            price_val = 0
                        treatment_dict[name] = price_val
                
                # Guarantee essential system procedures (like 'قلع سن' and 'معالجة ما بعد القلع') are always preserved
                if "قلع سن" not in treatment_dict:
                    treatment_dict["قلع سن"] = 80000
                if "معالجة ما بعد القلع" not in treatment_dict:
                    treatment_dict["معالجة ما بعد القلع"] = 30000

                set_setting("treatment_prices", json.dumps(treatment_dict))
            
            is_ar = request.cookies.get("lang") == "ar" or request.cookies.get("lang") != "en"
            flash("تم تحديث الإعدادات بنجاح!" if is_ar else "Settings updated successfully!", "success")
            current_app.logger.info("Settings updated successfully")
        except Exception:
            current_app.logger.exception("Failed to update system settings")
            is_ar = request.cookies.get("lang") == "ar" or request.cookies.get("lang") != "en"
            flash("فشل في تحديث الإعدادات. يرجى المحاولة مرة أخرى." if is_ar else "Failed to update settings. Please try again.", "danger")
            
        active_tab = request.form.get("active_tab", "").strip()
        if active_tab and active_tab.startswith("#"):
            return redirect(url_for("settings.settings_page") + active_tab)
        return redirect(url_for("settings.settings_page"))

    # GET request: load values
    settings_data = {}
    for key in DEFAULT_SETTINGS.keys():
        settings_data[key] = get_setting(key)
        
    treatment_prices = get_treatment_prices()
    
    from models import User, NotificationLog, StaffSalary
    users = User.query.all()
    notifications = NotificationLog.query.order_by(NotificationLog.sent_at.desc()).limit(100).all()

    # Salary management: staff eligible (doctors + receptionists), keyed configs
    salary_configs = {sc.user_id: sc for sc in StaffSalary.query.all()}
    salary_staff = User.query.filter(User.role.in_(["doctor", "receptionist"])).order_by(User.role, User.first_name).all()

    # Read backups
    import os
    from utils.backup_helper import BACKUP_DIR
    from datetime import datetime
    backups_list = []
    if os.path.exists(BACKUP_DIR):
        for f in os.listdir(BACKUP_DIR):
            p = os.path.join(BACKUP_DIR, f)
            if os.path.isfile(p) and f.startswith('backup_') and (f.endswith('.sql') or f.endswith('.db')):
                stats = os.stat(p)
                size_kb = round(stats.st_size / 1024, 2)
                mtime = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %I:%M:%S %p')
                backups_list.append({
                    'filename': f,
                    'mtime': mtime,
                    'size': f"{size_kb} KB"
                })
        # Sort backups by date descending (newest first)
        backups_list.sort(key=lambda x: x['mtime'], reverse=True)
    
    from utils.license_helper import get_current_license_status
    license_info = get_current_license_status()

    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    host_parts = request.host.split(":")
    port = host_parts[1] if len(host_parts) > 1 else "5000"
    server_network_url = f"http://{local_ip}:{port}"

    return render_template(
        "settings/settings.html",
        settings=settings_data,
        treatment_prices=treatment_prices,
        users=users,
        backups=backups_list,
        notifications=notifications,
        license_info=license_info,
        salary_configs=salary_configs,
        salary_staff=salary_staff,
        server_network_url=server_network_url
    )


@settings_bp.route("/appearance-settings")
@role_required("receptionist")
def appearance_settings_page():
    """Appearance-only settings page for the receptionist role."""
    return render_template("settings/nurse_settings.html")


@settings_bp.route("/settings/users/add", methods=["POST"])
@role_required("admin")
def add_user():
    from models import db, User
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "receptionist").strip()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()

    if not username or not password:
        flash("Username and Password are required.", "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    is_ar = request.cookies.get('lang', 'ar') != 'en'

    if not username or not password or not role:
        msg = "جميع الحقول المطلوبة يجب تعبئتها." if is_ar else "All required fields must be provided."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    if len(username) > 80:
        msg = "اسم المستخدم لا يمكن أن يتجاوز 80 حرفاً." if is_ar else "Username cannot exceed 80 characters."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    if len(password) < 6:
        msg = "كلمة السر يجب أن تكون 6 أحرف على الأقل." if is_ar else "Password must be at least 6 characters long."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    if role not in {"admin", "doctor", "receptionist"}:
        msg = "دور المستخدم غير صالح." if is_ar else "Invalid user role specified."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    if len(first_name) > 100 or len(last_name) > 100:
        msg = "الاسم الأول والاسم الأخير لا يمكن أن يتجاوزا 100 حرف." if is_ar else "First name and Last name cannot exceed 100 characters."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    existing = User.query.filter_by(username=username).first()
    if existing:
        msg = "اسم المستخدم موجود مسبقاً." if is_ar else "Username already exists."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page"))

    try:
        new_user = User(
            username=username,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        msg = f"تم إنشاء حساب المستخدم '{username}' بنجاح!" if is_ar else f"User account '{username}' created successfully!"
        flash(msg, "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to add user: {e}")
        msg = "فشل إنشاء حساب المستخدم." if is_ar else "Failed to create user account."
        flash(msg, "danger")

    return redirect(url_for("settings.settings_page") + "#tab-users")


@settings_bp.route("/settings/users/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def delete_user(user_id):
    from models import db, User
    from flask import session
    is_ar = request.cookies.get('lang', 'ar') != 'en'
    
    # Prevent deleting oneself
    if session.get("user_id") == user_id:
        msg = "لا يمكنك حذف حسابك الحالي." if is_ar else "You cannot delete your own account."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    user = User.query.get(user_id)
    if not user:
        msg = "المستخدم غير موجود." if is_ar else "User not found."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    try:
        db.session.delete(user)
        db.session.commit()
        msg = f"تم حذف حساب المستخدم '{user.username}' بنجاح." if is_ar else f"User account '{user.username}' deleted successfully."
        flash(msg, "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete user: {e}")
        msg = "فشل حذف حساب المستخدم." if is_ar else "Failed to delete user account."
        flash(msg, "danger")

    return redirect(url_for("settings.settings_page") + "#tab-users")


@settings_bp.route("/settings/users/<int:user_id>/edit", methods=["POST"])
@role_required("admin")
def edit_user(user_id):
    from models import db, User
    from flask import session
    is_ar = request.cookies.get('lang', 'ar') != 'en'

    user = User.query.get(user_id)
    if not user:
        msg = "المستخدم غير موجود." if is_ar else "User not found."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "").strip()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()

    if not username:
        msg = "اسم المستخدم مطلوب." if is_ar else "Username is required."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    if len(username) > 80:
        msg = "اسم المستخدم لا يمكن أن يتجاوز 80 حرفاً." if is_ar else "Username cannot exceed 80 characters."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    if password and len(password) < 6:
        msg = "كلمة السر يجب أن تكون 6 أحرف على الأقل." if is_ar else "Password must be at least 6 characters long."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    if role and role not in {"admin", "doctor", "receptionist", "patient"}:
        msg = "دور المستخدم غير صالح." if is_ar else "Invalid user role specified."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    if len(first_name) > 100 or len(last_name) > 100:
        msg = "الاسم الأول والاسم الأخير لا يمكن أن يتجاوزا 100 حرف." if is_ar else "First name and Last name cannot exceed 100 characters."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    # Check if username is taken by another user
    existing = User.query.filter(User.username == username, User.id != user_id).first()
    if existing:
        msg = "اسم المستخدم مستخدم مسبقاً من قِبل حساب آخر." if is_ar else "Username already taken by another user."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    try:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name

        if role:
            user.role = role

        # Only update password if provided
        if password:
            user.set_password(password)

        db.session.commit()
        msg = f"تم تحديث حساب المستخدم '{username}' بنجاح!" if is_ar else f"User account '{username}' updated successfully!"
        flash(msg, "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update user: {e}")
        msg = "فشل تحديث حساب المستخدم." if is_ar else "Failed to update user account."
        flash(msg, "danger")

    return redirect(url_for("settings.settings_page") + "#tab-users")


@settings_bp.route("/settings/backups/create", methods=["POST"])
@role_required("admin")
def create_backup():
    is_ar = request.cookies.get('lang', 'ar') != 'en'
    try:
        from utils.backup_helper import run_database_backup
        filename = run_database_backup()
        msg = f"تم إنشاء النسخة الاحتياطية بنجاح: {filename}" if is_ar else f"Backup created successfully: {filename}"
        flash(msg, "success")
    except Exception as e:
        current_app.logger.exception("Failed to create database backup")
        msg = f"فشل إنشاء النسخة الاحتياطية: {e}" if is_ar else f"Failed to create database backup: {e}"
        flash(msg, "danger")
    return redirect(url_for("settings.settings_page") + "#tab-backups")


@settings_bp.route("/settings/backups/<filename>/download")
@role_required("admin")
def download_backup(filename):
    import os
    from flask import send_from_directory, abort
    from utils.backup_helper import BACKUP_DIR
    is_ar = request.cookies.get('lang', 'ar') != 'en'
    
    # Secure filename check to prevent directory traversal
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        abort(400, "Invalid backup filename.")
        
    backup_path = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_path) and os.path.isfile(backup_path):
        return send_from_directory(BACKUP_DIR, filename, as_attachment=True)
    else:
        msg = "ملف النسخة الاحتياطية غير موجود." if is_ar else "Backup file not found."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-backups")


@settings_bp.route("/settings/backups/<filename>/delete", methods=["POST"])
@role_required("admin")
def delete_backup(filename):
    import os
    from flask import abort
    from utils.backup_helper import BACKUP_DIR
    is_ar = request.cookies.get('lang', 'ar') != 'en'
    
    # Secure filename check to prevent directory traversal
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        abort(400, "Invalid backup filename.")
        
    backup_path = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_path) and os.path.isfile(backup_path):
        try:
            os.remove(backup_path)
            msg = "تم حذف ملف النسخة الاحتياطية بنجاح." if is_ar else "Backup file deleted successfully."
            flash(msg, "success")
        except Exception as e:
            current_app.logger.error(f"Failed to delete backup file: {e}")
            msg = "فشل حذف ملف النسخة الاحتياطية." if is_ar else "Failed to delete backup file."
            flash(msg, "danger")
    else:
        msg = "ملف النسخة الاحتياطية غير موجود." if is_ar else "Backup file not found."
        flash(msg, "danger")
    return redirect(url_for("settings.settings_page") + "#tab-backups")


# ─────────────────────────────────────────────────────────────────────────────
#  Test Notification Endpoints — called via AJAX from the settings page
# ─────────────────────────────────────────────────────────────────────────────

@settings_bp.route("/settings/test-sms", methods=["POST"])
@role_required("admin")
def test_sms():
    from flask import jsonify
    from utils.notification_helper import send_commpeak_sms
    phone = request.form.get("phone", "").strip()
    api_key = request.form.get("api_key", "").strip() or None
    stream_id = request.form.get("stream_id", "").strip() or None

    if not phone:
        return jsonify({"success": False, "message": "Please enter a phone number."})
    body = "Test SMS from Dental Clinic MS. CommPeak is working!"
    success, msg = send_commpeak_sms(phone, body, api_key=api_key, stream_id=stream_id)
    return jsonify({"success": success, "message": msg})


@settings_bp.route("/settings/test-email", methods=["POST"])
@role_required("admin")
def test_email():
    from flask import jsonify
    from utils.notification_helper import send_smtp_email
    email = request.form.get("email", "").strip()
    smtp_host = request.form.get("smtp_host", "").strip() or None
    smtp_port = request.form.get("smtp_port", "").strip() or None
    smtp_user = request.form.get("smtp_user", "").strip() or None
    smtp_password = request.form.get("smtp_password", "").strip() or None
    smtp_from_email = request.form.get("smtp_from_email", "").strip() or None

    if not email:
        return jsonify({"success": False, "message": "Please enter an email address."})
    success, msg = send_smtp_email(
        email,
        "Test Email — Dental Clinic MS",
        "Test email from Dental Clinic MS. SMTP is working!",
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        from_email=smtp_from_email
    )
    return jsonify({"success": success, "message": msg})


@settings_bp.route("/settings/test-telegram", methods=["POST"])
@role_required("admin")
def test_telegram():
    from flask import jsonify
    from utils.notification_helper import send_telegram_message
    chat_id = request.form.get("chat_id", "").strip()
    bot_token = request.form.get("bot_token", "").strip() or None

    if not chat_id:
        return jsonify({"success": False, "message": "Please enter a Chat ID."})
    body = "Test from Dental Clinic MS. Telegram Bot is working!"
    success, msg = send_telegram_message(chat_id, body, bot_token=bot_token)
    return jsonify({"success": success, "message": msg})


@settings_bp.route("/settings/check-update", methods=["POST"])
@role_required("admin")
def check_system_update():
    """Triggers an automated git pull to update system code and dependencies."""
    from flask import jsonify
    import subprocess
    import sys
    import os

    current_app.logger.info("Manual system update triggered by admin")

    try:
        # Execute git pull in project root
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        stdout = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""

        if result.returncode != 0:
            current_app.logger.error(f"Git pull error: {stderr}")
            return jsonify({
                "success": False,
                "message": f"حدث خطأ أثناء التحديث: {stderr or 'فشل سحب التحديثات من المستودع.'}"
            })

        if "Already up to date" in stdout or "Already up-to-date" in stdout:
            return jsonify({
                "success": True,
                "updated": False,
                "message": "النظام يعمل بأحدث إصدار بالفعل! لا توجد تحديثات جديدة حالياً. ✅"
            })
        else:
            # Optionally install missing/updated packages
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    capture_output=True,
                    text=True,
                    timeout=90
                )
            except Exception as pe:
                current_app.logger.warning(f"Pip install warning during update: {pe}")

            # Touch WSGI file if running on PythonAnywhere to reload app
            try:
                wsgi_candidates = [
                    "/var/www/nasipjr_pythonanywhere_com_wsgi.py",
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "wsgi.py")
                ]
                for wsgi_path in wsgi_candidates:
                    if os.path.exists(wsgi_path):
                        os.utime(wsgi_path, None)
                        break
            except Exception:
                pass

            return jsonify({
                "success": True,
                "updated": True,
                "message": f"🎉 تم تحديث النظام بنجاح إلى أحدث إصدار!\n{stdout}"
            })

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "message": "انتهت مهلة التحديث (Timeout). يرجى التأكد من الاتصال بالإنترنت والإعادة."
        })
    except Exception as e:
        current_app.logger.exception(f"Unexpected error during system update: {e}")
        return jsonify({
            "success": False,
            "message": f"حدث خطأ أثناء تنفيذ التحديث: {str(e)}"
        })


@settings_bp.route("/settings/reset-clinic", methods=["POST"])
@role_required("admin")
def reset_clinic():
    """Resets all operational clinic database records (patients, appointments, treatments, invoices, payments, expenses, etc.)
    while preserving system settings, notification configurations/tokens, and user accounts.
    Requires admin username & password verification."""
    from models import (
        db, User, Patient, Appointment, Treatment, ToothHistory,
        Invoice, Payment, PaymentAllocation, PatientFile, NotificationLog, Expense
    )
    is_ar = request.cookies.get('lang', 'ar') != 'en'

    admin_username = request.form.get("admin_username", "").strip()
    admin_password = request.form.get("admin_password", "").strip()

    if not admin_username or not admin_password:
        msg = "يرجى إدخال اسم المستخدم وكلمة المرور الخاصة بالمدير." if is_ar else "Admin username and password are required."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page"))

    # Verify admin user credentials
    admin_user = User.query.filter_by(username=admin_username).first()
    if not admin_user or admin_user.role != "admin" or not admin_user.check_password(admin_password):
        current_app.logger.warning(f"Failed clinic reset attempt: invalid admin credentials for username '{admin_username}'.")
        msg = "اسم المستخدم أو كلمة المرور الخاصة بالمدير غير صحيحة، أو أنك لا تملك صلاحيات مدير." if is_ar else "Invalid admin username or password, or insufficient permissions."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page"))

    try:
        current_app.logger.warning(f"Admin '{admin_username}' initiated full clinic database reset.")

        # Disable foreign key checks for reset transaction
        try:
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0;"))
        except Exception:
            pass
        try:
            db.session.execute(db.text("PRAGMA foreign_keys = OFF;"))
        except Exception:
            pass

        # 1. Unlink patient user accounts from Patient table so User rows aren't restricted by FK
        User.query.update({User.patient_id: None}, synchronize_session=False)

        # 2. Delete patient portal user accounts if any exist (role == 'patient')
        User.query.filter_by(role='patient').delete(synchronize_session=False)

        # 3. Delete clinical and operational data in FK-safe order
        db.session.query(PaymentAllocation).delete(synchronize_session=False)
        db.session.query(Payment).delete(synchronize_session=False)
        db.session.query(Invoice).delete(synchronize_session=False)
        db.session.query(Treatment).delete(synchronize_session=False)
        db.session.query(Appointment).delete(synchronize_session=False)
        db.session.query(ToothHistory).delete(synchronize_session=False)
        db.session.query(PatientFile).delete(synchronize_session=False)
        db.session.query(NotificationLog).delete(synchronize_session=False)
        db.session.query(Expense).delete(synchronize_session=False)
        db.session.query(Patient).delete(synchronize_session=False)

        # Re-enable foreign key checks
        try:
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1;"))
        except Exception:
            pass
        try:
            db.session.execute(db.text("PRAGMA foreign_keys = ON;"))
        except Exception:
            pass

        db.session.commit()

        # 4. Remove physical patient upload files if present
        import os
        import shutil
        uploads_dir = os.path.join(current_app.root_path, "static", "uploads")
        if os.path.exists(uploads_dir):
            for item in os.listdir(uploads_dir):
                item_path = os.path.join(uploads_dir, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as fe:
                    current_app.logger.warning(f"Could not delete file {item_path}: {fe}")

        msg = "تمت إعادة ضبط العيادة وتصفير كافة البيانات بنجاح، مع الاحتفاظ بجميع الإعدادات والتوكنز وحسابات المستخدمين." if is_ar else "Clinic database reset successfully. All settings, tokens, and user accounts have been preserved."
        flash(msg, "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Error resetting clinic database: {e}")
        msg = f"حدث خطأ أثناء تصفير قاعدة البيانات: {str(e)}" if is_ar else f"Error resetting clinic database: {str(e)}"
        flash(msg, "danger")

    return redirect(url_for("settings.settings_page"))


@settings_bp.route("/settings/restore-backup", methods=["POST"])
@settings_bp.route("/settings/restore-latest-backup", methods=["POST"])
@role_required("admin")
def restore_backup():
    """Restores the database from a selected backup file in backups/ directory.
    Requires admin username & password verification."""
    import os
    from models import User
    from utils.backup_helper import list_backups, restore_database_backup

    is_ar = request.cookies.get('lang', 'ar') != 'en'

    admin_username = request.form.get("admin_username", "").strip()
    admin_password = request.form.get("admin_password", "").strip()
    backup_filename = request.form.get("backup_filename", "").strip()

    if not admin_username or not admin_password:
        msg = "يرجى إدخال اسم المستخدم وكلمة المرور الخاصة بالمدير." if is_ar else "Admin username and password are required."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page"))

    # Verify admin user credentials
    admin_user = User.query.filter_by(username=admin_username).first()
    if not admin_user or admin_user.role != "admin" or not admin_user.check_password(admin_password):
        current_app.logger.warning(f"Failed database restore attempt: invalid admin credentials for username '{admin_username}'.")
        msg = "اسم المستخدم أو كلمة المرور الخاصة بالمدير غير صحيحة، أو أنك لا تملك صلاحيات مدير." if is_ar else "Invalid admin username or password, or insufficient permissions."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page"))

    backups = list_backups()
    if not backups:
        msg = "لم يتم العثور على أي ملف نسخة احتياطية لاستعادته." if is_ar else "No backup file found to restore from."
        flash(msg, "warning")
        return redirect(url_for("settings.settings_page"))

    if not backup_filename:
        backup_filename = backups[0]["filename"]
    else:
        # Sanitize filename
        backup_filename = os.path.basename(backup_filename)
        valid_files = [b["filename"] for b in backups]
        if backup_filename not in valid_files:
            msg = "ملف النسخة الاحتياطية المحددة غير موجود." if is_ar else "Specified backup file not found."
            flash(msg, "danger")
            return redirect(url_for("settings.settings_page"))

    try:
        current_app.logger.warning(f"Admin '{admin_username}' requested database restore from backup file '{backup_filename}'.")
        restore_database_backup(backup_filename)
        msg = f"تمت استعادة كافة البيانات بنجاح من النسخة الاحتياطية: ({backup_filename})" if is_ar else f"Data restored successfully from backup: ({backup_filename})"
        flash(msg, "success")
    except Exception as e:
        current_app.logger.exception(f"Error restoring database from {backup_filename}: {e}")
        msg = f"حدث خطأ أثناء استعادة النسخة الاحتياطية: {str(e)}" if is_ar else f"Error restoring database: {str(e)}"
        flash(msg, "danger")

    return redirect(url_for("settings.settings_page"))


# ──────────────────────────────────────────────────────────────────────────────
# Staff Salary Management Routes
# ──────────────────────────────────────────────────────────────────────────────

@settings_bp.route("/settings/salary/save", methods=["POST"])
@role_required("admin")
def save_staff_salary():
    """Save or update salary config for a specific staff member."""
    from models import db, User, StaffSalary
    is_ar = request.cookies.get("lang", "ar") != "en"
    try:
        user_id = int(request.form.get("user_id", 0))
        salary_type = request.form.get("salary_type", "fixed").strip()
        amount_str = request.form.get("amount", "0").strip()
        deduction_day = int(request.form.get("deduction_day", 1))
        is_active = request.form.get("is_active") == "1"
        notes = request.form.get("notes", "").strip()

        if salary_type not in ("fixed", "percentage"):
            salary_type = "fixed"
        deduction_day = max(1, min(28, deduction_day))

        try:
            amount = float(amount_str.replace(",", ""))
            if amount < 0:
                amount = 0.0
        except ValueError:
            amount = 0.0

        user = User.query.get_or_404(user_id)
        if user.role not in ("doctor", "receptionist"):
            flash("يمكن تعيين الراتب للأطباء والموظفين فقط." if is_ar else "Salaries can only be set for doctors and receptionists.", "danger")
            return redirect(url_for("settings.settings_page") + "#tab-billing")

        existing = StaffSalary.query.filter_by(user_id=user_id).first()
        if existing:
            existing.salary_type = salary_type
            existing.amount = amount
            existing.deduction_day = deduction_day
            existing.is_active = is_active
            existing.notes = notes
        else:
            new_salary = StaffSalary(
                user_id=user_id,
                salary_type=salary_type,
                amount=amount,
                deduction_day=deduction_day,
                is_active=is_active,
                notes=notes
            )
            db.session.add(new_salary)

        db.session.commit()
        current_app.logger.info(f"Salary config saved for user_id={user_id}")
        flash("تم حفظ إعدادات الراتب بنجاح." if is_ar else "Salary config saved successfully.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to save staff salary")
        flash("فشل في حفظ إعدادات الراتب." if is_ar else "Failed to save salary config.", "danger")

    return redirect(url_for("settings.settings_page") + "#tab-billing")


@settings_bp.route("/settings/salary/deduct/<int:user_id>", methods=["POST"])
@role_required("admin")
def deduct_salary_now(user_id):
    """Immediately deduct salary for a staff member and record it as an Expense."""
    from models import db, User, StaffSalary, Expense, Invoice, Appointment
    from sqlalchemy import func
    from datetime import datetime
    is_ar = request.cookies.get("lang", "ar") != "en"
    try:
        salary_cfg = StaffSalary.query.filter_by(user_id=user_id).first_or_404()
        user = User.query.get_or_404(user_id)

        amount_to_deduct = 0.0
        if salary_cfg.salary_type == "fixed":
            amount_to_deduct = float(salary_cfg.amount)
        else:
            # percentage of total invoiced amount for completed appointments of this doctor
            from models import Treatment
            total_invoiced = float(
                db.session.query(func.coalesce(func.sum(Invoice.total_amount_col), 0.0))
                .join(Invoice.appointment)
                .filter(Appointment.doctor_id == user_id, Appointment.status == "Done")
                .scalar() or 0.0
            )
            # Fallback: sum treatment costs
            total_invoiced = float(
                db.session.query(func.coalesce(func.sum(Treatment.total_cost), 0.0))
                .filter(Treatment.doctor_id == user_id)
                .scalar() or 0.0
            )
            amount_to_deduct = round(total_invoiced * float(salary_cfg.amount) / 100.0, 2)

        if amount_to_deduct <= 0:
            flash("مبلغ الراتب يجب أن يكون أكبر من صفر." if is_ar else "Salary amount must be greater than zero.", "warning")
            return redirect(url_for("settings.settings_page") + "#tab-billing")

        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
        role_label = "طبيب" if user.role == "doctor" else "موظف استقبال"
        note_text = f"راتب {role_label}: {full_name}" if is_ar else f"Salary - {user.role.capitalize()}: {full_name}"

        expense = Expense(
            category="Salaries",
            amount=amount_to_deduct,
            expense_date=datetime.now().date(),
            notes=note_text
        )
        db.session.add(expense)

        # Record this month as deducted
        salary_cfg.last_deducted_month = datetime.now().strftime("%Y-%m")
        db.session.commit()

        current_app.logger.info(f"Salary deducted for user_id={user_id} amount={amount_to_deduct}")
        flash(f"{'تم خصم راتب' if is_ar else 'Salary deducted'}: {full_name} — {amount_to_deduct}", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to deduct salary for user_id={user_id}")
        flash("فشل في خصم الراتب." if is_ar else "Failed to deduct salary.", "danger")

    return redirect(url_for("settings.settings_page") + "#tab-billing")


def auto_process_salary_deductions(app):
    """
    Called on app startup. Checks all active salary configs whose deduction_day
    matches today's day and last_deducted_month != current month, then auto-deducts.
    """
    from datetime import datetime
    with app.app_context():
        try:
            from models import db, User, StaffSalary, Expense, Treatment
            from sqlalchemy import func
            today = datetime.now()
            current_month = today.strftime("%Y-%m")
            current_day = today.day

            due_salaries = StaffSalary.query.filter(
                StaffSalary.is_active == True,
                StaffSalary.deduction_day == current_day,
            ).all()

            deducted = 0
            for sal in due_salaries:
                # Skip if already deducted this month
                if sal.last_deducted_month == current_month:
                    continue

                user = sal.user
                if not user or user.role not in ("doctor", "receptionist"):
                    continue

                amount_to_deduct = 0.0
                if sal.salary_type == "fixed":
                    amount_to_deduct = float(sal.amount)
                else:
                    total_invoiced = float(
                        db.session.query(func.coalesce(func.sum(Treatment.total_cost), 0.0))
                        .filter(Treatment.doctor_id == user.id)
                        .scalar() or 0.0
                    )
                    amount_to_deduct = round(total_invoiced * float(sal.amount) / 100.0, 2)

                if amount_to_deduct <= 0:
                    continue

                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
                note_text = f"Salary - {user.role.capitalize()}: {full_name} (Auto)"

                expense = Expense(
                    category="Salaries",
                    amount=amount_to_deduct,
                    expense_date=today.date(),
                    notes=note_text
                )
                db.session.add(expense)
                sal.last_deducted_month = current_month
                deducted += 1

            if deducted > 0:
                db.session.commit()
                app.logger.info(f"Auto-deducted salaries for {deducted} staff members.")
        except Exception:
            app.logger.exception("Auto salary deduction failed")
