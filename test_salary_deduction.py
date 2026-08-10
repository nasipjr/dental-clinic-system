"""
test_salary_deduction.py
========================
سكريبت اختبار لمنطق خصم الراتب التلقائي.

يفحص كل إعدادات الرواتب النشطة ويحاكي ما الذي
سيحدث لو تم تشغيل auto_process_salary_deductions الآن.

الاستخدام:
    python test_salary_deduction.py            ← dry-run (لا يُغيّر شيء)
    python test_salary_deduction.py --force    ← ينفّذ الخصم الفعلي الآن بغض النظر عن اليوم
    python test_salary_deduction.py --reset    ← يمسح last_deducted_month لكل الموظفين (للاختبار فقط)
"""

import sys
import os

# Fix Windows terminal encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app
from models import db, StaffSalary, Expense, Treatment
from sqlalchemy import func
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────

RESET_MODE = "--reset" in sys.argv
FORCE_MODE = "--force" in sys.argv

CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def hr(char="─", n=60):
    print(char * n)


def run_test():
    with app.app_context():
        today = datetime.now()
        current_month = today.strftime("%Y-%m")
        current_day   = today.day

        print()
        hr("═")
        print(f"{BOLD}{CYAN}  🧪 اختبار منطق خصم الراتب التلقائي{RESET}")
        print(f"  📅 اليوم: {today.strftime('%Y-%m-%d')}  |  اليوم رقم: {current_day}  |  الشهر الحالي: {current_month}")
        hr("═")

        # ── Reset mode ───────────────────────────────────────────────────────
        if RESET_MODE:
            print(f"\n{YELLOW}⚠️  وضع إعادة الضبط — سيتم مسح last_deducted_month لكل الموظفين{RESET}")
            salaries = StaffSalary.query.all()
            for s in salaries:
                s.last_deducted_month = None
            db.session.commit()
            print(f"{GREEN}✅ تم مسح سجل الخصم لـ {len(salaries)} موظف.{RESET}")
            print("  الآن شغّل السكريبت بدون --reset لاختبار الخصم.")
            return

        # ── Fetch all active salary configs ──────────────────────────────────
        all_salaries = StaffSalary.query.filter_by(is_active=True).all()

        if not all_salaries:
            print(f"\n{YELLOW}⚠️  لا توجد إعدادات رواتب نشطة في قاعدة البيانات.{RESET}")
            return

        print(f"\n  إجمالي الموظفين بإعدادات راتب نشطة: {BOLD}{len(all_salaries)}{RESET}\n")
        hr()

        eligible   = []
        ineligible = []

        for sal in all_salaries:
            user = sal.user
            name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
            role = user.role.capitalize()

            already_deducted = (sal.last_deducted_month == current_month)
            day_matches      = (sal.deduction_day == current_day)

            # حساب المبلغ
            if sal.salary_type == "fixed":
                amount = float(sal.amount)
                type_label = f"ثابت"
            else:
                total_invoiced = float(
                    db.session.query(func.coalesce(func.sum(Treatment.total_cost), 0.0))
                    .filter(Treatment.doctor_id == user.id)
                    .scalar() or 0.0
                )
                amount = round(total_invoiced * float(sal.amount) / 100.0, 2)
                type_label = f"نسبة {sal.amount}% من {total_invoiced:.2f}"

            info = {
                "id": sal.id,
                "name": name,
                "role": role,
                "deduction_day": sal.deduction_day,
                "salary_type": sal.salary_type,
                "type_label": type_label,
                "amount": amount,
                "last_deducted": sal.last_deducted_month or "لم يُخصم بعد",
                "already_deducted": already_deducted,
                "day_matches": day_matches,
            }

            # مؤهل للخصم؟
            if FORCE_MODE:
                is_eligible = not already_deducted and amount > 0
            else:
                is_eligible = day_matches and not already_deducted and amount > 0

            if is_eligible:
                eligible.append(info)
            else:
                ineligible.append(info)

            # طباعة تفاصيل الموظف
            status_icon = "OK" if is_eligible else "SKIP"
            print(f"  [{status_icon}]  {name}  [{role}]")
            print(f"       يوم الخصم: {sal.deduction_day}  |  اليوم الحالي: {current_day}  |  يطابق: {'نعم' if day_matches else 'لا'}")
            print(f"       النوع: {sal.salary_type} ({type_label})  |  المبلغ: {amount:.2f}")
            print(f"       آخر خصم: {sal.last_deducted_month or 'لم يُخصم'}  |  خُصم هذا الشهر: {'نعم (تجاوز)' if already_deducted else 'لا <- مؤهل'}")
            if not is_eligible and not day_matches and not FORCE_MODE:
                print(f"       الخصم مجدول ليوم {sal.deduction_day} — اليوم هو {current_day}")
            print()

        hr()
        print(f"\n  ملخص:")
        print(f"    مؤهلون للخصم الآن : {len(eligible)}")
        print(f"    غير مؤهلين        : {len(ineligible)}")

        if not eligible:
            print(f"\n  لا احد مؤهل للخصم الآن.")
            if not FORCE_MODE:
                print(f"  جرب: python test_salary_deduction.py --force   لتجاوز قيد اليوم")
                print(f"  او  : python test_salary_deduction.py --reset   لمسح سجل الخصم")
            return

        print(f"\n  {'DRY-RUN (لا تغيير)' if not FORCE_MODE else 'تنفيذ فعلي'}:")
        for e in eligible:
            print(f"    -> {e['name']} ({e['role']})  :  {e['amount']:.2f}  [{e['type_label']}]")

        total = sum(e["amount"] for e in eligible)
        print(f"\n  الاجمالي الذي سيُخصم: {total:.2f}")

        if not FORCE_MODE:
            print(f"\n  هذا dry-run فقط — لا شيء تغيّر في قاعدة البيانات.")
            print(f"  لتنفيذ الخصم الفعلي: python test_salary_deduction.py --force")
            return

        # ── Actual deduction ─────────────────────────────────────────────────
        print(f"\n  ⚡ تنفيذ الخصم...")
        for e in eligible:
            sal = StaffSalary.query.get(e["id"])
            expense = Expense(
                category="Salaries",
                amount=e["amount"],
                expense_date=today.date(),
                notes=f"Salary (Test-Force) - {e['role']}: {e['name']}"
            )
            db.session.add(expense)
            sal.last_deducted_month = current_month
            print(f"    + خُصم {e['amount']:.2f} لـ {e['name']}")

        db.session.commit()
        print(f"\n  تم تسجيل {len(eligible)} خصم راتب في سجل المصاريف بنجاح!")
        print(f"  افتح صفحة التقارير > المصاريف للتحقق.\n")
        hr("═")


if __name__ == "__main__":
    run_test()
