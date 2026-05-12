import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


def build_database_uri():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "1234")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3308")
    db_name = os.getenv("DB_NAME", "dental_clinic")

    return (
        f"mysql+pymysql://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLINIC_CONFIG_FILE = BASE_DIR / "config" / "clinic_config.json"
    LOG_FILE_NAME = os.getenv("LOG_FILE_NAME", "clinic.log")