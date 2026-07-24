import unittest
from datetime import datetime
from decimal import Decimal

from utils.validators import (
    parse_treatment_money,
    parse_patient_data,
    parse_payment_amount,
)
from utils.license_helper import generate_license_key, verify_license_key


class DentalClinicTestCase(unittest.TestCase):
    def test_parse_treatment_money(self):
        total, paid, err = parse_treatment_money(100, 50)
        self.assertIsNone(err)
        self.assertEqual(total, 100.0)
        self.assertEqual(paid, 50.0)

        total, paid, err = parse_treatment_money(-10, 0)
        self.assertIsNone(total)
        self.assertIn("cannot be negative", err)

    def test_parse_patient_data(self):
        form = {
            "first_name": "Sami",
            "last_name": "Karim",
            "gender": "Male",
            "date_of_birth": "1988-11-20"
        }
        data, err = parse_patient_data(form)
        self.assertIsNone(err)
        self.assertEqual(data["first_name"], "Sami")

    def test_license_key_generation_and_verification(self):
        key = generate_license_key(days=30, license_type="trial")
        self.assertTrue(key.startswith("DCMS-"))
        is_valid, data = verify_license_key(key)
        self.assertTrue(is_valid)
        self.assertIsInstance(data, dict)
        self.assertEqual(data["license_type"], "trial")
        self.assertGreaterEqual(data["days_remaining"], 29)

    def test_payment_validation(self):
        amount, err = parse_payment_amount("150.00", 200.00)
        self.assertIsNone(err)
        self.assertEqual(amount, 150.0)

        amount, err = parse_payment_amount("250.00", 200.00)
        self.assertIsNone(amount)
        self.assertIn("cannot be greater than", err)


if __name__ == "__main__":
    unittest.main()
