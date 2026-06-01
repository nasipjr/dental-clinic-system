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


app = Flask(__name__)
app.config.from_object(Config)

LOG_DIRECTORY = app.config["LOG_DIRECTORY"]
LOG_FILE_NAME = app.config["LOG_FILE_NAME"]

db.init_app(app)

with app.app_context():
    db.create_all()

setup_logging(app, LOG_DIRECTORY, LOG_FILE_NAME)
app.logger.info("Application started successfully")

app.register_blueprint(dashboard_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(treatments_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(invoices_bp)


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