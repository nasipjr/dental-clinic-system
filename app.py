from flask import Flask, request, session, redirect, url_for, g

from models import db
from settings import Config
from utils.logging_config import setup_logging

from routes.dashboard import dashboard_bp
from routes.patients import patients_bp
from routes.appointments import appointments_bp
from routes.treatments import treatments_bp
from routes.payments import payments_bp
from routes.invoices import invoices_bp
from routes.reports import reports_bp
from routes.settings import settings_bp
from routes.auth import auth_bp


app = Flask(__name__)
app.config.from_object(Config)

LOG_DIRECTORY = app.config["LOG_DIRECTORY"]
LOG_FILE_NAME = app.config["LOG_FILE_NAME"]

db.init_app(app)


def populate_default_settings():
    from models import SystemSetting
    from utils.settings_helper import DEFAULT_SETTINGS
    try:
        for key, val in DEFAULT_SETTINGS.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                db.session.add(SystemSetting(key=key, value=val))
        db.session.commit()
    except Exception:
        db.session.rollback()


def check_and_add_discount_column():
    from sqlalchemy import text
    try:
        db.session.execute(text("SELECT discount FROM invoice LIMIT 1"))
    except Exception:
        db.session.rollback()
        try:
            app.logger.info("Adding discount column to invoice table")
            db.session.execute(text("ALTER TABLE invoice ADD COLUMN discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00"))
            db.session.commit()
            app.logger.info("Successfully added discount column")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to add discount column: {e}")

    try:
        db.session.execute(text("SELECT discount_type FROM invoice LIMIT 1"))
    except Exception:
        db.session.rollback()
        try:
            app.logger.info("Adding discount_type column to invoice table")
            db.session.execute(text("ALTER TABLE invoice ADD COLUMN discount_type VARCHAR(20) NOT NULL DEFAULT 'value'"))
            db.session.commit()
            app.logger.info("Successfully added discount_type column")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to add discount_type column: {e}")


def ensure_default_admin():
    from models import User
    try:
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            app.logger.info("Seeding default admin account...")
            default_admin = User(
                username="admin",
                role="admin",
                first_name="Admin",
                last_name="User"
            )
            default_admin.set_password("admin123")
            db.session.add(default_admin)
            db.session.commit()
            app.logger.info("Successfully seeded default admin account!")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to seed default admin: {e}")


with app.app_context():
    db.create_all()
    populate_default_settings()
    check_and_add_discount_column()
    ensure_default_admin()

setup_logging(app, LOG_DIRECTORY, LOG_FILE_NAME)
app.logger.info("Application started successfully")


@app.template_filter("format_price")
def format_price(value):
    if value is None:
        return "0"
    try:
        val = float(value)
        # Format with whole number and thousands separator
        formatted = "{:,.0f}".format(val)
        # Replace commas with dots
        return formatted.replace(",", ".")
    except (ValueError, TypeError):
        return str(value)


@app.before_request
def load_logged_in_user():
    from models import User
    user_id = session.get("user_id")
    if user_id is None:
        g.current_user = None
    else:
        g.current_user = User.query.get(user_id)


@app.before_request
def check_login():
    # Exclude login and static resources
    if request.endpoint in ("auth.login", "static") or not request.endpoint:
        return
    if "user_id" not in session:
        return redirect(url_for("auth.login"))


@app.context_processor
def inject_settings():
    from utils.settings_helper import get_setting, get_currency_symbol
    from datetime import datetime

    # Get dynamic operating hours formatting
    start_str = get_setting("working_hours_start", "08:00")
    end_str = get_setting("working_hours_end", "18:00")
    
    def to_12h(t_str):
        try:
            return datetime.strptime(t_str, "%H:%M").strftime("%I:%M %p").lstrip("0")
        except Exception:
            return t_str
            
    hours_formatted = f"{to_12h(start_str)} - {to_12h(end_str)}"
    
    wd_str = get_setting("working_days", "0,1,2,3,4,6")
    active_days = set()
    for x in wd_str.split(","):
        if x.strip().isdigit():
            active_days.add(int(x))
            
    DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    SHORT_DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    
    active_names = [SHORT_DAY_NAMES[d] for d in range(7) if d in active_days]
    closed_names = [DAY_NAMES[d] for d in range(7) if d not in active_days]
    
    active_set = set(active_days)
    if active_set == {0, 1, 2, 3, 4, 6}:
        days_str = "Sat - Thu"
    elif active_set == {0, 1, 2, 3, 4}:
        days_str = "Sun - Thu"
    elif active_set == {1, 2, 3, 4, 5}:
        days_str = "Mon - Fri"
    elif active_set == {1, 2, 3, 4, 5, 6}:
        days_str = "Mon - Sat"
    elif active_set == {0, 1, 2, 3, 4, 5, 6}:
        days_str = "Every day"
    else:
        days_str = ", ".join(active_names)
        
    if not closed_names:
        closed_str = "None"
    else:
        closed_str = ", ".join(closed_names)

    return {
        "clinic_name": get_setting("clinic_name", "Clinic"),
        "currency_symbol": get_currency_symbol(),
        "clinic_phone": get_setting("clinic_phone", "+963 958 948 727"),
        "clinic_email": get_setting("clinic_email", "kh.nasipdragon@gmail.com"),
        "clinic_address": get_setting("clinic_address", "Damascus, Syria"),
        "current_user": g.current_user if "current_user" in dir(g) else None,
        "operating_hours": hours_formatted,
        "operating_days": days_str,
        "operating_closed": closed_str,
        "working_days": wd_str,
        "working_hours_start": start_str,
        "working_hours_end": end_str
    }


app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(treatments_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(invoices_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(settings_bp)



@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f"404 Not Found | path={request.path}")
    return "page not found", 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.exception("500 Internal Server Error")
    return "internal server error", 500


if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully or already exist")
        except Exception:
            app.logger.exception("Failed to create database tables")

    app.logger.info("Flask app is running")
    app.run(debug=True)