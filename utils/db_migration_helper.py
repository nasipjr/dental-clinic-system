from sqlalchemy import text

def ensure_database_schema(app, db):
    """
    Consolidated helper to verify and dynamically patch missing SQLite/MySQL database columns
    for seamless backwards-compatibility across app versions.
    """
    with app.app_context():
        migrations = [
            ("invoice", "discount", "ALTER TABLE invoice ADD COLUMN discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00"),
            ("invoice", "discount_type", "ALTER TABLE invoice ADD COLUMN discount_type VARCHAR(20) NOT NULL DEFAULT 'value'"),
            ("invoice", "additional_charges", "ALTER TABLE invoice ADD COLUMN additional_charges DECIMAL(10, 2) NOT NULL DEFAULT 0.00"),
            ("invoice", "tax_rate", "ALTER TABLE invoice ADD COLUMN tax_rate DECIMAL(5, 2) NOT NULL DEFAULT 0.00"),
            ("invoice", "patient_id", "ALTER TABLE invoice ADD COLUMN patient_id INT NULL"),
            ("invoice", "notes", "ALTER TABLE invoice ADD COLUMN notes TEXT NULL"),
            ("invoice", "issue_date", "ALTER TABLE invoice ADD COLUMN issue_date DATETIME NULL"),
            ("user", "patient_id", "ALTER TABLE user ADD COLUMN patient_id INT NULL"),
            ("appointment", "duration", "ALTER TABLE appointment ADD COLUMN duration INT NOT NULL DEFAULT 30"),
            ("appointment", "session_opened_at", "ALTER TABLE appointment ADD COLUMN session_opened_at DATETIME NULL"),
            ("patient", "telegram_chat_id", "ALTER TABLE patient ADD COLUMN telegram_chat_id VARCHAR(50) NULL"),
            ("patient", "reminders_enabled", "ALTER TABLE patient ADD COLUMN reminders_enabled BOOLEAN NOT NULL DEFAULT 1"),
            ("patient", "primary_doctor_id", "ALTER TABLE patient ADD COLUMN primary_doctor_id INT NULL"),
            ("patient", "appointment_notes", "ALTER TABLE patient ADD COLUMN appointment_notes TEXT NULL"),
            ("patient", "occupation", "ALTER TABLE patient ADD COLUMN occupation VARCHAR(150) NULL"),
            ("patient", "emergency_contact", "ALTER TABLE patient ADD COLUMN emergency_contact VARCHAR(150) NULL"),
            ("patient", "medicare_number", "ALTER TABLE patient ADD COLUMN medicare_number VARCHAR(100) NULL"),
            ("appointment", "doctor_id", "ALTER TABLE appointment ADD COLUMN doctor_id INT NULL"),
            ("treatment", "doctor_id", "ALTER TABLE treatment ADD COLUMN doctor_id INT NULL"),
            ("treatment", "use_anesthesia", "ALTER TABLE treatment ADD COLUMN use_anesthesia BOOLEAN NOT NULL DEFAULT 0"),
            ("treatment", "anesthesia_needles", "ALTER TABLE treatment ADD COLUMN anesthesia_needles INT NOT NULL DEFAULT 0"),
            ("treatment", "anesthesia_cost", "ALTER TABLE treatment ADD COLUMN anesthesia_cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00"),
            ("treatment", "anesthesia_type", "ALTER TABLE treatment ADD COLUMN anesthesia_type VARCHAR(150) NULL"),
            ("treatment", "teeth_range", "ALTER TABLE treatment ADD COLUMN teeth_range VARCHAR(100) NULL"),
            ("treatment", "quadrant", "ALTER TABLE treatment ADD COLUMN quadrant VARCHAR(50) NULL"),
            ("treatment", "jaw", "ALTER TABLE treatment ADD COLUMN jaw VARCHAR(50) NULL"),
            ("treatment", "salary_expense_id", "ALTER TABLE treatment ADD COLUMN salary_expense_id INT NULL"),
            ("tooth_history", "appointment_id", "ALTER TABLE tooth_history ADD COLUMN appointment_id INT NULL"),
            ("tooth_history", "history_date", "ALTER TABLE tooth_history ADD COLUMN history_date DATE NULL"),
            ("tooth_history", "created_at", "ALTER TABLE tooth_history ADD COLUMN created_at DATETIME NULL"),
        ]


        for table, column, sql in migrations:
            try:
                db.session.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
            except Exception:
                db.session.rollback()
                try:
                    app.logger.info(f"Auto-migrating schema: Adding {column} column to {table} table")
                    db.session.execute(text(sql))
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    app.logger.debug(f"Migration note for {table}.{column}: {e}")

        # Backfill invoice.patient_id from appointment.patient_id for existing records where patient_id is NULL
        try:
            db.session.execute(text(
                "UPDATE invoice SET patient_id = ("
                "SELECT appointment.patient_id FROM appointment WHERE appointment.id = invoice.appointment_id"
                ") WHERE invoice.patient_id IS NULL"
            ))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.debug(f"Backfill invoice.patient_id note: {e}")

