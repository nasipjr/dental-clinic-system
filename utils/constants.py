APPOINTMENT_REASONS = {
    "Check-up",
    "Cleaning",
    "Filling",
    "Root Canal",
    "Extraction",
    "Crown / Bridge",
    "Braces / Orthodontics",
    "Whitening",
    "Emergency Pain",
    "Follow-up",
}


PATIENT_GENDERS = {
    "Male",
    "Female",
}


TREATMENT_PRICES = {
    "Check-up": 25000,
    "Cleaning": 50000,
    "Filling": 75000,
    "Root Canal": 150000,
    "Extraction": 80000,
    "Crown / Bridge": 200000,
    "Braces / Orthodontics": 300000,
    "Whitening": 120000,
    "Emergency Pain": 60000,
    "Follow-up": 20000,
}


TREATMENT_PROCEDURE_TYPES = set(TREATMENT_PRICES.keys())