/**
 * Dental Clinic Management System - Invoice Creation Core Controller
 * Real-time row calculations, categorized procedure generation, discount & additional charges, and payment status detection.
 */

window.initInvoiceAdd = function (config) {
    const treatmentPrices = config.treatmentPrices || {};
    const treatmentDetails = config.treatmentDetails || {};
    const currencySymbol = config.currencySymbol || '';
    const isAr = config.isArabic !== undefined ? config.isArabic : (document.documentElement.lang === 'ar' || document.dir === 'rtl');

    const itemsBody = document.getElementById("invoice-items-body");
    const addItemButton = document.getElementById("add-item-btn");
    const clearChargesBtn = document.getElementById("btn-clear-charges");
    const invoiceTotalElement = document.getElementById("invoice-total");
    const invoiceSubtotalElement = document.getElementById("invoice-subtotal");
    const discountInput = document.getElementById("invoice-discount-input");
    const discountTypeSelect = document.getElementById("invoice-discount-type");
    const additionalChargesInput = document.getElementById("invoice-additional-charges-input");

    const paymentOption = document.getElementById("payment-option");
    const customPaymentBox = document.getElementById("custom-payment-box");
    const customPaymentAmount = document.getElementById("custom-payment-amount");
    const selectedPaymentDisplay = document.getElementById("selected-payment-display");
    const expectedStatusDisplay = document.getElementById("expected-status-display");

    const categories = [
        'فحص وتشخيص',
        'حشوات ومعالجات تجميلية',
        'علاج عصب وجذور',
        'جراحة وقلع',
        'تعويضات وتيجان',
        'تقويم أسنان',
        'أسنان أطفال',
        'إجراءات عامة وأخرى'
    ];

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

        let additionalCharges = Number(additionalChargesInput ? additionalChargesInput.value : 0);
        if (additionalCharges < 0) {
            additionalCharges = 0;
            if (additionalChargesInput) additionalChargesInput.value = 0;
        }

        const total = Math.max(0, subtotal - discountAmount + additionalCharges);

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

    function buildProcedureOptionsHtml() {
        let html = `<option value="">${isAr ? '-- اختر نوع الإجراء من القائمة --' : '-- Select Procedure --'}</option>`;

        categories.forEach(function (cat) {
            let catOptions = '';
            Object.keys(treatmentPrices).forEach(function (procName) {
                const price = Number(treatmentPrices[procName] || 0);
                const detail = treatmentDetails[procName] || {};
                const itemCat = detail.category || 'إجراءات عامة وأخرى';
                if (itemCat === cat) {
                    const formattedPrice = price.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                    catOptions += `<option value="${procName}" data-price="${price}">${procName} (${formattedPrice} ${currencySymbol})</option>`;
                }
            });
            if (catOptions) {
                html += `<optgroup label="── ${cat} ──">${catOptions}</optgroup>`;
            }
        });

        let otherOptions = '';
        Object.keys(treatmentPrices).forEach(function (procName) {
            const detail = treatmentDetails[procName] || {};
            const itemCat = detail.category || 'إجراءات عامة وأخرى';
            if (!categories.includes(itemCat)) {
                const price = Number(treatmentPrices[procName] || 0);
                const formattedPrice = price.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                otherOptions += `<option value="${procName}" data-price="${price}">${procName} (${formattedPrice} ${currencySymbol})</option>`;
            }
        });
        if (otherOptions) {
            html += `<optgroup label="── ${isAr ? 'إجراءات أخرى' : 'Other Procedures'} ──">${otherOptions}</optgroup>`;
        }

        return html;
    }

    function createItemRow() {
        const row = document.createElement("tr");
        row.className = "invoice-item-row";

        const procedureOptions = buildProcedureOptionsHtml();

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
                <input type="text" name="notes" class="form-control" placeholder="${isAr ? 'ملاحظات إضافية...' : 'Notes...'}">
            </td>
            <td>
                <span class="price-badge"><span class="item-price">0</span> ${currencySymbol}</span>
            </td>
            <td class="text-center">
                <button type="button" class="btn-delete-row-squircle remove-item-btn">
                    <i class="bi bi-trash"></i>
                    <span>${isAr ? 'حذف' : 'Delete'}</span>
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

    if (clearChargesBtn && additionalChargesInput) {
        clearChargesBtn.addEventListener("click", function () {
            additionalChargesInput.value = 0;
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
    if (additionalChargesInput) additionalChargesInput.addEventListener("input", calculateTotal);

    updateRemoveButtons();
    calculateTotal();
};
