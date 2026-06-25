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
