from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        if session.get("role") == "patient":
            return redirect(url_for("portal.dashboard"))
        return redirect(url_for("dashboard.home"))

    lang = request.cookies.get('lang', 'en')

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user_type = request.form.get("user_type", "staff").strip()

        if not username or not password:
            err_msg = {
                "ar": "يرجى إدخال اسم المستخدم وكلمة المرور.",
                "en": "Please enter both username and password."
            }.get(lang, "Please enter both username and password.")
            flash(err_msg, "danger")
            return render_template("auth/login.html", active_tab=user_type)

        if user_type == "patient":
            user = User.query.filter_by(username=username, role="patient").first()
        else:
            user = User.query.filter(User.username == username, User.role != "patient").first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role
            name_to_use = user.first_name or user.username
            
            welcome_msg = {
                "ar": f"مرحباً بك مجدداً، {name_to_use}!",
                "en": f"Welcome back, {name_to_use}!"
            }.get(lang, f"Welcome back, {name_to_use}!")
            
            if user.role == "patient":
                session["patient_id"] = user.patient_id
                session.permanent = True
                flash(welcome_msg, "success")
                return redirect(url_for("portal.dashboard"))
            else:
                session.permanent = True
                flash(welcome_msg, "success")
                return redirect(url_for("dashboard.home"))
        else:
            invalid_msg = {
                "ar": "اسم المستخدم أو كلمة المرور غير صالحة.",
                "en": "Invalid username or password."
            }.get(lang, "Invalid username or password.")
            flash(invalid_msg, "danger")
            return render_template("auth/login.html", active_tab=user_type)

    return render_template("auth/login.html", active_tab="staff")

@auth_bp.route("/logout")
def logout():
    session.clear()
    lang = request.cookies.get('lang', 'ar')
    msg = {
        "ar": "تم تسجيل الخروج بنجاح.",
        "en": "You have been logged out successfully."
    }.get(lang, "تم تسجيل الخروج بنجاح.")
    flash(msg, "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/activate", methods=["GET", "POST"])
def activate_license():
    """Activation screen for entering and verifying system license keys."""
    from utils.license_helper import get_current_license_status, verify_license_key
    from utils.settings_helper import set_setting

    lang = request.cookies.get('lang', 'ar')

    if request.method == "POST":
        key_input = request.form.get("license_key", "").strip()
        is_valid, data_or_msg = verify_license_key(key_input)

        if not is_valid:
            flash(str(data_or_msg), "danger")
        else:
            from utils.license_helper import reset_clock_activity
            set_setting("active_license_key", data_or_msg["key"])
            set_setting("license_type", data_or_msg["license_type"])
            set_setting("license_expires_at", data_or_msg["expires_at"].strftime("%Y-%m-%d %H:%M:%S"))
            reset_clock_activity()

            success_msg = {
                "ar": f"🎉 تم تفعيل ترخيص النظام بنجاح! متبقي {data_or_msg['days_remaining']} يوماً.",
                "en": f"🎉 License activated successfully! {data_or_msg['days_remaining']} days remaining."
            }.get(lang, "License activated successfully.")
            
            flash(success_msg, "success")
            if "user_id" in session:
                return redirect(url_for("dashboard.home"))
            else:
                return redirect(url_for("auth.login"))

    from utils.settings_helper import get_setting
    status = get_current_license_status()
    current_lang = request.cookies.get('lang', 'ar')
    raw_dev_phone = get_setting("developer_whatsapp", "963958948727")
    developer_phone = raw_dev_phone.replace(" ", "").replace("+", "").replace("-", "")

    return render_template(
        "auth/activate.html",
        status_code=status["status_code"],
        message=status["message"],
        current_lang=current_lang,
        developer_phone=developer_phone
    )

