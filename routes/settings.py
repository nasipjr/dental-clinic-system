import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from utils.settings_helper import get_setting, set_setting, get_treatment_prices, DEFAULT_SETTINGS

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings", methods=["GET", "POST"])
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
            
            # 2. Update treatment prices
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
    
    return render_template(
        "settings/settings.html",
        settings=settings_data,
        treatment_prices=treatment_prices
    )
