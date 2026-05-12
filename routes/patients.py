from flask import Blueprint, current_app, render_template, request, redirect, url_for

from models import db, Patient, Appointment, Treatment
from utils.validators import parse_patient_data


patients_bp = Blueprint("patients", __name__)


@patients_bp.route("/patients")
def patients():
    search_query = request.args.get("search", "")
    sort_by = request.args.get("sort", "id")
    order = request.args.get("order", "desc")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    current_app.logger.info("Patients page opened")

    try:
        query = Patient.query

        if search_query:
            query = query.filter(
                (Patient.first_name.ilike(f"%{search_query}%")) |
                (Patient.last_name.ilike(f"%{search_query}%")) |
                (Patient.phone.ilike(f"%{search_query}%")) |
                (Patient.email.ilike(f"%{search_query}%")) |
                (Patient.city.ilike(f"%{search_query}%"))
            )

        sort_columns = {
            "id": Patient.id,
            "first_name": Patient.first_name,
            "last_name": Patient.last_name,
            "phone": Patient.phone,
            "email": Patient.email,
            "city": Patient.city,
            "date_of_birth": Patient.date_of_birth,
        }

        sort_column = sort_columns.get(sort_by, Patient.id)

        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        return render_template(
            "patients/patients.html",
            patients=pagination.items,
            pagination=pagination,
            search_query=search_query,
            sort_by=sort_by,
            order=order,
        )

    except Exception:
        current_app.logger.exception("Error while loading patients page")
        return "Error Loading PatientsPage", 500


@patients_bp.route("/patients/add", methods=["GET", "POST"])
def add_patient():
    if request.method == "POST":
        patient_data, patient_error = parse_patient_data(request.form)

        if patient_error:
            return render_template(
                "patients/add_patient.html",
                error_message=patient_error,
            ), 400

        new_patient = Patient(**patient_data)

        db.session.add(new_patient)
        db.session.commit()

        return redirect(url_for("patients.patients"))

    return render_template("patients/add_patient.html")


@patients_bp.route("/patients/<int:patient_id>")
def patient_detail(patient_id):
    current_app.logger.info(f"Patient detail page opened | patient_id={patient_id}")

    try:
        patient = Patient.query.get_or_404(patient_id)

        appointment_sort = request.args.get("appointment_sort", "date")
        appointment_order = request.args.get("appointment_order", "desc")

        treatment_sort = request.args.get("treatment_sort", "date")
        treatment_order = request.args.get("treatment_order", "desc")

        active_tab = request.args.get("tab", "appointments")

        appointment_sort_columns = {
            "id": Appointment.id,
            "date": Appointment.appointment_date,
            "reason": Appointment.reason,
            "status": Appointment.status,
        }

        appointment_sort_column = appointment_sort_columns.get(
            appointment_sort,
            Appointment.appointment_date,
        )

        appointments_query = Appointment.query.filter_by(patient_id=patient.id)

        if appointment_order == "asc":
            appointments_query = appointments_query.order_by(appointment_sort_column.asc())
        else:
            appointments_query = appointments_query.order_by(appointment_sort_column.desc())

        patient_appointments = appointments_query.all()

        treatment_sort_columns = {
            "id": Treatment.id,
            "date": Treatment.treatment_date,
            "procedure_type": Treatment.procedure_type,
            "tooth_number": Treatment.tooth_number,
        }

        treatment_sort_column = treatment_sort_columns.get(
            treatment_sort,
            Treatment.treatment_date,
        )

        treatments_query = (
            Treatment.query
            .join(Appointment)
            .filter(Appointment.patient_id == patient.id)
        )

        if treatment_order == "asc":
            treatments_query = treatments_query.order_by(treatment_sort_column.asc())
        else:
            treatments_query = treatments_query.order_by(treatment_sort_column.desc())

        patient_treatments = treatments_query.all()

        total_cost_sum = patient.total_invoice_amount
        total_paid_sum = patient.total_payments_amount
        total_remaining_sum = patient.outstanding_amount
        credit_amount = patient.credit_amount

        return render_template(
            "patients/patient_detail.html",
            patient=patient,
            patient_appointments=patient_appointments,
            patient_treatments=patient_treatments,
            total_cost_sum=total_cost_sum,
            total_paid_sum=total_paid_sum,
            total_remaining_sum=total_remaining_sum,
            credit_amount=credit_amount,
            appointment_sort=appointment_sort,
            appointment_order=appointment_order,
            treatment_sort=treatment_sort,
            treatment_order=treatment_order,
            active_tab=active_tab,
        )

    except Exception:
        current_app.logger.exception(
            f"Error while loading patient detail | patient_id={patient_id}"
        )
        return "Error Loading PatientsInfo", 500


@patients_bp.route("/patients/<int:patient_id>/appointments-table")
def patient_appointments_table(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    appointment_sort = request.args.get("appointment_sort", "date")
    appointment_order = request.args.get("appointment_order", "desc")

    sort_columns = {
        "id": Appointment.id,
        "date": Appointment.appointment_date,
        "reason": Appointment.reason,
        "status": Appointment.status,
    }

    sort_column = sort_columns.get(appointment_sort, Appointment.appointment_date)

    query = Appointment.query.filter_by(patient_id=patient.id)

    if appointment_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    patient_appointments = query.all()

    return render_template(
        "partials/_patient_appointments_table.html",
        patient=patient,
        patient_appointments=patient_appointments,
        appointment_sort=appointment_sort,
        appointment_order=appointment_order,
    )


@patients_bp.route("/patients/<int:patient_id>/treatments-table")
def patient_treatments_table(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    treatment_sort = request.args.get("treatment_sort", "date")
    treatment_order = request.args.get("treatment_order", "desc")

    sort_columns = {
        "id": Treatment.id,
        "date": Treatment.treatment_date,
        "procedure_type": Treatment.procedure_type,
        "tooth_number": Treatment.tooth_number,
    }

    sort_column = sort_columns.get(treatment_sort, Treatment.treatment_date)

    query = (
        Treatment.query
        .join(Appointment)
        .filter(Appointment.patient_id == patient.id)
    )

    if treatment_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    patient_treatments = query.all()

    return render_template(
        "partials/_patient_treatments_table.html",
        patient=patient,
        patient_treatments=patient_treatments,
        treatment_sort=treatment_sort,
        treatment_order=treatment_order,
    )


@patients_bp.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    current_app.logger.info(f"Edit patient page/request | patient_id={patient_id}")

    try:
        patient = Patient.query.get_or_404(patient_id)

        if request.method == "POST":
            patient_data, patient_error = parse_patient_data(request.form)

            if patient_error:
                return render_template(
                    "patients/edit_patient.html",
                    patient=patient,
                    mode="edit",
                    error_message=patient_error,
                ), 400

            for field, value in patient_data.items():
                setattr(patient, field, value)

            db.session.commit()

            current_app.logger.info(
                f"Patient updated successfully | patient_id={patient.id}"
            )
            return redirect(url_for("patients.patient_detail", patient_id=patient.id))

        return render_template(
            "patients/edit_patient.html",
            patient=patient,
            mode="edit",
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to edit patient | patient_id={patient_id}")
        return "Failed to edit patient", 500


@patients_bp.route("/patients/<int:patient_id>/view")
def view_patient(patient_id):
    current_app.logger.info(f"View patient page opened | patient_id={patient_id}")

    try:
        patient = Patient.query.get_or_404(patient_id)

        return render_template(
            "patients/edit_patient.html",
            patient=patient,
            mode="view",
        )

    except Exception:
        current_app.logger.exception(f"Failed to view patient | patient_id={patient_id}")
        return "Failed to view patient", 500


@patients_bp.route("/patients/<int:patient_id>/delete", methods=["GET", "POST"])
def delete_patient(patient_id):
    current_app.logger.warning(f"Delete patient page/request | patient_id={patient_id}")

    try:
        patient = Patient.query.get_or_404(patient_id)

        if patient.appointments:
            return render_template(
                "error_message.html",
                title="Action Not Allowed",
                message=(
                    "Cannot delete this patient because they have appointments "
                    "linked to their medical history."
                ),
                back_url=url_for("patients.patient_detail", patient_id=patient.id),
            ), 403

        if request.method == "POST":
            db.session.delete(patient)
            db.session.commit()

            current_app.logger.info(
                f"Patient deleted successfully | patient_id={patient_id}"
            )
            return redirect(url_for("patients.patients"))

        return render_template("patients/delete_patient.html", patient=patient)

    except Exception:
        db.session.rollback()
        current_app.logger.exception(f"Failed to delete patient | patient_id={patient_id}")
        return render_template(
            "error_message.html",
            title="Error",
            message="Failed to delete patient.",
            back_url=url_for("patients.patients"),
        ), 500