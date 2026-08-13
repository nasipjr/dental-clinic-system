from datetime import datetime
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash, Response, g
from sqlalchemy import func
from sqlalchemy.orm import subqueryload
from utils.auth_helper import role_required

from models import db, Patient, Appointment, Treatment, Payment, PaymentAllocation, Invoice, Expense

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@role_required("admin")
def reports_dashboard():
    current_app.logger.info("Reports dashboard page opened")

    try:
        from sqlalchemy import extract
        today = datetime.now()

        # Available years for filtering (Full contiguous range from oldest record to current/future)
        min_year = today.year
        max_year = today.year

        for model, col_name in [(Invoice, 'issue_date'), (Payment, 'payment_date'), (Expense, 'expense_date')]:
            col = getattr(model, col_name)
            min_d, max_d = db.session.query(func.min(col), func.max(col)).first()
            if min_d and min_d.year < min_year:
                min_year = min_d.year
            if max_d and max_d.year > max_year:
                max_year = max_d.year

        available_years = list(range(max_year, min_year - 1, -1))

        # Year filter handling ('all' or specific integer year)
        year_param = request.args.get("year", "all").strip().lower()
        if year_param in ("all", "الكل", ""):
            selected_year = "all"
            filter_year = None
        else:
            try:
                filter_year = int(year_param)
                selected_year = str(filter_year)
            except ValueError:
                selected_year = "all"
                filter_year = None

        if filter_year:
            start_date_year = datetime(filter_year, 1, 1)
            end_date_year = datetime(filter_year + 1, 1, 1)
        else:
            start_date_year = None
            end_date_year = None

        # Reusable Invoice subqueries
        subtotal_sub = (
            db.select(func.coalesce(func.sum(Treatment.total_cost), 0.0))
            .where(Treatment.appointment_id == Invoice.appointment_id)
            .scalar_subquery()
        )

        discount_amt_sub = db.case(
            (Invoice.discount_type == "percentage", subtotal_sub * func.coalesce(Invoice.discount, 0.0) / 100.0),
            else_=func.coalesce(Invoice.discount, 0.0)
        )

        net_total_sub = db.case(
            (subtotal_sub - discount_amt_sub + func.coalesce(Invoice.additional_charges, 0.0) > 0,
             subtotal_sub - discount_amt_sub + func.coalesce(Invoice.additional_charges, 0.0)),
            else_=0.0
        )

        # 1. KPI Cards Data (Filtered by year if selected)
        if filter_year:
            patient_cnt = Patient.query.join(Patient.appointments).filter(
                Appointment.appointment_date >= start_date_year,
                Appointment.appointment_date < end_date_year
            ).distinct().count()
            total_patients = patient_cnt if patient_cnt > 0 else Patient.query.count()

            total_appointments = Appointment.query.filter(
                Appointment.appointment_date >= start_date_year,
                Appointment.appointment_date < end_date_year
            ).count()

            total_invoiced_q = db.session.query(
                func.coalesce(func.sum(net_total_sub), 0.0)
            ).join(Appointment, Invoice.appointment_id == Appointment.id).filter(
                Appointment.status != "Cancelled",
                Invoice.issue_date >= start_date_year,
                Invoice.issue_date < end_date_year
            )
            total_invoiced = float(total_invoiced_q.scalar() or 0.0)

            total_payments = float(db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(
                Payment.payment_date >= start_date_year,
                Payment.payment_date < end_date_year
            ).scalar() or 0.0)

            expenses_q = Expense.query.filter(
                Expense.expense_date >= start_date_year.date(),
                Expense.expense_date < end_date_year.date()
            )
            expenses = expenses_q.order_by(Expense.expense_date.desc(), Expense.id.desc()).limit(50).all()
            total_expenses = float(db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
                Expense.expense_date >= start_date_year.date(),
                Expense.expense_date < end_date_year.date()
            ).scalar() or 0.0)
        else:
            total_patients = Patient.query.count()
            total_appointments = Appointment.query.count()

            total_invoiced_q = db.session.query(
                func.coalesce(func.sum(net_total_sub), 0.0)
            ).join(Appointment, Invoice.appointment_id == Appointment.id).filter(
                Appointment.status != "Cancelled"
            )
            total_invoiced = float(total_invoiced_q.scalar() or 0.0)

            total_payments = float(db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar() or 0.0)

            expenses = Expense.query.order_by(Expense.expense_date.desc(), Expense.id.desc()).limit(50).all()
            total_expenses = float(db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).scalar() or 0.0)

        cash_net_profit = total_payments - total_expenses
        accrual_net_profit = total_invoiced - total_expenses

        # Expense categories breakdown
        expense_categories = {"Materials": 0.0, "Rent": 0.0, "Salaries": 0.0, "Other": 0.0}
        exp_cat_query = db.session.query(Expense.category, func.coalesce(func.sum(Expense.amount), 0.0))
        if filter_year:
            exp_cat_query = exp_cat_query.filter(
                Expense.expense_date >= start_date_year.date(),
                Expense.expense_date < end_date_year.date()
            )
        exp_cat_rows = exp_cat_query.group_by(Expense.category).all()
        for cat, amt in exp_cat_rows:
            c_key = cat if cat in expense_categories else "Other"
            expense_categories[c_key] += float(amt)

        # Pre-query monthly totals in bulk via SQL GROUP BY
        monthly_billed_q = db.session.query(
            extract('year', Invoice.issue_date).label('yr'),
            extract('month', Invoice.issue_date).label('mon'),
            func.coalesce(func.sum(net_total_sub), 0.0).label('total_billed')
        ).join(Appointment, Invoice.appointment_id == Appointment.id).filter(
            Appointment.status != "Cancelled"
        )
        if filter_year:
            monthly_billed_q = monthly_billed_q.filter(
                Invoice.issue_date >= start_date_year,
                Invoice.issue_date < end_date_year
            )
        billed_by_month = {(int(yr), int(mon)): float(tot) for yr, mon, tot in monthly_billed_q.group_by('yr', 'mon').all() if yr and mon}

        monthly_paid_q = db.session.query(
            extract('year', Payment.payment_date).label('yr'),
            extract('month', Payment.payment_date).label('mon'),
            func.coalesce(func.sum(Payment.amount), 0.0).label('total_paid')
        )
        if filter_year:
            monthly_paid_q = monthly_paid_q.filter(
                Payment.payment_date >= start_date_year,
                Payment.payment_date < end_date_year
            )
        paid_by_month = {(int(yr), int(mon)): float(tot) for yr, mon, tot in monthly_paid_q.group_by('yr', 'mon').all() if yr and mon}

        monthly_exp_q = db.session.query(
            extract('year', Expense.expense_date).label('yr'),
            extract('month', Expense.expense_date).label('mon'),
            func.coalesce(func.sum(Expense.amount), 0.0).label('total_exp')
        )
        if filter_year:
            monthly_exp_q = monthly_exp_q.filter(
                Expense.expense_date >= start_date_year.date(),
                Expense.expense_date < end_date_year.date()
            )
        exp_by_month = {(int(yr), int(mon)): float(tot) for yr, mon, tot in monthly_exp_q.group_by('yr', 'mon').all() if yr and mon}

        # 2. Monthly Income Chart (Billed vs Paid)
        monthly_labels = []
        monthly_billed = []
        monthly_paid = []

        if filter_year:
            target_months = [(filter_year, m, datetime(filter_year, m, 1)) for m in range(1, 13)]
        else:
            months_list = []
            for i in range(11, -1, -1):
                y = today.year
                m = today.month - i
                if m <= 0:
                    m += 12
                    y -= 1
                months_list.append((y, m, datetime(y, m, 1)))
            target_months = months_list

        ARABIC_MONTHS = {
            1: "كانون الثاني", 2: "شباط", 3: "آذار", 4: "نيسان",
            5: "أيار", 6: "حزيران", 7: "تموز", 8: "آب",
            9: "أيلول", 10: "تشرين الأول", 11: "تشرين الثاني", 12: "كانون الأول"
        }
        is_ar = request.cookies.get("lang") == "ar" or request.cookies.get("lang") != "en"

        for yr, m, date_start in target_months:
            monthly_labels.append(f"{ARABIC_MONTHS[m]} {yr}" if is_ar else date_start.strftime("%b %Y"))
            monthly_billed.append(billed_by_month.get((yr, m), 0.0))
            monthly_paid.append(paid_by_month.get((yr, m), 0.0))

        # 3. Appointment Status Counts
        appt_status_q = db.session.query(Appointment.status, func.count(Appointment.id))
        if filter_year:
            appt_status_q = appt_status_q.filter(
                Appointment.appointment_date >= start_date_year,
                Appointment.appointment_date < end_date_year
            )
        status_counts = appt_status_q.group_by(Appointment.status).all()

        appointment_statuses = {"Scheduled": 0, "Done": 0, "Cancelled": 0}
        for status, count in status_counts:
            if status in appointment_statuses:
                appointment_statuses[status] = count

        appointment_status_labels = list(appointment_statuses.keys())
        appointment_status_values = list(appointment_statuses.values())

        # 4. Top 5 Procedures
        proc_q = db.session.query(
            Treatment.procedure_type,
            func.count(Treatment.id),
            func.sum(Treatment.total_cost)
        )
        if filter_year:
            proc_q = proc_q.join(Appointment, Treatment.appointment_id == Appointment.id).filter(
                Appointment.appointment_date >= start_date_year,
                Appointment.appointment_date < end_date_year
            )
        procedure_counts = proc_q.group_by(Treatment.procedure_type).order_by(func.count(Treatment.id).desc()).limit(5).all()

        procedure_labels = [p[0] for p in procedure_counts]
        procedure_values_counts = [p[1] for p in procedure_counts]
        procedure_values_revenue = [float(p[2] or 0.0) for p in procedure_counts]

        # 5. Patient Gender Demographics
        gender_q = db.session.query(Patient.gender, func.count(Patient.id))
        if filter_year:
            gender_q = gender_q.join(Patient.appointments).filter(
                Appointment.appointment_date >= start_date_year,
                Appointment.appointment_date < end_date_year
            )
        gender_counts = gender_q.group_by(Patient.gender).all()
        if not gender_counts:
            gender_counts = db.session.query(Patient.gender, func.count(Patient.id)).group_by(Patient.gender).all()

        gender_labels = [g[0] or "Not Specified" for g in gender_counts]
        gender_values = [g[1] for g in gender_counts]

        # 6. Patient Balances: All Debtors and All Credited Patients (ALWAYS CUMULATIVE ALL TIME)
        patient_invoiced_rows = db.session.query(
            Invoice.patient_id,
            func.coalesce(func.sum(net_total_sub), 0.0)
        ).join(Appointment, Invoice.appointment_id == Appointment.id).filter(
            Appointment.status != "Cancelled"
        ).group_by(Invoice.patient_id).all()

        patient_invoiced = {p_id: float(tot) for p_id, tot in patient_invoiced_rows if p_id}

        patient_payments = dict(
            db.session.query(
                Payment.patient_id,
                func.coalesce(func.sum(Payment.amount), 0.0)
            ).group_by(Payment.patient_id).all()
        )

        all_patient_ids = set(patient_invoiced.keys()).union(set(patient_payments.keys()))
        all_patients_map = {p.id: p for p in Patient.query.filter(Patient.id.in_(all_patient_ids)).all()} if all_patient_ids else {}

        all_debtors = []
        all_credited_patients = []

        for p_id in all_patient_ids:
            p = all_patients_map.get(p_id)
            if not p:
                continue
            billed = float(patient_invoiced.get(p_id, 0.0))
            paid = float(patient_payments.get(p_id, 0.0))
            diff = billed - paid

            p_data = {
                "id": p.id,
                "name": f"{p.first_name} {p.last_name}",
                "first_name": p.first_name,
                "last_name": p.last_name,
                "phone": p.phone or "No phone",
                "total_billed": billed,
                "total_paid": paid,
                "outstanding": max(0.0, diff),
                "credit": max(0.0, -diff)
            }

            if diff > 0.01:
                all_debtors.append(p_data)
            elif diff < -0.01:
                all_credited_patients.append(p_data)

        all_debtors.sort(key=lambda x: x["outstanding"], reverse=True)
        all_credited_patients.sort(key=lambda x: x["credit"], reverse=True)
        top_debtors = all_debtors[:5]

        total_outstanding = sum(x["outstanding"] for x in all_debtors)
        total_credit = sum(x["credit"] for x in all_credited_patients)

        # 7. Monthly Financial Summary Table
        monthly_summary = []
        summary_years = [filter_year] if filter_year else sorted(available_years)

        for yr_val in summary_years:
            for month in range(1, 13):
                date_start = datetime(yr_val, month, 1)

                billed_m = billed_by_month.get((yr_val, month), 0.0)
                paid_m = paid_by_month.get((yr_val, month), 0.0)
                expenses_m = exp_by_month.get((yr_val, month), 0.0)

                net_profit_m = paid_m - expenses_m
                accrual_profit_m = billed_m - expenses_m

                if filter_year or billed_m > 0 or paid_m > 0 or expenses_m > 0:
                    monthly_summary.append({
                        "month_label": f"{ARABIC_MONTHS[month]} {yr_val}" if is_ar else date_start.strftime("%B %Y"),
                        "billed": billed_m,
                        "paid": paid_m,
                        "expenses": expenses_m,
                        "net_profit": net_profit_m,
                        "accrual_profit": accrual_profit_m
                    })

        # 8. Doctor Revenue Share Report
        from models import User, StaffSalary
        doctors = User.query.filter_by(role="doctor").order_by(User.first_name).all()
        doc_ids = [d.id for d in doctors]

        salary_cfgs = {s.user_id: s for s in StaffSalary.query.filter(StaffSalary.user_id.in_(doc_ids)).all()} if doc_ids else {}

        appts_cnt_q = db.session.query(Appointment.doctor_id, func.count(Appointment.id)).filter(Appointment.doctor_id.in_(doc_ids))
        if filter_year:
            appts_cnt_q = appts_cnt_q.filter(Appointment.appointment_date >= start_date_year, Appointment.appointment_date < end_date_year)
        appts_by_doc = dict(appts_cnt_q.group_by(Appointment.doctor_id).all()) if doc_ids else {}

        treat_q = db.session.query(
            Appointment.doctor_id,
            func.count(Treatment.id),
            func.coalesce(func.sum(Treatment.total_cost), 0.0)
        ).join(Appointment, Treatment.appointment_id == Appointment.id).filter(Appointment.doctor_id.in_(doc_ids))
        if filter_year:
            treat_q = treat_q.filter(Appointment.appointment_date >= start_date_year, Appointment.appointment_date < end_date_year)
        treat_by_doc = {doc_id: (cnt, float(rev or 0.0)) for doc_id, cnt, rev in treat_q.group_by(Appointment.doctor_id).all()} if doc_ids else {}

        doctors_report = []

        for doc in doctors:
            doc_appts = appts_by_doc.get(doc.id, 0)
            doc_treatment_count, doc_revenue = treat_by_doc.get(doc.id, (0, 0.0))

            salary_cfg = salary_cfgs.get(doc.id)
            salary_type = salary_cfg.salary_type if salary_cfg else "fixed"
            salary_amount = float(salary_cfg.amount) if salary_cfg else 0.0

            if salary_type == "percentage":
                doctor_earned = round(doc_revenue * salary_amount / 100.0, 2)
                pct_display = salary_amount
            else:
                doctor_earned = salary_amount
                pct_display = round((doctor_earned / doc_revenue * 100.0), 1) if doc_revenue > 0 else 0.0

            clinic_net = max(0.0, doc_revenue - doctor_earned)

            doctors_report.append({
                "doctor": doc,
                "appointment_count": doc_appts,
                "treatment_count": doc_treatment_count,
                "total_revenue": doc_revenue,
                "salary_type": salary_type,
                "salary_amount": salary_amount,
                "doctor_earned": doctor_earned,
                "clinic_net": clinic_net,
                "pct_display": min(100.0, max(0.0, pct_display))
            })

        return render_template(
            "reports/reports.html",
            doctors_report=doctors_report,
            total_patients=total_patients,
            total_appointments=total_appointments,
            total_invoiced=total_invoiced,
            total_payments=total_payments,
            total_outstanding=total_outstanding,
            total_credit=total_credit,
            monthly_labels=monthly_labels,
            monthly_billed=monthly_billed,
            monthly_paid=monthly_paid,
            appointment_status_labels=appointment_status_labels,
            appointment_status_values=appointment_status_values,
            procedure_labels=procedure_labels,
            procedure_values_counts=procedure_values_counts,
            procedure_values_revenue=procedure_values_revenue,
            gender_labels=gender_labels,
            gender_values=gender_values,
            top_debtors=top_debtors,
            all_debtors=all_debtors,
            all_credited_patients=all_credited_patients,
            expenses=expenses,
            total_expenses=total_expenses,
            cash_net_profit=cash_net_profit,
            accrual_net_profit=accrual_net_profit,
            expense_categories=expense_categories,
            monthly_summary=monthly_summary,
            summary_labels=[item["month_label"] for item in monthly_summary],
            summary_billed=[item["billed"] for item in monthly_summary],
            summary_paid=[item["paid"] for item in monthly_summary],
            summary_expenses=[item["expenses"] for item in monthly_summary],
            summary_net_profit=[item["net_profit"] for item in monthly_summary],
            summary_accrual_profit=[item["accrual_profit"] for item in monthly_summary],
            available_years=available_years,
            selected_year=selected_year,
            now=datetime.now()
        )

    except Exception:
        current_app.logger.exception("Failed to generate reports dashboard data")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to load reports dashboard.",
        ), 500


@reports_bp.route("/reports/expenses/add", methods=["POST"])
@role_required("admin")
def add_expense():
    current_app.logger.info("Adding clinic expense")
    try:
        category = request.form.get("category", "Other").strip()
        amount_str = request.form.get("amount", "0").strip()
        expense_date_str = request.form.get("expense_date", "").strip()
        notes = request.form.get("notes", "").strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "danger")
            return redirect(url_for("reports.reports_dashboard") + "#tab-expenses")

        try:
            expense_date = datetime.strptime(expense_date_str, "%Y-%m-%d").date()
        except ValueError:
            expense_date = datetime.now().date()

        new_expense = Expense(
            category=category,
            amount=amount,
            expense_date=expense_date,
            notes=notes
        )
        db.session.add(new_expense)
        is_ar = request.cookies.get("lang", "ar") != "en"
        flash("تم تسجيل المصروف بنجاح." if is_ar else "Expense recorded successfully.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to add expense")
        is_ar = request.cookies.get("lang", "ar") != "en"
        flash("فشل في تسجيل المصروف." if is_ar else "Failed to record expense.", "danger")
    return redirect(url_for("reports.reports_dashboard") + "#tab-expenses")


@reports_bp.route("/reports/expenses/<int:expense_id>/delete", methods=["POST"])
@role_required("admin")
def delete_expense(expense_id):
    current_app.logger.warning(f"Deleting expense | id={expense_id}")
    is_ar = request.cookies.get("lang", "ar") != "en"
    try:
        from models import Treatment
        expense = Expense.query.get_or_404(expense_id)
        # Unmark linked treatments so "Deducted" tag is removed
        Treatment.query.filter_by(salary_expense_id=expense.id).update({"salary_expense_id": None}, synchronize_session=False)
        db.session.delete(expense)
        db.session.commit()
        flash("تم حذف المصروف وإلغاء شارة الخصم عن المعالجات المرتبطة به بنجاح." if is_ar else "Expense deleted successfully and treatment deduction tags removed.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to delete expense {expense_id}")
        flash("فشل في حذف المصروف." if is_ar else "Failed to delete expense.", "danger")
    return redirect(url_for("reports.reports_dashboard") + "#tab-expenses")


@reports_bp.route("/reports/export/<string:report_type>")
@role_required("admin")
def export_report(report_type):
    import io
    import csv
    
    current_app.logger.info(f"Exporting report | type={report_type}")
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d')}.csv"
        
        if report_type == "expenses":
            writer.writerow(["ID", "Category", "Amount", "Date", "Notes"])
            expenses = Expense.query.order_by(Expense.expense_date.asc()).all()
            for e in expenses:
                writer.writerow([e.id, e.category, e.amount, e.expense_date.strftime("%Y-%m-%d"), e.notes or ""])
        elif report_type == "income":
            writer.writerow(["Invoice Number", "Patient Name", "Issue Date", "Subtotal", "Discount", "Total Amount", "Total Paid", "Outstanding", "Status"])
            invoices = Invoice.query.join(Invoice.appointment).filter(Appointment.status != "Cancelled").all()
            for inv in invoices:
                patient_name = f"{inv.patient.first_name} {inv.patient.last_name}"
                writer.writerow([
                    inv.invoice_number,
                    patient_name,
                    inv.issue_date.strftime("%Y-%m-%d"),
                    inv.subtotal,
                    inv.discount_amount,
                    inv.total_amount,
                    inv.total_paid,
                    inv.outstanding_amount,
                    inv.status
                ])
        else:
            return "Invalid report type", 400
            
        output.seek(0)
        bom = b'\xef\xbb\xbf'
        content = bom + output.getvalue().encode('utf-8')
        
        return Response(
            content,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"}
        )
    except Exception:
        current_app.logger.exception("Failed to export report CSV")
        return "Internal Server Error", 500


@reports_bp.route("/reports/financial-calendar-data")
@role_required("admin")
def financial_calendar_data():
    try:
        year_str = request.args.get("year")
        month_str = request.args.get("month")
        
        today = datetime.now()
        try:
            year = int(year_str) if year_str and year_str.lower() != 'all' else today.year
        except (ValueError, TypeError):
            year = today.year

        try:
            month = int(month_str) if month_str else today.month
        except (ValueError, TypeError):
            month = today.month
        
        import calendar as py_calendar
        _, num_days = py_calendar.monthrange(year, month)
        
        start_date = datetime(year, month, 1, 0, 0, 0)
        end_date = datetime(year, month, num_days, 23, 59, 59)
        
        invoices = Invoice.query.join(Invoice.appointment).filter(
            Appointment.status != "Cancelled",
            Invoice.issue_date >= start_date,
            Invoice.issue_date <= end_date
        ).all()
        
        payments = Payment.query.filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).all()
        
        expenses = Expense.query.filter(
            Expense.expense_date >= start_date.date(),
            Expense.expense_date <= end_date.date()
        ).all()
        
        day_data = {}
        for day in range(1, num_days + 1):
            day_data[day] = {
                "billed": 0.0,
                "paid": 0.0,
                "expenses": 0.0,
                "net_profit": 0.0,
                "invoices": [],
                "payments": [],
                "expenses_list": []
            }
            
        for inv in invoices:
            day = inv.issue_date.day
            amount = float(inv.total_amount)
            day_data[day]["billed"] += amount
            day_data[day]["invoices"].append({
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "patient_name": f"{inv.patient.first_name} {inv.patient.last_name}",
                "total_amount": amount
            })
            
        for pay in payments:
            day = pay.payment_date.day
            amount = float(pay.amount)
            day_data[day]["paid"] += amount
            day_data[day]["payments"].append({
                "id": pay.id,
                "patient_name": f"{pay.patient.first_name} {pay.patient.last_name}",
                "amount": amount,
                "notes": pay.notes or ""
            })
            
        for exp in expenses:
            day = exp.expense_date.day
            amount = float(exp.amount)
            day_data[day]["expenses"] += amount
            day_data[day]["expenses_list"].append({
                "id": exp.id,
                "category": exp.category,
                "amount": amount,
                "notes": exp.notes or ""
            })
            
        for day in range(1, num_days + 1):
            day_data[day]["net_profit"] = day_data[day]["paid"] - day_data[day]["expenses"]
            
        return {
            "year": year,
            "month": month,
            "days_in_month": num_days,
            "day_data": day_data
        }
    except Exception:
        current_app.logger.exception("Failed to load financial calendar data")
        return {"error": "Failed to load financial calendar data"}, 500


# ──────────────────────────────────────────────────────────────────────────────
# AJAX: Paginated/Filtered Expenses Table
# ──────────────────────────────────────────────────────────────────────────────

@reports_bp.route("/reports/expenses/list")
@role_required("admin")
def expenses_list():
    """Returns paginated, filtered, sortable expenses as JSON for AJAX table."""
    try:
        page       = request.args.get("page", 1, type=int)
        per_page   = request.args.get("per_page", 10, type=int)
        category   = request.args.get("category", "").strip()
        year_str   = request.args.get("year", "").strip()
        month_str  = request.args.get("month", "").strip()
        date_from  = request.args.get("date_from", "").strip()
        date_to    = request.args.get("date_to", "").strip()
        search     = request.args.get("search", "").strip()
        sort_by    = request.args.get("sort", "date")
        order      = request.args.get("order", "desc")

        query = Expense.query

        if category:
            query = query.filter(Expense.category == category)
        if search:
            query = query.filter(Expense.notes.ilike(f"%{search}%"))

        from sqlalchemy import extract

        has_yr = year_str and year_str not in ("all", "الكل")
        has_mo = month_str and month_str not in ("all", "الكل")

        if has_yr and has_mo:
            try:
                yr_val = int(year_str)
                mo_val = int(month_str)
                query = query.filter(
                    extract("year", Expense.expense_date) == yr_val,
                    extract("month", Expense.expense_date) == mo_val
                )
            except ValueError:
                pass
        elif has_yr:
            try:
                from datetime import date
                yr_val = int(year_str)
                start_dt = date(yr_val, 1, 1)
                end_dt = date(yr_val + 1, 1, 1)
                query = query.filter(Expense.expense_date >= start_dt, Expense.expense_date < end_dt)
            except ValueError:
                pass
        elif has_mo:
            try:
                mo_val = int(month_str)
                query = query.filter(extract("month", Expense.expense_date) == mo_val)
            except ValueError:
                pass
        else:
            if date_from:
                try:
                    from datetime import date
                    df = datetime.strptime(date_from, "%Y-%m-%d").date()
                    query = query.filter(Expense.expense_date >= df)
                except ValueError:
                    pass
            if date_to:
                try:
                    dt = datetime.strptime(date_to, "%Y-%m-%d").date()
                    query = query.filter(Expense.expense_date <= dt)
                except ValueError:
                    pass

        sort_map = {
            "date":     Expense.expense_date,
            "amount":   Expense.amount,
            "category": Expense.category,
            "notes":    Expense.notes,
        }
        sort_col = sort_map.get(sort_by, Expense.expense_date)
        query = query.order_by(sort_col.asc() if order == "asc" else sort_col.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        rows = []
        for e in pagination.items:
            rows.append({
                "id":       e.id,
                "category": e.category,
                "amount":   float(e.amount),
                "date":     e.expense_date.strftime("%Y-%m-%d"),
                "notes":    e.notes or "",
            })

        total_filtered = float(query.order_by(None).with_entities(
            func.coalesce(func.sum(Expense.amount), 0.0)
        ).scalar() or 0.0)

        return {
            "rows":           rows,
            "total":          pagination.total,
            "pages":          pagination.pages,
            "current_page":   pagination.page,
            "total_filtered_amount": total_filtered,
        }
    except Exception:
        current_app.logger.exception("Failed to load expenses list")
        return {"error": "Failed to load expenses"}, 500


# ──────────────────────────────────────────────────────────────────────────────
# AJAX: Doctor Completed Appointments with Financial Details
# ──────────────────────────────────────────────────────────────────────────────

@reports_bp.route("/reports/doctor-appointments")
@role_required("admin")
def doctor_appointments_report():
    """Returns paginated completed appointments for a specific doctor (or all), with monthly defaults and deduction status."""
    try:
        from models import User, Patient, Treatment
        from datetime import datetime, timedelta
        import calendar

        doctor_id  = request.args.get("doctor_id", "", type=str).strip()
        page       = request.args.get("page", 1, type=int)
        per_page   = request.args.get("per_page", 10, type=int)
        sort_by    = request.args.get("sort", "date")
        order      = request.args.get("order", "desc")
        month      = request.args.get("month", "").strip()
        date_from  = request.args.get("date_from", "").strip()
        date_to    = request.args.get("date_to", "").strip()
        search     = request.args.get("search", "").strip()

        # If a specific month is selected (YYYY-MM), filter by that month
        if month:
            try:
                m_date = datetime.strptime(month, "%Y-%m")
                _, last_day = calendar.monthrange(m_date.year, m_date.month)
                date_from = f"{m_date.year:04d}-{m_date.month:02d}-01"
                date_to = f"{m_date.year:04d}-{m_date.month:02d}-{last_day:02d}"
            except ValueError:
                pass

        query = (
            Appointment.query
            .join(Patient, Appointment.patient_id == Patient.id)
            .filter(Appointment.status == "Done")
        )

        if doctor_id:
            try:
                query = query.filter(Appointment.doctor_id == int(doctor_id))
            except ValueError:
                pass

        if search:
            query = query.filter(
                db.or_(
                    Patient.first_name.ilike(f"%{search}%"),
                    Patient.last_name.ilike(f"%{search}%"),
                    Appointment.reason.ilike(f"%{search}%")
                )
            )

        if date_from:
            try:
                df = datetime.strptime(date_from, "%Y-%m-%d")
                query = query.filter(Appointment.appointment_date >= df)
            except ValueError:
                pass
        if date_to:
            try:
                dt = datetime.strptime(date_to, "%Y-%m-%d")
                query = query.filter(Appointment.appointment_date < dt + timedelta(days=1))
            except ValueError:
                pass

        sort_map = {
            "date":    Appointment.appointment_date,
            "patient": Patient.first_name,
            "status":  Appointment.status,
        }
        sort_col = sort_map.get(sort_by, Appointment.appointment_date)
        query = query.order_by(sort_col.asc() if order == "asc" else sort_col.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        rows = []
        total_invoiced_sum = 0.0
        total_paid_sum = 0.0

        for appt in pagination.items:
            patient = appt.patient
            inv_total = float(appt.invoice_total or 0)
            paid      = float(appt.total_paid or 0)
            remaining = max(0.0, inv_total - paid)

            doc = appt.doctor
            doc_name = ""
            if doc:
                doc_name = f"{doc.first_name or ''} {doc.last_name or ''}".strip() or doc.username

            total_invoiced_sum += inv_total
            total_paid_sum += paid

            date_val = appt.appointment_date.strftime("%Y-%m-%d") if appt.appointment_date else "—"
            time_val = appt.appointment_date.strftime("%I:%M %p") if appt.appointment_date else ""

            # Deduction status: check if any treatment on this appointment has been deducted
            treatments = Treatment.query.filter_by(appointment_id=appt.id).all()
            is_deducted = len(treatments) > 0 and any(t.salary_expense_id is not None for t in treatments)

            rows.append({
                "id":           appt.id,
                "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "—",
                "date":         date_val,
                "time":         time_val,
                "doctor":       doc_name,
                "invoice_total": inv_total,
                "total_paid":   paid,
                "remaining":    remaining,
                "reason":       appt.reason or "",
                "is_deducted":  is_deducted
            })

        # Build list of doctors for the filter dropdown
        doctors = User.query.filter(User.role.in_(["admin", "doctor"])).order_by(User.first_name).all()
        doctors_list = [
            {"id": d.id, "name": f"{d.first_name or ''} {d.last_name or ''}".strip() or d.username}
            for d in doctors
        ]

        return {
            "rows":             rows,
            "total":            pagination.total,
            "pages":            pagination.pages,
            "current_page":     pagination.page,
            "total_invoiced":   total_invoiced_sum,
            "total_paid":       total_paid_sum,
            "doctors":          doctors_list,
            "active_month":     month,
        }
    except Exception:
        current_app.logger.exception("Failed to load doctor appointments report")
        return {"error": "Failed to load doctor appointments"}, 500


@reports_bp.route("/reports/doctor-revenue-share")
@role_required("admin")
def doctor_revenue_share_report():
    """Returns paginated doctors performance & revenue share analysis with monthly defaults and deduction tracking."""
    try:
        from models import User, StaffSalary, Appointment, Treatment, db
        from sqlalchemy import func
        from datetime import datetime, timedelta
        import calendar

        doctor_id = request.args.get("doctor_id", "", type=str).strip()
        page      = request.args.get("page", 1, type=int)
        per_page  = request.args.get("per_page", 10, type=int)
        sort_by   = request.args.get("sort", "revenue")
        order     = request.args.get("order", "desc")
        month     = request.args.get("month", "").strip()
        year      = request.args.get("year", "").strip().lower()
        date_from = request.args.get("date_from", "").strip()
        date_to   = request.args.get("date_to", "").strip()
        search    = request.args.get("search", "").strip()

        # If a specific month is selected (YYYY-MM) or full year (YYYY), filter by that period
        if month:
            if len(month) == 4 and month.isdigit():
                try:
                    yr_val = int(month)
                    date_from = f"{yr_val:04d}-01-01"
                    date_to = f"{yr_val:04d}-12-31"
                except ValueError:
                    pass
            else:
                try:
                    m_date = datetime.strptime(month, "%Y-%m")
                    _, last_day = calendar.monthrange(m_date.year, m_date.month)
                    date_from = f"{m_date.year:04d}-{m_date.month:02d}-01"
                    date_to = f"{m_date.year:04d}-{m_date.month:02d}-{last_day:02d}"
                except ValueError:
                    pass
        elif year and year not in ("all", "الكل"):
            try:
                yr_val = int(year)
                date_from = f"{yr_val:04d}-01-01"
                date_to = f"{yr_val:04d}-12-31"
            except ValueError:
                pass

        # Fetch only assistant doctors (excluding admin)
        all_docs = User.query.filter_by(role="doctor").order_by(User.first_name).all()
        doctors_list = [{"id": d.id, "name": f"{d.first_name or ''} {d.last_name or ''}".strip() or d.username} for d in all_docs]

        doc_query = User.query.filter_by(role="doctor")

        if doctor_id:
            try:
                doc_query = doc_query.filter(User.id == int(doctor_id))
            except ValueError:
                pass

        if search:
            doc_query = doc_query.filter(
                db.or_(
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%")
                )
            )

        matched_docs = doc_query.all()

        df = None
        dt = None
        if date_from:
            try:
                df = datetime.strptime(date_from, "%Y-%m-%d")
            except ValueError:
                pass
        if date_to:
            try:
                dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            except ValueError:
                pass

        calculated_rows = []
        tot_rev_sum = 0.0
        tot_earned_sum = 0.0
        tot_net_sum = 0.0

        for doc in matched_docs:
            appt_query = Appointment.query.filter_by(doctor_id=doc.id)
            if df:
                appt_query = appt_query.filter(Appointment.appointment_date >= df)
            if dt:
                appt_query = appt_query.filter(Appointment.appointment_date < dt)

            appts_count = appt_query.count()

            t_query = db.session.query(func.coalesce(func.sum(Treatment.total_cost), 0.0)).join(Appointment, Treatment.appointment_id == Appointment.id).filter(Appointment.doctor_id == doc.id)
            if df:
                t_query = t_query.filter(Appointment.appointment_date >= df)
            if dt:
                t_query = t_query.filter(Appointment.appointment_date < dt)

            doc_revenue = float(t_query.scalar() or 0.0)

            # Count deducted vs pending treatments
            t_base = Treatment.query.join(Appointment, Treatment.appointment_id == Appointment.id).filter(Appointment.doctor_id == doc.id)
            if df:
                t_base = t_base.filter(Appointment.appointment_date >= df)
            if dt:
                t_base = t_base.filter(Appointment.appointment_date < dt)

            deducted_count = t_base.filter(Treatment.salary_expense_id != None).count()
            pending_count = t_base.filter(Treatment.salary_expense_id == None).count()

            # Pending months breakdown (global across all time so all pending months are visible)
            from sqlalchemy import extract
            pending_months_q = db.session.query(
                extract('year', Appointment.appointment_date).label('yr'),
                extract('month', Appointment.appointment_date).label('mon'),
                func.count(Treatment.id).label('cnt')
            ).join(Appointment, Treatment.appointment_id == Appointment.id).filter(
                Appointment.doctor_id == doc.id,
                Treatment.salary_expense_id == None
            )

            pending_months_rows = pending_months_q.group_by('yr', 'mon').order_by(extract('year', Appointment.appointment_date).desc(), extract('month', Appointment.appointment_date).desc()).all()

            ARABIC_MONTHS = {
                1: "كانون الثاني", 2: "شباط", 3: "آذار", 4: "نيسان",
                5: "أيار", 6: "حزيران", 7: "تموز", 8: "آب",
                9: "أيلول", 10: "تشرين الأول", 11: "تشرين الثاني", 12: "كانون الأول"
            }

            pending_months_list = []
            for yr_v, mon_v, cnt_v in pending_months_rows:
                if yr_v and mon_v:
                    y_i = int(yr_v)
                    m_i = int(mon_v)
                    m_str = f"{y_i:04d}-{m_i:02d}"
                    m_label_ar = f"{ARABIC_MONTHS[m_i]} {y_i}"
                    m_label_en = f"{datetime(y_i, m_i, 1).strftime('%b %Y')}"
                    pending_months_list.append({
                        "ym": m_str,
                        "label_ar": m_label_ar,
                        "label_en": m_label_en,
                        "count": cnt_v
                    })

            sc = StaffSalary.query.filter_by(user_id=doc.id).first()
            s_type = sc.salary_type if sc else "fixed"
            s_amount = float(sc.amount) if sc else 0.0
            current_month_str = datetime.now().strftime("%Y-%m")

            # Determine if this doctor's salary is already deducted for the selected period
            if s_type == "percentage":
                if month:
                    # Check if an Expense row exists in the DB for exactly this doctor & this month
                    from models import Expense as _Exp
                    import calendar as _cal
                    try:
                        _m = datetime.strptime(month, "%Y-%m")
                        _last_day = _cal.monthrange(_m.year, _m.month)[1]
                        _start = _m.replace(day=1).date()
                        _end   = _m.replace(day=_last_day).date()
                        _name_part = doc.last_name or doc.first_name or doc.username
                        _linked = (
                            _Exp.query
                            .filter(
                                _Exp.category == "Salaries",
                                _Exp.expense_date >= _start,
                                _Exp.expense_date <= _end,
                                _Exp.notes.ilike(f"%{_name_part}%")
                            )
                            .first()
                        )
                        is_period_deducted = _linked is not None
                    except Exception:
                        is_period_deducted = (deducted_count > 0 and pending_count == 0)
                else:
                    # No month filter → check current month via last_deducted_month
                    is_period_deducted = bool(sc and sc.last_deducted_month == current_month_str)
            else:
                # Fixed salary: rely on last_deducted_month
                if month:
                    is_period_deducted = bool(sc and sc.last_deducted_month and sc.last_deducted_month >= month)
                else:
                    is_period_deducted = bool(sc and sc.last_deducted_month == current_month_str)

            if s_type == "percentage":
                doc_earned = round(doc_revenue * s_amount / 100.0, 2)
                pct_rate = s_amount
            else:
                doc_earned = s_amount
                pct_rate = round((doc_earned / doc_revenue * 100.0), 1) if doc_revenue > 0 else 0.0

            # If date or month filter is active, skip doctors who have no appointments and no revenue in this period
            if (df or dt or month) and appts_count == 0 and doc_revenue == 0.0:
                continue

            clinic_net = max(0.0, doc_revenue - doc_earned)

            tot_rev_sum += doc_revenue
            tot_earned_sum += doc_earned
            tot_net_sum += clinic_net

            calculated_rows.append({
                "id": doc.id,
                "first_name": doc.first_name or "",
                "last_name": doc.last_name or "",
                "username": doc.username,
                "appointment_count": appts_count,
                "total_revenue": doc_revenue,
                "salary_type": s_type,
                "salary_amount": s_amount,
                "doctor_earned": doc_earned,
                "clinic_net": clinic_net,
                "pct_display": min(100.0, max(0.0, pct_rate)),
                "deducted_count": deducted_count,
                "pending_count": pending_count,
                "pending_months": pending_months_list,
                "is_deducted": is_period_deducted,
                "deducted_this_month": is_period_deducted,
                "last_deducted_month": sc.last_deducted_month if sc else None,
            })

        reverse = (order == "desc")
        if sort_by == "name":
            calculated_rows.sort(key=lambda x: f"{x['first_name']} {x['last_name']}".strip(), reverse=reverse)
        elif sort_by == "appts":
            calculated_rows.sort(key=lambda x: x["appointment_count"], reverse=reverse)
        elif sort_by == "earned":
            calculated_rows.sort(key=lambda x: x["doctor_earned"], reverse=reverse)
        elif sort_by == "net":
            calculated_rows.sort(key=lambda x: x["clinic_net"], reverse=reverse)
        else:
            calculated_rows.sort(key=lambda x: x["total_revenue"], reverse=reverse)

        total_items = len(calculated_rows)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_rows = calculated_rows[start_idx:end_idx]
        total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 1

        return {
            "rows": page_rows,
            "total": total_items,
            "pages": total_pages,
            "current_page": page,
            "total_revenue_sum": tot_rev_sum,
            "total_earned_sum": tot_earned_sum,
            "total_net_sum": tot_net_sum,
            "doctors": doctors_list,
            "active_month": month,
        }
    except Exception:
        current_app.logger.exception("Failed to load doctor revenue share report")
        return {"error": "Failed to load doctor revenue share report"}, 500


@reports_bp.route("/reports/expenses/<int:expense_id>/edit", methods=["POST"])
@role_required("admin")
def edit_expense(expense_id):
    """Edit an existing expense record."""
    try:
        expense = Expense.query.get_or_404(expense_id)
        expense.category = request.form.get("category", expense.category).strip()
        expense.notes    = request.form.get("notes", expense.notes or "").strip()
        amount_str = request.form.get("amount", "").strip()
        date_str   = request.form.get("expense_date", "").strip()
        if amount_str:
            try:
                expense.amount = float(amount_str)
            except ValueError:
                pass
        if date_str:
            try:
                expense.expense_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        db.session.commit()
        flash("تم تعديل المصروف بنجاح." if request.cookies.get("lang","ar")!="en" else "Expense updated successfully.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to edit expense {expense_id}")
        flash("تعديل المصروف." if request.cookies.get("lang","ar")!="en" else "Failed to update expense.", "danger")
    return redirect(url_for("reports.reports_dashboard") + "#tab-expenses")


@reports_bp.route("/reports/export/financial-csv")
@role_required("admin")
def export_financial_csv():
    """Export complete financial summary to CSV format for Excel and accounting software."""
    import csv
    import io
    from sqlalchemy.orm import joinedload

    output = io.StringIO()
    # Write UTF-8 BOM for Microsoft Excel compatibility with Arabic text
    output.write('\ufeff')
    writer = csv.writer(output, csv.QUOTE_MINIMAL)

    lang = request.cookies.get("lang", "ar")
    if lang == "ar":
        writer.writerow(["رقم الفاتورة", "تاريخ الإصدار", "اسم المريض", "الإجمالي", "المدفوع", "المتبقي", "الحالة"])
    else:
        writer.writerow(["Invoice Ref", "Issue Date", "Patient Name", "Total Amount", "Paid Amount", "Outstanding", "Status"])

    invoices = Invoice.query.join(Invoice.appointment).options(
        joinedload(Invoice.patient),
        joinedload(Invoice.appointment)
    ).order_by(Invoice.issue_date.desc()).all()

    for inv in invoices:
        patient_name = f"{inv.patient.first_name} {inv.patient.last_name}" if inv.patient else "N/A"
        writer.writerow([
            inv.invoice_number,
            inv.issue_date.strftime("%Y-%m-%d") if inv.issue_date else "",
            patient_name,
            float(inv.total_amount or 0),
            float(inv.total_paid or 0),
            float(inv.outstanding_amount or 0),
            inv.status
        ])

    response = Response(output.getvalue(), mimetype="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = "attachment; filename=dental_clinic_financial_report.csv"
    return response


@reports_bp.route("/reports/print")
@role_required("admin")
def print_full_report():
    """Renders a dedicated, perfectly formatted multi-page document for PDF printing."""
    try:
        today = datetime.now()
        year_param = request.args.get("year", "all").strip().lower()
        if year_param in ("all", "الكل", ""):
            selected_year = "all"
            filter_year = None
        else:
            try:
                filter_year = int(year_param)
                selected_year = str(filter_year)
            except ValueError:
                filter_year = today.year
                selected_year = str(today.year)

        if filter_year:
            start_date_year = datetime(filter_year, 1, 1)
            end_date_year = datetime(filter_year + 1, 1, 1)
            total_invoiced = sum(float(inv.total_amount) for inv in Invoice.query.join(Invoice.appointment).filter(Appointment.status != "Cancelled", Invoice.issue_date >= start_date_year, Invoice.issue_date < end_date_year).all())
            total_payments = float(db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)).filter(Payment.payment_date >= start_date_year, Payment.payment_date < end_date_year).scalar())
        else:
            total_invoiced = sum(float(inv.total_amount) for inv in Invoice.query.join(Invoice.appointment).filter(Appointment.status != "Cancelled").all())
            total_payments = float(db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar())

        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        total_outstanding = max(0.0, total_invoiced - total_payments)
        total_credit = max(0.0, total_payments - total_invoiced)

        # Top 5 Procedures
        proc_q = db.session.query(
            Treatment.procedure_type,
            func.count(Treatment.id),
            func.sum(Treatment.total_cost)
        )
        if filter_year:
            proc_q = proc_q.join(Appointment, Treatment.appointment_id == Appointment.id).filter(Appointment.appointment_date >= start_date_year, Appointment.appointment_date < end_date_year)
        procedure_counts = proc_q.group_by(Treatment.procedure_type).order_by(func.count(Treatment.id).desc()).limit(5).all()

        procedure_labels = [p[0] for p in procedure_counts]
        procedure_values_counts = [p[1] for p in procedure_counts]
        procedure_values_revenue = [float(p[2] or 0.0) for p in procedure_counts]

        # Gender Demographics
        gender_counts = db.session.query(
            Patient.gender, func.count(Patient.id)
        ).group_by(Patient.gender).all()

        gender_labels = [g[0] or "Not Specified" for g in gender_counts]
        gender_values = [g[1] for g in gender_counts]

        # Monthly Summary
        monthly_summary = []
        summary_years = [filter_year] if filter_year else [today.year]

        for yr_val in summary_years:
            for month in range(1, 13):
                date_start = datetime(yr_val, month, 1)
                date_end = datetime(yr_val + 1, 1, 1) if month == 12 else datetime(yr_val, month + 1, 1)

                invoices_m = Invoice.query.join(Invoice.appointment).filter(
                    Appointment.status != "Cancelled",
                    Invoice.issue_date >= date_start,
                    Invoice.issue_date < date_end
                ).all()
                billed_m = sum(float(inv.total_amount) for inv in invoices_m)

                paid_m = float(db.session.query(func.sum(Payment.amount)).filter(
                    Payment.payment_date >= date_start,
                    Payment.payment_date < date_end
                ).scalar() or 0.0)

                expenses_m = float(db.session.query(func.sum(Expense.amount)).filter(
                    Expense.expense_date >= date_start.date(),
                    Expense.expense_date < date_end.date()
                ).scalar() or 0.0)

                ARABIC_MONTHS = {
                    1: "كانون الثاني", 2: "شباط", 3: "آذار", 4: "نيسان",
                    5: "أيار", 6: "حزيران", 7: "تموز", 8: "آب",
                    9: "أيلول", 10: "تشرين الأول", 11: "تشرين الثاني", 12: "كانون الأول"
                }
                is_ar = request.cookies.get("lang") == "ar" or request.cookies.get("lang") != "en"

                monthly_summary.append({
                    "month_label": f"{ARABIC_MONTHS[month]} {yr_val}" if is_ar else date_start.strftime("%B %Y"),
                    "billed": billed_m,
                    "paid": paid_m,
                    "expenses": expenses_m,
                    "net_profit": paid_m - expenses_m,
                    "accrual_profit": billed_m - expenses_m
                })

        # Doctors Performance
        from models import User
        doctors = User.query.filter(User.role.in_(["admin", "doctor"])).all()
        doctors_report = []
        for doc in doctors:
            doc_appts = Appointment.query.filter_by(doctor_id=doc.id).count()
            doc_treatment_count = Treatment.query.filter_by(doctor_id=doc.id).count()
            doc_revenue = float(db.session.query(func.coalesce(func.sum(Treatment.total_cost), 0.0)).filter_by(doctor_id=doc.id).scalar())
            doctors_report.append({
                "doctor": doc,
                "appointment_count": doc_appts,
                "treatment_count": doc_treatment_count,
                "total_revenue": doc_revenue
            })

        # Debtors & Credited Patients
        patient_invoiced = {}
        for inv in Invoice.query.join(Invoice.appointment).filter(Appointment.status != "Cancelled").all():
            patient_invoiced[inv.patient_id] = patient_invoiced.get(inv.patient_id, 0.0) + float(inv.total_amount)

        patient_payments = dict(
            db.session.query(
                Payment.patient_id,
                func.coalesce(func.sum(Payment.amount), 0.0)
            ).group_by(Payment.patient_id).all()
        )

        all_patient_ids = set(patient_invoiced.keys()).union(set(patient_payments.keys()))
        all_patients_map = {p.id: p for p in Patient.query.filter(Patient.id.in_(all_patient_ids)).all()} if all_patient_ids else {}

        all_debtors = []
        all_credited_patients = []

        for p_id, p in all_patients_map.items():
            billed = float(patient_invoiced.get(p_id, 0.0))
            paid = float(patient_payments.get(p_id, 0.0))
            diff = billed - paid

            p_data = {
                "name": f"{p.first_name} {p.last_name}",
                "phone": p.phone or "—",
                "total_billed": billed,
                "total_paid": paid,
                "outstanding": max(0.0, diff),
                "credit": max(0.0, -diff)
            }

            if diff > 0.01:
                all_debtors.append(p_data)
            elif diff < -0.01:
                all_credited_patients.append(p_data)

        all_debtors.sort(key=lambda x: x["outstanding"], reverse=True)
        all_credited_patients.sort(key=lambda x: x["credit"], reverse=True)

        return render_template(
            "reports/print_report.html",
            total_patients=total_patients,
            total_appointments=total_appointments,
            total_invoiced=total_invoiced,
            total_payments=total_payments,
            total_outstanding=total_outstanding,
            total_credit=total_credit,
            procedure_labels=procedure_labels,
            procedure_values_counts=procedure_values_counts,
            procedure_values_revenue=procedure_values_revenue,
            gender_labels=gender_labels,
            gender_values=gender_values,
            monthly_summary=monthly_summary,
            doctors_report=doctors_report,
            all_debtors=all_debtors,
            all_credited_patients=all_credited_patients,
            selected_year=selected_year,
            print_date=today.strftime("%Y-%m-%d %I:%M %p")
        )
    except Exception:
        current_app.logger.exception("Failed to render print report")
        flash("فشل في تجهيز طباعة التقرير." if request.cookies.get("lang","ar")!="en" else "Failed to render print report.", "danger")
        return redirect(url_for("reports.reports_dashboard"))


@reports_bp.route("/my-reports")
@role_required("admin", "doctor")
def my_reports():
    current_app.logger.info("Doctor personal reports page opened")
    user = g.get("current_user")

    target_doctor_id = request.args.get("doctor_id", type=int)
    if not target_doctor_id:
        if user and user.role == "doctor":
            target_doctor_id = user.id
        else:
            from models import User
            first_doc = User.query.filter_by(role="doctor").first()
            target_doctor_id = first_doc.id if first_doc else (user.id if user else 1)

    return doctor_personal_report(target_doctor_id)


@reports_bp.route("/clinic-guide")
def clinic_guide_html():
    return render_template("reports/../docs/dental_clinic_master_guide.html")


@reports_bp.route("/clinic-guide-pdf")
def clinic_guide_pdf():
    import os
    from flask import send_from_directory
    static_docs = os.path.join(current_app.root_path, "static", "docs")
    return send_from_directory(static_docs, "clinic_user_guide.pdf", as_attachment=False)


@reports_bp.route("/reports/doctor-print/<int:doctor_id>")
@role_required("admin", "doctor")
def doctor_print_report(doctor_id):
    user = g.get("current_user")
    if user and user.role == "doctor" and user.id != doctor_id:
        flash("غير مصرح لك بطباعة تقارير أطباء آخرين." if request.cookies.get("lang", "ar") != "en" else "You are not authorized to print reports of other doctors.", "danger")
        return redirect(url_for("reports.my_reports"))
    return doctor_personal_report(doctor_id, is_print=True)


def doctor_personal_report(doctor_id, is_print=False):
    from models import User, StaffSalary, Appointment, Treatment, Patient, Invoice
    from sqlalchemy.orm import joinedload
    import json

    doctor = User.query.get_or_404(doctor_id)
    all_doctors = User.query.filter_by(role="doctor").order_by(User.first_name).all()

    # Salary configuration
    salary_cfg = StaffSalary.query.filter_by(user_id=doctor.id).first()
    salary_type = salary_cfg.salary_type if salary_cfg else "fixed"
    salary_amount = float(salary_cfg.amount) if salary_cfg else 0.0

    today = datetime.now()

    # Available years for filter
    min_year = today.year
    max_year = today.year
    min_date = db.session.query(func.min(Appointment.appointment_date)).filter(Appointment.doctor_id == doctor.id).scalar()
    max_date = db.session.query(func.max(Appointment.appointment_date)).filter(Appointment.doctor_id == doctor.id).scalar()
    if min_date and min_date.year < min_year:
        min_year = min_date.year
    if max_date and max_date.year > max_year:
        max_year = max_date.year
    available_years = list(range(max_year, min_year - 1, -1))

    # Year and month filter params
    year_param = request.args.get("year", "all").strip().lower()
    month_param = request.args.get("month", "all").strip().lower()

    if year_param in ("all", "الكل", ""):
        selected_year = "all"
        filter_year = None
    else:
        try:
            filter_year = int(year_param)
            selected_year = str(filter_year)
        except ValueError:
            selected_year = "all"
            filter_year = None

    if month_param in ("all", "الكل", ""):
        selected_month = "all"
        filter_month = None
    else:
        try:
            filter_month = int(month_param)
            selected_month = str(filter_month)
        except ValueError:
            selected_month = "all"
            filter_month = None

    # Base query for treatments
    treatments_query = (
        Treatment.query
        .join(Appointment, Treatment.appointment_id == Appointment.id)
        .options(
            joinedload(Treatment.appointment).joinedload(Appointment.patient),
            joinedload(Treatment.appointment).joinedload(Appointment.invoice)
        )
        .filter(Appointment.doctor_id == doctor.id)
    )

    if filter_year:
        treatments_query = treatments_query.filter(func.extract('year', Appointment.appointment_date) == filter_year)
    if filter_month:
        treatments_query = treatments_query.filter(func.extract('month', Appointment.appointment_date) == filter_month)

    treatments_raw = treatments_query.order_by(Appointment.appointment_date.desc(), Treatment.id.desc()).all()

    treatments_list = []
    total_revenue = 0.0
    total_earned = 0.0

    for t in treatments_raw:
        cost = float(t.total_cost or 0.0)
        total_revenue += cost

        if salary_type == "percentage":
            share = round(cost * (salary_amount / 100.0), 2)
            pct_display = salary_amount
        else:
            share = 0.0
            pct_display = 0.0

        total_earned += share

        treatments_list.append({
            "id": t.id,
            "procedure_name": t.procedure_type,
            "tooth_number": t.tooth_number or "—",
            "cost": cost,
            "doctor_share": share,
            "doctor_pct": pct_display,
            "notes": t.notes or "",
            "date": t.appointment.appointment_date if t.appointment else None,
            "patient_id": t.appointment.patient.id if (t.appointment and t.appointment.patient) else None,
            "patient_name": f"{t.appointment.patient.first_name} {t.appointment.patient.last_name}" if (t.appointment and t.appointment.patient) else "—",
            "status": t.appointment.status if t.appointment else "—",
            "invoice": t.appointment.invoice if t.appointment else None
        })

    if salary_type == "fixed":
        total_earned = salary_amount

    clinic_net = max(0.0, total_revenue - total_earned)

    # Base query for appointments
    appts_query = Appointment.query.filter_by(doctor_id=doctor.id)
    if filter_year:
        appts_query = appts_query.filter(func.extract('year', Appointment.appointment_date) == filter_year)
    if filter_month:
        appts_query = appts_query.filter(func.extract('month', Appointment.appointment_date) == filter_month)

    total_appointments_count = appts_query.count()

    status_counts = dict(
        db.session.query(Appointment.status, func.count(Appointment.id))
        .filter(Appointment.doctor_id == doctor.id)
        .group_by(Appointment.status)
        .all()
    )

    scheduled_count = status_counts.get("Scheduled", 0)
    done_count = status_counts.get("Done", 0)
    cancelled_count = status_counts.get("Cancelled", 0)
    checked_in_count = status_counts.get("Checked In", 0)
    in_chair_count = status_counts.get("In Chair", 0)

    # Monthly chart data (12 months of current/filtered year)
    chart_year = filter_year or today.year
    monthly_revenue = [0.0] * 12
    monthly_earned = [0.0] * 12

    monthly_rows = (
        db.session.query(
            func.extract('month', Appointment.appointment_date).label('m'),
            func.coalesce(func.sum(Treatment.total_cost), 0.0)
        )
        .join(Appointment, Treatment.appointment_id == Appointment.id)
        .filter(Appointment.doctor_id == doctor.id)
        .filter(func.extract('year', Appointment.appointment_date) == chart_year)
        .group_by('m')
        .all()
    )

    for m_val, rev in monthly_rows:
        idx = int(m_val) - 1
        r_val = float(rev or 0.0)
        monthly_revenue[idx] = r_val
        if salary_type == "percentage":
            monthly_earned[idx] = round(r_val * (salary_amount / 100.0), 2)
        else:
            monthly_earned[idx] = salary_amount if r_val > 0 else 0.0

    month_names_ar = [
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]

    if is_print:
        return render_template(
            "reports/print_doctor_report.html",
            doctor=doctor,
            salary_cfg=salary_cfg,
            salary_type=salary_type,
            salary_amount=salary_amount,
            selected_year=selected_year,
            selected_month=selected_month,
            treatments_list=treatments_list,
            total_treatments_count=len(treatments_list),
            total_revenue=total_revenue,
            total_earned=total_earned,
            clinic_net=clinic_net,
            total_appointments_count=total_appointments_count,
            scheduled_count=scheduled_count,
            done_count=done_count,
            cancelled_count=cancelled_count,
            print_date=today.strftime("%Y-%m-%d %I:%M %p")
        )

    return render_template(
        "reports/doctor_reports.html",
        doctor=doctor,
        all_doctors=all_doctors,
        salary_cfg=salary_cfg,
        salary_type=salary_type,
        salary_amount=salary_amount,
        available_years=available_years,
        selected_year=selected_year,
        selected_month=selected_month,
        treatments_list=treatments_list,
        total_treatments_count=len(treatments_list),
        total_revenue=total_revenue,
        total_earned=total_earned,
        clinic_net=clinic_net,
        total_appointments_count=total_appointments_count,
        scheduled_count=scheduled_count,
        done_count=done_count,
        cancelled_count=cancelled_count,
        checked_in_count=checked_in_count,
        in_chair_count=in_chair_count,
        chart_year=chart_year,
        month_names_ar=json.dumps(month_names_ar, ensure_ascii=False),
        monthly_revenue=json.dumps(monthly_revenue),
        monthly_earned=json.dumps(monthly_earned),
        status_counts_json=json.dumps({
            "مجدول": scheduled_count + checked_in_count + in_chair_count,
            "منجز": done_count,
            "ملغى": cancelled_count
        }, ensure_ascii=False)
    )
