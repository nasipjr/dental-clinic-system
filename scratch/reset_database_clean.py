import os
import sys
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, SystemSetting
from scratch.restore_settings_from_backup import restore_settings

def reset_database():
    app.app_context().push()

    # 1. Backup current database file first
    instance_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
    db_file = os.path.join(instance_dir, 'dental_clinic.db')
    backups_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')
    os.makedirs(backups_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backups_dir, f'backup_before_clean_reset_{timestamp}.db')

    if os.path.exists(db_file):
        shutil.copy2(db_file, backup_path)
        print(f"Safety DB backup created at: {backup_path}")

    # 2. Drop all tables and recreate them safely
    print("Dropping all existing database tables...")
    from sqlalchemy import text
    try:
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    except Exception:
        pass

    # Explicitly drop all tables to prevent MySQL named FK constraint issues
    for table_name in reversed(db.metadata.sorted_tables):
        try:
            db.session.execute(text(f"DROP TABLE IF EXISTS `{table_name.name}` CASCADE;"))
        except Exception:
            try:
                db.session.execute(text(f"DROP TABLE IF EXISTS `{table_name.name}`;"))
            except Exception:
                pass
    
    try:
        db.drop_all()
    except Exception:
        pass

    try:
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    except Exception:
        pass

    db.session.commit()

    print("Re-creating clean database tables...")
    db.create_all()

    # 3. Create fresh admin account
    print("Creating fresh admin user account...")
    admin = User(
        username="admin",
        role="admin",
        first_name="Admin",
        last_name="User"
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    print("Admin user seeded successfully: admin / admin123")

    # 4. Restore notification tokens and system settings
    print("Restoring all tokens and clinic settings from backup...")
    restore_settings()

    print("\n=========================================================")
    print("   CLEAN DATABASE RESET COMPLETED SUCCESSFULLY!")
    print("=========================================================")

if __name__ == '__main__':
    reset_database()
