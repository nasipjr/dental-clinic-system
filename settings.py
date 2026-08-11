import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

#gives us Path object for settings.py then gives us the parent directory of settings.py which is the root of our project. This allows us to construct paths to other files in a way that works regardless of where the code is run from.
import sys

if getattr(sys, 'frozen', False):
    # Path of the folder where the .exe file resides
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent


def is_port_open(host, port, timeout=1.0):
    import socket
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except Exception:
        return False


def build_database_uri():
    if os.getenv("TESTING") == "true":
        instance_dir = BASE_DIR / "instance"
        instance_dir.mkdir(parents=True, exist_ok=True)
        test_db_path = instance_dir / "test_suite_dental_clinic.db"
        return f"sqlite:///{test_db_path.as_posix()}"

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    db_engine = os.getenv("DB_ENGINE", "").lower()
    is_pythonanywhere = (
        "PYTHONANYWHERE_DOMAIN" in os.environ
        or "PYTHONANYWHERE_SITE" in os.environ
        or "PYTHONANYWHERE_SERVICE" in os.environ
    )

    if db_engine == "mysql":
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "1234")
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "dental_clinic")
        return (
            f"mysql+pymysql://{db_user}:{db_password}"
            f"@{db_host}:{db_port}/{db_name}"
        )

    # Only probe port 3308 on local dev if DB_ENGINE is unspecified and not on PythonAnywhere
    if not db_engine and not is_pythonanywhere:
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "1234")
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = os.getenv("DB_PORT", "3308")
        db_name = os.getenv("DB_NAME", "dental_clinic")
        if is_port_open(db_host, db_port):
            return (
                f"mysql+pymysql://{db_user}:{db_password}"
                f"@{db_host}:{db_port}/{db_name}"
            )

    # Fallback to zero-dependency embedded SQLite database
    instance_dir = BASE_DIR / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)
    db_path = instance_dir / "dental_clinic.db"
    return f"sqlite:///{db_path.as_posix()}"


def get_or_create_secret_key():
    """
    Returns SECRET_KEY from environment if available.
    Otherwise, reads or generates a secure random secret key saved in instance/.secret_key.
    This ensures every installation/deployment has a unique, cryptographically strong secret key.
    """
    secret = os.getenv("SECRET_KEY")
    if secret:
        return secret

    instance_dir = BASE_DIR / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)
    key_file = instance_dir / ".secret_key"

    if key_file.exists():
        try:
            stored_key = key_file.read_text(encoding="utf-8").strip()
            if stored_key:
                return stored_key
        except Exception:
            pass

    import secrets
    new_key = secrets.token_hex(32)
    try:
        key_file.write_text(new_key, encoding="utf-8")
    except Exception:
        pass

    return new_key


class Config:
    SECRET_KEY = get_or_create_secret_key()

    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", str(BASE_DIR / "logs"))
    LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "clinic.log")

    # Auto-deploy via GitHub Webhook
    DEPLOY_SECRET = os.getenv("DEPLOY_SECRET", "")