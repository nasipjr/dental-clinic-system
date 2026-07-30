import os
import sys
import random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Patient

def seed_patients():
    app.app_context().push()

    first_names_m = ["أحمد", "محمد", "عمر", "خالد", "طارق", "يوسف", "عبد الرحمن", "حمزة", "بلال", "زياد"]
    first_names_f = ["سارة", "فاطمة", "مريم", "ريم", "ليلى", "هدى", "نور الهدى", "رانيا", "أمل", "سلمى"]
    last_names = ["العلي", "الحمصي", "الشامي", "البغدادي", "الخطيب", "الحلبي", "الأحمد", "الأتاسي", "الجابري", "قدور", "الكردي", "الصالح", "النابلسي", "الحكيم", "درويش", "الساعدي", "المرادي", "زريق", "الخوري", "الجراح"]
    cities = ["دمشق", "حلب", "حمص", "اللاذقية", "حماة", "طرطوس"]
    medical_notes = [
        "لا توجد أمراض مزمنة",
        "حساسية للبنسلين",
        "ارتفاع ضغط الدم - يتناول أدوية منظمة",
        "سكري من النوع الثاني",
        "حامل بالشهر الخامس",
        "نزف لثة خفيف عند التفريش",
        "لا توجد حساسية معروفة"
    ]

    patients_to_add = []
    
    for i in range(20):
        gender = random.choice(["Male", "Female"])
        if gender == "Male":
            first_name = first_names_m[i % len(first_names_m)]
            title = "السيد"
        else:
            first_name = first_names_f[i % len(first_names_f)]
            title = "الآنسة/السيدة"
            
        last_name = last_names[i % len(last_names)]
        phone_suffix = f"{random.randint(1000000, 9999999)}"
        phone = f"+9639{phone_suffix}"
        
        # Random DOB between 18 and 60 years ago
        days_old = random.randint(18 * 365, 60 * 365)
        dob = date.today() - timedelta(days=days_old)
        
        p = Patient(
            title=title,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            phone=phone,
            email=f"patient{i+1}@clinic.com",
            date_of_birth=dob,
            city=random.choice(cities),
            address=f"حي {random.choice(['الروضة', 'المالكي', 'المزة', 'الفرقان', 'الزهراء', 'الميدان'])}",
            medical_information=random.choice(medical_notes),
            notes="مريض جديد تم إضافته تلقائياً للاختبار"
        )
        patients_to_add.append(p)
        db.session.add(p)

    db.session.commit()
    print(f"SUCCESS: Seeded {len(patients_to_add)} random patients into database!")

if __name__ == '__main__':
    seed_patients()
