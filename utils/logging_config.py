import json
import logging
from pathlib import Path


def load_log_directory(config_file: Path) -> str:
    if not config_file.exists():
        raise RuntimeError(
            "System is not configured yet. Please run setup.py first."
        )

    try:
        with config_file.open("r", encoding="utf-8") as file:
            config_data = json.load(file)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Configuration file is invalid. Please check config/clinic_config.json."
        ) from exc

    log_directory = str(config_data.get("log_directory", "")).strip()

    if not log_directory:
        raise RuntimeError(
            "Configuration is incomplete. Missing log_directory."
        )

    return log_directory


def setup_logging(app, log_directory: str, log_file_name: str) -> None:
    log_dir = Path(log_directory).expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / log_file_name

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False