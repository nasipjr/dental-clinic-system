/**
 * Dental Clinic MS - Appointment Session Core Script
 * Comprehensive modular controller for session odontogram, modals, calculations, and actions.
 */

window.confirmRevertSession = function() {
    const isAr = document.documentElement.lang === 'ar' || document.cookie.includes('lang=ar');
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isAr ? 'التراجع عن فتح الجلسة؟' : 'Undo Session Start?',
            text: isAr ? 'هل أنت متأكد من الخروج والتراجع عن بدء الجلسة لإعادة الموعد كـ "مجدول" بدون أي تعديل؟' : 'Are you sure you want to exit and revert this session back to Scheduled status?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: isAr ? 'نعم، تراجع عن الجلسة' : 'Yes, Undo Session',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                const form = document.getElementById('revertSessionForm');
                if (form) form.submit();
            }
        });
    } else {
        if (confirm(isAr ? 'هل أنت متأكد من الخروج والتراجع عن بدء الجلسة؟' : 'Undo session start?')) {
            const form = document.getElementById('revertSessionForm');
            if (form) form.submit();
        }
    }
};

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

window.updatePlanDefaultCost = function(selectEl) {
    if (!selectEl) return;
    const opt = selectEl.options[selectEl.selectedIndex];
    const costInput = document.getElementById('s-plan-estimated-cost');
    if (opt && opt.dataset.price && costInput) {
        costInput.value = opt.dataset.price;
    }
};

window.initAppointmentSession = function(config) {
    const isAr = config.isAr;
    const prices = config.prices || {};
    const currency = config.currency;
    const appointmentId = config.appointmentId;
    const patientId = config.patientId;
    const currentTreatments = config.currentTreatments || [];
    const historyTreatments = config.historyTreatments || [];
    const toothHistoryDict = config.toothHistoryDict || {};
    const plannedTeethDict = config.plannedTeethDict || {};
    const csrfToken = config.csrfToken;
    const isScheduled = config.isScheduled;

    const fdiMap = {
        '1': '18', '2': '17', '3': '16', '4': '15', '5': '14', '6': '13', '7': '12', '8': '11',
        '9': '21', '10': '22', '11': '23', '12': '24', '13': '25', '14': '26', '15': '27', '16': '28',
        '17': '38', '18': '37', '19': '36', '20': '35', '21': '34', '22': '33', '23': '32', '24': '31',
        '25': '41', '26': '42', '27': '43', '28': '44', '29': '45', '30': '46', '31': '47', '32': '48'
    };

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

    const activeTeeth = {};
    const historyTeeth = {};

    for (let i = 1; i <= 32; i++) {
        const toothStr = i.toString();
        const fdiNum = fdiMap[toothStr];
        activeTeeth[toothStr] = currentTreatments.filter(t => appliesToTooth(t, toothStr));
        historyTeeth[toothStr] = historyTreatments.filter(t => appliesToTooth(t, toothStr));

        const priorHistories = getToothItemsFromDict(toothHistoryDict, toothStr, fdiNum);
        const plannedItems = getToothItemsFromDict(plannedTeethDict, toothStr, fdiNum);

        const hasActiveExtraction = activeTeeth[toothStr].some(t => isExtractionProcedure(t.procedure));
        const hasHistoryExtraction = historyTeeth[toothStr].some(t => isExtractionProcedure(t.procedure));
        const hasPriorExtraction = priorHistories.some(h => isExtractionProcedure(h.procedure));
        const isExtracted = hasActiveExtraction || hasHistoryExtraction || hasPriorExtraction;

        const teethElements = document.querySelectorAll(`[data-tooth="${toothStr}"]`);
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
            } else if (activeTeeth[toothStr].length > 0) {
                el.classList.add('active-treatment', 'active');
            } else if (historyTeeth[toothStr].length > 0) {
                el.classList.add('history-treatment', 'history');
            } else {
                el.classList.add('no-treatment');
            }

            if (priorHistories.length > 0) {
                el.classList.add('history-external');
                if (!el.querySelector('.prior-history-indicator')) {
                    const starDot = document.createElement('span');
                    starDot.className = 'prior-history-indicator';
                    starDot.title = isAr ? 'سوابق مرضية وخارجية' : 'Pre-existing Condition';
                    starDot.innerHTML = '<i class="bi bi-star-fill"></i>';
                    el.appendChild(starDot);
                }
            }

            if (plannedItems.length > 0) {
                el.classList.add('has-plan-treatment');
                if (!el.querySelector('.plan-golden-indicator')) {
                    const starEl = document.createElement('span');
                    starEl.className = 'plan-golden-indicator';
                    starEl.title = isAr ? 'توجد خطة علاج مستقبلية مقترحة لهذا السن ⭐️' : 'Future Treatment Plan ⭐️';
                    starEl.innerHTML = '<i class="bi bi-star-fill"></i>';
                    el.appendChild(starEl);
                }
            }

            // Vector SVG Star Indicators (for Anatomical Arch Odontogram)
            const svgIndElements = document.querySelectorAll('.ind-' + fdiNum);
            if (svgIndElements && svgIndElements.length > 0) {
                const starPathD = "M 0.0 -7.0 L 1.6 -2.3 L 6.7 -2.2 L 2.7 0.9 L 4.1 5.7 L 0.0 2.8 L -4.1 5.7 L -2.7 0.9 L -6.7 -2.2 L -1.6 -2.3 Z";
                let indSvgHtml = '';
                if (priorHistories.length > 0 && plannedItems.length > 0) {
                    indSvgHtml = `<g transform="translate(-7, 0)"><path class="svg-star-purple" d="${starPathD}" /></g><g transform="translate(7, 0)"><path class="svg-star-gold" d="${starPathD}" /></g>`;
                } else if (priorHistories.length > 0) {
                    indSvgHtml = `<path class="svg-star-purple" d="${starPathD}" />`;
                } else if (plannedItems.length > 0) {
                    indSvgHtml = `<path class="svg-star-gold" d="${starPathD}" />`;
                }
                svgIndElements.forEach(indEl => {
                    indEl.innerHTML = indSvgHtml;
                });
            }

            let tooltipHtml = `<strong class="d-block mb-1">${isAr ? 'السن' : 'Tooth'} ${fdiNum}</strong>`;
            if (isExtracted) {
                tooltipHtml += `<div class="text-danger small fw-bold mb-1"><i class="bi bi-x-circle-fill me-1"></i>${isAr ? 'تم قلع السن (سابق/عيادة) ❌' : 'Tooth Extracted ❌'}</div>`;
            }
            if (priorHistories.length > 0) {
                tooltipHtml += `<div class="text-purple small mt-1" style="color:#c084fc;"><i class="bi bi-journal-medical me-1"></i>${isAr ? 'السوابق المرضية:' : 'Pre-existing History:'}</div>`;
                priorHistories.forEach(h => {
                    tooltipHtml += `<div class="ms-2 small text-nowrap" style="color:#e9d5ff;">• 🟣 ${h.procedure}</div>`;
                });
            }
            if (activeTeeth[toothStr].length > 0) {
                tooltipHtml += `<div class="text-success small mt-1"><i class="bi bi-clipboard2-pulse me-1"></i>${isAr ? 'الجلسة الحالية:' : 'Current Session:'}</div>`;
                activeTeeth[toothStr].forEach(t => {
                    const docText = t.doctor ? ` (${t.doctor})` : '';
                    tooltipHtml += `<div class="ms-2 small text-nowrap">• ${t.procedure}${docText}</div>`;
                });
            }
            if (historyTeeth[toothStr].length > 0) {
                tooltipHtml += `<div class="text-info small mt-1"><i class="bi bi-clock-history me-1"></i>${isAr ? 'معالجات سابقة بالعيادة:' : 'Clinic History:'}</div>`;
                historyTeeth[toothStr].forEach(t => {
                    const docText = t.doctor ? ` - د. ${t.doctor}` : '';
                    tooltipHtml += `<div class="ms-2 small text-nowrap">• ${t.procedure} (${t.date.split(' ')[0]})${docText}</div>`;
                });
            }
            if (plannedItems.length > 0) {
                tooltipHtml += `<div class="text-warning small mt-1"><i class="bi bi-calendar2-check me-1"></i>${isAr ? 'خطة علاج مستقبلية:' : 'Treatment Plan:'}</div>`;
                plannedItems.forEach(p => {
                    tooltipHtml += `<div class="ms-2 small text-nowrap" style="color:#fde047;">• 🟡 ${p.procedure}</div>`;
                });
            }

            el.setAttribute('data-bs-toggle', 'tooltip');
            el.setAttribute('data-bs-html', 'true');
            el.setAttribute('data-bs-title', tooltipHtml);
        });
    }

    // Toggle inline forms
    const sToggleBtn = document.getElementById('s-toggle-add-history-btn');
    const sFormContainer = document.getElementById('s-add-history-form-container');
    if (sToggleBtn && sFormContainer) {
        sToggleBtn.addEventListener('click', function () {
            sFormContainer.classList.toggle('d-none');
        });
    }

    const sTogglePlanBtn = document.getElementById('s-toggle-add-plan-btn');
    const sPlanFormContainer = document.getElementById('s-add-plan-form-container');
    if (sTogglePlanBtn && sPlanFormContainer) {
        sTogglePlanBtn.addEventListener('click', function () {
            sPlanFormContainer.classList.toggle('d-none');
        });
    }

    // Multi-Select Teeth State
    let isMultiSelectMode = false;
    const selectedTeethSet = new Set();

    const btnToggleMultiSelect = document.getElementById('btn-toggle-multi-select');
    const multiSelectBar = document.getElementById('multi-select-bar');
    const multiSelectCountBadge = document.getElementById('multi-select-count-badge');
    const btnOpenBulkModal = document.getElementById('btn-open-bulk-modal');
    const btnClearMultiSelect = document.getElementById('btn-clear-multi-select');

    function updateMultiSelectUI() {
        const count = selectedTeethSet.size;
        if (multiSelectCountBadge) {
            const teethWord = isAr ? (count === 1 ? 'سن واحد' : (count === 2 ? 'سنان' : (count >= 3 && count <= 10 ? `${count} أسنان` : `${count} سن`))) : `${count} teeth`;
            multiSelectCountBadge.textContent = teethWord;
        }
        if (btnOpenBulkModal) {
            btnOpenBulkModal.disabled = count === 0;
        }
        document.querySelectorAll('.tooth-wrapper, .anatomical-tooth-item, .anatomical-tooth-btn, .vector-tooth-item, .tooth-btn, .p-tooth-btn').forEach(wrapper => {
            const toothNum = wrapper.dataset.tooth || wrapper.dataset.patientTooth;
            const fdiNum = String(wrapper.dataset.fdi || fdiMap[toothNum] || toothNum || '');
            if (fdiNum && selectedTeethSet.has(fdiNum)) {
                wrapper.classList.add('multi-selected');
            } else {
                wrapper.classList.remove('multi-selected');
            }
        });
    }

    function clearMultiSelect() {
        selectedTeethSet.clear();
        updateMultiSelectUI();
    }

    if (btnToggleMultiSelect) {
        btnToggleMultiSelect.addEventListener('click', function () {
            isMultiSelectMode = !isMultiSelectMode;
            if (isMultiSelectMode) {
                this.classList.add('active');
                this.innerHTML = `<i class="bi bi-check-square-fill me-1"></i><span>${isAr ? 'إلغاء وضع التحديد' : 'Exit Multi-Select'}</span>`;
                if (multiSelectBar) multiSelectBar.style.setProperty('display', 'flex', 'important');
            } else {
                this.classList.remove('active');
                this.innerHTML = `<i class="bi bi-ui-checks me-1"></i><span>${isAr ? 'تحديد أسنان متعددة' : 'Multi-Select Teeth'}</span>`;
                if (multiSelectBar) multiSelectBar.style.setProperty('display', 'none', 'important');
                clearMultiSelect();
            }
        });
    }

    if (btnClearMultiSelect) {
        btnClearMultiSelect.addEventListener('click', clearMultiSelect);
    }

    // Tooth Click Handlers (For Anatomical and Circular Charts)
    document.querySelectorAll('.tooth-wrapper, .anatomical-tooth-item, .anatomical-tooth-btn, .vector-tooth-item, .tooth-btn, .p-tooth-btn').forEach(wrapper => {
        wrapper.addEventListener('click', function (e) {
            const toothNum = this.dataset.tooth || this.dataset.patientTooth;
            const fdiNum = String(this.dataset.fdi || fdiMap[toothNum] || toothNum || '');
            if (!fdiNum) return;

            if (isMultiSelectMode) {
                e.preventDefault();
                e.stopPropagation();
                if (selectedTeethSet.has(fdiNum)) {
                    selectedTeethSet.delete(fdiNum);
                } else {
                    selectedTeethSet.add(fdiNum);
                }
                updateMultiSelectUI();
                return;
            }

            const modalTitle = document.getElementById('toothModalLabel');
            if (modalTitle) modalTitle.textContent = `${isAr ? 'تفاصيل وإجراءات السن' : 'Tooth Details & Actions'} ${fdiNum}`;

            const sHistoryToothInput = document.getElementById('s-history-form-tooth-number');
            if (sHistoryToothInput) sHistoryToothInput.value = fdiNum || toothNum;

            const toothInput = document.getElementById('modal-tooth-input');
            if (toothInput) toothInput.value = fdiNum || toothNum;

            // Prior Histories
            const priorHistories = getToothItemsFromDict(toothHistoryDict, toothNum, fdiNum);
            const priorList = document.getElementById('modal-prior-history-list');
            if (priorList) {
                priorList.innerHTML = '';
                if (priorHistories.length === 0) {
                    priorList.innerHTML = `<div class="small py-2 px-3 rounded-3 text-muted border border-dashed mb-3" style="background: rgba(255,255,255,0.02);">${isAr ? 'لا توجد سوابق مرضية مسجلة.' : 'No pre-existing conditions.'}</div>`;
                } else {
                    priorHistories.forEach(h => {
                        const dateLabel = h.history_date ? h.history_date : (isAr ? 'غير محدد' : 'Unspecified');
                        const safeProc = (h.procedure || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                        const safeNotes = (h.notes || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
                        const safeDate = h.history_date || '';
                        let hHtml = `
                            <div class="card card-body mb-2 p-2 border rounded-3 shadow-xs mb-2" style="background: rgba(168, 85, 247, 0.08); border-color: rgba(168, 85, 247, 0.25) !important;">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <div class="d-flex align-items-center gap-1.5 mb-1">
                                            <span class="badge badge-history-external px-2 py-0.5 fw-bold" style="font-size: 0.75rem;">
                                                <i class="bi bi-journal-medical me-1"></i>${h.procedure}
                                            </span>
                                            <span class="badge duration-badge" style="font-size: 0.72rem;">
                                                <i class="bi bi-calendar3 me-1"></i>${dateLabel}
                                            </span>
                                        </div>
                                        <p class="mb-0 text-secondary small mt-1" style="font-size: 0.78rem;">${h.notes || (isAr ? 'سجل خارجي (لا توجد ملاحظات)' : 'External record')}</p>
                                    </div>
                                    <div class="d-flex align-items-center gap-1 ms-auto">
                                        <button type="button" class="btn btn-xs btn-outline-primary rounded-circle p-1"
                                                onclick="openEditToothHistoryModal(${patientId}, ${h.id}, '${safeProc}', '${safeNotes}', '${safeDate}', ${appointmentId})"
                                                data-tooltip="${isAr ? 'تعديل السابقة المرضية' : 'Edit History Record'}">
                                            <i class="bi bi-pencil" style="font-size: 0.75rem;"></i>
                                        </button>
                                        <form method="POST" action="/patients/${patientId}/tooth-history/${h.id}/delete" onsubmit="return confirmDelete(event, '${isAr ? 'هل أنت متأكد من حذف هذه السابقة المرضية؟' : 'Delete this history record?'}');">
                                            <input type="hidden" name="csrf_token" value="${csrfToken}">
                                            <input type="hidden" name="appointment_id" value="${appointmentId}">
                                            <button type="submit" class="btn btn-xs btn-outline-danger rounded-circle p-1" data-tooltip="${isAr ? 'حذف السابقة المرضية' : 'Delete History Record'}">
                                                <i class="bi bi-trash" style="font-size: 0.75rem;"></i>
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

            // Current treatments
            const currentList = document.getElementById('modal-current-treatments-list');
            if (currentList) {
                currentList.innerHTML = '';
                const activeItems = activeTeeth[toothNum] || [];
                if (activeItems.length === 0) {
                    currentList.innerHTML = `<div class="small py-2.5 px-3 rounded-3" style="background: color-mix(in srgb, var(--default-color), transparent 95%); color: color-mix(in srgb, var(--default-color), transparent 45%); border: 1px solid color-mix(in srgb, var(--default-color), transparent 90%);">${isAr ? 'لا توجد معالجات في هذه الجلسة بعد.' : 'No treatments in this session yet.'}</div>`;
                } else {
                    activeItems.forEach(t => {
                        const formattedCost = parseFloat(t.cost).toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                        let anesthesiaText = '';
                        if (t.use_anesthesia) {
                            const suffix = t.anesthesia_needles === 1 ? (isAr ? 'حقنة' : 'injection') : (isAr ? 'حقن' : 'injections');
                            const typeLabel = t.anesthesia_type ? ` [${t.anesthesia_type}]` : '';
                            anesthesiaText = `<div class="text-secondary small mt-0.5" style="font-size: 0.8rem; font-weight: 500;"><i class="bi bi-shield-fill-plus me-1 text-info"></i>+ ${isAr ? 'تخدير' : 'Anesthesia'}${typeLabel} (${t.anesthesia_needles} ${suffix})</div>`;
                        }
                        let docBadge = t.doctor ? `<span class="doctor-badge ms-2" style="font-size:0.75rem; padding: 2px 8px;"><i class="bi bi-person-badge me-1"></i>${t.doctor}</span>` : '';
                        let html = `
                            <div class="list-group-item border rounded-3 mb-2 p-3 bg-light-subtle shadow-xs">
                                <div class="d-flex w-100 justify-content-between align-items-center mb-1">
                                    <div class="d-flex flex-column">
                                        <div class="d-flex align-items-center flex-wrap gap-1">
                                            <h6 class="mb-0 fw-bold text-success">${t.procedure}</h6>
                                            ${docBadge}
                                        </div>
                                        ${anesthesiaText}
                                    </div>
                                    <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1">${formattedCost} ${currency}</span>
                                </div>
                                <p class="mb-2 text-secondary small">${t.notes || (isAr ? 'بلا ملاحظات' : 'No notes available')}</p>
                                <div class="d-flex gap-2 justify-content-end border-top pt-2 mt-2">
                                    <a href="${t.edit_url}" class="btn btn-xs btn-outline-primary px-2.5 py-1 text-xs fw-semibold" style="font-size: 0.75rem;"><i class="bi bi-pencil-square me-1"></i>${isAr ? 'تعديل' : 'Edit'}</a>
                                    <a href="${t.delete_url}" onclick="return confirmDelete(event, '${isAr ? 'هل أنت متأكد من حذف هذه المعالجة؟' : 'Are you sure you want to delete this treatment?'}');" class="btn btn-xs btn-outline-danger px-2.5 py-1 text-xs fw-semibold" style="font-size: 0.75rem;"><i class="bi bi-trash me-1"></i>${isAr ? 'حذف' : 'Delete'}</a>
                                </div>
                            </div>
                        `;
                        currentList.insertAdjacentHTML('beforeend', html);
                    });
                }
            }

            // History treatments
            const historyList = document.getElementById('modal-history-treatments-list');
            if (historyList) {
                historyList.innerHTML = '';
                const historyItems = historyTeeth[toothNum] || [];
                if (historyItems.length === 0) {
                    historyList.innerHTML = `<div class="small py-2.5 px-3 rounded-3" style="background: color-mix(in srgb, var(--default-color), transparent 95%); color: color-mix(in srgb, var(--default-color), transparent 45%); border: 1px solid color-mix(in srgb, var(--default-color), transparent 90%);">${isAr ? 'لا يوجد سجل معالجات سابق لهذا السن.' : 'No history recorded for this tooth.'}</div>`;
                } else {
                    historyItems.forEach(t => {
                        const formattedCost = parseFloat(t.cost).toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                        let docBadge = t.doctor ? `<span class="doctor-badge ms-2" style="font-size:0.75rem; padding: 2px 8px;"><i class="bi bi-person-badge me-1"></i>${t.doctor}</span>` : '';
                        let html = `
                            <div class="list-group-item border rounded-3 mb-2 p-3 bg-light-subtle shadow-xs">
                                <div class="d-flex w-100 justify-content-between align-items-center mb-1">
                                    <div class="d-flex flex-column">
                                        <div class="d-flex align-items-center flex-wrap gap-1">
                                            <h6 class="mb-0 fw-semibold text-primary">${t.procedure}</h6>
                                            ${docBadge}
                                        </div>
                                    </div>
                                    <small class="text-muted fw-bold">${t.date.split(' ')[0]}</small>
                                </div>
                                <p class="mb-2 text-secondary small">${t.notes || (isAr ? 'بلا ملاحظات' : 'No notes available')}</p>
                                <div class="d-flex w-100 justify-content-between align-items-center border-top pt-2 mt-2">
                                    <span class="small text-muted">${isAr ? 'رقم الجلسة:' : 'Session #'} <strong class="text-dark">${t.appointment_id}</strong></span>
                                    <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-2 py-1">${formattedCost} ${currency}</span>
                                </div>
                            </div>
                        `;
                        historyList.insertAdjacentHTML('beforeend', html);
                    });
                }
            }

            // Planned treatments
            const sPlanToothInput = document.getElementById('s-plan-form-tooth-number');
            if (sPlanToothInput) sPlanToothInput.value = fdiNum || toothNum;

            const plannedItemsModal = getToothItemsFromDict(plannedTeethDict, toothNum, fdiNum);
            const planList = document.getElementById('modal-planned-treatments-list');
            if (planList) {
                planList.innerHTML = '';
                if (plannedItemsModal.length === 0) {
                    planList.innerHTML = `<div class="small py-2 px-3 rounded-3 text-muted border border-dashed mb-2" style="background: rgba(255,255,255,0.02);">${isAr ? 'لا توجد معالجات مستقبلية مخططة لهذا السن.' : 'No planned treatments for this tooth.'}</div>`;
                } else {
                    plannedItemsModal.forEach(p => {
                        const formattedCost = parseFloat(p.cost || 0).toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
                        let pHtml = `
                            <div class="card card-body mb-2 p-2.5 border rounded-3 shadow-xs" style="background: rgba(234, 179, 8, 0.07); border-color: rgba(234, 179, 8, 0.3) !important;">
                                <div class="d-flex justify-content-between align-items-center mb-1.5 flex-wrap gap-2">
                                    <div class="d-flex align-items-center gap-1.5 flex-wrap">
                                        <span class="badge bg-warning text-dark fw-bold px-2 py-1" style="font-size: 0.76rem;">
                                            <i class="bi bi-calendar2-check me-1"></i>${p.procedure}
                                        </span>
                                        <span class="badge bg-dark text-light border border-secondary px-2 py-1" style="font-size: 0.74rem;">
                                            ${formattedCost} ${currency}
                                        </span>
                                    </div>
                                    <div class="d-flex align-items-center gap-1 ms-auto">
                                        ${isScheduled ? `
                                        <form method="POST" action="/appointments/${appointmentId}/treatment-plans/${p.id}/execute" style="display:inline;" onsubmit="return confirmExecutePlan(event);">
                                            <input type="hidden" name="csrf_token" value="${csrfToken}">
                                            <button type="submit" class="btn btn-xs btn-success rounded-pill px-2.5 py-1 fw-bold d-flex align-items-center gap-1 shadow-xs" style="font-size: 0.74rem;">
                                                <i class="bi bi-lightning-fill text-warning"></i>
                                                <span>${isAr ? 'تنفيذ بالجلسة' : 'Execute'}</span>
                                            </button>
                                        </form>` : ''}
                                        <form method="POST" action="/patients/${patientId}/treatment-plans/${p.id}/delete" onsubmit="return confirmDeletePlan(event);" style="display:inline;">
                                            <input type="hidden" name="csrf_token" value="${csrfToken}">
                                            <input type="hidden" name="appointment_id" value="${appointmentId}">
                                            <button type="submit" class="btn btn-xs btn-outline-danger rounded-circle p-1">
                                                <i class="bi bi-trash" style="font-size: 0.75rem;"></i>
                                            </button>
                                        </form>
                                    </div>
                                </div>
                                <p class="mb-0 text-secondary small mt-0.5" style="font-size: 0.78rem;"><i class="bi bi-chat-left-text me-1 opacity-75"></i>${p.notes || (isAr ? 'خطة مقترحة (بدون ملاحظات إضافية)' : 'Proposed treatment plan')}</p>
                            </div>
                        `;
                        planList.insertAdjacentHTML('beforeend', pHtml);
                    });
                }
            }

            // Extraction check & lock
            const priorHistoriesModal = getToothItemsFromDict(toothHistoryDict, toothNum, fdiNum);
            const isToothExtracted = (activeTeeth[toothNum] || []).some(t => isExtractionProcedure(t.procedure)) ||
                (historyTeeth[toothNum] || []).some(t => isExtractionProcedure(t.procedure)) ||
                priorHistoriesModal.some(h => isExtractionProcedure(h.procedure));
            
            window.currentModalToothIsExtracted = isToothExtracted;
            const form = document.getElementById('modal-add-treatment-form');
            let extBanner = document.getElementById('extracted-tooth-banner');
            const modalProcSelectEl = document.getElementById('modal-procedure-type');
            const modalCardsContainer = document.getElementById('modal-sub-procedure-cards-container');
            const modalCatPills = document.querySelectorAll('#toothModal .tooth-cat-pill');

            if (isToothExtracted) {
                if (!extBanner && form) {
                    extBanner = document.createElement('div');
                    extBanner.id = 'extracted-tooth-banner';
                    form.parentNode.insertBefore(extBanner, form);
                }
                if (extBanner) {
                    extBanner.className = 'alert alert-danger no-auto-icon d-flex align-items-center py-2.5 px-3 small rounded-3 mb-3 shadow-xs border border-danger-subtle';
                    extBanner.innerHTML = `<i class="bi bi-shield-lock-fill me-2.5 fs-4 text-danger flex-shrink-0"></i><div><strong class="d-block text-danger">${isAr ? 'هذا السن مقلوع 🔒' : 'Tooth Extracted 🔒'}</strong><span class="small opacity-90">${isAr ? 'ممنوع إضافة أي معالجة لهذا السن سوى (معالجة ما بعد القلع).' : 'Only "Post-Extraction Treatment" can be added for this tooth.'}</span></div>`;
                }

                modalCatPills.forEach(btn => {
                    const cat = btn.dataset.cat;
                    if (cat === 'جراحة وقلع' || cat === 'Surgery') {
                        btn.style.display = 'inline-block';
                        btn.classList.add('active', 'btn-primary');
                    } else {
                        btn.style.display = 'none';
                        btn.classList.remove('active', 'btn-primary');
                    }
                });

                if (modalCardsContainer) {
                    const cards = modalCardsContainer.querySelectorAll('.modal-sub-proc-item-card');
                    let foundPostExtCard = null;
                    cards.forEach(card => {
                        const pName = (card.dataset.procName || '').toLowerCase();
                        if (pName.includes('ما بعد القلع') || pName.includes('post-extraction') || pName.includes('post extraction')) {
                            card.style.display = 'block';
                            foundPostExtCard = card;
                        } else {
                            card.style.display = 'none';
                        }
                    });
                    if (foundPostExtCard) {
                        const quickCard = foundPostExtCard.querySelector('.modal-procedure-quick-card');
                        if (quickCard) quickCard.classList.add('selected-card');
                    }
                }

                if (modalProcSelectEl) {
                    let autoSelectVal = '';
                    Array.from(modalProcSelectEl.options).forEach(opt => {
                        if (!opt.value) return;
                        const optVal = opt.value.toLowerCase();
                        if (optVal.includes('ما بعد القلع') || optVal.includes('post-extraction') || optVal.includes('post extraction')) {
                            opt.style.display = '';
                            opt.disabled = false;
                            autoSelectVal = opt.value;
                        } else {
                            opt.style.display = 'none';
                            opt.disabled = true;
                        }
                    });
                    if (autoSelectVal) {
                        modalProcSelectEl.value = autoSelectVal;
                        updateModalPrice();
                    }
                }
            } else {
                if (extBanner) extBanner.remove();
                modalCatPills.forEach(btn => {
                    btn.style.display = 'inline-block';
                    if (btn.dataset.cat === 'all') btn.classList.add('active');
                    else btn.classList.remove('active', 'btn-primary');
                });
                if (modalCardsContainer) {
                    const cards = modalCardsContainer.querySelectorAll('.modal-sub-proc-item-card');
                    cards.forEach(card => {
                        card.style.display = 'block';
                        const quickCard = card.querySelector('.modal-procedure-quick-card');
                        if (quickCard) quickCard.classList.remove('selected-card');
                    });
                }
                if (modalProcSelectEl) {
                    Array.from(modalProcSelectEl.options).forEach(opt => {
                        opt.style.display = '';
                        opt.disabled = false;
                    });
                }
            }

            const toothModal = new bootstrap.Modal(document.getElementById('toothModal'));
            toothModal.show();
        });
    });

    // Modal price updates & calculations
    function updateModalPrice() {
        const procSelect = document.getElementById('modal-procedure-type');
        const customCostInput = document.getElementById('modal-custom-cost-input');
        const useAnes = document.getElementById('modal-use-anesthesia');
        const anesType = document.getElementById('modal-anesthesia-type');
        const needles = document.getElementById('modal-needles');
        const priceDisplay = document.getElementById('modal-procedure-price-display');

        if (!procSelect || !priceDisplay) return;

        let basePrice = 0;
        if (customCostInput && customCostInput.value.trim() !== '') {
            basePrice = parseFloat(customCostInput.value) || 0;
        } else {
            const selectedOpt = procSelect.options[procSelect.selectedIndex];
            if (selectedOpt && selectedOpt.dataset.price) {
                basePrice = parseFloat(selectedOpt.dataset.price) || 0;
            } else if (procSelect.value && prices[procSelect.value]) {
                basePrice = parseFloat(prices[procSelect.value]) || 0;
            }
        }

        let anesthesiaCost = 0;
        if (useAnes && useAnes.checked && anesType && needles) {
            const anesOpt = anesType.options[anesType.selectedIndex];
            const unitPrice = anesOpt ? (parseFloat(anesOpt.dataset.price) || 0) : 0;
            const needleCount = parseInt(needles.value) || 1;
            anesthesiaCost = unitPrice * needleCount;
        }

        const totalCost = basePrice + anesthesiaCost;
        priceDisplay.textContent = `${totalCost.toLocaleString('de-DE')} ${currency}`;
    }

    const modalProcSelect = document.getElementById('modal-procedure-type');
    if (modalProcSelect) modalProcSelect.addEventListener('change', updateModalPrice);

    const modalCustomCost = document.getElementById('modal-custom-cost-input');
    if (modalCustomCost) modalCustomCost.addEventListener('input', updateModalPrice);

    const modalUseAnes = document.getElementById('modal-use-anesthesia');
    if (modalUseAnes) {
        modalUseAnes.addEventListener('change', function() {
            const wrap = document.getElementById('modal-anesthesia-details-wrapper');
            if (wrap) wrap.style.display = this.checked ? 'block' : 'none';
            updateModalPrice();
        });
    }

    const modalAnesType = document.getElementById('modal-anesthesia-type');
    if (modalAnesType) modalAnesType.addEventListener('change', updateModalPrice);

    const modalNeedles = document.getElementById('modal-needles');
    if (modalNeedles) modalNeedles.addEventListener('input', updateModalPrice);

    // Filter categories & select quick procedures
    window.filterToothModalCategory = function(category, pillBtn) {
        if (window.currentModalToothIsExtracted) return;
        document.querySelectorAll('#toothModal .tooth-cat-pill').forEach(btn => btn.classList.remove('active', 'btn-primary'));
        if (pillBtn) pillBtn.classList.add('active');

        const cards = document.querySelectorAll('.modal-sub-proc-item-card');
        cards.forEach(card => {
            const itemCat = card.dataset.category || 'عام';
            if (category === 'all' || itemCat === category) card.style.display = 'block';
            else card.style.display = 'none';
        });

        const procSelect = document.getElementById('modal-procedure-type');
        if (procSelect) {
            Array.from(procSelect.options).forEach(opt => {
                if (!opt.value) return;
                const optCat = opt.dataset.category || '';
                if (category === 'all' || optCat === category) {
                    opt.style.display = '';
                    opt.disabled = false;
                } else {
                    opt.style.display = 'none';
                    opt.disabled = true;
                }
            });
        }
    };

    window.selectModalQuickProcedure = function(procName, cardEl) {
        document.querySelectorAll('.modal-procedure-quick-card').forEach(c => c.classList.remove('selected-card'));
        if (cardEl) {
            const quickCard = cardEl.classList.contains('modal-procedure-quick-card') ? cardEl : cardEl.querySelector('.modal-procedure-quick-card');
            if (quickCard) quickCard.classList.add('selected-card');
        }
        const select = document.getElementById('modal-procedure-type');
        if (select) {
            select.value = procName;
            updateModalPrice();
        }
    };

    // Bulk treatment controls
    if (btnOpenBulkModal) {
        btnOpenBulkModal.addEventListener('click', function() {
            if (selectedTeethSet.size === 0) return;
            const displayEl = document.getElementById('bulk-selected-teeth-display');
            if (displayEl) {
                const teethArr = Array.from(selectedTeethSet).sort((a,b) => parseInt(a)-parseInt(b));
                displayEl.textContent = teethArr.join(', ');
            }
            updateBulkPrice();
            const bulkModal = new bootstrap.Modal(document.getElementById('bulkTreatmentModal'));
            bulkModal.show();
        });
    }

    function updateBulkPrice() {
        const procSelect = document.getElementById('bulk-procedure-type');
        const customCostInput = document.getElementById('bulk-custom-cost-input');
        const useAnes = document.getElementById('bulk-use-anesthesia');
        const anesType = document.getElementById('bulk-anesthesia-type');
        const needles = document.getElementById('bulk-needles');
        const priceDisplay = document.getElementById('bulk-price-display');

        if (!procSelect || !priceDisplay) return;

        const toothCount = selectedTeethSet.size || 1;
        let unitPrice = 0;
        if (customCostInput && customCostInput.value.trim() !== '') {
            unitPrice = parseFloat(customCostInput.value) || 0;
        } else {
            const selectedOpt = procSelect.options[procSelect.selectedIndex];
            if (selectedOpt && selectedOpt.dataset.price) {
                unitPrice = parseFloat(selectedOpt.dataset.price) || 0;
            }
        }

        let anesthesiaCost = 0;
        if (useAnes && useAnes.checked && anesType && needles) {
            const anesOpt = anesType.options[anesType.selectedIndex];
            const anesUnit = anesOpt ? (parseFloat(anesOpt.dataset.price) || 0) : 0;
            const needleCount = parseInt(needles.value) || 1;
            anesthesiaCost = anesUnit * needleCount;
        }

        const totalCost = (unitPrice * toothCount) + anesthesiaCost;
        priceDisplay.textContent = `${totalCost.toLocaleString('de-DE')} ${currency} (${toothCount} ${isAr ? 'أسنان' : 'teeth'})`;
    }

    const bulkProcSelect = document.getElementById('bulk-procedure-type');
    if (bulkProcSelect) bulkProcSelect.addEventListener('change', updateBulkPrice);

    const bulkCustomCost = document.getElementById('bulk-custom-cost-input');
    if (bulkCustomCost) bulkCustomCost.addEventListener('input', updateBulkPrice);

    const bulkUseAnes = document.getElementById('bulk-use-anesthesia');
    if (bulkUseAnes) {
        bulkUseAnes.addEventListener('change', function() {
            const wrap = document.getElementById('bulk-anesthesia-details-wrapper');
            if (wrap) wrap.style.display = this.checked ? 'block' : 'none';
            updateBulkPrice();
        });
    }

    const bulkAnesType = document.getElementById('bulk-anesthesia-type');
    if (bulkAnesType) bulkAnesType.addEventListener('change', updateBulkPrice);

    const bulkNeedles = document.getElementById('bulk-needles');
    if (bulkNeedles) bulkNeedles.addEventListener('input', updateBulkPrice);

    window.filterBulkCategory = function(category, pillBtn) {
        document.querySelectorAll('.bulk-cat-pill').forEach(btn => btn.classList.remove('active', 'btn-primary'));
        if (pillBtn) pillBtn.classList.add('active');

        const cards = document.querySelectorAll('.bulk-sub-proc-item-card');
        cards.forEach(card => {
            const itemCat = card.dataset.category || 'عام';
            if (category === 'all' || itemCat === category) card.style.display = 'block';
            else card.style.display = 'none';
        });

        const procSelect = document.getElementById('bulk-procedure-type');
        if (procSelect) {
            Array.from(procSelect.options).forEach(opt => {
                if (!opt.value) return;
                const optCat = opt.dataset.category || '';
                if (category === 'all' || optCat === category) {
                    opt.style.display = '';
                    opt.disabled = false;
                } else {
                    opt.style.display = 'none';
                    opt.disabled = true;
                }
            });
        }
    };

    window.selectBulkQuickProcedure = function(procName, cardEl) {
        document.querySelectorAll('.bulk-procedure-quick-card').forEach(c => c.classList.remove('selected-card'));
        if (cardEl) {
            const quickCard = cardEl.classList.contains('bulk-procedure-quick-card') ? cardEl : cardEl.querySelector('.bulk-procedure-quick-card');
            if (quickCard) quickCard.classList.add('selected-card');
        }
        const select = document.getElementById('bulk-procedure-type');
        if (select) {
            select.value = procName;
            updateBulkPrice();
        }
    };

    // Bulk form submit via AJAX
    const bulkForm = document.getElementById('bulk-treatment-form');
    if (bulkForm) {
        bulkForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const teethArr = Array.from(selectedTeethSet);
            if (teethArr.length === 0) return;

            const procType = document.getElementById('bulk-procedure-type').value;
            const customCost = document.getElementById('bulk-custom-cost-input').value;
            const notes = document.getElementById('bulk-notes').value;
            const useAnesthesia = document.getElementById('bulk-use-anesthesia').checked;
            const anesType = document.getElementById('bulk-anesthesia-type').value;
            const needles = document.getElementById('bulk-needles').value;

            const formData = new FormData();
            formData.append('csrf_token', csrfToken);
            formData.append('teeth', teethArr.join(','));
            formData.append('procedure_type', procType);
            formData.append('custom_cost', customCost);
            formData.append('notes', notes);
            formData.append('use_anesthesia', useAnesthesia ? 'on' : 'off');
            formData.append('anesthesia_type', anesType);
            formData.append('anesthesia_needles', needles);

            fetch(`/appointments/${appointmentId}/session/bulk-treatment`, {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({ icon: 'error', title: isAr ? 'خطأ' : 'Error', text: data.message || (isAr ? 'فشل حفظ المعالجة الجماعية' : 'Failed to save bulk treatment') });
                    } else {
                        alert(data.message || 'Error saving bulk treatment');
                    }
                }
            })
            .catch(err => {
                console.error(err);
                window.location.reload();
            });
        });
    }
};
