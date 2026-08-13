import sys
import os

# Set root directory in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def reset_admin_password(new_password="admin123"):
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", role="admin", first_name="Admin", last_name="User")
            db.session.add(admin)
            print("Creating default admin account...")
        
        admin.set_password(new_password)
        db.session.commit()
        print("===================================================")
        print(" SUCCESS: Admin password has been reset!")
        print(f" Username: admin")
        print(f" New Password: {new_password}")
        print("===================================================")

if __name__ == "__main__":
    pwd = sys.argv[1] if len(sys.argv) > 1 else "admin123"
    reset_admin_password(pwd)
