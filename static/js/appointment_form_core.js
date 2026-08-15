/**
 * Dental Clinic Management System - Appointment Form JavaScript Controller
 * Handles standard procedure dropdown selection, custom unlisted procedure creation, and form validation.
 */

window.toggleCustomReasonInput = function (forceOpen = false) {
    const container = document.getElementById('custom_reason_container');
    const reasonSel = document.getElementById('reason');
    if (container) {
        if (forceOpen || container.style.display === 'none' || !container.style.display) {
            container.style.display = 'block';
            if (reasonSel) {
                reasonSel.value = '__custom__';
                window.handleReasonChange(reasonSel);
            }
            const input = document.getElementById('custom_reason');
            if (input) input.focus();
        } else {
            container.style.display = 'none';
        }
    }
};

window.onCustomDurationChange = function (input) {
    const apptDateInput = document.getElementById('appointment_date');
    if (apptDateInput && input.value) {
        apptDateInput.setAttribute('data-duration', input.value);
    }
};

window.handleReasonChange = function (selectEl) {
    const customContainer = document.getElementById('custom_reason_container');
    const customInput = document.getElementById('custom_reason');
    const apptDateInput = document.getElementById('appointment_date');
    const selectedOption = selectEl.options[selectEl.selectedIndex];

    if (selectEl.value === '__custom__') {
        if (customContainer) customContainer.style.display = 'block';
        if (customInput) customInput.setAttribute('required', 'required');
        if (apptDateInput) apptDateInput.setAttribute('data-duration', '30');
    } else {
        if (customContainer) customContainer.style.display = 'none';
        if (customInput) customInput.removeAttribute('required');
        if (selectedOption && selectedOption.dataset.duration && apptDateInput) {
            apptDateInput.setAttribute('data-duration', selectedOption.dataset.duration);
        }
    }
};

window.confirmCustomProcedureCard = function () {
    const isAr = document.documentElement.lang === 'ar' || document.dir === 'rtl';
    const customReasonInput = document.getElementById('custom_reason');
    const customCatInput = document.getElementById('custom_reason_category');
    const customDurInput = document.getElementById('custom_reason_duration');
    const customPriceInput = document.getElementById('custom_reason_price');
    const reasonSelect = document.getElementById('reason');

    const nameVal = customReasonInput ? customReasonInput.value.trim() : '';
    if (!nameVal) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'warning',
                title: isAr ? 'اسم الإجراء مطلوب' : 'Name Required',
                text: isAr ? 'يرجى كتابة اسم الإجراء النصي المخصص أولاً.' : 'Please enter the custom procedure name first.',
                confirmButtonColor: '#0ea5e9',
                background: '#1e293b',
                color: '#f8fafc'
            });
        } else {
            alert(isAr ? 'يرجى كتابة اسم الإجراء النصي المخصص أولاً.' : 'Please enter the custom procedure name first.');
        }
        if (customReasonInput) customReasonInput.focus();
        return;
    }

    const catVal = customCatInput ? customCatInput.value : 'إجراءات عامة وأخرى';
    const durVal = customDurInput ? customDurInput.value : '30';
    const priceVal = customPriceInput ? customPriceInput.value : '0';

    const csrfMeta = document.querySelector('meta[name="csrf-token"]') || document.querySelector('input[name="csrf_token"]');
    const csrfToken = csrfMeta ? (csrfMeta.getAttribute('content') || csrfMeta.value) : '';

    fetch('/treatments/types/quick-add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify({
            name: nameVal,
            category: catVal,
            duration: durVal,
            price: priceVal
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.service) {
                const sName = data.service.name;
                const sDur = data.service.duration;
                const sPrice = data.service.price;
                const sCat = data.service.category || catVal;

                if (reasonSelect) {
                    let existingOpt = null;
                    try {
                        existingOpt = reasonSelect.querySelector(`option[value="${CSS.escape(sName)}"]`);
                    } catch (e) {
                        existingOpt = reasonSelect.querySelector(`option[value="${sName}"]`);
                    }

                    const priceFormatted = Number(sPrice).toLocaleString();
                    const currencyLabel = isAr ? 'ل.س' : 'SP';

                    if (!existingOpt) {
                        const newOpt = document.createElement('option');
                        newOpt.value = sName;
                        newOpt.setAttribute('data-category', sCat);
                        newOpt.setAttribute('data-duration', sDur);
                        newOpt.setAttribute('data-price', sPrice);
                        newOpt.textContent = `${sName} (${priceFormatted} ${currencyLabel})`;

                        const matchingOptgroup = reasonSelect.querySelector(`optgroup[data-group-category="${sCat}"]`);
                        if (matchingOptgroup) {
                            matchingOptgroup.appendChild(newOpt);
                        } else {
                            const customOpt = reasonSelect.querySelector('option[value="__custom__"]');
                            if (customOpt) {
                                reasonSelect.insertBefore(newOpt, customOpt);
                            } else {
                                reasonSelect.appendChild(newOpt);
                            }
                        }
                    }
                    reasonSelect.value = sName;
                    window.handleReasonChange(reasonSelect);
                }

                const customContainer = document.getElementById('custom_reason_container');
                if (customContainer) customContainer.style.display = 'none';

                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        icon: 'success',
                        title: isAr ? 'تم حفظ وإدراج الإجراء بجدول خدمات العيادة بنجاح ✔️' : 'Service Added & Confirmed ✔️',
                        text: isAr ? `تمت إضافة "${sName}" وتصنيفه تحت (${sCat})` : `Added "${sName}" under (${sCat})`,
                        timer: 2000,
                        showConfirmButton: false,
                        background: '#1e293b',
                        color: '#f8fafc'
                    });
                }
            } else {
                if (typeof Swal !== 'undefined') {
                    Swal.fire({ icon: 'error', title: isAr ? 'خطأ' : 'Error', text: data.message || 'فشل في حفظ الخدمة' });
                } else {
                    alert(data.message || 'Error saving service');
                }
            }
        })
        .catch(err => {
            console.error('Quick Add Service Error:', err);
        });
};

window.initAppointmentForm = function (config) {
    const isAr = config.isArabic !== undefined ? config.isArabic : (document.documentElement.lang === 'ar' || document.dir === 'rtl');
    const reasonSel = document.getElementById('reason');

    if (reasonSel && reasonSel.value) {
        const val = reasonSel.value;
        if (val === '__custom__') {
            window.toggleCustomReasonInput(true);
        } else {
            let existingOpt = null;
            try {
                existingOpt = reasonSel.querySelector(`option[value="${CSS.escape(val)}"]`);
            } catch (e) {
                existingOpt = reasonSel.querySelector(`option[value="${val}"]`);
            }
            if (!existingOpt) {
                const customReasonInput = document.getElementById('custom_reason');
                if (customReasonInput && !customReasonInput.value) {
                    customReasonInput.value = val;
                }
                window.toggleCustomReasonInput(true);
            } else {
                window.handleReasonChange(reasonSel);
            }
        }
    }

    const form = document.getElementById('add-patient-form');
    if (form) {
        form.addEventListener('submit', function (e) {
            const reasonSelect = document.getElementById('reason');
            const customReasonInput = document.getElementById('custom_reason');
            const customContainer = document.getElementById('custom_reason_container');
            const isCustomActive = customContainer && customContainer.style.display !== 'none';

            let reasonVal = reasonSelect ? reasonSelect.value : '';
            let customVal = customReasonInput ? customReasonInput.value.trim() : '';

            if ((!reasonVal || reasonVal === '') && (!isCustomActive || !customVal)) {
                e.preventDefault();
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        icon: 'warning',
                        title: isAr ? 'يرجى اختيار سبب المعالجة الطبية' : 'Please Select Procedure Reason',
                        text: isAr ? 'يرجى اختيار أحد الإجراءات الطبية من القائمة المنسدلة أو كتابة إجراء نصي مخصص أولاً.' : 'Please select a procedure from the list or enter a custom procedure first.',
                        confirmButtonColor: '#0ea5e9',
                        background: '#1e293b',
                        color: '#f8fafc'
                    });
                } else {
                    alert(isAr ? 'يرجى اختيار سبب المعالجة الطبية' : 'Please Select Procedure Reason');
                }
                if (reasonSelect) reasonSelect.focus();
            }
        });
    }
};
