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
                        "auto_cancel_expired_minutes", "auto_close_open_session_minutes",
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
                    if not val:
                        val = get_setting("anesthesia_needle_price", "50000")
                    try:
                        fval = float(val)
                        if fval < 0:
                            raise ValueError
                    except ValueError:
                        fval = 50000.0
                        val = "50000"
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
            
            # 2. Update treatment prices and details
            if "procedure_names[]" in request.form:
                names = request.form.getlist("procedure_names[]")
                prices = request.form.getlist("procedure_prices[]")
                durations = request.form.getlist("procedure_durations[]")
                actives = request.form.getlist("procedure_actives[]")
                categories = request.form.getlist("procedure_categories[]")
                
                treatment_dict = {}
                for idx, name in enumerate(names):
                    name = name.strip()
                    if name:
                        if len(name) > 200:
                            flash("Procedure name cannot exceed 200 characters.", "danger")
                            return redirect(url_for("settings.settings_page") + "#tab-treatments")
                        try:
                            price_raw = prices[idx] if idx < len(prices) else "0"
                            price_clean = price_raw.strip().replace(",", "")
                            price_val = float(price_clean) if '.' in price_clean else int(price_clean)
                            if price_val < 0:
                                price_val = 0
                        except (ValueError, IndexError):
                            price_val = 0

                        try:
                            dur_raw = durations[idx] if idx < len(durations) else "30"
                            dur_val = int(dur_raw.strip())
                            if dur_val <= 0:
                                dur_val = 30
                        except (ValueError, IndexError):
                            dur_val = 30

                        act_val = True
                        if idx < len(actives):
                            act_val = actives[idx].lower() in ("true", "1", "on", "yes")

                        cat_val = categories[idx].strip() if idx < len(categories) and categories[idx].strip() else "عام"

                        treatment_dict[name] = {
                            "price": price_val,
                            "duration": dur_val,
                            "active": act_val,
                            "category": cat_val
                        }
                
                # Guarantee essential system procedures (like 'جلسة فحص و استشارة', 'قلع سن عادي', and 'معالجة ما بعد القلع') are preserved
                if not any(k in treatment_dict for k in ["جلسة فحص و استشارة", "جلسة فحص واستشارة", "فحص دوري واستشارة", "فحص دوري", "Check-up", "Clinical Examination & Consultation"]):
                    treatment_dict["جلسة فحص و استشارة"] = {"price": 50000, "duration": 15, "active": True, "category": "فحص وتشخيص"}
                if "قلع سن" not in treatment_dict and "قلع سن عادي" not in treatment_dict:
                    treatment_dict["قلع سن عادي"] = {"price": 80000, "duration": 30, "active": True, "category": "جراحة وقلع"}
                if "معالجة ما بعد القلع" not in treatment_dict:
                    treatment_dict["معالجة ما بعد القلع"] = {"price": 30000, "duration": 20, "active": True, "category": "جراحة وقلع"}

                # Process Anesthesia Types
                anesthesia_names = request.form.getlist("anesthesia_names[]")
                anesthesia_prices = request.form.getlist("anesthesia_prices[]")
                anesthesia_list = []
                for idx, a_name in enumerate(anesthesia_names):
                    clean_a_name = a_name.strip()
                    if clean_a_name:
                        try:
                            a_price = float(anesthesia_prices[idx])
                        except (ValueError, IndexError):
                            a_price = 50000.0
                        anesthesia_list.append({"name": clean_a_name, "price": a_price})
                if anesthesia_list:
                    set_setting("anesthesia_types", json.dumps(anesthesia_list))
                    set_setting("anesthesia_needle_price", str(anesthesia_list[0]["price"]))

                set_setting("treatment_prices", json.dumps(treatment_dict, ensure_ascii=False))
            
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
        
    from utils.settings_helper import get_treatment_details, get_anesthesia_types
    treatment_prices = get_treatment_prices()
    treatment_details = get_treatment_details()
    anesthesia_types = get_anesthesia_types()
    
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
    
    import socket
    local_ips = []
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and ip not in local_ips:
                local_ips.append(ip)
    except Exception:
        pass

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        connected_ip = s.getsockname()[0]
        s.close()
        if not connected_ip.startswith("127.") and connected_ip not in local_ips:
            local_ips.append(connected_ip)
    except Exception:
        pass

    def ip_priority(ip):
        if ip.startswith("192.168."):
            return 0
        if ip.startswith("172."):
            return 1
        if ip.startswith("10."):
            return 2
        return 3

    local_ips.sort(key=ip_priority)
    primary_ip = local_ips[0] if local_ips else "127.0.0.1"

    host_parts = request.host.split(":")
    port = host_parts[1] if len(host_parts) > 1 else "5000"
    server_network_url = f"http://{primary_ip}:{port}"
    all_network_urls = [f"http://{ip}:{port}" for ip in local_ips]

    from utils.license_helper import get_current_license_status
    license_info = get_current_license_status()

    return render_template(
        "settings/settings.html",
        settings=settings_data,
        treatment_prices=treatment_prices,
        treatment_details=treatment_details,
        anesthesia_types=anesthesia_types,
        users=users,
        backups=backups_list,
        notifications=notifications,
        license_info=license_info,
        salary_configs=salary_configs,
        salary_staff=salary_staff,
        server_network_url=server_network_url,
        all_network_urls=all_network_urls
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

    user = db.session.get(User, user_id)
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

    user = db.session.get(User, user_id)
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


@settings_bp.route("/settings/backups/open-folder")
@role_required("admin")
def open_backups_folder():
    import os
    import subprocess
    from utils.backup_helper import BACKUP_DIR
    is_ar = request.cookies.get('lang', 'ar') != 'en'
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    try:
        if os.name == 'nt':
            os.startfile(BACKUP_DIR)
        else:
            subprocess.Popen(['xdg-open', BACKUP_DIR])
        msg = "تم فتح مجلد النسخ الاحتياطية على جهازك بنجاح." if is_ar else "Backups folder opened successfully."
        flash(msg, "success")
    except Exception as e:
        msg = f"فشل فتح المجلد: {e}" if is_ar else f"Failed to open folder: {e}"
        flash(msg, "danger")
    return redirect(url_for("settings.settings_page") + "#tab-backups")


@settings_bp.route("/settings/backups/<filename>/download")
@role_required("admin")
def download_backup(filename):
    import os
    import shutil
    from flask import send_file, redirect, url_for, flash, current_app
    from utils.backup_helper import BACKUP_DIR
    is_ar = request.cookies.get('lang', 'ar') != 'en'
    
    # Secure filename check to prevent directory traversal
    filename = os.path.basename(filename)
    backup_path = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(backup_path) or not os.path.isfile(backup_path):
        msg = "ملف النسخة الاحتياطية غير موجود." if is_ar else "Backup file not found."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page") + "#tab-backups")
        
    try:
        user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(user_downloads):
            dest_path = os.path.join(user_downloads, filename)
            shutil.copy2(backup_path, dest_path)
            if os.name == 'nt':
                try:
                    os.startfile(user_downloads)
                except Exception:
                    pass
            msg = f"تم تصدير النسخة الاحتياطية بنجاح إلى مجلد التنزيلات (Downloads): {filename}" if is_ar else f"Backup saved to Downloads: {filename}"
            flash(msg, "success")
            return redirect(url_for("settings.settings_page") + "#tab-backups")
    except Exception as fe:
        current_app.logger.warning(f"Could not auto-copy to Downloads folder: {fe}")
        
    return send_file(backup_path, as_attachment=True, download_name=filename)


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
    is_ar = request.cookies.get('lang', 'ar') != 'en'

    phone = request.form.get("phone", "").strip()
    api_key = request.form.get("api_key", "").strip() or None
    stream_id = request.form.get("stream_id", "").strip() or None

    if not phone:
        msg = "يرجى إدخال رقم الهاتف للتجربة." if is_ar else "Please enter a phone number."
        return jsonify({"success": False, "message": msg})

    body = "اختبار رسالة SMS من نظام عيادة الأسنان. البوابة تعمل بنجاح! ✅" if is_ar else "Test SMS from Dental Clinic MS. CommPeak is working!"
    success, msg = send_commpeak_sms(phone, body, api_key=api_key, stream_id=stream_id)
    if success and "Mock Sent" in msg:
        msg = "تمت محاكاة الإرسال بنجاح (مفاتيح API غير مضبوطة)." if is_ar else msg
    elif success:
        msg = "تم إرسال رسالة SMS التجريبية بنجاح! ✅" if is_ar else msg
    else:
        msg = f"فشل الإرسال: {msg}" if is_ar else msg

    return jsonify({"success": success, "message": msg})


@settings_bp.route("/settings/test-email", methods=["POST"])
@role_required("admin")
def test_email():
    from flask import jsonify
    from utils.notification_helper import send_smtp_email
    is_ar = request.cookies.get('lang', 'ar') != 'en'

    email = request.form.get("email", "").strip()
    smtp_host = request.form.get("smtp_host", "").strip() or None
    smtp_port = request.form.get("smtp_port", "").strip() or None
    smtp_user = request.form.get("smtp_user", "").strip() or None
    smtp_password = request.form.get("smtp_password", "").strip() or None
    smtp_from_email = request.form.get("smtp_from_email", "").strip() or None

    if not email:
        msg = "يرجى إدخال عنوان البريد الإلكتروني للتجربة." if is_ar else "Please enter an email address."
        return jsonify({"success": False, "message": msg})

    subject = "تجربة بريد إلكتروني — نظام إدارة عيادة الأسنان" if is_ar else "Test Email — Dental Clinic MS"
    body = "هذه رسالة اختبار من نظام عيادة الأسنان. خادم البريد SMTP يعمل بنجاح! ✅" if is_ar else "Test email from Dental Clinic MS. SMTP is working!"
    success, msg = send_smtp_email(
        email,
        subject,
        body,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        from_email=smtp_from_email
    )
    if success and "Mock Sent" in msg:
        msg = "تمت محاكاة الإرسال بنجاح (بيانات SMTP غير مضبوطة)." if is_ar else msg
    elif success:
        msg = "تم إرسال البريد الإلكتروني التجريبي بنجاح! ✅" if is_ar else msg
    else:
        msg = f"فشل الإرسال: {msg}" if is_ar else msg

    return jsonify({"success": success, "message": msg})


@settings_bp.route("/settings/test-telegram", methods=["POST"])
@role_required("admin")
def test_telegram():
    from flask import jsonify
    from utils.notification_helper import send_telegram_message
    is_ar = request.cookies.get('lang', 'ar') != 'en'

    chat_id = request.form.get("chat_id", "").strip()
    bot_token = request.form.get("bot_token", "").strip() or None

    if not chat_id:
        msg = "يرجى إدخال معرّف المحادثة (Chat ID)." if is_ar else "Please enter a Chat ID."
        return jsonify({"success": False, "message": msg})

    body = "اختبار رسالة تيليغرام من نظام عيادة الأسنان. البوت يعمل بنجاح! ✅" if is_ar else "Test from Dental Clinic MS. Telegram Bot is working!"
    success, msg = send_telegram_message(chat_id, body, bot_token=bot_token)
    if success and "Mock Sent" in msg:
        msg = "تمت محاكاة الإرسال بنجاح (توكن البوت غير مفعّل بعد)." if is_ar else msg
    elif success:
        msg = "تم إرسال رسالة الاختبار عبر تيليغرام بنجاح! ✅" if is_ar else msg
    else:
        msg = f"فشل الإرسال: {msg}" if is_ar else msg

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


def reset_db_auto_increments(tables=None):
    """Resets MySQL/MariaDB AUTO_INCREMENT and SQLite sqlite_sequence counters back to 1."""
    from models import db
    if tables is None:
        tables = [
            "payment_allocation", "payment", "invoice", "treatment", "appointment",
            "tooth_history", "treatment_plan_item", "patient_file", "notification_log",
            "expense", "staff_salary", "patient", "user", "system_setting"
        ]
    for tbl in tables:
        try:
            db.session.execute(db.text(f"ALTER TABLE `{tbl}` AUTO_INCREMENT = 1;"))
        except Exception:
            pass
        try:
            db.session.execute(db.text(f"DELETE FROM sqlite_sequence WHERE name = '{tbl}';"))
        except Exception:
            pass


@settings_bp.route("/settings/reset-clinic", methods=["POST"])
@role_required("admin")
def reset_clinic():
    """Resets all operational clinic database records (patients, appointments, treatments, invoices, payments, expenses, etc.)
    while preserving system settings, notification configurations/tokens, and user accounts.
    Requires admin username & password verification."""
    from models import (
        db, User, Patient, Appointment, Treatment, ToothHistory, TreatmentPlanItem,
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
        current_app.logger.warning(f"Admin '{admin_username}' initiated operational clinic database reset.")

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
        db.session.query(TreatmentPlanItem).delete(synchronize_session=False)
        db.session.query(PatientFile).delete(synchronize_session=False)
        db.session.query(NotificationLog).delete(synchronize_session=False)
        db.session.query(Expense).delete(synchronize_session=False)
        db.session.query(Patient).delete(synchronize_session=False)

        # Reset auto-increment counters for clinical & operational tables back to 1
        reset_db_auto_increments([
            "payment_allocation", "payment", "invoice", "treatment", "appointment",
            "tooth_history", "treatment_plan_item", "patient_file", "notification_log",
            "expense", "patient"
        ])

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
        db.session.expunge_all()

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

        msg = "تمت إعادة ضبط العيادة وتصفير كافة البيانات بنجاح، وتصفير الترقيم التلقائي للسجلات ليبدأ من 1 مجدداً." if is_ar else "Clinic database reset successfully. Auto-increment IDs reset to start from 1."
        flash(msg, "success")

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Error resetting clinic database: {e}")
        msg = f"حدث خطأ أثناء تصفير قاعدة البيانات: {str(e)}" if is_ar else f"Error resetting clinic database: {str(e)}"
        flash(msg, "danger")

    return redirect(url_for("settings.settings_page"))


@settings_bp.route("/settings/factory-reset", methods=["POST"])
@role_required("admin")
def factory_reset_clinic():
    """Performs a full factory reset of the clinic system:
    - Wipes all patients, appointments, treatments, tooth histories, treatment plans, invoices, payments, allocations, files, expenses, notification logs.
    - Wipes ALL user accounts and staff salary configurations.
    - Wipes SystemSetting table and re-populates default settings.
    - Deletes uploaded files.
    - Resets all table AUTO_INCREMENT counters to 1.
    - Creates single default admin account (username: 'admin', password: 'admin123', role: 'admin').
    - Clears session and redirects to login page.
    """
    from models import (
        db, User, Patient, Appointment, Treatment, ToothHistory, TreatmentPlanItem,
        Invoice, Payment, PaymentAllocation, PatientFile, NotificationLog, Expense,
        StaffSalary, SystemSetting
    )
    from utils.settings_helper import populate_default_settings
    from flask import session, g

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
        current_app.logger.warning(f"Failed clinic factory reset attempt: invalid admin credentials for username '{admin_username}'.")
        msg = "اسم المستخدم أو كلمة المرور الخاصة بالمدير غير صحيحة، أو أنك لا تملك صلاحيات مدير." if is_ar else "Invalid admin username or password, or insufficient permissions."
        flash(msg, "danger")
        return redirect(url_for("settings.settings_page"))

    try:
        current_app.logger.warning(f"Admin '{admin_username}' initiated full clinic factory reset.")

        # Disable foreign key checks for reset transaction
        try:
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0;"))
        except Exception:
            pass
        try:
            db.session.execute(db.text("PRAGMA foreign_keys = OFF;"))
        except Exception:
            pass

        # 1. Unlink patient user accounts from Patient table
        User.query.update({User.patient_id: None}, synchronize_session=False)

        # 2. Delete clinical and operational data in FK-safe order
        db.session.query(PaymentAllocation).delete(synchronize_session=False)
        db.session.query(Payment).delete(synchronize_session=False)
        db.session.query(Invoice).delete(synchronize_session=False)
        db.session.query(Treatment).delete(synchronize_session=False)
        db.session.query(Appointment).delete(synchronize_session=False)
        db.session.query(ToothHistory).delete(synchronize_session=False)
        db.session.query(TreatmentPlanItem).delete(synchronize_session=False)
        db.session.query(PatientFile).delete(synchronize_session=False)
        db.session.query(NotificationLog).delete(synchronize_session=False)
        db.session.query(Expense).delete(synchronize_session=False)
        db.session.query(StaffSalary).delete(synchronize_session=False)
        db.session.query(Patient).delete(synchronize_session=False)

        # 3. Delete ALL Users
        db.session.query(User).delete(synchronize_session=False)

        # 4. Delete SystemSetting rows
        db.session.query(SystemSetting).delete(synchronize_session=False)

        # Reset auto-increment counters for ALL tables back to 1
        reset_db_auto_increments([
            "payment_allocation", "payment", "invoice", "treatment", "appointment",
            "tooth_history", "treatment_plan_item", "patient_file", "notification_log",
            "expense", "staff_salary", "patient", "user", "system_setting"
        ])

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
        db.session.expunge_all()

        # 5. Re-populate default system settings
        populate_default_settings()

        # 6. Create single default admin account (admin / admin123)
        default_admin = User(
            username="admin",
            role="admin",
            first_name="المدير",
            last_name="العام"
        )
        default_admin.set_password("admin123")
        db.session.add(default_admin)
        db.session.commit()

        if hasattr(g, "system_settings_cache"):
            g.system_settings_cache = {}

        # 7. Remove physical patient upload files if present
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

        # 8. Logout current user session
        session.clear()

        msg = "تمت إعادة ضبط العيادة بالكامل للمصنع وتصفير جميع السجلات والمستخدمين وحذفها، وإرجاع كافة الإعدادات للقيم الافتراضية. يمكنك تسجيل الدخول باستخدام الحساب الافتراضي: admin / admin123" if is_ar else "Clinic factory reset completed successfully. All data and user accounts wiped. Default admin credentials: admin / admin123"
        flash(msg, "success")
        return redirect(url_for("auth.login"))

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(f"Error resetting clinic database: {e}")
        msg = f"حدث خطأ أثناء إعادة الضبط المصنعي للعيادة: {str(e)}" if is_ar else f"Error resetting clinic database: {str(e)}"
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

    if backup_filename == "__upload__" or "manual_backup_file" in request.files:
        uploaded_file = request.files.get("manual_backup_file")
        if not uploaded_file or not uploaded_file.filename:
            msg = "يرجى اختيار ملف نسخة احتياطية من جهازك أولاً." if is_ar else "Please select a backup file from your computer."
            flash(msg, "warning")
            return redirect(url_for("settings.settings_page") + "#tab-backups")

        filename_orig = os.path.basename(uploaded_file.filename)
        ext = os.path.splitext(filename_orig)[1].lower()

        if ext not in (".db", ".sql"):
            msg = "صيغة الملف غير مدعومة. يرجى اختيار ملف بصلة (.db) أو (.sql)." if is_ar else "Unsupported file format. Please upload a (.db) or (.sql) backup file."
            flash(msg, "danger")
            return redirect(url_for("settings.settings_page") + "#tab-backups")

        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('mysql') and ext != '.sql':
            msg = "النظام يعمل حالياً بقواعد بيانات ماي اس كيو ال (MySQL)، يرجى اختيار ملف نسخة احتياطية بصيغة (.sql)." if is_ar else "Active DB is MySQL. Please upload a (.sql) backup file."
            flash(msg, "danger")
            return redirect(url_for("settings.settings_page") + "#tab-backups")
        elif db_uri.startswith('sqlite') and ext != '.db':
            msg = "النظام يعمل حالياً بقواعد بيانات سكيولايت (SQLite)، يرجى اختيار ملف نسخة احتياطية بصيغة (.db)." if is_ar else "Active DB is SQLite. Please upload a (.db) backup file."
            flash(msg, "danger")
            return redirect(url_for("settings.settings_page") + "#tab-backups")

        from utils.backup_helper import BACKUP_DIR
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"backup_uploaded_{timestamp}{ext}"
        saved_filepath = os.path.join(BACKUP_DIR, saved_filename)

        try:
            uploaded_file.save(saved_filepath)

            # SQLite validation check
            if ext == ".db":
                with open(saved_filepath, "rb") as f:
                    header = f.read(16)
                    if not header.startswith(b"SQLite format 3"):
                        os.remove(saved_filepath)
                        msg = "الملف المرفوع ليس ملف قاعدة بيانات سكيولايت صحيح (Corrupted SQLite DB)." if is_ar else "The uploaded file is not a valid SQLite database."
                        flash(msg, "danger")
                        return redirect(url_for("settings.settings_page") + "#tab-backups")

            backup_filename = saved_filename
        except Exception as fe:
            current_app.logger.exception(f"Failed to save uploaded backup file: {fe}")
            msg = "فشل في حفظ ملف النسخة الاحتياطية المرفوع." if is_ar else "Failed to save uploaded backup file."
            flash(msg, "danger")
            return redirect(url_for("settings.settings_page") + "#tab-backups")
    else:
        if not backups:
            msg = "لم يتم العثور على أي ملف نسخة احتياطية لاستعادته." if is_ar else "No backup file found to restore from."
            flash(msg, "warning")
            return redirect(url_for("settings.settings_page") + "#tab-backups")

        if not backup_filename:
            backup_filename = backups[0]["filename"]
        else:
            # Sanitize filename
            backup_filename = os.path.basename(backup_filename)
            valid_files = [b["filename"] for b in backups]
            if backup_filename not in valid_files:
                msg = "ملف النسخة الاحتياطية المحددة غير موجود." if is_ar else "Specified backup file not found."
                flash(msg, "danger")
                return redirect(url_for("settings.settings_page") + "#tab-backups")

    try:
        current_app.logger.warning(f"Admin '{admin_username}' requested database restore from backup file '{backup_filename}'.")
        restore_database_backup(backup_filename)
        msg = f"تمت استعادة كافة البيانات بنجاح من النسخة الاحتياطية: ({backup_filename})" if is_ar else f"Data restored successfully from backup: ({backup_filename})"
        flash(msg, "success")
    except Exception as e:
        current_app.logger.exception(f"Error restoring database from {backup_filename}: {e}")
        msg = f"حدث خطأ أثناء استعادة النسخة الاحتياطية: {str(e)}" if is_ar else f"Error restoring database: {str(e)}"
        flash(msg, "danger")
    finally:
        if backup_filename and backup_filename.startswith("backup_uploaded_"):
            try:
                uploaded_path = os.path.join(BACKUP_DIR, backup_filename)
                if os.path.exists(uploaded_path):
                    os.remove(uploaded_path)
            except Exception:
                pass

    return redirect(url_for("settings.settings_page") + "#tab-backups")


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


def process_monthly_salary_deductions(user_id, target_month=None):
    """
    Process salary deductions month-by-month for a user up to current month.
    If target_month is provided (YYYY-MM), only deducts for that specific month.
    Returns (created_expenses_count, total_amount_deducted).
    """
    from models import db, User, StaffSalary, Expense, Appointment, Treatment
    from datetime import datetime, date
    from collections import defaultdict
    from sqlalchemy import extract

    salary_cfg = StaffSalary.query.filter_by(user_id=user_id).first()
    user = db.session.get(User, user_id)

    if not salary_cfg or not user:
        return 0, 0.0

    today = datetime.now()
    current_year = today.year
    current_month = today.month
    current_month_str = today.strftime("%Y-%m")

    target_ym = None
    if target_month and target_month != "all":
        try:
            parts = target_month.strip().split("-")
            if len(parts) == 2:
                target_ym = (int(parts[0]), int(parts[1]))
        except ValueError:
            target_ym = None

    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
    role_label = "طبيب" if user.role == "doctor" else "موظف استقبال"

    total_created_expenses = 0
    total_amount_deducted = 0.0

    if salary_cfg.salary_type == "fixed":
        fixed_amount = float(salary_cfg.amount)
        if fixed_amount <= 0:
            return 0, 0.0

        if target_ym:
            months_to_process = [target_ym]
        else:
            if salary_cfg.last_deducted_month:
                try:
                    last_yr, last_m = map(int, salary_cfg.last_deducted_month.split("-"))
                    if last_m == 12:
                        start_yr, start_m = last_yr + 1, 1
                    else:
                        start_yr, start_m = last_yr, last_m + 1
                except ValueError:
                    start_yr, start_m = current_year, current_month
            else:
                earliest_t = (
                    Treatment.query
                    .join(Appointment, Treatment.appointment_id == Appointment.id)
                    .filter(Appointment.doctor_id == user_id)
                    .order_by(Appointment.appointment_date.asc())
                    .first()
                )
                if earliest_t and earliest_t.appointment and earliest_t.appointment.appointment_date:
                    start_yr = earliest_t.appointment.appointment_date.year
                    start_m = earliest_t.appointment.appointment_date.month
                else:
                    start_yr, start_m = current_year, current_month

            months_to_process = []
            cur_yr, cur_m = start_yr, start_m
            while (cur_yr < current_year) or (cur_yr == current_year and cur_m <= current_month):
                months_to_process.append((cur_yr, cur_m))
                if cur_m == 12:
                    cur_yr += 1
                    cur_m = 1
                else:
                    cur_m += 1

        for cur_yr, cur_m in months_to_process:
            exp_date = date(cur_yr, cur_m, 1)
            note_text = f"راتب {role_label}: {full_name} عن شهر {cur_m:02d}/{cur_yr:04d} (راتب ثابت)"

            existing = Expense.query.filter(
                Expense.category == "Salaries",
                Expense.expense_date == exp_date,
                Expense.notes == note_text
            ).first()

            if not existing:
                expense = Expense(
                    category="Salaries",
                    amount=fixed_amount,
                    expense_date=exp_date,
                    notes=note_text
                )
                db.session.add(expense)
                total_created_expenses += 1
                total_amount_deducted += fixed_amount

        if not target_ym:
            salary_cfg.last_deducted_month = current_month_str
        else:
            t_str = f"{target_ym[0]:04d}-{target_ym[1]:02d}"
            if not salary_cfg.last_deducted_month or t_str > salary_cfg.last_deducted_month:
                salary_cfg.last_deducted_month = t_str

        db.session.commit()
        return total_created_expenses, total_amount_deducted

    else: # percentage
        percentage_rate = float(salary_cfg.amount)
        if percentage_rate <= 0:
            return 0, 0.0

        q = (
            Treatment.query
            .join(Appointment, Treatment.appointment_id == Appointment.id)
            .filter(Appointment.doctor_id == user_id, Treatment.salary_expense_id == None)
        )
        if target_ym:
            q = q.filter(
                extract('year', Appointment.appointment_date) == target_ym[0],
                extract('month', Appointment.appointment_date) == target_ym[1]
            )

        undeducted_treatments = q.order_by(Appointment.appointment_date.asc()).all()

        if not undeducted_treatments:
            return 0, 0.0

        treatments_by_month = defaultdict(list)
        for t in undeducted_treatments:
            t_date = (t.treatment_date or (t.appointment.appointment_date if t.appointment else None))
            if not t_date:
                t_date = datetime.now()
            m_key = (t_date.year, t_date.month)
            treatments_by_month[m_key].append(t)

        for (yr, m), m_treatments in sorted(treatments_by_month.items()):
            doc_revenue = sum(float(t.total_cost or 0.0) for t in m_treatments)
            amount_to_deduct = round(doc_revenue * percentage_rate / 100.0, 2)

            if amount_to_deduct > 0:
                m_str = f"{m:02d}/{yr:04d}"
                note_text = f"تسديد مستحقات ونسبة د. {full_name} عن شهر {m_str}"
                exp_date = date(yr, m, 1)

                expense = Expense(
                    category="Salaries",
                    amount=amount_to_deduct,
                    expense_date=exp_date,
                    notes=note_text
                )
                db.session.add(expense)
                db.session.flush()

                for t in m_treatments:
                    t.salary_expense_id = expense.id

                total_created_expenses += 1
                total_amount_deducted += amount_to_deduct

        if not target_ym:
            salary_cfg.last_deducted_month = current_month_str
        else:
            t_str = f"{target_ym[0]:04d}-{target_ym[1]:02d}"
            if not salary_cfg.last_deducted_month or t_str > salary_cfg.last_deducted_month:
                salary_cfg.last_deducted_month = t_str

        db.session.commit()
        return total_created_expenses, total_amount_deducted


@settings_bp.route("/settings/salary/deduct/<int:user_id>", methods=["POST"])
@role_required("admin")
def deduct_salary_now(user_id):
    """Immediately deduct salary for a staff member and record separate Expenses per month."""
    from models import db, User, StaffSalary
    from utils.settings_helper import get_setting
    from datetime import datetime
    is_ar = request.cookies.get("lang", "ar") != "en"
    try:
        salary_cfg = StaffSalary.query.filter_by(user_id=user_id).first()
        user = User.query.get_or_404(user_id)

        if not salary_cfg:
            msg = "يرجى تعيين وتأكيد إعدادات الراتب لهذا الموظف أولاً قبل الضغط على الخصم." if is_ar else "Please configure salary settings for this user first."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return {"success": False, "message": msg}, 400
            flash(msg, "warning")
            return redirect(url_for("settings.settings_page") + "#tab-billing")

        target_month = (request.form.get("month") or request.args.get("month") or "").strip()
        created_cnt, total_amount = process_monthly_salary_deductions(user_id, target_month=target_month)

        if created_cnt == 0 or total_amount <= 0:
            msg = "لا توجد مستحقات أو رواتب معلقة لخصمها بهذا الشهر." if is_ar else "No pending salary or revenue deductions found."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return {"success": False, "message": msg}, 400
            flash(msg, "warning")
            return redirect(url_for("settings.settings_page") + "#tab-billing")

        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
        currency = get_setting("currency_symbol", "ل.س")
        current_app.logger.info(f"Salary deducted for user_id={user_id} count={created_cnt} total={total_amount}")
        msg = (f"تم خصم وتسجيل {created_cnt} رواتب شهرياً لـ ({full_name}) — إجمالي: ({total_amount:,.0f} {currency})"
               if is_ar else
               f"Deducted {created_cnt} monthly salary entries for {full_name} — Total: ({total_amount:,.0f} {currency})")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return {"success": True, "message": msg, "amount": total_amount, "count": created_cnt}

        flash(msg, "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to deduct salary for user_id={user_id}")
        msg = "فشل في خصم الراتب." if is_ar else "Failed to deduct salary."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return {"success": False, "message": msg}, 500
        flash(msg, "danger")

    return redirect(url_for("settings.settings_page") + "#tab-billing")


@settings_bp.route("/settings/salary/undo/<int:user_id>", methods=["POST"])
@role_required("admin")
def undo_salary_deduction(user_id):
    """Reverse salary deduction for a staff member for a specific month (or current month)."""
    from models import db, User, StaffSalary, Expense, Treatment, Appointment
    from datetime import datetime
    from sqlalchemy import extract
    is_ar = request.cookies.get("lang", "ar") != "en"

    def _json_resp(success, msg, status=200):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            return {"success": success, "message": msg}, status
        flash(msg, "success" if success else "danger")
        return redirect(url_for("settings.settings_page") + "#tab-billing")

    try:
        sc = StaffSalary.query.filter_by(user_id=user_id).first()
        user = User.query.get_or_404(user_id)

        req_month = (request.form.get("month") or request.args.get("month") or "").strip()
        now = datetime.now()

        if req_month:
            try:
                target_yr, target_m = map(int, req_month.split("-"))
                target_month_str = f"{target_yr:04d}-{target_m:02d}"
            except ValueError:
                target_yr, target_m = now.year, now.month
                target_month_str = now.strftime("%Y-%m")
        else:
            target_yr, target_m = now.year, now.month
            target_month_str = now.strftime("%Y-%m")

        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username

        # Find expense recorded for this doctor and target month
        search_term = user.last_name or user.first_name or user.username
        expense = (
            Expense.query
            .filter(
                Expense.category == "Salaries",
                extract("year", Expense.expense_date) == target_yr,
                extract("month", Expense.expense_date) == target_m,
                Expense.notes.ilike(f"%{search_term}%")
            )
            .order_by(Expense.id.desc())
            .first()
        )

        unlinked_count = 0
        if expense:
            # Unlink treatments
            unlinked_count = Treatment.query.filter_by(salary_expense_id=expense.id).update(
                {"salary_expense_id": None}, synchronize_session=False
            )
            db.session.delete(expense)

        # Unlink any additional treatments in that month for this doctor
        additional_treatments = (
            Treatment.query
            .join(Appointment, Treatment.appointment_id == Appointment.id)
            .filter(
                Appointment.doctor_id == user_id,
                extract("year", Appointment.appointment_date) == target_yr,
                extract("month", Appointment.appointment_date) == target_m,
                Treatment.salary_expense_id != None
            )
            .all()
        )
        for t in additional_treatments:
            t.salary_expense_id = None
            unlinked_count += 1

        if sc and sc.last_deducted_month == target_month_str:
            sc.last_deducted_month = None

        db.session.commit()

        current_app.logger.info(f"Salary deduction reversed for user_id={user_id} month={target_month_str}")
        msg = (f"تم التراجع عن خصم راتب {full_name} لشهر {target_month_str} وإلغاء المصروف المرتبط."
               if is_ar else
               f"Salary deduction for {full_name} ({target_month_str}) has been reversed.")
        return _json_resp(True, msg)

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to undo salary deduction for user_id={user_id}")
        msg = "فشل في التراجع عن الخصم." if is_ar else "Failed to undo deduction."
        return _json_resp(False, msg, 500)


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
