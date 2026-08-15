/**
 * Dental Clinic Management System - Edit Payment Controller
 * Handles patient selection change and auto-redirect with query parameters.
 */

window.initEditPayment = function () {
    const patientSelect = document.getElementById('patient_id');

    if (patientSelect) {
        patientSelect.addEventListener('change', function () {
            const selectedPatientId = patientSelect.value;
            if (selectedPatientId) {
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('patient_id', selectedPatientId);
                window.location.href = currentUrl.toString();
            }
        });
    }
};
