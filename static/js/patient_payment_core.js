/**
 * Dental Clinic Management System - Patient Payment Core Controller
 * Handles patient selection change URL redirection, quick-pay button autofill, and input focus.
 */

window.initPatientPayment = function (config) {
    const baseUrl = config.baseUrl || '';
    const patientSelect = document.getElementById('patient_id');
    const invoiceBtn = document.getElementById('btn-invoice-payment');
    const totalDebtBtn = document.getElementById('btn-total-debt-payment');
    const paymentAmountInput = document.getElementById('payment_amount');

    if (patientSelect) {
        patientSelect.addEventListener('change', function () {
            const selectedPatientId = patientSelect.value;
            const urlParams = new URLSearchParams(window.location.search);
            const invoiceId = urlParams.get('invoice_id') || '';

            if (!selectedPatientId) {
                let targetUrl = baseUrl;
                if (invoiceId) {
                    targetUrl += "?invoice_id=" + encodeURIComponent(invoiceId);
                }
                window.location.href = targetUrl;
                return;
            }

            let targetUrl = baseUrl + "?patient_id=" + encodeURIComponent(selectedPatientId);
            if (invoiceId) {
                targetUrl += "&invoice_id=" + encodeURIComponent(invoiceId);
            }
            window.location.href = targetUrl;
        });
    }

    if (invoiceBtn && paymentAmountInput) {
        invoiceBtn.addEventListener('click', function () {
            const amount = invoiceBtn.getAttribute('data-amount');
            if (amount) {
                paymentAmountInput.value = amount;
                paymentAmountInput.focus();
            }
        });
    }

    if (totalDebtBtn && paymentAmountInput) {
        totalDebtBtn.addEventListener('click', function () {
            const amount = totalDebtBtn.getAttribute('data-amount');
            if (amount) {
                paymentAmountInput.value = amount;
                paymentAmountInput.focus();
            }
        });
    }
};
