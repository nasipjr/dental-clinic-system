from utils.license_helper import generate_license_key, verify_license_key

def test_generate_and_verify_valid_license():
    key = generate_license_key(days=30, license_type="trial")
    assert key.startswith("DCMS-")
    
    is_valid, data = verify_license_key(key)
    assert is_valid is True
    assert isinstance(data, dict)
    assert data["license_type"] == "trial"
    assert data["days_remaining"] >= 29

def test_verify_invalid_license():
    is_valid, err = verify_license_key("INVALID-LICENSE-KEY")
    assert is_valid is False
    assert "غير صحيحة" in str(err) or "غير متاح" in str(err)

def test_verify_tampered_signature():
    key = generate_license_key(days=30, license_type="trial")
    parts = key.split("-")
    tampered_key = f"{parts[0]}-{parts[1]}-{parts[2]}-0000000000"
    
    is_valid, err = verify_license_key(tampered_key)
    assert is_valid is False
    assert "تم التلاعب" in str(err)
