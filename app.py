from flask import Flask, request, session, redirect, url_for, g, flash

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
from routes.portal import portal_bp
from routes.deploy import deploy_bp


import sys
import os

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True
app.jinja_env.cache = None

try:
    from flask_wtf.csrf import CSRFProtect, generate_csrf
    csrf = CSRFProtect(app)
except ImportError:
    csrf = None

def safe_csrf_token():
    try:
        from flask_wtf.csrf import generate_csrf
        return generate_csrf()
    except Exception:
        return ""

app.jinja_env.globals['csrf_token'] = safe_csrf_token

LOG_DIRECTORY = app.config["LOG_DIRECTORY"]
LOG_FILE_NAME = app.config["LOG_FILE_NAME"]

db.init_app(app)

from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    import sqlite3
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        # WAL mode can fail on NFS file systems like PythonAnywhere; fall back gracefully if unsupported
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
        except Exception:
            pass
        try:
            cursor.execute("PRAGMA busy_timeout=30000;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
        cursor.close()


def populate_default_settings():
    from models import SystemSetting
    from utils.settings_helper import DEFAULT_SETTINGS
    try:
        for key, val in DEFAULT_SETTINGS.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                db.session.add(SystemSetting(key=key, value=val))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error initializing default settings: {e}")


from utils.db_migration_helper import ensure_database_schema


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


def init_db_tables():
    try:
        db.create_all()
        populate_default_settings()
        ensure_database_schema(app, db)
        ensure_default_admin()
        app.logger.info("Database initialized successfully.")
    except Exception as e:
        app.logger.error(f"Failed to complete database startup tasks: {e}")


with app.app_context():
    init_db_tables()


_db_initialized = False

@app.before_request
def check_db_initialized():
    global _db_initialized
    if not _db_initialized:
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if "user" not in inspector.get_table_names():
                init_db_tables()
            _db_initialized = True
        except Exception as e:
            app.logger.error(f"Error checking DB tables on request: {e}")


setup_logging(app, LOG_DIRECTORY, LOG_FILE_NAME)
app.logger.info("Application started successfully")


@app.template_filter("format_price")
def format_price(value):
    if value is None or value == "":
        return "0"
    try:
        from decimal import Decimal, InvalidOperation
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        val = Decimal(str(value))
        # Format with whole number and thousands separator
        return "{:,.0f}".format(val)
    except (ValueError, TypeError, InvalidOperation):
        return str(value)


@app.template_filter("no_decimal")
def no_decimal_filter(value):
    if value is None or value == "":
        return ""
    try:
        val = float(value)
        if val % 1 == 0:
            return str(int(val))
        return f"{val:g}"
    except (ValueError, TypeError):
        return str(value)


UNIVERSAL_TO_FDI_MAP = {
    '1': '18', '2': '17', '3': '16', '4': '15', '5': '14', '6': '13', '7': '12', '8': '11',
    '9': '21', '10': '22', '11': '23', '12': '24', '13': '25', '14': '26', '15': '27', '16': '28',
    '17': '38', '18': '37', '19': '36', '20': '35', '21': '34', '22': '33', '23': '32', '24': '31',
    '25': '41', '26': '42', '27': '43', '28': '44', '29': '45', '30': '46', '31': '47', '32': '48'
}

@app.template_filter("format_tooth_number")
@app.template_filter("fdi_tooth")
def format_tooth_number_filter(value):
    if not value:
        return ""
    val_str = str(value).strip()
    if not val_str:
        return ""
    parts = [p.strip() for p in val_str.split(',') if p.strip()]
    converted = []
    for p in parts:
        if p in UNIVERSAL_TO_FDI_MAP:
            converted.append(UNIVERSAL_TO_FDI_MAP[p])
        else:
            converted.append(p)
    return ", ".join(converted)


@app.template_filter("translate")
@app.template_filter("t")
def translate_filter(text):
    if not text:
        return ""
    from utils.translator import fast_translate_text
    return fast_translate_text(str(text))



@app.before_request
def load_logged_in_user():
    from models import User
    user_id = session.get("user_id")
    if user_id is None:
        g.current_user = None
    else:
        g.current_user = User.query.get(user_id)


@app.before_request
def enforce_system_license():
    # Exclude login, activation, static files, logout, and deploy webhook
    excluded_endpoints = ("auth.login", "auth.activate_license", "auth.logout", "static", "deploy.deploy")
    if not request.endpoint or request.endpoint in excluded_endpoints:
        return

    from utils.license_helper import get_current_license_status
    license_status = get_current_license_status()

    if not license_status["is_active"]:
        app.logger.warning(f"System access blocked by license middleware: {license_status['status_code']} - {license_status['message']}")
        return redirect(url_for("auth.activate_license"))


@app.before_request
def check_login():
    # Exclude login, activation, static resources, patient portal, and auto-deploy webhook
    excluded = ("auth.login", "auth.activate_license", "auth.logout", "static", "deploy.deploy")
    if request.endpoint in excluded or not request.endpoint or request.endpoint.startswith("portal."):
        return
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    if not g.current_user:
        session.clear()
        flash("Your account has been deleted or deactivated.", "danger")
        return redirect(url_for("auth.login"))


@app.after_request
def process_html_response(response):
    if response.mimetype == "text/html":
        import re

        # Disable browser caching for HTML pages to ensure updates appear immediately
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        # 1. Inject CSRF Token into forms if not already present
        try:
            if csrf:
                try:
                    from flask_wtf.csrf import generate_csrf
                    token = generate_csrf()
                except Exception:
                    token = ""
            else:
                token = ""
            html_data = response.get_data(as_text=True)
            if token and "<form" in html_data.lower() and 'name="csrf_token"' not in html_data.lower():
                csrf_input = f'<input type="hidden" name="csrf_token" value="{token}">'
                html_data = re.sub(r'(<form[^>]*>)', r'\1' + csrf_input, html_data, flags=re.IGNORECASE)
        except Exception as e:
            app.logger.error(f"Error generating CSRF token for response: {e}")
            html_data = response.get_data(as_text=True)
        
        # 2. Server-side translation
        lang = request.cookies.get("lang", "en")
        if lang == "ar":
            try:
                from utils.translator import translate_html
                html_data = translate_html(html_data)
            except Exception as e:
                app.logger.error(f"Server-side translation failed: {e}")
                
        response.set_data(html_data)
    return response


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

    from models import Appointment, User
    try:
        pending_count = Appointment.query.filter_by(status="Pending").count()
    except Exception:
        pending_count = 0

    try:
        doctors_list = User.query.filter(User.role.in_(["admin", "doctor"])).all()
    except Exception:
        doctors_list = []

    return {
        "clinic_name": get_setting("clinic_name", "Clinic"),
        "currency_symbol": get_currency_symbol(),
        "clinic_phone": get_setting("clinic_phone", "+963 958 948 727"),
        "clinic_email": get_setting("clinic_email", "kh.nasipdragon@gmail.com"),
        "clinic_address": get_setting("clinic_address", "Damascus, Syria"),
        "clinic_vat_number": get_setting("clinic_vat_number", ""),
        "current_user": g.current_user if "current_user" in dir(g) else None,
        "all_doctors": doctors_list,
        "doctors_list": doctors_list,
        "operating_hours": hours_formatted,
        "operating_days": days_str,
        "operating_closed": closed_str,
        "working_days": wd_str,
        "working_hours_start": start_str,
        "working_hours_end": end_str,
        "pending_count": pending_count,
        "booking_window_days": get_setting("booking_window_days", "30"),
        "default_appointment_duration": get_setting("default_appointment_duration", "30")
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
app.register_blueprint(portal_bp)
app.register_blueprint(deploy_bp)
if csrf:
    csrf.exempt(deploy_bp)



@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f"404 Not Found | path={request.path}")
    return "page not found", 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    err_detail = str(getattr(error, 'original_exception', error))
    app.logger.exception(f"500 Internal Server Error: {err_detail}")
    return f"Internal Server Error: {err_detail}", 500


@app.after_request
def add_static_cache_headers(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=86400'
    return response


if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully or already exist")
            
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'tooth_history' in inspector.get_table_names():
                columns = [c['name'] for c in inspector.get_columns('tooth_history')]
                if 'history_date' not in columns:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE tooth_history ADD COLUMN history_date DATE NULL"))
                        conn.commit()
                    app.logger.info("Added history_date column to tooth_history table")
        except Exception:
            app.logger.exception("Failed to create database tables or migrate columns")

        # Start background schedulers using Single-Instance Lock Guard
        try:
            from utils.scheduler_guard import start_app_schedulers
            start_app_schedulers(app)
        except Exception as e:
            app.logger.error(f"Failed to start background schedulers: {e}")

        # Auto-process pending salary deductions for today
        try:
            from routes.settings import auto_process_salary_deductions
            auto_process_salary_deductions(app)
        except Exception as e:
            app.logger.error(f"Failed to auto-process salary deductions: {e}")

    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    app.logger.info(f"Flask app is running (debug={debug_mode})")
    app.run(host="0.0.0.0", port=5000, debug=debug_mode, threaded=True)