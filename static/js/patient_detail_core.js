/**
 * Dental Clinic MS - Patient Detail Core Script
 * Modularized interactive logic for tabs, odontogram modals, and X-ray studio.
 */

window.openEditToothHistoryModal = function(patientId, historyId, procedure, notes, historyDate, appointmentId) {
    const modalEl = document.getElementById('editToothHistoryModal');
    if (!modalEl) return;
    const form = document.getElementById('editToothHistoryForm');
    if (form) form.action = `/patients/${patientId}/tooth-history/${historyId}/edit`;

    const procSelect = document.getElementById('edit-history-procedure-type');
    if (procSelect) {
        let found = false;
        for (let opt of procSelect.options) {
            if (opt.value === procedure) {
                opt.selected = true;
                found = true;
                break;
            }
        }
        if (!found) {
            const cleanProc = procedure.replace(/\s*\([^)]*\)/, '').trim();
            for (let opt of procSelect.options) {
                if (opt.value.includes(cleanProc)) {
                    opt.selected = true;
                    found = true;
                    break;
                }
            }
        }
        if (!found && procedure) {
            const opt = new Option(procedure, procedure, true, true);
            procSelect.add(opt);
        }
    }

    const notesInp = document.getElementById('edit-history-notes');
    if (notesInp) notesInp.value = notes || '';

    const dateInp = document.getElementById('edit-history-date');
    if (dateInp) dateInp.value = historyDate || '';

    const apptInp = document.getElementById('edit-history-appointment-id');
    if (apptInp) apptInp.value = appointmentId || '';

    const bsModal = new bootstrap.Modal(modalEl);
    bsModal.show();
};

window.updatePatientPlanDefaultCost = function(selectEl) {
    if (!selectEl) return;
    const opt = selectEl.options[selectEl.selectedIndex];
    const costInput = document.getElementById('p-plan-estimated-cost');
    if (opt && opt.dataset.price && costInput) {
        costInput.value = opt.dataset.price;
    }
};

window.initPatientDetail = function(config) {
    const isAr = config.isAr;
    const currency = config.currency;
    const patientId = config.patientId;
    const patientTreatments = config.patientTreatments || [];
    const toothHistoryDict = config.toothHistoryDict || {};
    const plannedTeethDict = config.plannedTeethDict || {};
    const patientImages = config.patientImages || [];

    const fdiMap = {
        '1': '18', '2': '17', '3': '16', '4': '15', '5': '14', '6': '13', '7': '12', '8': '11',
        '9': '21', '10': '22', '11': '23', '12': '24', '13': '25', '14': '26', '15': '27', '16': '28',
        '17': '38', '18': '37', '19': '36', '20': '35', '21': '34', '22': '33', '23': '32', '24': '31',
        '25': '41', '26': '42', '27': '43', '28': '44', '29': '45', '30': '46', '31': '47', '32': '48'
    };

    // Keep active tab on refresh
    const tabEl = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabEl.forEach(function(el) {
        el.addEventListener('shown.bs.tab', function(event) {
            const targetAttr = event.target.getAttribute('data-bs-target');
            if (targetAttr) {
                const targetId = targetAttr.replace('#', '').replace('-tab', '');
                const url = new URL(window.location.href);
                url.searchParams.set('tab', targetId);
                window.history.replaceState(null, '', url.toString());
            }
        });
    });

    function appliesToTooth(treatment, toothNum) {
        if (!treatment.tooth) return false;
        const toothStr = treatment.tooth.trim();
        if (toothStr === '11-48' || toothStr === '1-32' || toothStr.toLowerCase() === 'all' || toothStr === 'كافة الأسنان' || toothStr === 'الكل') {
            return true;
        }
        const teeth = toothStr.split(',').map(s => s.trim());
        const fdiNum = fdiMap[toothNum];
        if (fdiNum && teeth.includes(fdiNum)) return true;
        const fdiRegex = /^(1[1-8]|2[1-8]|3[1-8]|4[1-8]|5[1-5]|6[1-5]|7[1-5]|8[1-5])$/;
        return teeth.some(t => !fdiRegex.test(t) && t === toothNum);
    }

    function isExtractionProcedure(procName) {
        if (!procName) return false;
        const name = procName.toLowerCase();
        if (name.includes('ما بعد القلع') || name.includes('post-extraction')) return false;
        return name.includes('قلع') || name.includes('extract');
    }

    function getToothItemsFromDict(dict, toothStr, fdiNum) {
        if (!dict) return [];
        const fdiRegex = /^(1[1-8]|2[1-8]|3[1-8]|4[1-8]|5[1-5]|6[1-5]|7[1-5]|8[1-5])$/;
        const results = [];
        const seenIds = new Set();

        if (fdiNum && dict[fdiNum]) {
            dict[fdiNum].forEach(item => {
                if (!seenIds.has(item.id)) {
                    seenIds.add(item.id);
                    results.push(item);
                }
            });
        }

        if (toothStr && dict[toothStr] && !fdiRegex.test(toothStr)) {
            dict[toothStr].forEach(item => {
                if (!seenIds.has(item.id)) {
                    seenIds.add(item.id);
                    results.push(item);
                }
            });
        }

        return results;
    }

    const patientTeethData = {};

    for (let i = 1; i <= 32; i++) {
        const toothStr = i.toString();
        const fdiNum = fdiMap[toothStr];
        patientTeethData[toothStr] = patientTreatments.filter(t => appliesToTooth(t, toothStr));
        
        const priorHistories = getToothItemsFromDict(toothHistoryDict, toothStr, fdiNum);
        const plannedItems = getToothItemsFromDict(plannedTeethDict, toothStr, fdiNum);

        const isClinicExtracted = patientTeethData[toothStr].some(t => isExtractionProcedure(t.procedure));
        const isPriorExtracted = priorHistories.some(h => isExtractionProcedure(h.procedure));
        const isExtracted = isClinicExtracted || isPriorExtracted;

        const teethElements = document.querySelectorAll(`[data-patient-tooth="${toothStr}"]`);
        teethElements.forEach(el => {
            if (isExtracted) {
                el.classList.add('extracted-treatment', 'extracted');
                const svgContainer = el.querySelector('.tooth-svg-container') || el;
                if (!svgContainer.querySelector('.extracted-badge')) {
                    const badge = document.createElement('div');
                    badge.className = 'extracted-badge';
                    badge.innerHTML = '<i class="bi bi-x-lg"></i>';
                    svgContainer.appendChild(badge);
                }
            } else if (patientTeethData[toothStr].length > 0) {
                el.classList.add('history-treatment', 'history');
            } else {
                el.classList.add('no-treatment');
            }

            if (priorHistories.length > 0) {
                el.classList.add('history-external');
                const svgContainer = el.querySelector('.tooth-svg-container') || el;
                if (!svgContainer.querySelector('.prior-history-indicator')) {
                    const starDot = document.createElement('span');
                    starDot.className = 'prior-history-indicator';
                    starDot.title = isAr ? 'سوابق مرضية وخارجية' : 'Pre-existing Condition';
                    starDot.innerHTML = '<i class="bi bi-star-fill"></i>';
                    svgContainer.appendChild(starDot);
                }
            }

            if (plannedItems.length > 0) {
                el.classList.add('has-plan-treatment');
                const svgContainer = el.querySelector('.tooth-svg-container') || el;
                if (!svgContainer.querySelector('.plan-golden-indicator')) {
                    const starEl = document.createElement('span');
                    starEl.className = 'plan-golden-indicator';
                    starEl.title = isAr ? 'توجد خطة علاج مستقبلية مقترحة لهذا السن ⭐️' : 'Future Treatment Plan ⭐️';
                    starEl.innerHTML = '<i class="bi bi-star-fill"></i>';
                    svgContainer.appendChild(starEl);
                }
            }

            // Tooltip builder
            let tooltipHtml = `<strong class="d-block mb-1">${isAr ? 'السن' : 'Tooth'} ${fdiMap[toothStr]} (${isAr ? 'أميركي' : 'Univ'} ${toothStr})</strong>`;
            if (isExtracted) {
                tooltipHtml += `<div class="text-danger small fw-bold mb-1"><i class="bi bi-x-circle-fill me-1"></i>${isAr ? 'تم قلع السن (سابق/عيادة) ❌' : 'Tooth Extracted ❌'}</div>`;
            }
            if (priorHistories.length > 0) {
                tooltipHtml += `<div class="text-purple small mt-1" style="color:#c084fc;"><i class="bi bi-journal-medical me-1"></i>${isAr ? 'السوابق المرضية:' : 'Pre-existing History:'}</div>`;
                priorHistories.forEach(h => {
                    tooltipHtml += `<div class="ms-2 small text-nowrap" style="color:#e9d5ff;">• 🟣 ${h.procedure}</div>`;
                });
            }
            if (patientTeethData[toothStr].length > 0) {
                tooltipHtml += `<div class="text-info small mt-1"><i class="bi bi-clock-history me-1"></i>${isAr ? 'معالجات العيادة:' : 'Clinic Treatments:'}</div>`;
                patientTeethData[toothStr].forEach(t => {
                    tooltipHtml += `<div class="ms-2 small text-nowrap">• ${t.procedure} (${t.date})</div>`;
                });
            }
            if (plannedItems.length > 0) {
                tooltipHtml += `<div class="text-warning small mt-1"><i class="bi bi-calendar2-check me-1"></i>${isAr ? 'خطة علاج مستقبلية:' : 'Treatment Plan:'}</div>`;
                plannedItems.forEach(p => {
                    tooltipHtml += `<div class="ms-2 small text-nowrap" style="color:#fde047;">• 🟡 ${p.procedure}</div>`;
                });
            }
            if (priorHistories.length === 0 && patientTeethData[toothStr].length === 0 && plannedItems.length === 0) {
                tooltipHtml += `<div class="text-muted small">${isAr ? 'سليم / لا يوجد معالجات' : 'Healthy / No treatments'}</div>`;
            }

            el.setAttribute('data-bs-toggle', 'tooltip');
            el.setAttribute('data-bs-html', 'true');
            el.setAttribute('data-bs-title', tooltipHtml);
        });
    }

    // Toggle inline form for adding prior condition
    const toggleBtn = document.getElementById('toggle-add-history-btn');
    const formContainer = document.getElementById('add-history-form-container');
    if (toggleBtn && formContainer) {
        toggleBtn.addEventListener('click', function() {
            formContainer.classList.toggle('d-none');
        });
    }

    // Toggle inline form for adding plan in patient detail
    const pTogglePlanBtn = document.getElementById('p-toggle-add-plan-btn');
    const pPlanFormContainer = document.getElementById('p-add-plan-form-container');
    if (pTogglePlanBtn && pPlanFormContainer) {
        pTogglePlanBtn.addEventListener('click', function() {
            pPlanFormContainer.classList.toggle('d-none');
        });
    }

    // Handle Patient Tooth Click
    document.querySelectorAll('[data-patient-tooth]').forEach(el => {
        el.addEventListener('click', function() {
            const toothNum = this.dataset.patientTooth;
            const fdiNum = fdiMap[toothNum];

            const formToothInput = document.getElementById('history-form-tooth-number');
            if (formToothInput) formToothInput.value = fdiNum || toothNum;
            
            const pPlanToothInput = document.getElementById('p-plan-form-tooth-number');
            if (pPlanToothInput) pPlanToothInput.value = fdiNum || toothNum;
            
            const modalTitle = document.getElementById('patientToothModalLabel');
            if (modalTitle) {
                modalTitle.textContent = `${isAr ? 'تفاصيل وسجل المعالجات للسن' : 'Tooth Details & Documentation'} ${fdiNum}`;
            }

            const priorHistories = getToothItemsFromDict(toothHistoryDict, toothNum, fdiNum);
            const plannedItems = getToothItemsFromDict(plannedTeethDict, toothNum, fdiNum);

            const clinicTreatments = patientTeethData[toothNum] || [];
            const isClinicExtracted = clinicTreatments.some(t => isExtractionProcedure(t.procedure));
            const isPriorExtracted = priorHistories.some(h => isExtractionProcedure(h.procedure));
            const isExtracted = isClinicExtracted || isPriorExtracted;

            const statusBadge = document.getElementById('patient-tooth-status-badge');
            if (statusBadge) {
                if (isPriorExtracted) {
                    statusBadge.innerHTML = `<div class="alert alert-danger no-auto-icon py-3 px-3 mb-0 rounded-3 small d-flex align-items-center gap-3 shadow-xs border border-danger-subtle"><i class="bi bi-x-circle-fill fs-4 text-danger flex-shrink-0"></i><div><strong class="d-block mb-0.5 fs-6">${isAr ? 'تم قلع هذا السن سابقاً ❌' : 'Tooth Extracted Previously ❌'}</strong><span class="opacity-85">${isAr ? 'السن مقلوع سابقاً. لا يمكن إضافة معالجات سوى معالجة ما بعد القلع.' : 'Tooth was extracted previously. Only post-extraction care can be added.'}</span></div></div>`;
                } else if (isClinicExtracted) {
                    statusBadge.innerHTML = `<div class="alert alert-danger no-auto-icon py-3 px-3 mb-0 rounded-3 small d-flex align-items-center gap-3 shadow-xs border border-danger-subtle"><i class="bi bi-x-circle-fill fs-4 text-danger flex-shrink-0"></i><div><strong class="d-block mb-0.5 fs-6">${isAr ? 'تم قلع هذا السن في العيادة ❌' : 'Tooth Extracted in Clinic ❌'}</strong><span class="opacity-85">${isAr ? 'تم قلع السن بداخل العيادة. لا يمكن إضافة معالجات سوى معالجة ما بعد القلع.' : 'Tooth was extracted in clinic. Only post-extraction care can be added.'}</span></div></div>`;
                } else if (priorHistories.length > 0) {
                    statusBadge.innerHTML = `<div class="alert alert-purple no-auto-icon py-3 px-3 mb-0 rounded-3 small d-flex align-items-center gap-3 shadow-xs badge-history-external"><i class="bi bi-journal-medical fs-4 flex-shrink-0" style="color: #c084fc;"></i><div><strong class="d-block mb-0.5 fs-6" style="color: #c084fc;">${isAr ? 'سن يحتوي على سوابق مرضية 🟣' : 'Pre-existing Condition Recorded 🟣'}</strong><span class="opacity-85">${isAr ? 'مسجل عليه إجراءات توثيقية سابقة.' : 'Contains pre-existing recorded conditions.'}</span></div></div>`;
                } else if (clinicTreatments.length > 0) {
                    statusBadge.innerHTML = `<div class="alert alert-info no-auto-icon py-3 px-3 mb-0 rounded-3 small d-flex align-items-center gap-3 shadow-xs border border-info-subtle"><i class="bi bi-info-circle-fill fs-4 text-info flex-shrink-0"></i><div><strong class="d-block mb-0.5 fs-6">${isAr ? 'سن مُعالج في العيادة 🩺' : 'Clinic Treated Tooth 🩺'}</strong><span class="opacity-85">${isAr ? 'توجد إجراءات سابقة مسجلة لهذا السن في العيادة.' : 'Previous recorded procedures in clinic.'}</span></div></div>`;
                } else {
                    statusBadge.innerHTML = `<div class="alert alert-success no-auto-icon py-3 px-3 mb-0 rounded-3 small d-flex align-items-center gap-3 shadow-xs border border-success-subtle"><i class="bi bi-check-circle-fill fs-4 text-success flex-shrink-0"></i><div><strong class="d-block mb-0.5 fs-6">${isAr ? 'سن سليم ✨' : 'Healthy Tooth ✨'}</strong><span class="opacity-85">${isAr ? 'لا يوجد أي إجراءات علاجية سابقة مُسجلة لهذا السن.' : 'No previous treatments recorded for this tooth.'}</span></div></div>`;
                }
            }

            // Populate Section 1: Prior History Notes
            const priorList = document.getElementById('patient-modal-prior-history-list');
            if (priorList) {
                priorList.innerHTML = '';
                if (priorHistories.length === 0) {
                    priorList.innerHTML = `<div class="small py-3 px-3 rounded-3 text-center text-muted border border-dashed mb-3" style="background: rgba(255,255,255,0.02);">${isAr ? 'لا توجد سوابق مرضية أو تشخيص أولي مسجل لهذا السن.' : 'No pre-existing conditions recorded for this tooth.'}</div>`;
                } else {
                    priorHistories.forEach(h => {
                        const dateLabel = h.history_date ? h.history_date : (isAr ? 'تاريخ المعالجة: غير محدد' : 'Treatment Date: Unspecified');
                        const safeProc = (h.procedure || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                        const safeNotes = (h.notes || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                        const safeDate = h.history_date || '';
                        let hHtml = `
                            <div class="card card-body mb-2 p-3 border rounded-3 shadow-xs" style="background: rgba(168, 85, 247, 0.08); border-color: rgba(168, 85, 247, 0.25) !important;">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <div class="d-flex align-items-center gap-2 mb-1">
                                            <span class="badge badge-history-external px-2.5 py-1 fw-bold fs-6">
                                                <i class="bi bi-journal-medical me-1"></i>${h.procedure}
                                            </span>
                                            <span class="badge bg-secondary-subtle text-secondary border px-2 py-1 text-xs">
                                                <i class="bi bi-calendar3 me-1"></i>${dateLabel}
                                            </span>
                                        </div>
                                        <p class="mb-0 text-secondary small mt-1.5">${h.notes || (isAr ? 'سجل خارجي (لا توجد ملاحظات)' : 'External record')}</p>
                                    </div>
                                    <div class="d-flex align-items-center gap-1.5 ms-auto">
                                        <button type="button" class="btn btn-sm btn-outline-primary rounded-circle p-1.5"
                                                onclick="openEditToothHistoryModal(${patientId}, ${h.id}, '${safeProc}', '${safeNotes}', '${safeDate}')"
                                                title="${isAr ? 'تعديل السابقة المرضية' : 'Edit History Record'}">
                                            <i class="bi bi-pencil fs-6"></i>
                                        </button>
                                        <form method="POST" action="/patients/${patientId}/tooth-history/${h.id}/delete" onsubmit="return confirmDelete(event, '${isAr ? 'هل أنت متأكد من حذف هذه السابقة المرضية؟' : 'Delete this history record?'}', '${isAr ? 'حذف السابقة المرضية' : 'Delete History Record'}');">
                                            <input type="hidden" name="csrf_token" value="${config.csrfToken}">
                                            <button type="submit" class="btn btn-sm btn-outline-danger rounded-circle p-1.5" title="${isAr ? 'حذف السابقة' : 'Delete History'}">
                                                <i class="bi bi-trash fs-6"></i>
                                            </button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        `;
                        priorList.insertAdjacentHTML('beforeend', hHtml);
                    });
                }
            }

            // Populate Section 2: Clinic Treatments
            const historyList = document.getElementById('patient-modal-history-list');
            if (historyList) {
                historyList.innerHTML = '';
                if (clinicTreatments.length === 0) {
                    historyList.innerHTML = `<div class="small py-3 px-3 rounded-3 text-center text-muted border border-dashed" style="background: rgba(255,255,255,0.03);">${isAr ? 'لا توجد أي معالجات منفذة داخل العيادة لهذا السن.' : 'No clinic treatment history for this tooth.'}</div>`;
                } else {
                    clinicTreatments.forEach(t => {
                        const formattedCost = parseFloat(t.cost).toLocaleString('de-DE', {minimumFractionDigits: 0, maximumFractionDigits: 0});
                        let anesthesiaText = '';
                        if (t.use_anesthesia) {
                            const label = isAr ? `+ تخدير (${t.anesthesia_needles} حقنة)` : `+ Anesthesia (${t.anesthesia_needles} needles)`;
                            anesthesiaText = `<div class="text-secondary small mt-1" style="font-size: 0.82rem;"><i class="bi bi-shield-fill-plus me-1 text-info"></i>${label}</div>`;
                        }
                        let html = `
                            <div class="list-group-item border rounded-3 mb-3 p-3 shadow-xs" style="background: color-mix(in srgb, var(--surface-color), #ffffff 3%); border-color: color-mix(in srgb, var(--accent-color), transparent 85%) !important;">
                                <div class="d-flex w-100 justify-content-between align-items-center mb-2">
                                    <div>
                                        <h6 class="mb-0 fw-bold text-primary fs-6">${t.procedure}</h6>
                                        ${anesthesiaText}
                                    </div>
                                    <span class="badge bg-secondary-subtle text-secondary border px-2.5 py-1.5 fw-bold font-monospace" style="font-size: 0.82rem;">
                                        <i class="bi bi-calendar3 me-1"></i>${t.date}
                                    </span>
                                </div>
                                <p class="mb-3 text-secondary small" style="line-height: 1.5; font-size: 0.88rem;">${t.notes || (isAr ? 'بلا ملاحظات مدونة' : 'No notes available')}</p>
                                <div class="d-flex w-100 justify-content-between align-items-center border-top pt-2.5 mt-2">
                                    <a href="/appointments/${t.appointment_id}/session" class="btn btn-sm btn-outline-primary rounded-pill px-3 py-1.5 fw-bold d-inline-flex align-items-center gap-1.5 shadow-xs" style="transition: all 0.2s ease;">
                                        <i class="bi bi-clipboard2-pulse"></i>
                                        <span>${isAr ? 'الجلسة #' : 'Session #'} ${t.appointment_id}</span>
                                        <i class="bi bi-box-arrow-up-right small ms-1"></i>
                                    </a>
                                    <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-3 py-1.5 fs-6 fw-bold">${formattedCost} ${currency}</span>
                                </div>
                            </div>
                        `;
                        historyList.insertAdjacentHTML('beforeend', html);
                    });
                }
            }

            // Populate Section 3: Future Planned Treatments
            const planList = document.getElementById('patient-modal-planned-treatments-list');
            if (planList) {
                planList.innerHTML = '';
                if (plannedItems.length === 0) {
                    planList.innerHTML = `<div class="small py-3 px-3 rounded-3 text-center text-muted border border-dashed mb-2" style="background: rgba(255,255,255,0.02);">${isAr ? 'لا توجد أي معالجات مستقبلية مخططة لهذا السن.' : 'No planned treatments for this tooth.'}</div>`;
                } else {
                    plannedItems.forEach(p => {
                        const formattedCost = parseFloat(p.cost || 0).toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                        let pHtml = `
                            <div class="card card-body mb-2 p-2.5 border rounded-3 shadow-xs" style="background: rgba(234, 179, 8, 0.07); border-color: rgba(234, 179, 8, 0.3) !important;">
                                <div class="d-flex justify-content-between align-items-center mb-1 flex-wrap gap-2">
                                    <div class="d-flex align-items-center gap-2 flex-wrap">
                                        <span class="badge bg-warning text-dark fw-bold px-2.5 py-1" style="font-size: 0.8rem;">
                                            <i class="bi bi-calendar2-check me-1"></i>${p.procedure}
                                        </span>
                                        <span class="badge bg-dark text-light border border-secondary px-2 py-1" style="font-size: 0.76rem;">
                                            ${formattedCost} ${currency}
                                        </span>
                                    </div>
                                    <form method="POST" action="/patients/${patientId}/treatment-plans/${p.id}/delete" onsubmit="return confirmDelete(event, '${isAr ? 'هل أنت متأكد من حذف هذا الإجراء من خطة العلاج؟' : 'Delete this planned item?'}', '${isAr ? 'حذف من الخطة' : 'Delete from Plan'}');" style="display:inline;">
                                        <input type="hidden" name="csrf_token" value="${config.csrfToken}">
                                        <button type="submit" class="btn btn-sm btn-outline-danger rounded-circle p-1.5" title="${isAr ? 'حذف من الخطة' : 'Delete'}">
                                            <i class="bi bi-trash" style="font-size: 0.8rem;"></i>
                                        </button>
                                    </form>
                                </div>
                                <p class="mb-0 text-secondary small mt-1" style="font-size: 0.82rem;"><i class="bi bi-chat-left-text me-1 opacity-75"></i>${p.notes || (isAr ? 'خطة مقترحة (بدون ملاحظات إضافية)' : 'Proposed treatment plan')}</p>
                            </div>
                        `;
                        planList.insertAdjacentHTML('beforeend', pHtml);
                    });
                }
            }

            const modal = new bootstrap.Modal(document.getElementById('patientToothModal'));
            modal.show();
        });
    });

    // Initialize X-Ray Studio Controls
    initXrayStudio(patientImages);
};

function initXrayStudio(patientImages) {
    const selectXray = document.getElementById('select-xray-image');
    const selectBefore = document.getElementById('compare-select-before');
    const selectAfter = document.getElementById('compare-select-after');
    
    if (selectXray && selectBefore && selectAfter) {
        patientImages.forEach(img => {
            const opt1 = document.createElement('option');
            opt1.value = img.url;
            opt1.dataset.filename = img.filename;
            opt1.dataset.date = img.date;
            opt1.textContent = `${img.filename} (${img.date})`;
            selectXray.appendChild(opt1);
            
            const opt2 = document.createElement('option');
            opt2.value = img.url;
            opt2.textContent = `${img.filename} (${img.date})`;
            selectBefore.appendChild(opt2);
            
            const opt3 = document.createElement('option');
            opt3.value = img.url;
            opt3.textContent = `${img.filename} (${img.date})`;
            selectAfter.appendChild(opt3);
        });
    }

    const viewerImg = document.getElementById('viewer-img');
    const placeholder = document.querySelector('.no-image-placeholder');
    const viewport = document.querySelector('.image-viewport');
    const overlay = document.getElementById('viewer-overlay');
    const overlayFilename = document.getElementById('overlay-filename');
    const overlayDate = document.getElementById('overlay-date');
    
    const sliderZoom = document.getElementById('slider-zoom');
    const zoomVal = document.getElementById('zoom-val');
    const btnZoomIn = document.getElementById('btn-zoom-in');
    const btnZoomOut = document.getElementById('btn-zoom-out');
    
    const sliderRotate = document.getElementById('slider-rotate');
    const rotateVal = document.getElementById('rotate-val');
    const btnRotateLeft = document.getElementById('btn-rotate-left');
    const btnRotateRight = document.getElementById('btn-rotate-right');
    
    const sliderBrightness = document.getElementById('slider-brightness');
    const brightnessVal = document.getElementById('brightness-val');
    
    const sliderContrast = document.getElementById('slider-contrast');
    const contrastVal = document.getElementById('contrast-val');
    
    const switchInvert = document.getElementById('switch-invert');
    const btnReset = document.getElementById('btn-reset-adjuster');

    let zoom = 100, rotation = 0, brightness = 100, contrast = 100, invert = false, panX = 0, panY = 0, isDragging = false, startX = 0, startY = 0;

    function applyTransforms() {
        if (!viewerImg) return;
        const scale = zoom / 100;
        const invertStr = invert ? 'invert(1)' : 'invert(0)';
        viewerImg.style.filter = `brightness(${brightness}%) contrast(${contrast}%) ${invertStr}`;
        viewerImg.style.transform = `translate(${panX}px, ${panY}px) scale(${scale}) rotate(${rotation}deg)`;
    }

    function updateLabels() {
        if (zoomVal) zoomVal.textContent = zoom + '%';
        if (rotateVal) rotateVal.textContent = rotation + '°';
        if (brightnessVal) brightnessVal.textContent = brightness + '%';
        if (contrastVal) contrastVal.textContent = contrast + '%';
    }

    function resetAdjustments() {
        zoom = 100; rotation = 0; brightness = 100; contrast = 100; invert = false; panX = 0; panY = 0;
        if (sliderZoom) sliderZoom.value = 100;
        if (sliderRotate) sliderRotate.value = 0;
        if (sliderBrightness) sliderBrightness.value = 100;
        if (sliderContrast) sliderContrast.value = 100;
        if (switchInvert) switchInvert.checked = false;
        updateLabels();
        applyTransforms();
    }

    if (selectXray) {
        selectXray.addEventListener('change', function() {
            const url = this.value;
            if (!url) {
                if (placeholder) placeholder.classList.remove('d-none');
                if (viewport) viewport.classList.add('d-none');
                if (overlay) overlay.classList.add('d-none');
                return;
            }
            const selectedOpt = this.options[this.selectedIndex];
            if (placeholder) placeholder.classList.add('d-none');
            if (viewport) viewport.classList.remove('d-none');
            if (overlay) {
                overlay.classList.remove('d-none');
                overlayFilename.textContent = selectedOpt.dataset.filename;
                overlayDate.textContent = selectedOpt.dataset.date;
            }
            viewerImg.src = url;
            resetAdjustments();
        });
    }

    if (sliderZoom) sliderZoom.addEventListener('input', function() { zoom = parseInt(this.value); updateLabels(); applyTransforms(); });
    if (sliderRotate) sliderRotate.addEventListener('input', function() { rotation = parseInt(this.value); updateLabels(); applyTransforms(); });
    if (sliderBrightness) sliderBrightness.addEventListener('input', function() { brightness = parseInt(this.value); updateLabels(); applyTransforms(); });
    if (sliderContrast) sliderContrast.addEventListener('input', function() { contrast = parseInt(this.value); updateLabels(); applyTransforms(); });
    if (switchInvert) switchInvert.addEventListener('change', function() { invert = this.checked; applyTransforms(); });
    if (btnReset) btnReset.addEventListener('click', resetAdjustments);

    if (btnZoomIn) btnZoomIn.addEventListener('click', function() { zoom = Math.min(300, zoom + 10); if (sliderZoom) sliderZoom.value = zoom; updateLabels(); applyTransforms(); });
    if (btnZoomOut) btnZoomOut.addEventListener('click', function() { zoom = Math.max(50, zoom - 10); if (sliderZoom) sliderZoom.value = zoom; updateLabels(); applyTransforms(); });
    if (btnRotateLeft) btnRotateLeft.addEventListener('click', function() { rotation = Math.max(-180, rotation - 15); if (sliderRotate) sliderRotate.value = rotation; updateLabels(); applyTransforms(); });
    if (btnRotateRight) btnRotateRight.addEventListener('click', function() { rotation = Math.min(180, rotation + 15); if (sliderRotate) sliderRotate.value = rotation; updateLabels(); applyTransforms(); });

    if (viewport) {
        viewport.addEventListener('mousedown', function(e) {
            if (!selectXray.value) return;
            isDragging = true;
            viewport.style.cursor = 'grabbing';
            startX = e.clientX - panX;
            startY = e.clientY - panY;
        });
        window.addEventListener('mouseup', function() { isDragging = false; if (viewport) viewport.style.cursor = 'grab'; });
        viewport.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            panX = e.clientX - startX;
            panY = e.clientY - startY;
            applyTransforms();
        });
    }

    // Comparison slider
    const beforeImg = document.getElementById('compare-img-before');
    const afterImg = document.getElementById('compare-img-after');
    const comparePlaceholder = document.querySelector('.compare-placeholder');
    const compareContainer = document.getElementById('slider-comparison-container');
    const compareSlider = document.getElementById('compare-range-slider');
    
    function updateComparisonView() {
        const beforeUrl = selectBefore.value;
        const afterUrl = selectAfter.value;
        if (!beforeUrl || !afterUrl) {
            if (comparePlaceholder) comparePlaceholder.classList.remove('d-none');
            if (compareContainer) compareContainer.classList.add('d-none');
            return;
        }
        if (comparePlaceholder) comparePlaceholder.classList.add('d-none');
        if (compareContainer) compareContainer.classList.remove('d-none');
        beforeImg.src = beforeUrl;
        afterImg.src = afterUrl;
        if (compareSlider) {
            compareSlider.value = 50;
            compareContainer.style.setProperty('--clip-percent', '50%');
            const divider = document.getElementById('compare-divider');
            if (divider) divider.style.left = '50%';
        }
    }
    
    if (selectBefore) selectBefore.addEventListener('change', updateComparisonView);
    if (selectAfter) selectAfter.addEventListener('change', updateComparisonView);
    
    if (compareSlider) {
        compareSlider.addEventListener('input', function() {
            const val = this.value;
            const clipRight = 100 - val;
            compareContainer.style.setProperty('--clip-percent', `${clipRight}%`);
            const divider = document.getElementById('compare-divider');
            if (divider) divider.style.left = `${val}%`;
        });
    }
}
