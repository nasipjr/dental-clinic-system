/**
 * Dental Clinic Management System - Edit Treatment JavaScript Controller
 * Isolated client-side logic for FDI anatomical tooth selector, extractions validation, anesthesia controls, and delete confirmation.
 */

window.initTreatmentEdit = function (config) {
    const isAr = config.isAr !== undefined ? config.isAr : (document.documentElement.lang === 'ar' || document.dir === 'rtl');
    const isLocked = !!config.isLocked;
    const needlePrice = parseFloat(config.needlePrice) || 50000;
    const editingTreatmentId = config.editingTreatmentId;
    const currentTreatments = config.currentTreatments || [];
    const historyTreatments = config.historyTreatments || [];
    const toothHistoryDict = config.toothHistoryDict || {};

    const procSelect = document.getElementById('procedure_type');
    const customCostInput = document.getElementById('custom_cost');
    const useAnesthesia = document.getElementById('use_anesthesia');
    const needlesWrapper = document.getElementById('needles_wrapper');
    const needlesInput = document.getElementById('anesthesia_needles');
    const toothInput = document.getElementById('tooth_number');
    const selectedToothBadge = document.getElementById('selected-tooth-badge');
    const clearToothBtn = document.getElementById('btn-clear-tooth');
    const deleteActionInput = document.getElementById('delete_action');

    let prices = {};
    if (procSelect && procSelect.dataset.prices) {
        try { prices = JSON.parse(procSelect.dataset.prices); } catch (e) { }
    }

    const fdiMap = {
        1: 18, 2: 17, 3: 16, 4: 15, 5: 14, 6: 13, 7: 12, 8: 11,
        9: 21, 10: 22, 11: 23, 12: 24, 13: 25, 14: 26, 15: 27, 16: 28,
        17: 38, 18: 37, 19: 36, 20: 35, 21: 34, 22: 33, 23: 32, 24: 31,
        25: 41, 26: 42, 27: 43, 28: 44, 29: 45, 30: 46, 31: 47, 32: 48
    };

    function isExtractionProcedure(procName) {
        if (!procName) return false;
        const name = procName.toLowerCase();
        if (name.includes('ما بعد القلع') || name.includes('post-extraction')) return false;
        return name.includes('قلع') || name.includes('extract');
    }

    function appliesToTooth(treatment, toothNum) {
        if (!treatment.tooth) return false;
        const toothStr = treatment.tooth.trim();
        if (toothStr === '11-48' || toothStr === '1-32' || toothStr.toLowerCase() === 'all' || toothStr === 'كافة الأسنان' || toothStr === 'الكل') {
            return true;
        }
        const teeth = toothStr.split(',').map(s => s.trim());
        const fdiNum = fdiMap[toothNum];
        if (fdiNum && teeth.includes(String(fdiNum))) return true;
        const fdiRegex = /^(1[1-8]|2[1-8]|3[1-8]|4[1-8]|5[1-5]|6[1-5]|7[1-5]|8[1-5])$/;
        return teeth.some(t => !fdiRegex.test(t) && t === String(toothNum));
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
    const extractedTeeth = new Set();

    for (let i = 1; i <= 32; i++) {
        const toothStr = i.toString();
        const fdiNum = fdiMap[toothStr];
        activeTeeth[toothStr] = currentTreatments.filter(t => appliesToTooth(t, toothStr));
        historyTeeth[toothStr] = historyTreatments.filter(t => appliesToTooth(t, toothStr));

        const priorHistories = getToothItemsFromDict(toothHistoryDict, toothStr, fdiNum);
        const hasActiveExt = activeTeeth[toothStr].some(t => isExtractionProcedure(t.procedure) && t.id !== editingTreatmentId);
        const hasHistoryExt = historyTeeth[toothStr].some(t => isExtractionProcedure(t.procedure));
        const hasPriorExt = priorHistories.some(h => isExtractionProcedure(h.procedure));

        if (hasActiveExt || hasHistoryExt || hasPriorExt) {
            extractedTeeth.add(toothStr);
        }
    }

    function setGeneralTreatmentBadge() {
        if (selectedToothBadge) {
            selectedToothBadge.className = 'badge rounded-pill px-3 py-1.5 fw-bold fs-6';
            selectedToothBadge.style = 'background: rgba(14, 165, 233, 0.15); border: 1px solid #0ea5e9; color: #38bdf8;';
            selectedToothBadge.textContent = isAr ? 'معالجة عامة (بدون سن محدد)' : 'General (No specific tooth)';
        }
    }

    function setSelectedToothBadge(fdiNum) {
        if (selectedToothBadge) {
            selectedToothBadge.className = 'badge rounded-pill px-3 py-1.5 fw-bold fs-6';
            selectedToothBadge.style = 'background: rgba(14, 165, 233, 0.15); border: 1px solid #0ea5e9; color: #38bdf8;';
            selectedToothBadge.textContent = (isAr ? 'السن ' : 'Tooth ') + fdiNum;
        }
    }

    // Tooth Click Handler
    document.querySelectorAll('.edit-tooth-btn').forEach(btn => {
        const toothStr = btn.dataset.tooth;
        const fdiNum = fdiMap[toothStr];
        const isExtracted = extractedTeeth.has(toothStr) || extractedTeeth.has(String(fdiNum));

        if (isExtracted) {
            btn.classList.add('extracted-treatment');
        } else if (activeTeeth[toothStr] && activeTeeth[toothStr].length > 0) {
            btn.classList.add('active-treatment');
        } else if (historyTeeth[toothStr] && historyTeeth[toothStr].length > 0) {
            btn.classList.add('history-treatment');
        }

        // Build Hover Tooltip HTML
        let tooltipHtml = `<strong class="d-block mb-1">${isAr ? 'السن' : 'Tooth'} ${fdiNum}</strong>`;
        if (isExtracted) {
            tooltipHtml += `<div class="text-danger small fw-bold mb-1"><i class="bi bi-x-circle-fill me-1"></i>${isAr ? 'تم قلع السن ❌' : 'Tooth Extracted ❌'}</div>`;
        }
        if (activeTeeth[toothStr] && activeTeeth[toothStr].length > 0) {
            tooltipHtml += `<div class="text-success small mt-1"><i class="bi bi-clipboard2-pulse me-1"></i>${isAr ? 'معالجة بالجلسة الحالية:' : 'Current Session:'}</div>`;
            activeTeeth[toothStr].forEach(t => {
                const docText = t.doctor ? ` (${t.doctor})` : '';
                tooltipHtml += `<div class="ms-2 small text-nowrap">• ${t.procedure}${docText}</div>`;
            });
        }
        if (historyTeeth[toothStr] && historyTeeth[toothStr].length > 0) {
            tooltipHtml += `<div class="text-info small mt-1"><i class="bi bi-clock-history me-1"></i>${isAr ? 'معالجات سابقة بالعيادة:' : 'Clinic History:'}</div>`;
            historyTeeth[toothStr].forEach(t => {
                const docText = t.doctor ? ` - د. ${t.doctor}` : '';
                tooltipHtml += `<div class="ms-2 small text-nowrap">• ${t.procedure} (${t.date.split(' ')[0]})${docText}</div>`;
            });
        }

        btn.setAttribute('data-bs-toggle', 'tooltip');
        btn.setAttribute('data-bs-html', 'true');
        btn.setAttribute('data-bs-title', tooltipHtml);

        btn.addEventListener('click', function () {
            if (isLocked) return;

            const selectedProc = procSelect ? procSelect.value.toLowerCase() : '';
            const isPostExtraction = selectedProc.includes('بعد القلع') || selectedProc.includes('post-extraction');

            if (isExtracted && !isPostExtraction) {
                alert(isAr ? `عذراً! السن ${fdiNum} مقلوع سابقاً. لا يمكن إضافة أو تعديل معالجات على سن مقلوع سوى (معالجة ما بعد القلع).`
                    : `Tooth ${fdiNum} is extracted. Only post-extraction care can be assigned.`);
                return;
            }

            if (toothInput.value === toothStr || toothInput.value === String(fdiNum)) {
                // Deselect -> Switch to general mouth treatment
                toothInput.value = '';
                if (deleteActionInput) deleteActionInput.value = '0';
                document.querySelectorAll('.edit-tooth-btn').forEach(b => b.classList.remove('selected-tooth'));
                setGeneralTreatmentBadge();
            } else {
                // Select tooth
                if (deleteActionInput) deleteActionInput.value = '0';
                document.querySelectorAll('.edit-tooth-btn').forEach(b => b.classList.remove('selected-tooth'));
                this.classList.add('selected-tooth');
                toothInput.value = toothStr;
                setSelectedToothBadge(fdiNum);
            }
        });
    });

    // Initialize Bootstrap tooltips safely
    if (window.bootstrap && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    if (clearToothBtn) {
        clearToothBtn.addEventListener('click', function () {
            if (isLocked) return;
            toothInput.value = '';
            if (deleteActionInput) deleteActionInput.value = '0';
            document.querySelectorAll('.edit-tooth-btn').forEach(b => b.classList.remove('selected-tooth'));
            setGeneralTreatmentBadge();
        });
    }

    window.triggerDeleteTreatment = function () {
        if (isLocked) return;
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: isAr ? 'حذف المعالجة' : 'Delete Treatment',
                text: isAr ? 'هل أنت متأكد من إلغاء وحذف هذه المعالجة نهائياً وتحديث الفاتورة؟' : 'Are you sure you want to permanently delete this treatment and update the invoice?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: isAr ? 'نعم، حذف المعالجة' : 'Yes, delete treatment',
                cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    if (deleteActionInput) deleteActionInput.value = '1';
                    const form = document.getElementById('edit-treatment-form');
                    if (form) form.submit();
                }
            });
        } else {
            if (confirm(isAr ? 'هل أنت متأكد من إلغاء وحذف هذه المعالجة نهائياً وتحديث الفاتورة؟' : 'Are you sure you want to permanently delete this treatment and update the invoice?')) {
                if (deleteActionInput) deleteActionInput.value = '1';
                const form = document.getElementById('edit-treatment-form');
                if (form) form.submit();
            }
        }
    };

    // Anesthesia toggle
    if (useAnesthesia && needlesWrapper) {
        useAnesthesia.addEventListener('change', function () {
            if (isLocked) return;
            needlesWrapper.style.display = this.checked ? 'block' : 'none';
            updateDefaultPrice();
        });
    }

    if (needlesInput) {
        needlesInput.addEventListener('input', function () {
            if (isLocked) return;
            updateDefaultPrice();
        });
    }

    if (procSelect) {
        procSelect.addEventListener('change', function () {
            if (isLocked) return;
            updateDefaultPrice();
        });
    }

    function updateDefaultPrice() {
        if (isLocked) return;
        const proc = procSelect ? procSelect.value : '';
        if (!proc || prices[proc] === undefined) return;

        const basePrice = parseFloat(prices[proc]) || 0;
        const withAnesthesia = useAnesthesia ? useAnesthesia.checked : false;
        const needlesCount = needlesInput ? (parseInt(needlesInput.value) || 1) : 1;
        const anesthesiaCost = withAnesthesia ? needlesCount * needlePrice : 0;
        const defaultTotal = basePrice + anesthesiaCost;

        if (customCostInput) {
            customCostInput.value = Math.round(defaultTotal);
        }
    }

    // Doctor Select Live Update
    const docSelect = document.getElementById('doctor_id');
    const attendingDocName = document.getElementById('attending-doctor-name');
    if (docSelect && attendingDocName) {
        docSelect.addEventListener('change', function () {
            const selectedOpt = this.options[this.selectedIndex];
            if (selectedOpt) {
                attendingDocName.textContent = selectedOpt.text.replace(/^د\.\s*/, '').replace(/\s*\([^)]*\)$/, '');
            }
        });
    }
};
