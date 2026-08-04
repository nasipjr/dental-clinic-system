import hashlib
import hmac
import os
import sys
from datetime import datetime, timedelta
from flask import current_app

def get_master_license_secret() -> str:
    """
    Returns the master secret used for signing and verifying license keys.
    Reads from LICENSE_MASTER_SECRET env variable or local .master_key file.
    """
    secret = os.getenv("LICENSE_MASTER_SECRET")
    if secret:
        return secret

    from pathlib import Path
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).resolve().parent.parent

    key_file = base_dir / "instance" / ".master_key"
    if key_file.exists():
        try:
            content = key_file.read_text(encoding="utf-8").strip()
            if content:
                return content
        except Exception:
            pass

    return "DCMS-SECRET-LICENSE-KEY-DENTAL-CLINIC-2026-PROTECTED"


TYPE_CODES = {
    "T14": ("trial", 14),
    "T30": ("trial", 30),
    "T60": ("trial", 60),
    "T90": ("trial", 90),
    "A1Y": ("annual", 365),
    "A2Y": ("annual", 730),
    "LIFE": ("lifetime", 36500), # ~100 years
}


def _compute_hmac(payload: str) -> str:
    """Compute HMAC-SHA256 signature for payload and return first 10 hex chars."""
    secret = get_master_license_secret()
    mac = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256)
    return mac.hexdigest()[:10].upper()


def get_local_machine_hwid() -> str:
    """
    Generates a unique, stable Machine Hardware ID (HWID) based on machine system attributes.
    Returns format: HWID-XXXX-YYYY-ZZZZ
    """
    import uuid
    import platform
    raw_info = f"{platform.node()}:{uuid.getnode()}:{platform.processor()}"
    digest = hashlib.sha256(raw_info.encode("utf-8")).hexdigest().upper()
    return f"HWID-{digest[:4]}-{digest[4:8]}-{digest[8:12]}"


def generate_license_key(days: int = 30, license_type: str = "trial", hwid: str = None) -> str:
    """
    Generates a cryptographically signed license key string.
    If hwid is provided, the key will be locked exclusively to that machine.
    Format Universal: DCMS-{TYPE_CODE}-{EXPIRY_YYYYMMDD}-{SIGNATURE}
    Format Locked:    DCMS-{TYPE_CODE}-{EXPIRY_YYYYMMDD}-{HWID_SHORT}-{SIGNATURE}
    """
    now = datetime.now()
    expires_at = now + timedelta(days=days)
    date_str = expires_at.strftime("%Y%m%d")

    # Determine type code
    type_code = "T30"
    for code, (l_type, d_val) in TYPE_CODES.items():
        if l_type == license_type and d_val == days:
            type_code = code
            break
    else:
        if license_type == "lifetime":
            type_code = "LIFE"
            expires_at = now + timedelta(days=36500)
            date_str = expires_at.strftime("%Y%m%d")
        else:
            type_code = f"T{days}"

    clean_hwid = hwid.strip().upper() if hwid else None
    if clean_hwid:
        raw_payload = f"{type_code}:{date_str}:{clean_hwid}"
        sig = _compute_hmac(raw_payload)
        hwid_part = clean_hwid.replace("-", "")
        return f"DCMS-{type_code}-{date_str}-{hwid_part}-{sig}"
    else:
        raw_payload = f"{type_code}:{date_str}"
        sig = _compute_hmac(raw_payload)
        return f"DCMS-{type_code}-{date_str}-{sig}"


def verify_license_key(key_string: str, current_hwid: str = None) -> tuple[bool, dict | str]:
    """
    Verifies that a license key string is authentic and valid for the current machine.
    Returns (True, payload_dict) or (False, error_message).
    """
    if not key_string or not isinstance(key_string, str):
        return False, "مفتاح الترخيص غير متاح أو فارغ."

    clean_key = key_string.strip().upper()
    parts = clean_key.split("-")

    if parts[0] != "DCMS":
        return False, "صيغة مفتاح الترخيص غير صحيحة."

    if len(parts) == 4:
        # Universal License: DCMS-TYPE-DATE-SIG
        prefix, type_code, date_str, sig = parts
        raw_payload = f"{type_code}:{date_str}"
        bound_hwid = None
    elif len(parts) >= 5:
        # Machine Locked License: DCMS-TYPE-DATE-HWID_PART-SIG
        prefix = parts[0]
        type_code = parts[1]
        date_str = parts[2]
        sig = parts[-1]
        bound_hwid_part = "-".join(parts[3:-1])
        
        # Check current machine HWID
        if not current_hwid:
            current_hwid = get_local_machine_hwid()
            
        clean_current_hwid = current_hwid.strip().upper()
        raw_payload = f"{type_code}:{date_str}:{clean_current_hwid}"
        bound_hwid = clean_current_hwid
    else:
        return False, "صيغة مفتاح الترخيص غير صحيحة."

    # Re-verify HMAC signature
    expected_sig = _compute_hmac(raw_payload)

    if not hmac.compare_digest(sig, expected_sig):
        if len(parts) >= 5:
            return False, "مفتاح الترخيص غير مخصص لهذا الكمبيوتر (HWID Mismatch)."
        return False, "مفتاح الترخيص غير صالح أو تم التلاعب برموزه."

    try:
        expires_at = datetime.strptime(date_str, "%Y%m%d")
        expires_at = expires_at.replace(hour=23, minute=59, second=59)
    except ValueError:
        return False, "تاريخ الانتهاء المشفر في المفتاح غير صالح."
        return False, "تاريخ الانتهاء المشفر في المفتاح غير صالح."

    # Determine license type description
    l_type = "trial"
    if type_code.startswith("A"):
        l_type = "annual"
    elif type_code == "LIFE":
        l_type = "lifetime"

    now = datetime.now()
    if expires_at < now:
        return False, f"انتهت صلاحية هذا المفتاح بتاريخ {expires_at.strftime('%Y-%m-%d')}."

    days_remaining = (expires_at - now).days

    return True, {
        "key": clean_key,
        "type_code": type_code,
        "license_type": l_type,
        "expires_at": expires_at,
        "days_remaining": days_remaining,
    }


def check_clock_tampering() -> tuple[bool, str]:
    """
    Checks if the system clock was set backwards to cheat trial period.
    Returns (is_tampered, message).
    """
    from utils.settings_helper import get_setting, set_setting

    last_seen_str = get_setting("last_system_activity", "")
    now = datetime.now()

    if last_seen_str:
        try:
            last_seen = datetime.strptime(last_seen_str, "%Y-%m-%d %H:%M:%S")
            # Allow 5 minutes tolerance for minor clock drift
            if now < (last_seen - timedelta(minutes=5)):
                return True, f"تم الكشف عن تلاعب بتاريخ الكمبيوتر! (التاريخ الحالي {now.strftime('%Y-%m-%d')} أقدم من آخر نشاط {last_seen.strftime('%Y-%m-%d')})"
        except ValueError:
            pass

    # Update last seen timestamp
    set_setting("last_system_activity", now.strftime("%Y-%m-%d %H:%M:%S"))
    return False, ""


def reset_clock_activity():
    """Resets the last system activity timestamp to current system time."""
    from utils.settings_helper import set_setting
    set_setting("last_system_activity", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))



def get_current_license_status() -> dict:
    """
    Returns current active license status details from DB.
    """
    from utils.settings_helper import get_setting

    active_key = get_setting("active_license_key", "")

    if not active_key:
        return {
            "is_active": False,
            "status_code": "NO_LICENSE",
            "message": "لم يتم تفعيل أي مفتاح ترخيص بعد.",
            "days_remaining": 0,
            "license_type": "None",
            "expires_at": None,
        }

    # Check clock tampering first
    is_tampered, tamper_msg = check_clock_tampering()
    if is_tampered:
        return {
            "is_active": False,
            "status_code": "CLOCK_TAMPERED",
            "message": tamper_msg,
            "days_remaining": 0,
            "license_type": "Tampered",
            "expires_at": None,
        }

    is_valid, data = verify_license_key(active_key)
    if not is_valid:
        return {
            "is_active": False,
            "status_code": "EXPIRED_OR_INVALID",
            "message": str(data),
            "days_remaining": 0,
            "license_type": "Expired",
            "expires_at": None,
        }

    return {
        "is_active": True,
        "status_code": "VALID",
        "message": f"الترخيص مفعل وجاهز ({data['days_remaining']} يوماً متبقية).",
        "days_remaining": data["days_remaining"],
        "license_type": data["license_type"],
        "expires_at": data["expires_at"].strftime("%Y-%m-%d"),
        "key": data["key"],
    }
