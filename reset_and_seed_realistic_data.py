import os
import sys
import random
from datetime import datetime, date, timedelta, time
from decimal import Decimal

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

from app import app, db
from models import (
    User, Patient, Appointment, Treatment, ToothHistory,
    TreatmentPlanItem, Invoice, Payment, PaymentAllocation,
    Expense, StaffSalary, PatientFile, NotificationLog, SystemSetting
)
from utils.settings_helper import populate_default_settings, get_treatment_details, get_treatment_prices, set_setting
from services.payment_service import allocate_patient_payments_to_invoices

# ==========================================
# 1. REALISTIC ARABIC / SYRIAN DATA ARRAYS
# ==========================================
FIRST_NAMES_MALE = [
    "أحمد", "محمد", "عمر", "خالد", "سامر", "يوسف", "طارق", "حسن", "علي", "باسل",
    "ماهر", "رامي", "فادي", "عصام", "زياد", "أيمن", "هاني", "أنس", "نضال", "كريم",
    "بلال", "وسيم", "وليد", "غياث", "عمار", "مأمون", "براء", "جهاد", "معتز", "فراس",
    "حسام", "شادي", "جمال", "سامي", "نبيل", "مروان", "تامر", "عدنان", "صبحي", "منير",
    "سليمان", "إبراهيم", "حمزة", "عبد الرحمن", "عبد الله", "يحيى", "مصطفى", "بشير", "خلدون", "طلال"
]

FIRST_NAMES_FEMALE = [
    "مريم", "سارة", "فاطمة", "رانيا", "نور", "هدى", "لينا", "دينا", "منى", "رشا",
    "ياسمين", "سحر", "ريم", "هبة", "عبير", "أميرة", "غادة", "وفاء", "زينب", "سناء",
    "لجين", "شهد", "تالا", "مايا", "حلا", "آية", "رزان", "روان", "ميس", "ندى",
    "سمر", "لبنى", "خلود", "إلهام", "بشرى", "ديمة", "سوزان", "جوانا", "رهف", "لمى",
    "بيان", "سلوى", "نغم", "لارا", "يارا", "جود", "سيلين", "نادين", "هالة", "فرح"
]

LAST_NAMES = [
    "الخليل", "الحسن", "الأحمد", "المصطفى", "الشامي", "الخطيب", "العلي", "السيد",
    "النجار", "الحداد", "البيطار", "الحكيم", "الصالح", "الرفاعي", "العمري", "العطار",
    "الزعبي", "الحوراني", "المصري", "الكردي", "الحلبي", "القاسمي", "البغدادي", "الدمشقي",
    "حيدر", "سليمان", "عباس", "منصور", "مراد", "عثمان", "درويش", "داوود", "إسماعيل",
    "شاهين", "طحان", "غزال", "صابوني", "بركات", "ديب", "حموي", "لاذقاني", "طرابيشي",
    "عجلاني", "ملكي", "جركيس", "بيازيد", "عرقسوسي", "مارديني", "قنواتي", "سيروان"
]

DISTRICTS_DAMASCUS = [
    "المزة - فيلات غربية", "المزة - أوتوستراد", "الميدان - الجزماتية", "كفرسوسة - تنظيم جديد",
    "الشعلان - شارع الحبيب", "الصالحية - الشهداء", "المهاجرين - خورشيد", "أبو رمانة",
    "القصاع - ساحة جورج خوري", "باب توما", "مشروع دمر - الجزيرة الأولى", "قدسيا الجديدة",
    "جرمانا - القريات", "جرمانا - كشكول", "صحنايا", "المالكي", "البرامكة", "ركن الدين"
]

OTHER_CITIES = [
    "دمشق", "ريف دمشق", "حلب", "حمص", "حماة", "اللاذقية", "طرطوس", "السويداء", "درعا"
]

OCCUPATIONS = [
    "مهندس معلوماتية", "مهندس مدني", "مهندس عمارة", "طبيب عام", "صيدلاني", "محامي",
    "مدرس لغة عربية", "مدرسة لغة إنجليزية", "أستاذ جامعي", "محاسب مالي", "مدير تسويق",
    "تاجر أقمشة", "صاحب متجر", "طالب جامعي", "طالبة ثانوية", "ربة منزل", "موظف بنك",
    "مصمم جرافيك", "مترجم فوري", "موظف حكومي", "فني مختبر", "ممرضة", "رجل أعمال", "متقاعد"
]

MEDICAL_NOTES_LIST = [
    "لا يعاني من أي أمراض مزمنة أو تحسس دوائي.",
    "تحسس حاد من البنسلين ومشتقاته (Penicillin Allergy).",
    "ارتفاع ضغط الدم الشرياني - يتناول علاج أملوديبين بانتظام.",
    "مرض السكري النمط الثاني - منضبط بالحمية والعلاج الفموي.",
    "ربو قصبي تحسسي - يستخدم بخاخ فنتولين عند اللزوم.",
    "سوابق نزفية خفيفة بعد القلع الجراحي.",
    "حامل في الثلث الثاني - تجنب الأشعة السينية غير الضرورية.",
    "حساسية من مادة اللاتكس (Latex Allergy).",
    "مركب صمام قلبي صناعي - يتطلب وقاية بالمضادات الحيوية قبل الجراحة.",
    "قصور درق معالج بالإلتروكسين.",
    "سليم تماماً وبصحة جيدة جداً."
]

PRIOR_HISTORIES = [
    ("قلع سن (سابق)", "تم القلع خارج العيادة قبل عدة سنوات لتهدم التاج."),
    ("حشوة قديمة (سابق)", "حشوة أملغم فضية قديمة موضوعة منذ أكثر من 5 سنوات."),
    ("علاج عصب سابق", "معالجة لبية سابقة غير مكتملة خارج القطر."),
    ("تاج خزفي سابق", "تلبيسة بورسلين قديمة على السن المذكور."),
    ("جسر أسنان سابق", "جسر تعويضي قديم ثابت تم تركيبه في عيادة سابقة.")
]

# All available FDI teeth numbers
ALL_FDI_TEETH = [
    "18", "17", "16", "15", "14", "13", "12", "11",
    "21", "22", "23", "24", "25", "26", "27", "28",
    "38", "37", "36", "35", "34", "33", "32", "31",
    "41", "42", "43", "44", "45", "46", "47", "48"
]


def random_datetime_between(start_dt, end_dt):
    """Generates a realistic clinical working-hour appointment datetime between start_dt and end_dt."""
    delta_seconds = int((end_dt - start_dt).total_seconds())
    if delta_seconds <= 0:
        return start_dt
    rand_sec = random.randint(0, delta_seconds)
    dt = start_dt + timedelta(seconds=rand_sec)
    
    # Force Sunday (0) to Thursday (4) or Saturday (6), skip Friday if possible
    # Working days: 0, 1, 2, 3, 4, 6
    if dt.weekday() == 4: # Friday in python (Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6)
        dt = dt + timedelta(days=1)
    
    # Working hours: 09:00 to 18:30
    rand_hour = random.randint(9, 18)
    rand_min = random.choice([0, 15, 30, 45])
    return dt.replace(hour=rand_hour, minute=rand_min, second=0, microsecond=0)


def reset_and_seed_database():
    print("=" * 80)
    print("  بدأت عملية إعادة تعيين وتوليد قاعدة بيانات العيادة السنية الشاملة")
    print("=" * 80)

    with app.app_context():
        # 1. Complete wipe and rebuild safely
        print("1. تصفير وإعادة تهيئة جداول قاعدة البيانات...")
        try:
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0;"))
        except Exception:
            pass
        try:
            db.session.execute(db.text("PRAGMA foreign_keys = OFF;"))
        except Exception:
            pass
        db.session.commit()

        # Delete all tables data in order
        from routes.settings import reset_db_auto_increments
        for model in [PaymentAllocation, Payment, Invoice, Treatment, Appointment, ToothHistory, TreatmentPlanItem, PatientFile, NotificationLog, Expense, StaffSalary, User, Patient, SystemSetting]:
            try:
                db.session.query(model).delete(synchronize_session=False)
            except Exception:
                pass
        db.session.commit()

        reset_db_auto_increments([
            "payment_allocation", "payment", "invoice", "treatment", "appointment",
            "tooth_history", "treatment_plan_item", "patient_file", "notification_log",
            "expense", "staff_salary", "patient", "user", "system_setting"
        ])

        try:
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1;"))
        except Exception:
            pass
        try:
            db.session.execute(db.text("PRAGMA foreign_keys = ON;"))
        except Exception:
            pass
        db.session.commit()
        db.session.expunge_all()

        populate_default_settings()

        # Ensure working calendar settings
        set_setting("working_days", "0,1,2,3,4,5,6")
        set_setting("working_hours_start", "08:30")
        set_setting("working_hours_end", "19:30")
        set_setting("booking_window_days", "30")
        set_setting("anesthesia_needle_price", "50000")

        # 2. Seed Staff and Doctors
        print("2. إنشاء حسابات الطاقم الطبي والإداري...")
        admin = User(
            username="admin",
            role="admin",
            first_name="خالد",
            last_name="ناصيف"
        )
        admin.set_password("admin123")
        db.session.add(admin)

        dr_sami = User(
            username="dr_sami",
            role="doctor",
            first_name="سامي",
            last_name="الأحمد"
        )
        dr_sami.set_password("doc123")
        db.session.add(dr_sami)

        dr_nour = User(
            username="dr_nour",
            role="doctor",
            first_name="نور",
            last_name="الشامي"
        )
        dr_nour.set_password("doc123")
        db.session.add(dr_nour)

        receptionist = User(
            username="reception",
            role="receptionist",
            first_name="سارة",
            last_name="الخالد"
        )
        receptionist.set_password("rec123")
        db.session.add(receptionist)
        db.session.commit()

        # Doctor / Staff Salary Configurations
        db.session.add(StaffSalary(user_id=dr_sami.id, salary_type="percentage", amount=Decimal("40.00"), deduction_day=1, notes="نسبة 40% من معالجات الطبيب"))
        db.session.add(StaffSalary(user_id=dr_nour.id, salary_type="percentage", amount=Decimal("35.00"), deduction_day=1, notes="نسبة 35% من معالجات الطبيب"))
        db.session.add(StaffSalary(user_id=receptionist.id, salary_type="fixed", amount=Decimal("1200000.00"), deduction_day=1, notes="راتب شهري ثابت لموظفة الاستقبال"))
        db.session.commit()

        set_setting("currency_symbol", "ل.س")
        doctors = [admin, dr_sami, dr_nour]
        doctor_ids = [d.id for d in doctors]

        # 3. Pull strictly configured procedures from Settings
        procedures_dict = get_treatment_details()
        if not procedures_dict:
            from utils.settings_helper import DEFAULT_TREATMENT_DETAILS
            procedures_dict = DEFAULT_TREATMENT_DETAILS

        procedure_names = list(procedures_dict.keys())
        print(f"3. تم تحميل {len(procedure_names)} إجراء علاجي معتمد حصراً من إعدادات النظام.")

        # 4. Generate 200 Patients
        print("4. توليد 200 مريض مع بيانات تفصيلية...")
        patients = []
        now_dt = datetime.now()
        used_phones = set()

        for i in range(1, 201):
            is_female = (i % 2 == 0)
            first_name = random.choice(FIRST_NAMES_FEMALE if is_female else FIRST_NAMES_MALE)
            last_name = random.choice(LAST_NAMES)
            gender = "Female" if is_female else "Male"
            title = ("السيدة" if random.random() < 0.7 else "الآنسة") if is_female else "السيد"
            
            # Age between 6 and 75
            age_years = random.randint(6, 75)
            birth_year = now_dt.year - age_years
            dob = date(birth_year, random.randint(1, 12), random.randint(1, 28))

            # Phone: +9639XXXXXXXX
            while True:
                phone_num = f"+9639{random.randint(30000000, 99999999)}"
                if phone_num not in used_phones:
                    used_phones.add(phone_num)
                    break

            city = random.choice(OTHER_CITIES)
            district = random.choice(DISTRICTS_DAMASCUS)
            address = f"{district} - {city}" if city in ("دمشق", "ريف دمشق") else f"الشارع العام - وسط المدينة - {city}"
            
            med_note = random.choice(MEDICAL_NOTES_LIST)
            occupation = random.choice(OCCUPATIONS) if age_years >= 18 else ("طالب مدرسي" if age_years >= 6 else "طفل")
            emergency_contact = f"{random.choice(FIRST_NAMES_MALE)} {last_name} (+9639{random.randint(30000000, 99999999)})"

            primary_doc_id = random.choice(doctor_ids)

            patient = Patient(
                title=title,
                first_name=first_name,
                last_name=last_name,
                preferred_first_name=first_name,
                gender=gender,
                date_of_birth=dob,
                phone=phone_num,
                email=f"patient{i}_{first_name.lower()}@gmail.com" if random.random() < 0.6 else None,
                city=city,
                state="دمشق" if city in ("دمشق", "ريف دمشق") else city,
                country="الجمهورية العربية السورية",
                address=address,
                medical_information=med_note,
                notes="مريض مسجل في عيادة طب الأسنان.",
                occupation=occupation,
                emergency_contact=emergency_contact,
                reminders_enabled=random.choice([True, True, True, False]),
                primary_doctor_id=primary_doc_id
            )
            db.session.add(patient)
            patients.append(patient)

        db.session.flush()

        # Create portal user accounts for 40 patients
        for p_idx in range(40):
            p = patients[p_idx]
            portal_user = User(
                username=f"patient_{p.id}",
                role="patient",
                first_name=p.first_name,
                last_name=p.last_name,
                patient_id=p.id
            )
            portal_user.set_password("patient123")
            db.session.add(portal_user)

        db.session.commit()
        print("   ✅ تم إنشاء 200 مريض مع 40 حساب بوابة مرضى بنجاح.")

        # 5. Add Prior Tooth Histories for ~75 Patients
        print("5. إضافة معالجات وسوابق سنية سابقة (Tooth History) على مخطط FDI...")
        history_count = 0
        for patient in random.sample(patients, 75):
            num_hist = random.randint(1, 4)
            chosen_teeth = random.sample(ALL_FDI_TEETH, num_hist)
            for tooth in chosen_teeth:
                proc_type, note = random.choice(PRIOR_HISTORIES)
                h_date = date(random.randint(2018, 2022), random.randint(1, 12), random.randint(1, 28))
                th = ToothHistory(
                    patient_id=patient.id,
                    tooth_number=tooth,
                    procedure_type=proc_type,
                    notes=note,
                    history_date=h_date
                )
                db.session.add(th)
                history_count += 1
        db.session.commit()
        print(f"   ✅ تمت إضافة {history_count} سجل سوابق سنية سابقة.")

        # 6. Add Planned Treatments (TreatmentPlanItem) for ~50 Patients
        print("6. إضافة خطط علاجية مقترحة (Planned Treatments)...")
        plan_count = 0
        for patient in random.sample(patients, 50):
            num_plans = random.randint(1, 3)
            for _ in range(num_plans):
                proc = random.choice(procedure_names)
                proc_data = procedures_dict[proc]
                tooth = random.choice(ALL_FDI_TEETH)
                cost = Decimal(str(proc_data.get("price", 60000)))
                tpi = TreatmentPlanItem(
                    patient_id=patient.id,
                    tooth_number=tooth,
                    procedure_type=proc,
                    estimated_cost=cost,
                    notes="مجدول للمتابعة ضمن الخطة العلاجية الشاملة.",
                    status="Planned",
                    created_at=now_dt - timedelta(days=random.randint(5, 60))
                )
                db.session.add(tpi)
                plan_count += 1
        db.session.commit()
        print(f"   ✅ تمت إضافة {plan_count} بند خطة علاجية مقترحة.")

        # 7. Generate Chronological Appointments, Treatments, Invoices & Payments (2023 - 2026)
        print("7. توليد المواعيد والمعالجات والفواتير والمدفوعات من 2023 حتى 2026...")

        start_date_2023 = datetime(2023, 1, 5, 9, 0)
        today_now = datetime.now()
        future_cutoff = today_now + timedelta(days=30)

        # Classify patients into financial categories to strictly control balances:
        # Category A (60%): Fully settled (Balance = 0)
        # Category B (25%): Has Debt (Outstanding balance > 0)
        # Category C (15%): Has Credit (Overpaid advance balance > 0)
        shuffled_patients = list(patients)
        random.shuffle(shuffled_patients)
        debt_patients = set(p.id for p in shuffled_patients[:50])       # 50 patients have debt
        credit_patients = set(p.id for p in shuffled_patients[50:80])   # 30 patients have credit
        # Remaining 120 patients will be fully paid

        total_appts = 0
        total_treatments = 0
        total_invoices = 0
        total_payments = 0

        for patient in patients:
            # Each patient has between 2 and 8 visits across 2023 to 2026
            num_visits = random.randint(2, 7)

            # Generate random distinct dates in sorted order
            visit_dates = sorted([random_datetime_between(start_date_2023, future_cutoff) for _ in range(num_visits)])

            for appt_dt in visit_dates:
                assigned_doc = random.choice(doctors)
                proc_name = random.choice(procedure_names)
                proc_info = procedures_dict[proc_name]

                # Determine Appointment Status accurately:
                if appt_dt > today_now:
                    # Future: Scheduled
                    status = "Scheduled"
                else:
                    # Past: Done (90%) or Cancelled (10%)
                    if random.random() < 0.10:
                        status = "Cancelled"
                    else:
                        status = "Done"

                appointment = Appointment(
                    patient_id=patient.id,
                    appointment_date=appt_dt,
                    duration=proc_info.get("duration", 30),
                    reason=proc_name,
                    status=status,
                    doctor_id=assigned_doc.id,
                    session_opened_at=appt_dt if status == "Done" else None
                )
                db.session.add(appointment)
                db.session.flush()
                total_appts += 1

                # ONLY Done appointments get Treatments and Invoices
                if status == "Done":
                    # Add 1 to 2 treatments to this session
                    num_tx = random.choice([1, 1, 1, 2])
                    session_treatments = []

                    for t_i in range(num_tx):
                        p_type = proc_name if t_i == 0 else random.choice(procedure_names)
                        p_meta = procedures_dict[p_type]
                        tooth = random.choice(ALL_FDI_TEETH)
                        base_cost = Decimal(str(p_meta.get("price", 50000)))

                        # Anesthesia logic
                        use_anest = random.random() < 0.35 and "فحص" not in p_type
                        needles = random.choice([1, 2]) if use_anest else 0
                        anest_cost = Decimal(str(needles * 50000))
                        total_cost = base_cost + anest_cost

                        treatment = Treatment(
                            appointment_id=appointment.id,
                            treatment_date=appt_dt,
                            procedure_type=p_type,
                            tooth_number=tooth,
                            notes=f"تم إنجاز {p_type} للسن رقم {tooth} بنجاح.",
                            total_cost=total_cost,
                            use_anesthesia=use_anest,
                            anesthesia_needles=needles,
                            anesthesia_cost=anest_cost,
                            anesthesia_type="ليدوكائين مع أدرينالين" if use_anest else None,
                            doctor_id=assigned_doc.id
                        )
                        db.session.add(treatment)
                        session_treatments.append(treatment)
                        total_treatments += 1

                    db.session.flush()

                    # Create Invoice for this Completed Appointment
                    discount_val = Decimal('0.00')
                    discount_type = "value"
                    if random.random() < 0.15: # 15% chance of discount
                        discount_val = Decimal(str(random.choice([10000, 20000, 50000])))

                    invoice = Invoice(
                        appointment_id=appointment.id,
                        patient_id=patient.id,
                        issue_date=appt_dt,
                        discount=discount_val,
                        discount_type=discount_type,
                        notes="فاتورة معالجة سنية نظامية."
                    )
                    db.session.add(invoice)
                    db.session.flush()
                    total_invoices += 1

                    inv_net = invoice.total_amount

                    # Financial payment behavior by patient profile:
                    if patient.id in debt_patients:
                        # 40% chance fully unpaid, 60% chance partially paid
                        if random.random() < 0.60:
                            partial_amt = (inv_net * Decimal('0.50')).quantize(Decimal('0.01'))
                            if partial_amt > 0:
                                payment = Payment(
                                    patient_id=patient.id,
                                    invoice_id=invoice.id,
                                    amount=partial_amt,
                                    payment_date=appt_dt + timedelta(minutes=random.randint(20, 60)),
                                    notes="دفعة جزئية وباقي المبلغ ذمة على المريض"
                                )
                                db.session.add(payment)
                                total_payments += 1
                    elif patient.id in credit_patients:
                        # Paid more than invoice (e.g. advance + 50,000 to 100,000)
                        overpay_amt = inv_net + Decimal(str(random.choice([50000, 100000])))
                        payment = Payment(
                            patient_id=patient.id,
                            invoice_id=invoice.id,
                            amount=overpay_amt,
                            payment_date=appt_dt + timedelta(minutes=random.randint(15, 45)),
                            notes="سداد كامل مع دفعة مقدمة كرصيد دائن للمريض"
                        )
                        db.session.add(payment)
                        total_payments += 1
                    else:
                        # Fully Settled Patient (100% paid)
                        if inv_net > 0:
                            payment = Payment(
                                patient_id=patient.id,
                                invoice_id=invoice.id,
                                amount=inv_net,
                                payment_date=appt_dt + timedelta(minutes=random.randint(15, 45)),
                                notes="سداد نقدي كامل عند الاستقبال"
                            )
                            db.session.add(payment)
                            total_payments += 1

        db.session.commit()
        print(f"   ✅ تم إنشاء {total_appts} موعد، {total_treatments} معالجة، {total_invoices} فاتورة، {total_payments} دفعة مالية.")

        # 8. Re-allocate all payments to invoices systematically
        print("8. ضبط ومطابقة وتخصيص المدفوعات والفواتير بدقة (Payment Allocations)...")
        for patient in patients:
            allocate_patient_payments_to_invoices(patient.id)
        db.session.commit()
        print("   ✅ تم تحديث تخصيص الفواتير وحساب الأرصدة والديون بنجاح.")

        # 9. Generate Monthly Clinic Expenses from 2023 to 2026
        print("9. توليد سجل النفقات والمصروفات الدورية للعيادة (2023 - 2026)...")
        exp_categories = [
            ("مواد سنية ومستهلكات طبية", Decimal("850000.00")),
            ("أجور مخبر تعويضات أسنان", Decimal("1200000.00")),
            ("إيجار العيادة الشهري", Decimal("2500000.00")),
            ("كهرباء واشتراك مولدة", Decimal("600000.00")),
            ("صيانة وتطهير وتعقيم أجهزة", Decimal("350000.00")),
            ("ضيافة ونظافة ومستلزمات عامة", Decimal("200000.00")),
        ]

        exp_count = 0
        cur_year = 2023
        while cur_year <= now_dt.year:
            max_m = 12 if cur_year < now_dt.year else now_dt.month
            for m in range(1, max_m + 1):
                for cat_name, base_val in exp_categories:
                    # Variation +/- 15%
                    factor = Decimal(str(random.uniform(0.85, 1.20)))
                    exp_amt = (base_val * factor).quantize(Decimal('0.00'))
                    exp_date = date(cur_year, m, random.randint(1, 25))
                    exp = Expense(
                        category=cat_name,
                        amount=exp_amt,
                        expense_date=exp_date,
                        notes=f"مصروف {cat_name} لشهر {cur_year}-{m:02d}"
                    )
                    db.session.add(exp)
                    exp_count += 1
            cur_year += 1

        db.session.commit()
        print(f"   ✅ تمت إضافة {exp_count} سجل مصروفات للعيادة.")

        # 10. Verification of Metrics
        total_p = Patient.query.count()
        total_a = Appointment.query.count()
        total_done = Appointment.query.filter_by(status="Done").count()
        total_sched = Appointment.query.filter_by(status="Scheduled").count()
        total_canc = Appointment.query.filter_by(status="Cancelled").count()
        total_pend = Appointment.query.filter_by(status="Pending").count()
        total_tx = Treatment.query.count()
        total_inv = Invoice.query.count()
        total_pay = Payment.query.count()

        print("\n" + "=" * 80)
        print("  🎉 اكتملت العملية بنجاح! ملخص قاعدة البيانات الجديدة:")
        print("=" * 80)
        print(f"  • إجمالي المرضى: {total_p} مريض")
        print(f"  • إجمالي المواعيد: {total_a} موعد")
        print(f"    - المنجزة (Done): {total_done} (تحتوي على معالجات وفواتير)")
        print(f"    - المجدولة (Scheduled): {total_sched} (مواعيد قادمة ونشطة)")
        print(f"    - الملغاة (Cancelled): {total_canc} (مواعيد ملغية دون معالجات)")
        print(f"    - المعلقة (Pending): {total_pend} (طلبات حجز عبر البوابة)")
        print(f"  • إجمالي المعالجات السنية: {total_tx} معالجة (حصراً من الإعدادات)")
        print(f"  • إجمالي الفواتير: {total_inv} فاتورة")
        print(f"  • إجمالي الدفعات المالية: {total_pay} دفعة")
        print(f"  • السوابق السنية القديمة (Tooth History): {ToothHistory.query.count()} سجل")
        print(f"  • الخطط العلاجية المستقبلية: {TreatmentPlanItem.query.count()} بند")
        print(f"  • سجل المصروفات: {Expense.query.count()} مصروف")
        print("=" * 80)


if __name__ == "__main__":
    reset_and_seed_database()
