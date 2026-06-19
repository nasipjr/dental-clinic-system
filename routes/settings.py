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
                        "currency_symbol"]:
                val = request.form.get(key, "").strip()
                set_setting(key, val)
            
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
                        try:
                            # Convert price to number
                            price_clean = price.strip().replace(",", "")
                            price_val = float(price_clean) if '.' in price_clean else int(price_clean)
                            if price_val < 0:
                                price_val = 0
                        except ValueError:
                            price_val = 0
                        treatment_dict[name] = price_val
                
                set_setting("treatment_prices", json.dumps(treatment_dict))
            
            flash("Settings updated successfully!", "success")
            current_app.logger.info("Settings updated successfully")
        except Exception:
            current_app.logger.exception("Failed to update system settings")
            flash("Failed to update settings. Please try again.", "danger")
            
        return redirect(url_for("settings.settings_page"))

    # GET request: load values
    settings_data = {}
    for key in DEFAULT_SETTINGS.keys():
        settings_data[key] = get_setting(key)
        
    treatment_prices = get_treatment_prices()
    
    from models import User
    users = User.query.all()
    
    return render_template(
        "settings/settings.html",
        settings=settings_data,
        treatment_prices=treatment_prices,
        users=users
    )


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
        return redirect(url_for("settings.settings_page"))

    existing = User.query.filter_by(username=username).first()
    if existing:
        flash("Username already exists.", "danger")
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
        flash(f"User account '{username}' created successfully!", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to add user: {e}")
        flash("Failed to create user account.", "danger")

    return redirect(url_for("settings.settings_page") + "#tab-users")


@settings_bp.route("/settings/users/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def delete_user(user_id):
    from models import db, User
    from flask import session
    
    # Prevent deleting oneself
    if session.get("user_id") == user_id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"User account '{user.username}' deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete user: {e}")
        flash("Failed to delete user account.", "danger")

    return redirect(url_for("settings.settings_page") + "#tab-users")


@settings_bp.route("/settings/users/<int:user_id>/edit", methods=["POST"])
@role_required("admin")
def edit_user(user_id):
    from models import db, User
    from flask import session

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "").strip()
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()

    if not username:
        flash("Username is required.", "danger")
        return redirect(url_for("settings.settings_page") + "#tab-users")

    # Check if username is taken by another user
    existing = User.query.filter(User.username == username, User.id != user_id).first()
    if existing:
        flash("Username already taken by another user.", "danger")
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
        flash(f"User account '{username}' updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update user: {e}")
        flash("Failed to update user account.", "danger")

    return redirect(url_for("settings.settings_page") + "#tab-users")
