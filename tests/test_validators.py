from datetime import datetime, timedelta
from utils.validators import (
    parse_treatment_money,
    parse_patient_data,
    parse_payment_amount,
    parse_invoice_payment_amount,
)

def test_parse_treatment_money_valid():
    total, paid, err = parse_treatment_money(100, 50)
    assert err is None
    assert total == 100.0
    assert paid == 50.0

def test_parse_treatment_money_invalid_negative():
    total, paid, err = parse_treatment_money(-50, 0)
    assert total is None
    assert "cannot be negative" in err

def test_parse_treatment_money_paid_exceeds_total():
    total, paid, err = parse_treatment_money(50, 100)
    assert total is None
    assert "cannot be greater than" in err

def test_parse_patient_data_missing_fields():
    patient_data, err = parse_patient_data({})
    assert patient_data is None
    assert "First name is required" in err

def test_parse_patient_data_valid(app):
    form = {
        "first_name": "Ahmad",
        "last_name": "Sami",
        "gender": "Male",
        "date_of_birth": "1990-05-15",
        "phone": "+963958948727",
        "email": "ahmad@example.com"
    }
    patient_data, err = parse_patient_data(form)
    assert err is None
    assert patient_data["first_name"] == "Ahmad"
    assert patient_data["last_name"] == "Sami"

def test_parse_payment_amount_valid():
    amt, err = parse_payment_amount("150", 200)
    assert err is None
    assert amt == 150.0

def test_parse_payment_amount_exceeds_remaining():
    amt, err = parse_payment_amount("300", 200)
    assert amt is None
    assert "cannot be greater than the remaining amount" in err
