/**
 * Dental Clinic Management System - Invoice Creation Core Controller
 * Real-time row calculations, dynamic item generation, discount handler, and payment status detection.
 */

window.initInvoiceAdd = function (config) {
    const treatmentPrices = config.treatmentPrices || {};
    const currencySymbol = config.currencySymbol || '';
    const isAr = config.isArabic !== undefined ? config.isArabic : (document.documentElement.lang === 'ar' || document.dir === 'rtl');

    const itemsBody = document.getElementById("invoice-items-body");
    const addItemButton = document.getElementById("add-item-btn");
    const invoiceTotalElement = document.getElementById("invoice-total");
    const invoiceSubtotalElement = document.getElementById("invoice-subtotal");
    const discountInput = document.getElementById("invoice-discount-input");
    const discountTypeSelect = document.getElementById("invoice-discount-type");

    const paymentOption = document.getElementById("payment-option");
    const customPaymentBox = document.getElementById("custom-payment-box");
    const customPaymentAmount = document.getElementById("custom-payment-amount");
    const selectedPaymentDisplay = document.getElementById("selected-payment-display");
    const expectedStatusDisplay = document.getElementById("expected-status-display");

    function getProcedurePrice(procedureType) {
        if (!procedureType || !treatmentPrices[procedureType]) {
            return 0;
        }
        return Number(treatmentPrices[procedureType]);
    }

    function updateRemoveButtons() {
        if (!itemsBody) return;
        const rows = itemsBody.querySelectorAll(".invoice-item-row");
        const removeButtons = itemsBody.querySelectorAll(".remove-item-btn");

        removeButtons.forEach(function (button) {
            button.disabled = rows.length <= 1;
        });
    }

    function calculateTotal() {
        if (!itemsBody) return;
        let subtotal = 0;
        const rows = itemsBody.querySelectorAll(".invoice-item-row");

        rows.forEach(function (row) {
            const procedureSelect = row.querySelector(".procedure-select");
            const priceElement = row.querySelector(".item-price");
            const price = getProcedurePrice(procedureSelect ? procedureSelect.value : "");

            if (priceElement) {
                priceElement.textContent = price.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
            }
            subtotal += price;
        });

        if (invoiceSubtotalElement) {
            invoiceSubtotalElement.textContent = subtotal.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
        }

        let discount = Number(discountInput ? discountInput.value : 0);
        let discountType = discountTypeSelect ? discountTypeSelect.value : "value";
        if (discount < 0) {
            discount = 0;
            if (discountInput) discountInput.value = 0;
        }

        let discountAmount = 0;
        if (discountType === "percentage") {
            if (discount > 100) {
                discount = 100;
                if (discountInput) discountInput.value = 100;
            }
            discountAmount = (subtotal * discount) / 100;
        } else {
            if (discount > subtotal) {
                discount = subtotal;
                if (discountInput) discountInput.value = subtotal;
            }
            discountAmount = discount;
        }

        const total = Math.max(0, subtotal - discountAmount);

        if (invoiceTotalElement) {
            invoiceTotalElement.textContent = total.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
        }
        updatePaymentDisplay();
    }

    function updatePaymentDisplay() {
        if (!invoiceTotalElement || !paymentOption) return;
        const total = Number(invoiceTotalElement.textContent.replace(/\./g, '') || 0);
        const option = paymentOption.value;

        let selectedPayment = 0;
        let statusText = isAr ? "غير مسددة" : "Unpaid";
        let statusClass = "due-badge";

        if (option === "full_price") {
            selectedPayment = total;
            if (total > 0) {
                statusText = isAr ? "مسددة بالكامل" : "Paid";
                statusClass = "paid-badge";
            }
        } else if (option === "custom_amount") {
            if (customPaymentBox) customPaymentBox.style.display = "block";
            selectedPayment = Number(customPaymentAmount ? customPaymentAmount.value : 0);

            if (selectedPayment <= 0) {
                statusText = isAr ? "غير مسددة" : "Unpaid";
                statusClass = "due-badge";
            } else if (selectedPayment < total) {
                statusText = isAr ? "مسددة جزئياً" : "Partial";
                statusClass = "due-badge";
            } else if (selectedPayment === total) {
                statusText = isAr ? "مسددة بالكامل" : "Paid";
                statusClass = "paid-badge";
            } else {
                statusText = isAr ? "مبلغ زائد" : "Too High";
                statusClass = "due-badge";
            }
        } else {
            if (customPaymentBox) customPaymentBox.style.display = "none";
            if (customPaymentAmount) customPaymentAmount.value = "";
            selectedPayment = 0;
            statusText = isAr ? "غير مسددة" : "Unpaid";
            statusClass = "due-badge";
        }

        if (selectedPaymentDisplay) {
            selectedPaymentDisplay.textContent = selectedPayment.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
        }

        if (expectedStatusDisplay) {
            expectedStatusDisplay.textContent = statusText;
            expectedStatusDisplay.className = statusClass;
        }
    }

    function createItemRow() {
        const row = document.createElement("tr");
        row.className = "invoice-item-row";

        let procedureOptions = `<option value="">${isAr ? '-- اختر الإجراء --' : 'Select procedure'}</option>`;
        Object.keys(treatmentPrices).forEach(function (procedureType) {
            procedureOptions += `<option value="${procedureType}">${procedureType}</option>`;
        });

        row.innerHTML = `
            <td>
                <select name="procedure_type" class="form-select procedure-select" required>
                    ${procedureOptions}
                </select>
            </td>
            <td>
                <input type="text" name="tooth_number" class="form-control" placeholder="${isAr ? 'رقم السن (اختياري)' : 'Tooth number'}">
            </td>
            <td>
                <input type="text" name="notes" class="form-control" placeholder="${isAr ? 'ملاحظات إضافية' : 'Notes'}">
            </td>
            <td>
                <span class="price-badge"><span class="item-price">0</span> ${currencySymbol}</span>
            </td>
            <td class="text-center">
                <button type="button" class="btn btn-outline-danger btn-sm remove-item-btn">
                    <i class="bi bi-trash me-1"></i>${isAr ? 'حذف' : 'Remove'}
                </button>
            </td>
        `;
        return row;
    }

    if (addItemButton && itemsBody) {
        addItemButton.addEventListener("click", function () {
            const newRow = createItemRow();
            itemsBody.appendChild(newRow);
            updateRemoveButtons();
            calculateTotal();
        });
    }

    if (itemsBody) {
        itemsBody.addEventListener("change", function (event) {
            if (event.target.classList.contains("procedure-select")) {
                calculateTotal();
            }
        });

        itemsBody.addEventListener("click", function (event) {
            if (event.target.closest(".remove-item-btn")) {
                event.target.closest(".invoice-item-row").remove();
                updateRemoveButtons();
                calculateTotal();
            }
        });
    }

    if (paymentOption) paymentOption.addEventListener("change", updatePaymentDisplay);
    if (customPaymentAmount) customPaymentAmount.addEventListener("input", updatePaymentDisplay);
    if (discountInput) discountInput.addEventListener("input", calculateTotal);
    if (discountTypeSelect) discountTypeSelect.addEventListener("change", calculateTotal);

    updateRemoveButtons();
    calculateTotal();
};
