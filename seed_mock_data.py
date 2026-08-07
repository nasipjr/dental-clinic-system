import sys
import random
from datetime import datetime, timedelta, time
from decimal import Decimal

from app import app
from models import db, Patient, Appointment, Treatment, Invoice, Payment, PaymentAllocation, User

from utils.settings_helper import get_treatment_prices

# Realistic Arabic Sample Data
FIRST_NAMES_MALE = [
    "أحمد", "محمود", "عمر", "خالد", "محمد", "سامر", "يوسف", "طارق", "حسن", "علي",
    "باسل", "ماهر", "رامي", "فادي", "عصام", "زياد", "أيمن", "هاني", "أنس", "نضال"
]

FIRST_NAMES_FEMALE = [
    "مريم", "سارة", "فاطمة", "رانيا", "نور", "هدى", "لينا", "دينا", "منى", "رشا",
    "ياسمين", "سحر", "ريم", "هبة", "عبير", "أميرة", "غادة", "وفاء", "زينب", "سناء"
]

LAST_NAMES = [
    "الخليل", "الحسن", "الأحمد", "المصطفى", "الشامي", "الخطيب", "العلي", "السيد",
    "النجار", "الحداد", "البيطار", "الحكيم", "الصالح", "الرفاعي", "العمري", "العطار",
    "الزعبي", "الحوراني", "المصري", "الكردي"
]

CITIES = ["دمشق", "حلب", "حمص", "حماة", "اللاذقية", "طرطوس"]

def get_settings_procedures():
    prices = get_treatment_prices()
    teeth_options = [["11"], ["12"], ["21"], ["22"], ["16", "26"], ["36", "46"], ["الكل"]]
    procs = []
    for name, price in prices.items():
        procs.append({
            "name": name,
            "price": Decimal(str(price)),
            "teeth": random.choice(teeth_options)
        })
    return procs

MEDICAL_NOTES = [
    "لا يعاني من أي أمراض مزمنة.",
    "تحسس من البنسلين.",
    "ارتفاع ضغط الدم - يتناول علاج منتظم.",
    "سكري النمط الثاني - منضبط.",
    "حامل في الشهر الخامس.",
    "سوابق نزفية بسيطة.",
    "سليم تماماً."
]


def generate_random_date(start_date, end_date):
    delta_days = (end_date - start_date).days
    random_day = random.randint(0, delta_days)
    random_hour = random.randint(9, 18) # 9 AM to 6 PM
    random_minute = random.choice([0, 15, 30, 45])
    d = start_date + timedelta(days=random_day)
    return datetime.combine(d, time(random_hour, random_minute))


def seed_data():
    with app.app_context():
        print("Starting mock data generation (2024 - 2026)...")

        # Fix any past Scheduled appointments in DB
        now_dt = datetime.now()
        past_scheduled = Appointment.query.filter(
            Appointment.status == "Scheduled",
            Appointment.appointment_date < now_dt
        ).all()
        for p_appt in past_scheduled:
            if p_appt.treatments:
                p_appt.status = "Done"
            else:
                p_appt.status = "Cancelled"
        db.session.commit()

        # Fetch doctors
        doctors = User.query.filter(User.role.in_(["admin", "doctor"])).all()
        doctor_id = doctors[0].id if doctors else None

        start_2024 = datetime(2024, 1, 1).date()
        today = datetime.now().date() + timedelta(days=30) # allow future appointments up to 30 days ahead

        # 1. Create 60 Patients
        patients = []
        for i in range(60):
            is_female = random.choice([True, False])
            first_name = random.choice(FIRST_NAMES_FEMALE if is_female else FIRST_NAMES_MALE)
            last_name = random.choice(LAST_NAMES)
            gender = "Female" if is_female else "Male"
            dob = generate_random_date(datetime(1965, 1, 1).date(), datetime(2010, 1, 1).date()).date()
            phone = f"09{random.randint(30000000, 99999999)}"
            email = f"patient{i+1}@example.com"
            city = random.choice(CITIES)

            patient = Patient(
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=dob,
                phone=phone,
                email=email,
                city=city,
                address=f"شارع الرئيسي - {city}",
                medical_information=random.choice(MEDICAL_NOTES),
                reminders_enabled=random.choice([True, True, False]),
                primary_doctor_id=doctor_id
            )
            db.session.add(patient)
            patients.append(patient)

        db.session.commit()
        print(f"Added {len(patients)} patients successfully.")

        # 2. Create 350 Appointments
        appointments = []
        for i in range(350):
            patient = random.choice(patients)
            appt_datetime = generate_random_date(start_2024, today)
            
            # If date is in the future relative to now, status is Scheduled
            # If in the past, status is Done (85%) or Cancelled (15%)
            if appt_datetime > datetime.now():
                status = "Scheduled"
            else:
                status = "Done" if random.random() < 0.85 else "Cancelled"

            procedures_list = get_settings_procedures()
            proc = random.choice(procedures_list)
            reason = proc["name"]
            assigned_doc = random.choice(doctors) if doctors else None
            assigned_doc_id = assigned_doc.id if assigned_doc else None

            appointment = Appointment(
                patient_id=patient.id,
                appointment_date=appt_datetime,
                reason=reason,
                status=status,
                doctor_id=assigned_doc_id
            )
            db.session.add(appointment)
            appointments.append((appointment, proc))

        db.session.commit()
        print(f"Added {len(appointments)} appointments.")

        # 3. Create Treatments, Invoices, & Payments for Done Appointments
        treatments_count = 0
        invoices_count = 0
        payments_count = 0
        procedures_list = get_settings_procedures()

        for appt, proc in appointments:
            if appt.status == "Done":
                # Create 1 to 2 treatments
                num_treatments = random.choice([1, 1, 2])
                appt_treatments = []

                for t_idx in range(num_treatments):
                    p_info = proc if t_idx == 0 else random.choice(procedures_list)
                    tooth = random.choice(p_info["teeth"])
                    cost = p_info["price"]

                    treatment = Treatment(
                        appointment_id=appt.id,
                        treatment_date=appt.appointment_date,
                        procedure_type=p_info["name"],
                        tooth_number=tooth,
                        notes="تمت المعالجة بنجاح وبشكل سليم.",
                        total_cost=cost,
                        doctor_id=appt.doctor_id
                    )
                    db.session.add(treatment)
                    appt_treatments.append(treatment)
                    treatments_count += 1

                db.session.flush()

                # Create Invoice
                subtotal = sum(t.total_cost for t in appt_treatments)
                discount = Decimal('0.00')
                if random.random() < 0.2: # 20% chance of discount
                    discount = Decimal(str(random.choice([25, 50, 100])))

                invoice = Invoice(
                    appointment_id=appt.id,
                    patient_id=appt.patient_id,
                    issue_date=appt.appointment_date,
                    discount=discount,
                    discount_type="value"
                )
                db.session.add(invoice)
                db.session.flush()
                invoices_count += 1

                # Payment (85% paid or partially paid)
                if random.random() < 0.85:
                    total_to_pay = invoice.total_amount
                    if total_to_pay > 0:
                        # Paid amount: 100% full, or 50% partial
                        is_full = random.choice([True, True, True, False])
                        pay_amount = total_to_pay if is_full else (total_to_pay / Decimal('2.00')).quantize(Decimal('0.01'))

                        payment = Payment(
                            patient_id=appt.patient_id,
                            amount=pay_amount,
                            payment_date=appt.appointment_date + timedelta(minutes=random.randint(15, 60)),
                            notes="دفعة نقداً عند مغادرة العيادة"
                        )
                        db.session.add(payment)
                        db.session.flush()
                        payments_count += 1

                        allocation = PaymentAllocation(
                            payment_id=payment.id,
                            invoice_id=invoice.id,
                            amount=pay_amount
                        )
                        db.session.add(allocation)

        db.session.commit()
        print(f"Added {treatments_count} treatments.")
        print(f"Added {invoices_count} invoices.")
        print(f"Added {payments_count} payments.")

        print("Mock data generation completed successfully!")


if __name__ == "__main__":
    seed_data()
