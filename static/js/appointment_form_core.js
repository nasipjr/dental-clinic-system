/**
 * Dental Clinic Management System - Appointment Form JavaScript Controller
 * Handles procedure categories, quick procedure selection, custom procedure creation, and form validation.
 */

window.filterAppointmentCategory = function (category, pillBtn) {
    document.querySelectorAll('.procedure-cat-pill').forEach(btn => btn.classList.remove('active', 'btn-primary'));
    if (pillBtn) pillBtn.classList.add('active');

    const cards = document.querySelectorAll('.sub-proc-item-card');
    cards.forEach(card => {
        const itemCat = card.dataset.category || 'عام';
        if (category === 'all' || itemCat === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });

    const reasonSelect = document.getElementById('reason');
    if (reasonSelect) {
        Array.from(reasonSelect.options).forEach(opt => {
            if (opt.value === '' || opt.value === '__custom__') return;
            const optCat = opt.dataset.category || 'عام';
            if (category === 'all' || optCat === category) {
                opt.style.display = '';
            } else {
                opt.style.display = 'none';
            }
        });
    }
};

window.selectQuickProcedure = function (procName, duration, price, cardEl) {
    document.querySelectorAll('.procedure-quick-card').forEach(c => {
        c.classList.remove('selected-card');
        c.style.background = '';
        c.style.borderColor = '';
    });
    if (cardEl) {
        cardEl.classList.add('selected-card');
    }

    const reasonSelect = document.getElementById('reason');
    if (reasonSelect) {
        reasonSelect.value = procName;
        window.handleReasonChange(reasonSelect);
    }
};

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

                    if (!existingOpt) {
                        const newOpt = document.createElement('option');
                        newOpt.value = sName;
                        newOpt.setAttribute('data-category', sCat);
                        newOpt.setAttribute('data-duration', sDur);
                        newOpt.setAttribute('data-price', sPrice);
                        newOpt.textContent = `${sName} (${sDur} ${isAr ? 'دقيقة' : 'min'})`;

                        const customOpt = reasonSelect.querySelector('option[value="__custom__"]');
                        if (customOpt) {
                            reasonSelect.insertBefore(newOpt, customOpt);
                        } else {
                            reasonSelect.appendChild(newOpt);
                        }
                    }
                    reasonSelect.value = sName;
                    window.handleReasonChange(reasonSelect);
                }

                const cardsGrid = document.getElementById('sub-procedure-cards-container');
                if (cardsGrid) {
                    let existingCard = null;
                    try {
                        existingCard = cardsGrid.querySelector(`.sub-proc-item-card[data-proc-name="${CSS.escape(sName)}"]`);
                    } catch (e) {
                        existingCard = cardsGrid.querySelector(`.sub-proc-item-card[data-proc-name="${sName}"]`);
                    }

                    if (!existingCard) {
                        const colDiv = document.createElement('div');
                        colDiv.className = 'col-md-6 sub-proc-item-card';
                        colDiv.setAttribute('data-category', sCat);
                        colDiv.setAttribute('data-proc-name', sName);
                        colDiv.setAttribute('data-duration', sDur);
                        colDiv.setAttribute('data-price', sPrice);

                        const priceFormatted = Number(sPrice).toLocaleString();
                        const currencyLabel = isAr ? 'ل.س' : 'SP';

                        colDiv.innerHTML = `
                        <div class="procedure-quick-card cursor-pointer d-flex justify-content-between align-items-center h-100" onclick="selectQuickProcedure('${sName}', '${sDur}', '${sPrice}', this)">
                            <div>
                                <span class="fw-bold d-block proc-title mb-1">${sName}</span>
                                <span class="badge duration-badge">
                                    <i class="bi bi-clock me-1"></i>${sDur} ${isAr ? 'دقيقة' : 'min'}
                                </span>
                            </div>
                            <span class="badge price-badge ms-2">
                                ${priceFormatted} ${currencyLabel}
                            </span>
                        </div>
                    `;
                        cardsGrid.appendChild(colDiv);
                        existingCard = colDiv;
                    }

                    const cardInner = existingCard.querySelector('.procedure-quick-card');
                    if (cardInner) {
                        window.selectQuickProcedure(sName, sDur, sPrice, cardInner);
                    }

                    let matchingPill = null;
                    try {
                        matchingPill = document.querySelector(`.procedure-cat-pill[data-cat="${CSS.escape(sCat)}"]`);
                    } catch (e) {
                        matchingPill = document.querySelector(`.procedure-cat-pill[data-cat="${sCat}"]`);
                    }
                    if (matchingPill) {
                        window.filterAppointmentCategory(sCat, matchingPill);
                    }
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
            console.error(err);
            if (typeof Swal !== 'undefined') {
                Swal.fire({ icon: 'error', title: isAr ? 'خطأ' : 'Error', text: isAr ? 'فشل الاتصال بالخادم' : 'Server error' });
            }
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
            let matchingCardWrapper = null;
            try {
                matchingCardWrapper = document.querySelector(`.sub-proc-item-card[data-proc-name="${CSS.escape(val)}"]`);
            } catch (e) {
                matchingCardWrapper = document.querySelector(`.sub-proc-item-card[data-proc-name="${val}"]`);
            }

            if (matchingCardWrapper) {
                const cardInner = matchingCardWrapper.querySelector('.procedure-quick-card');
                if (cardInner) {
                    document.querySelectorAll('.procedure-quick-card').forEach(c => c.classList.remove('selected-card'));
                    cardInner.classList.add('selected-card');
                }

                const cat = matchingCardWrapper.dataset.category || 'all';

                let matchingPill = null;
                try {
                    matchingPill = document.querySelector(`.procedure-cat-pill[data-cat="${CSS.escape(cat)}"]`);
                } catch (e) {
                    matchingPill = document.querySelector(`.procedure-cat-pill[data-cat="${cat}"]`);
                }

                if (matchingPill) {
                    window.filterAppointmentCategory(cat, matchingPill);
                }

                setTimeout(() => {
                    matchingCardWrapper.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 150);
            } else {
                const customReasonInput = document.getElementById('custom_reason');
                if (customReasonInput && !customReasonInput.value) {
                    customReasonInput.value = val;
                }
                window.toggleCustomReasonInput(true);
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
                        text: isAr ? 'يرجى النقر على أحد الإجراءات الطبية المتاحة أو كتابة إجراء نصي مخصص أولاً.' : 'Please click on a procedure card or enter a custom procedure first.',
                        confirmButtonColor: '#0ea5e9',
                        background: '#1e293b',
                        color: '#f8fafc'
                    });
                } else {
                    alert(isAr ? 'يرجى اختيار سبب المعالجة الطبية' : 'Please Select Procedure Reason');
                }
                const subProcContainer = document.getElementById('sub-procedure-cards-container');
                if (subProcContainer) subProcContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }
};
