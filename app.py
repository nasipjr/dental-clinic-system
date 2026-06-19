from flask import Flask, request

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


with app.app_context():
    db.create_all()
    populate_default_settings()
    check_and_add_discount_column()

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


@app.context_processor
def inject_settings():
    from utils.settings_helper import get_setting, get_currency_symbol
    return {
        "clinic_name": get_setting("clinic_name", "Clinic"),
        "currency_symbol": get_currency_symbol(),
        "clinic_phone": get_setting("clinic_phone", "+963 958 948 727"),
        "clinic_email": get_setting("clinic_email", "kh.nasipdragon@gmail.com"),
        "clinic_address": get_setting("clinic_address", "Damascus, Syria")
    }


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