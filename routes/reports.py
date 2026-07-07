from datetime import datetime
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash, Response
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
        # 1. KPI Cards Data
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        total_invoiced = sum(float(inv.total_amount) for inv in Invoice.query.join(Invoice.appointment).filter(Appointment.status != "Cancelled").all())
        total_payments = sum(float(pay.amount) for pay in Payment.query.all())
        total_outstanding = max(0.0, total_invoiced - total_payments)
        total_credit = max(0.0, total_payments - total_invoiced)

        # Expenses & Net Profit calculations
        expenses = Expense.query.order_by(Expense.expense_date.desc(), Expense.id.desc()).all()
        total_expenses = sum(float(e.amount) for e in expenses)
        
        cash_net_profit = total_payments - total_expenses
        accrual_net_profit = total_invoiced - total_expenses

        expense_categories = {
            "Materials": 0.0,
            "Rent": 0.0,
            "Salaries": 0.0,
            "Other": 0.0
        }
        for e in expenses:
            cat = e.category if e.category in expense_categories else "Other"
            expense_categories[cat] += float(e.amount)

        # 2. Last 6 Months Income (Billed vs Paid) - DB Agnostic Python Logic
        today = datetime.now()
        months = []
        for i in range(5, -1, -1):
            year = today.year
            month = today.month - i
            if month <= 0:
                month += 12
                year -= 1
            months.append((year, month, datetime(year, month, 1)))

        monthly_labels = [m[2].strftime("%B %Y") for m in months]
        monthly_billed = []
        monthly_paid = []

        for year, month, date_start in months:
            if month == 12:
                date_end = datetime(year + 1, 1, 1)
            else:
                date_end = datetime(year, month + 1, 1)

            invoices_month = Invoice.query.join(Invoice.appointment).filter(
                Appointment.status != "Cancelled",
                Invoice.issue_date >= date_start,
                Invoice.issue_date < date_end
            ).all()
            billed_month = sum(float(inv.total_amount) for inv in invoices_month)
            monthly_billed.append(billed_month)

            paid_month = db.session.query(func.sum(Payment.amount)).filter(
                Payment.payment_date >= date_start,
                Payment.payment_date < date_end
            ).scalar() or 0.0
            monthly_paid.append(float(paid_month))

        # 3. Appointment Status Counts
        status_counts = db.session.query(
            Appointment.status, func.count(Appointment.id)
        ).group_by(Appointment.status).all()

        appointment_statuses = {"Scheduled": 0, "Done": 0, "Cancelled": 0}
        for status, count in status_counts:
            if status in appointment_statuses:
                appointment_statuses[status] = count

        appointment_status_labels = list(appointment_statuses.keys())
        appointment_status_values = list(appointment_statuses.values())

        # 4. Top 5 Procedures
        procedure_counts = db.session.query(
            Treatment.procedure_type,
            func.count(Treatment.id),
            func.sum(Treatment.total_cost)
        ).group_by(Treatment.procedure_type).order_by(func.count(Treatment.id).desc()).limit(5).all()

        procedure_labels = [p[0] for p in procedure_counts]
        procedure_values_counts = [p[1] for p in procedure_counts]
        procedure_values_revenue = [float(p[2] or 0.0) for p in procedure_counts]

        # 5. Patient Gender Demographics
        gender_counts = db.session.query(
            Patient.gender, func.count(Patient.id)
        ).group_by(Patient.gender).all()

        gender_labels = [g[0] or "Not Specified" for g in gender_counts]
        gender_values = [g[1] for g in gender_counts]

        # 6. Top Debtors (Outstanding Debt per Patient)
        all_patients = Patient.query.options(
            subqueryload(Patient.invoices).subqueryload(Invoice.appointment).subqueryload(Appointment.treatments),
            subqueryload(Patient.payments)
        ).all()
        debtors = [
            {
                "id": p.id,
                "name": f"{p.first_name} {p.last_name}",
                "phone": p.phone or "No phone",
                "total_billed": p.total_invoice_amount,
                "total_paid": p.total_payments_amount,
                "outstanding": p.outstanding_amount
            }
            for p in all_patients
            if p.outstanding_amount > 0
        ]
        top_debtors = sorted(debtors, key=lambda x: x["outstanding"], reverse=True)[:5]

        # Available years for filtering
        first_invoice = Invoice.query.order_by(Invoice.issue_date.asc()).first()
        first_payment = Payment.query.order_by(Payment.payment_date.asc()).first()
        first_expense = Expense.query.order_by(Expense.expense_date.asc()).first()
        
        years_with_data = {today.year}
        if first_invoice:
            years_with_data.add(first_invoice.issue_date.year)
        if first_payment:
            years_with_data.add(first_payment.payment_date.year)
        if first_expense:
            years_with_data.add(first_expense.expense_date.year)
            
        available_years = sorted(list(years_with_data), reverse=True)
        selected_year = request.args.get("year", default=today.year, type=int)

        # 7. Monthly Financial Summary for the Selected Calendar Year (January to December)
        monthly_summary = []
        for month in range(1, 13):
            date_start = datetime(selected_year, month, 1)
            if month == 12:
                date_end = datetime(selected_year + 1, 1, 1)
            else:
                date_end = datetime(selected_year, month + 1, 1)

            # Total Invoiced (Billed)
            invoices_m = Invoice.query.join(Invoice.appointment).filter(
                Appointment.status != "Cancelled",
                Invoice.issue_date >= date_start,
                Invoice.issue_date < date_end
            ).all()
            billed_m = sum(float(inv.total_amount) for inv in invoices_m)

            # Total Payments (Paid)
            paid_m = db.session.query(func.sum(Payment.amount)).filter(
                Payment.payment_date >= date_start,
                Payment.payment_date < date_end
            ).scalar() or 0.0
            paid_m = float(paid_m)

            # Total Expenses
            expenses_m = db.session.query(func.sum(Expense.amount)).filter(
                Expense.expense_date >= date_start.date(),
                Expense.expense_date < date_end.date()
            ).scalar() or 0.0
            expenses_m = float(expenses_m)

            # Cash Net Profit
            net_profit_m = paid_m - expenses_m
            # Accrual Net Profit
            accrual_profit_m = billed_m - expenses_m

            monthly_summary.append({
                "month_label": date_start.strftime("%B %Y"),
                "billed": billed_m,
                "paid": paid_m,
                "expenses": expenses_m,
                "net_profit": net_profit_m,
                "accrual_profit": accrual_profit_m
            })

        return render_template(
            "reports/reports.html",
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
        db.session.commit()
        flash("Expense recorded successfully.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to add expense")
        flash("Failed to record expense.", "danger")
    return redirect(url_for("reports.reports_dashboard") + "#tab-expenses")


@reports_bp.route("/reports/expenses/<int:expense_id>/delete", methods=["POST"])
@role_required("admin")
def delete_expense(expense_id):
    current_app.logger.warning(f"Deleting expense | id={expense_id}")
    try:
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        flash("Expense deleted successfully.", "success")
    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to delete expense {expense_id}")
        flash("Failed to delete expense.", "danger")
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
        year = int(year_str) if year_str else today.year
        month = int(month_str) if month_str else today.month
        
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
