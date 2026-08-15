/**
 * Dental Clinic Management System - Invoice Details JavaScript Controller
 * Isolated client-side logic for QR code generation, AJAX discounts/charges/notes updates, and instant invoice saving.
 */

window.initInvoiceDetail = function (config) {
    const clinicName = config.clinicName || '';
    const issueDateISO = config.issueDateISO || '';
    const totalAmount = config.totalAmount || '0';
    const invoiceNum = config.invoiceNum || '';
    const currencySymbol = config.currencySymbol || 'SP';
    const invoicesListUrl = config.invoicesListUrl || '/invoices';
    const isArabic = config.isArabic !== undefined ? config.isArabic : (document.documentElement.getAttribute('lang') === 'ar' || document.dir === 'rtl');

    // ── 1. QR Code Rendering ────────────────────────────────────────────────
    try {
        const qrValue = `Clinic: ${clinicName}\nInvoice: ${invoiceNum}\nDate: ${issueDateISO}\nTotal: ${totalAmount} ${currencySymbol}`;

        const canvasScreen = document.getElementById("invoice-qrcode");
        if (canvasScreen && typeof QRious !== 'undefined') {
            new QRious({ element: canvasScreen, value: qrValue, size: 150 });
        }

        const canvasPrint = document.getElementById("print-invoice-qrcode");
        if (canvasPrint && typeof QRious !== 'undefined') {
            new QRious({ element: canvasPrint, value: qrValue, size: 150 });
        }
    } catch (e) {
        console.warn("QR Code render skipped:", e);
    }

    // ── 2. DOM Updater Helper ───────────────────────────────────────────────
    function updateInvoiceDOM(data) {
        // 1. Discount amount badge
        const discBadge = document.getElementById('discount-amount-badge');
        if (discBadge) {
            discBadge.textContent = `- ${data.discount_amount_formatted} ${data.currency}`;
        }

        // 2. Discount row label
        const discLabel = document.getElementById('discount-row-label');
        if (discLabel) {
            let labelText = isArabic ? 'الخصم' : 'Discount';
            if (data.discount_label) {
                labelText += ` ${data.discount_label}`;
            }
            discLabel.textContent = labelText;
        }

        // 3. Additional charges amount badge
        const chargesBadge = document.getElementById('charges-amount-badge');
        if (chargesBadge) {
            chargesBadge.textContent = `+ ${data.additional_charges_amount_formatted} ${data.currency}`;
        }

        // 4. Bottom invoice total
        const bottomTotal = document.getElementById('bottom-invoice-total');
        if (bottomTotal) {
            bottomTotal.textContent = `${data.total_amount_formatted} ${data.currency}`;
        }

        // 5. Top invoice total
        const topTotal = document.getElementById('top-invoice-total');
        if (topTotal) {
            topTotal.textContent = `${data.total_amount_formatted} ${data.currency}`;
        }

        // 6. Top total paid
        const topPaid = document.getElementById('top-total-paid');
        if (topPaid) {
            topPaid.textContent = `${data.total_paid_formatted} ${data.currency}`;
        }

        // 7. Top outstanding / credit container
        const topOut = document.getElementById('top-outstanding-container');
        if (topOut) {
            if (data.credit > 0) {
                topOut.innerHTML = `<span class="credit-amount">${data.credit_formatted} ${data.currency} <span class="credit-badge">${isArabic ? 'رصيد' : 'Credit'}</span></span>`;
            } else if (data.outstanding_amount > 0) {
                topOut.innerHTML = `<span class="remaining-due">${data.outstanding_amount_formatted} ${data.currency} <span class="due-badge">${isArabic ? 'مستحق' : 'Due'}</span></span>`;
            } else {
                topOut.innerHTML = `<span class="remaining-clear">0 ${data.currency} <span class="paid-badge">${isArabic ? 'خالص' : 'Paid'}</span></span>`;
            }
        }

        // 8. Top invoice status container
        const topStatus = document.getElementById('top-status-container');
        if (topStatus) {
            if (data.status === 'Credit') {
                topStatus.innerHTML = `<span class="credit-badge">${isArabic ? 'رصيد مالي' : 'Credit'}</span>`;
            } else if (data.status === 'Paid') {
                topStatus.innerHTML = `<span class="paid-badge">${isArabic ? 'مدفوعة بالكامل' : 'Paid'}</span>`;
            } else if (data.status === 'Partially Paid') {
                topStatus.innerHTML = `<span class="due-badge">${isArabic ? 'دفعة جزئية' : 'Partial'}</span>`;
            } else {
                topStatus.innerHTML = `<span class="due-badge">${isArabic ? 'غير مدفوعة' : 'Unpaid'}</span>`;
            }
        }

        // 9. Invoice Notes
        const notesText = document.getElementById('invoice-notes-text');
        if (notesText) {
            notesText.textContent = data.notes || (isArabic ? 'لا توجد ملاحظات' : 'No notes');
        }
        const topNotes = document.getElementById('top-invoice-notes');
        if (topNotes) {
            if (data.notes) {
                topNotes.innerHTML = data.notes.replace(/\n/g, '<br>');
            } else {
                topNotes.innerHTML = `<span class="text-muted italic">${isArabic ? 'لا توجد ملاحظات' : 'No notes available'}</span>`;
            }
        }
        const printNotesSec = document.getElementById('print-notes-section');
        const printNotesTxt = document.getElementById('print-notes-text');
        if (printNotesSec && printNotesTxt) {
            if (data.notes) {
                printNotesTxt.textContent = data.notes;
                printNotesSec.classList.remove('d-none');
            } else {
                printNotesSec.classList.add('d-none');
            }
        }
    }

    // ── 3. Notification Helpers ─────────────────────────────────────────────
    function showWarningNotification(msg) {
        const titleText = isArabic ? 'تنبيـه' : 'Warning';
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'warning',
                title: titleText,
                text: msg || (isArabic ? 'تعذر حفظ الفاتورة.' : 'Failed to update invoice.'),
                confirmButtonText: isArabic ? 'موافق' : 'OK',
                confirmButtonColor: '#38bdf8',
                background: '#1e293b',
                color: '#ffffff',
                customClass: {
                    popup: 'rounded-4 shadow-lg border border-secondary-subtle'
                }
            });
        } else {
            alert(msg || 'Error updating invoice');
        }
    }

    function showSaveSuccessNotification(msg) {
        const titleText = isArabic ? 'تم حفظ الفاتورة بنجاح!' : 'Invoice Saved Successfully!';
        const bodyText = msg || (isArabic ? 'تمت معالجة وتثبيت كافة بيانات الفاتورة بنجاح في النظام.' : 'Invoice data updated and saved.');

        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: titleText,
                text: bodyText,
                timer: 2000,
                timerProgressBar: true,
                showConfirmButton: false,
                toast: true,
                position: 'top-end',
                background: '#1e293b',
                color: '#ffffff'
            });
        } else {
            alert(titleText + '\n' + bodyText);
        }
    }

    // ── 4. Save Invoice Main Button Handler -> Save & Redirect ─────────────
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('#btn-save-invoice');
        if (!btn) return;

        e.preventDefault();
        const origHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> <span>${isArabic ? 'جاري الحفظ...' : 'Saving...'}</span>`;

        const openForms = document.querySelectorAll('.collapse.show form');
        const fetchPromises = [];

        if (openForms.length > 0) {
            openForms.forEach(f => {
                fetchPromises.push(
                    fetch(f.action, {
                        method: 'POST',
                        body: new FormData(f),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'Accept': 'application/json'
                        }
                    }).then(res => res.json())
                );
            });
        }

        Promise.all(fetchPromises).then(results => {
            let hasError = false;
            let errorMsg = '';
            results.forEach(res => {
                if (res && res.success === false) {
                    hasError = true;
                    errorMsg = res.message;
                }
            });
            if (hasError) {
                btn.disabled = false;
                btn.innerHTML = origHtml;
                showWarningNotification(errorMsg);
            } else {
                showSaveSuccessNotification(isArabic ? 'تم حفظ التعديلات والانتقال إلى قائمة الفواتير...' : 'Saved successfully! Redirecting...');
                setTimeout(function () {
                    window.location.href = invoicesListUrl;
                }, 1200);
            }
        }).catch(err => {
            console.error(err);
            btn.disabled = false;
            btn.innerHTML = origHtml;
            showWarningNotification(isArabic ? 'حدث خطأ أثناء الاتصال بالسيرفر.' : 'Connection error.');
        });
    });

    // ── 5. AJAX Form Submit Listener ────────────────────────────────────────
    document.addEventListener('submit', function (e) {
        const form = e.target;
        if (!form || (form.id !== 'ajax-discount-form' && form.id !== 'ajax-charges-form' && form.id !== 'ajax-notes-form')) {
            return;
        }

        e.preventDefault();
        const collapseId = form.id === 'ajax-discount-form' ? 'edit-discount-form' : (form.id === 'ajax-charges-form' ? 'edit-additional-charges-form' : 'edit-notes-form');
        const submitBtn = form.querySelector('button[type="submit"]');
        const origHtml = submitBtn ? submitBtn.innerHTML : '';

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>';
        }

        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        })
            .then(res => res.json())
            .then(data => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = origHtml;
                }
                if (data.success) {
                    updateInvoiceDOM(data);
                    const collapseEl = document.getElementById(collapseId);
                    if (collapseEl && typeof bootstrap !== 'undefined') {
                        const bsCollapse = bootstrap.Collapse.getInstance(collapseEl) || new bootstrap.Collapse(collapseEl, { toggle: false });
                        bsCollapse.hide();
                    }
                    showSaveSuccessNotification(data.message);
                } else {
                    showWarningNotification(data.message);
                }
            })
            .catch(err => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = origHtml;
                }
                console.error(err);
                showWarningNotification(isArabic ? 'حدث خطأ أثناء حفظ البيانات.' : 'Error saving data.');
            });
    });
};
