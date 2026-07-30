import os
import sys
import random
from decimal import Decimal
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Patient, Appointment, Treatment, Invoice, Payment, PaymentAllocation, ToothHistory

def seed_clinic_data():
    app.app_context().push()

    patients = Patient.query.all()
    if not patients:
        print("No patients found! Please seed patients first.")
        return

    procedures_data = [
        {"name": "فحص دوري", "cost": Decimal("25000")},
        {"name": "تنظيف وتلميع", "cost": Decimal("50000")},
        {"name": "حشوة أسنان", "cost": Decimal("75000")},
        {"name": "علاج عصب السن", "cost": Decimal("150000")},
        {"name": "تاج / جسر", "cost": Decimal("200000")},
        {"name": "تقويم الأسنان", "cost": Decimal("300000")},
        {"name": "تبييض الأسنان", "cost": Decimal("120000")},
        {"name": "قلع سن", "cost": Decimal("80000")},
        {"name": "زيركون ليزري", "cost": Decimal("400000")},
    ]

    reasons = [
        "ألم شديد في الضرس",
        "مراجعة دورية وتنظيف",
        "تركيب حشوة ضوئية",
        "استكمال علاج العصب",
        "قلع سن العقل",
        "تبييض أسنان ليزري",
        "تركيب تاج زيركون"
    ]

    now = datetime.now()

    created_appointments = 0
    created_treatments = 0
    created_invoices = 0
    created_payments = 0

    # 1. Past Appointments (-60 days to -1 day)
    for p in patients:
        # Each patient gets 1 to 4 past appointments
        num_past = random.randint(1, 4)
        for _ in range(num_past):
            days_ago = random.randint(1, 60)
            hour = random.randint(9, 17)
            minute = random.choice([0, 15, 30, 45])
            appt_date = now - timedelta(days=days_ago, hours=now.hour - hour, minutes=now.minute - minute)
            
            # Status: 85% Completed, 15% Cancelled
            is_completed = random.random() < 0.85
            status = "Done" if is_completed else "Cancelled"

            appt = Appointment(
                patient_id=p.id,
                appointment_date=appt_date,
                reason=random.choice(reasons),
                status=status,
                session_opened_at=appt_date if is_completed else None
            )
            db.session.add(appt)
            db.session.flush() # get appt.id
            created_appointments += 1

            if is_completed:
                # Add 1 to 3 treatments
                num_treatments = random.randint(1, 3)
                treatments_for_appt = []
                for _ in range(num_treatments):
                    proc = random.choice(procedures_data)
                    tooth_num = str(random.randint(1, 32))
                    use_anest = random.choice([True, False])
                    anest_needles = random.randint(1, 2) if use_anest else 0
                    anest_cost = Decimal(str(anest_needles * 50000)) if use_anest else Decimal('0.00')

                    t = Treatment(
                        appointment_id=appt.id,
                        treatment_date=appt_date,
                        procedure_type=proc["name"],
                        tooth_number=tooth_num,
                        total_cost=proc["cost"] + anest_cost,
                        use_anesthesia=use_anest,
                        anesthesia_needles=anest_needles,
                        anesthesia_cost=anest_cost,
                        notes=f"تم إنجاز {proc['name']} بنجاح للسن رقم {tooth_num}"
                    )
                    db.session.add(t)
                    treatments_for_appt.append(t)
                    created_treatments += 1

                    # Add ToothHistory
                    th = ToothHistory(
                        patient_id=p.id,
                        tooth_number=tooth_num,
                        procedure_type=proc["name"],
                        notes=f"معالجة تاريخية للسن رقم {tooth_num}",
                        created_at=appt_date
                    )
                    db.session.add(th)

                db.session.flush()

                # Generate Invoice
                subtotal = sum((t.total_cost for t in treatments_for_appt), Decimal('0.00'))
                discount = Decimal('0.00')
                if random.random() < 0.3:
                    discount = Decimal(str(random.choice([10000, 20000, 25000])))

                inv = Invoice(
                    appointment_id=appt.id,
                    patient_id=p.id,
                    issue_date=appt_date,
                    discount=discount,
                    discount_type="value",
                    additional_charges=Decimal('0.00'),
                    tax_rate=Decimal('0.00')
                )
                db.session.add(inv)
                db.session.flush()
                created_invoices += 1

                # Generate Payments & Allocations
                total_due = inv.total_amount
                # Scenario: 50% Full Paid, 30% Partial Paid (Debtor), 20% Prepaid/Overpaid (Credit)
                pay_scenario = random.random()
                if pay_scenario < 0.5:
                    paid_amt = total_due
                elif pay_scenario < 0.8:
                    paid_amt = (total_due * Decimal('0.5')).quantize(Decimal('1.00'))
                else:
                    paid_amt = total_due + Decimal(str(random.choice([20000, 50000, 100000])))

                if paid_amt > 0:
                    pmt = Payment(
                        patient_id=p.id,
                        amount=paid_amt,
                        payment_date=appt_date + timedelta(minutes=45),
                        notes="سداد دفعة نقدية بالاستقبال"
                    )
                    db.session.add(pmt)
                    db.session.flush()
                    created_payments += 1

                    # Allocate to invoice up to total_due
                    alloc_amt = min(paid_amt, total_due)
                    if alloc_amt > 0:
                        alloc = PaymentAllocation(
                            payment_id=pmt.id,
                            invoice_id=inv.id,
                            amount=alloc_amt
                        )
                        db.session.add(alloc)

    # 2. Future Appointments (+1 day to +30 days)
    for p in patients[:12]:
        days_ahead = random.randint(1, 30)
        hour = random.randint(9, 16)
        minute = random.choice([0, 30])
        appt_date = now + timedelta(days=days_ahead, hours=hour - now.hour, minutes=minute - now.minute)

        appt = Appointment(
            patient_id=p.id,
            appointment_date=appt_date,
            reason=random.choice(reasons),
            status="Scheduled"
        )
        db.session.add(appt)
        created_appointments += 1

    db.session.commit()

    print("\n=========================================================")
    print(f"  CLINIC DATA SEEDED SUCCESSFULLY!")
    print(f"  - Appointments Created: {created_appointments}")
    print(f"  - Treatments Recorded: {created_treatments}")
    print(f"  - Invoices Issued:     {created_invoices}")
    print(f"  - Payments Processed:  {created_payments}")
    print("=========================================================")

if __name__ == '__main__':
    seed_clinic_data()
