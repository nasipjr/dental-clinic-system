import hashlib
import hmac
import logging
import os
import subprocess

from flask import Blueprint, request, jsonify

deploy_bp = Blueprint("deploy", __name__)
logger = logging.getLogger(__name__)


def _verify_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    """Verify that the request actually came from GitHub using HMAC-SHA256."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


@deploy_bp.route("/deploy", methods=["POST"])
def deploy():
    """
    GitHub Webhook endpoint.
    GitHub sends a POST request here on every push.
    We verify the secret, run git pull, then touch the WSGI file
    to trigger a reload on PythonAnywhere.
    """
    secret = os.getenv("DEPLOY_SECRET", "")

    if not secret:
        logger.error("DEPLOY_SECRET is not set – webhook rejected.")
        return jsonify({"error": "Deploy secret not configured"}), 500

    payload = request.get_data()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not _verify_signature(payload, signature, secret):
        logger.warning("Webhook received with invalid signature – rejected.")
        return jsonify({"error": "Invalid signature"}), 403

    try:
        # Run git pull in the project root
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        logger.info(f"git pull stdout: {result.stdout}")
        if result.returncode != 0:
            logger.error(f"git pull failed: {result.stderr}")
            return jsonify({"error": "git pull failed", "detail": result.stderr}), 500

    except subprocess.TimeoutExpired:
        logger.error("git pull timed out after 60 seconds.")
        return jsonify({"error": "git pull timed out"}), 500
    except Exception as e:
        logger.exception(f"Unexpected error during git pull: {e}")
        return jsonify({"error": str(e)}), 500

    # Touch the WSGI file to trigger a reload on PythonAnywhere
    try:
        wsgi_candidates = [
            "/var/www/nasipjr_pythonanywhere_com_wsgi.py",
        ]
        for wsgi_path in wsgi_candidates:
            if os.path.exists(wsgi_path):
                os.utime(wsgi_path, None)
                logger.info(f"Touched WSGI file: {wsgi_path}")
                break
    except Exception as e:
        logger.warning(f"Could not touch WSGI file (non-fatal): {e}")

    logger.info("Auto-deploy completed successfully.")
    return jsonify({"status": "ok", "output": result.stdout}), 200


@deploy_bp.route("/cron/daily-tasks", methods=["GET", "POST"])
def run_cron_daily_tasks():
    """
    Protected endpoint to trigger daily scheduled tasks (Backup, Reminders, Cleanup)
    via external cron job or PythonAnywhere scheduled tasks.
    """
    secret = os.getenv("DEPLOY_SECRET", "")
    req_secret = request.args.get("secret") or request.headers.get("X-Cron-Secret")
    if secret and req_secret != secret:
        return jsonify({"error": "Unauthorized"}), 403

    results = {}
    
    # 1. Database backup
    try:
        from utils.backup_helper import run_database_backup
        backup_file = run_database_backup()
        results["backup"] = f"Success ({backup_file})"
    except Exception as e:
        logger.error(f"Cron DB backup failed: {e}")
        results["backup"] = f"Error: {e}"

    # 2. Appointment reminders
    try:
        from utils.notification_helper import send_appointment_reminders
        sent_count = send_appointment_reminders()
        results["reminders"] = f"Success ({sent_count} sent)"
    except Exception as e:
        logger.error(f"Cron reminders failed: {e}")
        results["reminders"] = f"Error: {e}"

    # 3. Expired appointments cleanup
    try:
        from routes.appointments import cleanup_expired_pending_appointments
        cleaned_count = cleanup_expired_pending_appointments()
        results["cleanup"] = f"Success ({cleaned_count} cleaned)"
    except Exception as e:
        logger.error(f"Cron cleanup failed: {e}")
        results["cleanup"] = f"Error: {e}"

    return jsonify({"status": "completed", "results": results}), 200
