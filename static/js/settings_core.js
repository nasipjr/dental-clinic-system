/**
 * Dental Clinic Management System - Settings Core JavaScript Controller
 * Clean, modularized and isolated logic for the settings page.
 */

// ── Global Scope Helpers ──────────────────────────────────────────────────
function getIsArabic() {
    try {
        return document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
    } catch (e) {
        return document.documentElement.getAttribute('lang') === 'ar' || document.dir === 'rtl';
    }
}

window.getIsArabic = getIsArabic;

window.addNewAnesthesiaRow = function () {
    const tbody = document.getElementById('anesthesia-types-list');
    if (!tbody) return;
    const isAr = getIsArabic();
    const namePlaceholder = isAr ? 'اسم نوع التخدير الجديد' : 'New Anesthesia Type Name';
    const deleteTooltip = isAr ? 'حذف نوع التخدير' : 'Delete Anesthesia';
    const currencySymbol = window.settingsConfig ? window.settingsConfig.currencySymbol : 'SP';
    const row = document.createElement("tr");
    row.className = "anesthesia-row";
    row.innerHTML = `
        <td class="ps-3.5 py-2">
            <input type="text" name="anesthesia_names[]" form="main-settings-form" class="form-control form-control-sm treatment-name-input px-2 py-1" required placeholder="${namePlaceholder}">
        </td>
        <td class="py-2">
            <div class="input-group input-group-sm treatment-input-pill overflow-hidden" style="max-width: 170px;">
                <input type="text" name="anesthesia_prices[]" form="main-settings-form" class="form-control form-control-sm border-0 bg-transparent font-monospace text-end fw-bold px-2.5" value="50000" required placeholder="0">
                <span class="input-group-text unit-badge border-0 text-primary small fw-bold px-2.5">${currencySymbol}</span>
            </div>
        </td>
        <td class="text-center pe-3.5 py-2">
            <button type="button" class="btn btn-outline-danger btn-sm rounded-circle d-inline-flex align-items-center justify-content-center p-0" style="width:30px;height:30px;border: 1px solid rgba(239, 68, 68, 0.25); background: rgba(239, 68, 68, 0.08); color: #f87171;" onclick="deleteAnesthesiaRow(this)" data-tooltip="${deleteTooltip}">
                <i class="bi bi-trash3"></i>
            </button>
        </td>
    `;
    tbody.appendChild(row);
    const input = row.querySelector('input[name="anesthesia_names[]"]');
    if (input) {
        input.focus();
    }
};

window.deleteAnesthesiaRow = function (btn) {
    const row = btn ? btn.closest("tr") : null;
    if (!row) return;
    row.remove();
};

window.filterCategoryPill = function (catKey, btn) {
    document.querySelectorAll('#procedure-cat-pills .cat-pill-btn').forEach(b => {
        b.classList.remove('active');
    });
    if (btn) btn.classList.add('active');

    const searchInput = document.getElementById('search-settings-procedures');
    if (searchInput && catKey !== 'all') {
        searchInput.value = '';
    }

    const blocks = document.querySelectorAll('.procedure-category-block');
    blocks.forEach(block => {
        const blockCat = block.getAttribute('data-category');
        if (catKey === 'all') {
            const countBadge = block.querySelector('.cat-count-badge');
            const cnt = countBadge ? parseInt(countBadge.textContent || '0', 10) : 0;
            if (cnt > 0) {
                block.classList.remove('d-none');
                block.style.display = '';
            } else {
                block.style.display = 'none';
            }
        } else if (blockCat === catKey) {
            block.classList.remove('d-none');
            block.style.display = '';
        } else {
            block.style.display = 'none';
        }
    });
};

window.filterSettingsProcedures = function () {
    const input = document.getElementById('search-settings-procedures');
    if (!input) return;
    const q = input.value.toLowerCase().trim();

    const blocks = document.querySelectorAll('.procedure-category-block');
    blocks.forEach(block => {
        let hasMatch = false;
        const rows = block.querySelectorAll('tr.procedure-row');
        rows.forEach(r => {
            const inp = r.querySelector('input[name="procedure_names[]"]');
            const txt = inp ? inp.value.toLowerCase() : '';
            if (!q || txt.includes(q)) {
                r.style.display = '';
                hasMatch = true;
            } else {
                r.style.display = 'none';
            }
        });
        if (q) {
            block.style.display = hasMatch ? '' : 'none';
        } else {
            const activePill = document.querySelector('#procedure-cat-pills .cat-pill-btn.active');
            const currentCat = activePill ? activePill.getAttribute('data-cat') : 'all';
            block.style.display = (currentCat === 'all' || block.getAttribute('data-category') === currentCat) ? '' : 'none';
        }
    });
};

window.addNewProcedureRow = function (targetCategory) {
    const catKey = targetCategory || 'إجراءات عامة وأخرى';
    let targetBlock = document.querySelector(`.procedure-category-block[data-category="${catKey}"]`);
    if (!targetBlock) {
        targetBlock = document.querySelector('.procedure-category-block[data-category="إجراءات عامة وأخرى"]') || document.querySelector('.procedure-category-block');
    }
    if (!targetBlock) return;

    const tbody = targetBlock.querySelector('tbody.procedures-group-list');
    if (!tbody) return;

    const isAr = getIsArabic();
    const namePlaceholder = isAr ? 'اسم الإجراء الجديد' : 'New Procedure Name';
    const deleteTooltip = isAr ? 'حذف الإجراء' : 'Delete Procedure';
    const currencySymbol = window.settingsConfig ? window.settingsConfig.currencySymbol : 'SP';
    const row = document.createElement("tr");
    row.className = "procedure-row";
    row.innerHTML = `
        <td class="ps-3.5 py-2">
            <input type="text" name="procedure_names[]" form="main-settings-form" class="form-control form-control-sm treatment-name-input px-2 py-1 text-truncate" required placeholder="${namePlaceholder}">
            <input type="hidden" name="procedure_categories[]" form="main-settings-form" value="${catKey}">
            <input type="hidden" name="procedure_actives[]" form="main-settings-form" value="true">
        </td>
        <td class="py-2">
            <div class="input-group input-group-sm treatment-input-pill overflow-hidden" style="max-width: 130px;">
                <input type="number" name="procedure_durations[]" form="main-settings-form" class="form-control form-control-sm border-0 bg-transparent text-center font-monospace fw-bold" value="30" min="5" max="300" step="5" required placeholder="30">
                <span class="input-group-text unit-badge border-0 small px-2.5">${isAr ? 'دقيقة' : 'min'}</span>
            </div>
        </td>
        <td class="py-2">
            <div class="input-group input-group-sm treatment-input-pill overflow-hidden" style="max-width: 160px;">
                <input type="text" name="procedure_prices[]" form="main-settings-form" class="form-control form-control-sm border-0 bg-transparent font-monospace text-end fw-bold px-2.5" value="50000" required placeholder="0">
                <span class="input-group-text unit-badge border-0 text-primary small fw-bold px-2.5">${currencySymbol}</span>
            </div>
        </td>
        <td class="text-center pe-3.5 py-2">
            <button type="button" class="btn btn-outline-danger btn-sm rounded-circle d-inline-flex align-items-center justify-content-center p-0" style="width:30px;height:30px;border: 1px solid rgba(239, 68, 68, 0.25); background: rgba(239, 68, 68, 0.08); color: #f87171;" onclick="deleteProcedureRow(this)" data-tooltip="${deleteTooltip}">
                <i class="bi bi-trash3"></i>
            </button>
        </td>
    `;
    tbody.appendChild(row);

    targetBlock.classList.remove('d-none');
    targetBlock.style.display = '';
    const badge = targetBlock.querySelector('.cat-count-badge');
    if (badge) {
        badge.textContent = tbody.querySelectorAll('tr.procedure-row').length;
    }

    const nameInput = row.querySelector('input[name="procedure_names[]"]');
    if (nameInput) {
        nameInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => nameInput.focus(), 150);
    }
};

window.deleteProcedureRow = function (btn) {
    const row = btn ? btn.closest("tr") : null;
    if (!row) return;

    const nameInput = row.querySelector('input[name="procedure_names[]"]');
    const procName = nameInput ? nameInput.value.trim() : '';
    const isAr = getIsArabic();

    const protectedProcs = [
        'قلع سن عادي', 'قلع سن', 'معالجة ما بعد القلع', 'Extraction', 'Tooth Extraction', 'Post-Extraction Treatment',
        'جلسة فحص و استشارة', 'جلسة فحص واستشارة', 'فحص دوري واستشارة', 'فحص دوري', 'Check-up', 'Clinical Examination & Consultation'
    ];
    if (protectedProcs.includes(procName)) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: isAr ? '🔒 إجراء محمي بالنظام' : '🔒 Protected System Procedure',
                text: isAr ? `الإجراء (${procName}) هو إجراء أساسي محمي بالنظام ولا يمكن حذفه.` : `Procedure "${procName}" is an essential system procedure and cannot be deleted.`,
                icon: 'info',
                confirmButtonText: isAr ? 'حسناً' : 'OK',
                confirmButtonColor: '#0d6efd'
            });
        } else {
            alert(isAr ? `الإجراء (${procName}) محمي بالنظام ولا يمكن حذفه.` : `Procedure "${procName}" is protected and cannot be deleted.`);
        }
        return;
    }

    const confirmText = procName
        ? (isAr ? `هل أنت متأكد من رغبتك في حذف الإجراء (${procName})؟` : `Are you sure you want to delete procedure "${procName}"?`)
        : (isAr ? 'هل أنت متأكد من رغبتك في حذف هذا الإجراء؟' : 'Are you sure you want to delete this procedure?');

    const doDelete = function () {
        row.style.transition = 'opacity 0.25s, transform 0.25s';
        row.style.opacity = '0';
        row.style.transform = 'scale(0.95)';
        setTimeout(() => { row.remove(); }, 250);
    };

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isAr ? '⚠️ تأكيد حذف الإجراء' : '⚠️ Confirm Delete Procedure',
            text: confirmText,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: isAr ? 'نعم، حذف' : 'Yes, Delete',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                doDelete();
            }
        });
    } else {
        if (confirm(confirmText)) {
            doDelete();
        }
    }
};

window.setAppTheme = function (theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    document.cookie = "theme=" + theme + ";path=/;max-age=31536000;SameSite=Lax";
    updateThemeButtons(theme);
};

function updateThemeButtons(theme) {
    const lightBtn = document.getElementById('theme-light-btn');
    const darkBtn = document.getElementById('theme-dark-btn');
    if (!lightBtn || !darkBtn) return;

    if (theme === 'dark') {
        darkBtn.classList.add('active');
        lightBtn.classList.remove('active');
    } else {
        lightBtn.classList.add('active');
        darkBtn.classList.remove('active');
    }
}

window.setAppLang = function (lang) {
    document.cookie = "lang=" + lang + ";path=/;max-age=31536000;SameSite=Lax";
    localStorage.setItem('lang', lang);
    updateLangButtons(lang);
    window.location.reload();
};

function updateLangButtons(lang) {
    const enBtn = document.getElementById('lang-en-btn');
    const arBtn = document.getElementById('lang-ar-btn');
    if (!enBtn || !arBtn) return;

    if (lang === 'ar') {
        arBtn.classList.add('active');
        enBtn.classList.remove('active');
    } else {
        enBtn.classList.add('active');
        arBtn.classList.remove('active');
    }
}

window.deleteUser = function (userId) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/settings/users/${userId}/delete`;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = window.settingsConfig ? window.settingsConfig.csrfToken : '';
    form.appendChild(csrfInput);
    document.body.appendChild(form);
    form.submit();
};

window.confirmDeleteUser = function (userId, username) {
    const isAr = getIsArabic();
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isAr ? 'حذف حساب المستخدم' : 'Delete User Account',
            text: isAr ? `هل أنت متأكد من رغبتك في حذف المستخدم (${username})؟` : `Are you sure you want to delete user (${username})?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: isAr ? 'نعم، حذف المستخدم' : 'Yes, delete user',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                window.deleteUser(userId);
            }
        });
    } else {
        if (confirm(isAr ? 'هل أنت متأكد من رغبتك في حذف هذا المستخدم؟' : 'Are you sure you want to delete this user?')) {
            window.deleteUser(userId);
        }
    }
};

window.createBackup = function () {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = window.settingsConfig ? window.settingsConfig.createBackupUrl : '/settings/backups/create';
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = window.settingsConfig ? window.settingsConfig.csrfToken : '';
    form.appendChild(csrfInput);
    document.body.appendChild(form);
    form.submit();
};

window.deleteBackup = function (filename) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/settings/backups/${encodeURIComponent(filename)}/delete`;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = window.settingsConfig ? window.settingsConfig.csrfToken : '';
    form.appendChild(csrfInput);
    document.body.appendChild(form);
    form.submit();
};

window.confirmDeleteBackup = function (filename) {
    const isAr = getIsArabic();
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isAr ? 'حذف النسخة الاحتياطية' : 'Delete Backup File',
            text: isAr ? `هل أنت متأكد من رغبتك في حذف ملف النسخة الاحتياطية (${filename})؟` : `Are you sure you want to delete backup file (${filename})?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: isAr ? 'نعم، حذف الملف' : 'Yes, delete file',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                window.deleteBackup(filename);
            }
        });
    } else {
        if (confirm(isAr ? 'هل أنت متأكد من رغبتك في حذف ملف النسخة الاحتياطية هذا؟' : 'Are you sure you want to delete this backup file?')) {
            window.deleteBackup(filename);
        }
    }
};

window.normalizeArabicText = function (text) {
    if (!text) return '';
    return text.toString().toLowerCase()
        .replace(/[أإآ]/g, 'ا')
        .replace(/ة/g, 'ه')
        .replace(/ى/g, 'ي')
        .trim();
};

window.filterUserTable = function (tbodyId, query) {
    const q = window.normalizeArabicText(query);
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    const rows = tbody.querySelectorAll('tr');
    rows.forEach(row => {
        const username = row.children[0] ? row.children[0].textContent : '';
        const fullName = row.children[1] ? row.children[1].textContent : '';
        const combined = window.normalizeArabicText(username + ' ' + fullName);

        if (!q || combined.includes(q)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
};

window.triggerResetClinicFlow = function () {
    const isAr = getIsArabic();
    const openModal = function () {
        const modalEl = document.getElementById('resetClinicModal');
        if (modalEl) {
            const bsModal = new bootstrap.Modal(modalEl);
            bsModal.show();
        }
    };

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isAr ? '⚠️ تصفير سجلات العيادة' : '⚠️ Reset Operational Data',
            html: isAr ? `
                <div class="text-end dir-rtl p-1" style="direction: rtl; text-align: right;">
                    <p class="fw-bold text-danger mb-3 fs-6" style="line-height: 1.5;">هل أنت متأكد من رغبتك في تصفير وحذف سجلات العيادة التشغيلية؟</p>
                    <div class="p-3 bg-danger bg-opacity-10 border border-danger border-opacity-25 rounded-3 mb-3 small">
                        <div class="fw-bold mb-2 text-danger d-flex align-items-center gap-2" style="font-size: 0.92rem;">
                            <i class="bi bi-x-circle-fill fs-6"></i>
                            <span>سيتم حذف:</span>
                        </div>
                        <ul class="mb-0 text-secondary" style="list-style-type: disc; padding-right: 1.25rem; padding-left: 0; margin-right: 0.25rem; text-align: right; direction: rtl;">
                            <li class="mb-1">جميع المرضى والملفات والتقارير الطبية</li>
                            <li class="mb-1">جميع المواعيد والجلسات المعالجة</li>
                            <li>كافة الفواتير والمدفوعات والمصاريف</li>
                        </ul>
                    </div>
                    <div class="p-2.5 bg-success bg-opacity-10 border border-success border-opacity-25 rounded-3 small">
                        <div class="fw-bold text-success mb-1 d-flex align-items-center gap-2" style="font-size: 0.92rem;">
                            <i class="bi bi-check-circle-fill fs-6"></i>
                            <span>سيتم الحفاظ على:</span>
                        </div>
                        <span class="text-secondary small d-block" style="padding-right: 0.25rem;">إعدادات العيادة، توكنز الإشعارات، أسعار المعالجات، وحسابات المستخدمين والكوادر والمدراء.</span>
                    </div>
                </div>
            ` : 'Are you sure you want to reset operational clinic data?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: isAr ? 'متابعة للتحقق الأمني ⟵' : 'Proceed to Admin Verification ➔',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel',
            reverseButtons: isAr ? false : true
        }).then((result) => {
            if (result.isConfirmed) {
                openModal();
            }
        });
    } else {
        openModal();
    }
};

window.triggerFactoryResetClinicFlow = function () {
    const isAr = getIsArabic();
    const openModal = function () {
        const modalEl = document.getElementById('factoryResetClinicModal');
        if (modalEl) {
            const bsModal = new bootstrap.Modal(modalEl);
            bsModal.show();
        }
    };

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isAr ? '⚠️ تحذير شديد الخطورة (ضبط مصنعي)' : '⚠️ CRITICAL WARNING (Factory Reset)',
            html: isAr ? `
                <div class="text-end dir-rtl p-1" style="direction: rtl; text-align: right;">
                    <p class="fw-bold text-danger mb-3 fs-6" style="line-height: 1.5;">هل أنت متأكد تماماً من رغبتك في تصفير العيادة بالكامل وإعادتها لضبط المصنع؟</p>
                    <div class="p-3 bg-danger bg-opacity-10 border border-danger border-opacity-25 rounded-3 mb-3 small">
                        <div class="fw-bold mb-2 text-danger d-flex align-items-center gap-2" style="font-size: 0.92rem;">
                            <i class="bi bi-x-circle-fill fs-6"></i>
                            <span>سيتم مسح وتصفير:</span>
                        </div>
                        <ul class="mb-0 text-secondary" style="list-style-type: disc; padding-right: 1.25rem; padding-left: 0; margin-right: 0.25rem; text-align: right; direction: rtl;">
                            <li class="mb-1">جميع المرضى والملفات والتقارير الطبية</li>
                            <li class="mb-1">جميع المواعيد والجلسات المعالجة</li>
                            <li class="mb-1">كافة الفواتير والمدفوعات والمصاريف</li>
                            <li>جميع حسابات المستخدمين والكوادر والمدراء</li>
                        </ul>
                    </div>
                    <div class="p-2.5 bg-primary bg-opacity-10 border border-primary border-opacity-25 rounded-3 small">
                        <div class="fw-bold text-primary mb-1 d-flex align-items-center gap-2" style="font-size: 0.92rem;">
                            <i class="bi bi-arrow-counterclockwise fs-6"></i>
                            <span>سيتم الاستعادة التلقائية:</span>
                        </div>
                        <span class="text-secondary small d-block" style="padding-right: 0.25rem;">استعادة كافة الإعدادات والأسعار والأزمنة الافتراضية، وإنشاء حساب المدير الافتراضي الوحيد (admin / admin123).</span>
                    </div>
                </div>
            ` : 'Are you sure you want to perform a full factory reset of the clinic?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: isAr ? 'متابعة للتحقق الأمني ⟵' : 'Proceed to Admin Verification ➔',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel',
            reverseButtons: isAr ? false : true
        }).then((result) => {
            if (result.isConfirmed) {
                openModal();
            }
        });
    } else {
        openModal();
    }
};

window.triggerRestoreLatestBackupFlow = function () {
    const isAr = getIsArabic();
    const openModal = function () {
        const modalEl = document.getElementById('restoreBackupModal');
        if (modalEl) {
            const bsModal = new bootstrap.Modal(modalEl);
            bsModal.show();
        }
    };

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isAr ? '⚠️ استعادة أحدث نسخة احتياطية' : '⚠️ Restore Latest Backup',
            html: isAr ? `
                <div class="text-end dir-rtl p-1" style="direction: rtl; text-align: right;">
                    <p class="fw-bold text-warning text-dark-emphasis mb-2 fs-6" style="line-height: 1.5;">هل أنت متأكد من رغبتك في استعادة كافة بيانات العيادة؟</p>
                    <div class="p-3 bg-warning bg-opacity-10 border border-warning border-opacity-25 rounded-3 mb-2 small text-secondary">
                        <div class="d-flex align-items-center gap-2 text-warning mb-1 fw-bold">
                            <i class="bi bi-info-circle-fill"></i>
                            <span>تنبيه الاستعادة:</span>
                        </div>
                        <span class="d-block" style="padding-right: 0.25rem;">سيتم استبدال واسترجاع كافة سجلات المرضى والمواعيد والفواتير الموجودة بأحدث نسخة احتياطية محفوظة تلقائياً في النظام.</span>
                    </div>
                </div>
            ` : 'Are you sure you want to restore clinic database from the latest saved backup file?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#ffc107',
            cancelButtonColor: '#6c757d',
            confirmButtonText: isAr ? 'متابعة للتحقق الأمني ⟵' : 'Proceed to Admin Verification ➔',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel',
            reverseButtons: isAr ? false : true
        }).then((result) => {
            if (result.isConfirmed) {
                openModal();
            }
        });
    } else {
        openModal();
    }
};

window.confirmDeductSalary = function (form, e) {
    if (e) e.preventDefault();
    const isAr = getIsArabic();
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isAr ? 'خصم الراتب كمصروف' : 'Deduct Salary Now',
            text: isAr ? 'هل تريد خصم الراتب الآن وتسجيله كمصروف في سجل المصاريف؟' : 'Deduct salary now and log it as an expense?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ffc107',
            cancelButtonColor: '#6c757d',
            confirmButtonText: isAr ? 'نعم، الخصم الآن' : 'Yes, deduct now',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
        }).then((result) => {
            if (result.isConfirmed) {
                Swal.fire({
                    title: isAr ? 'جاري خصم وتسجيل الراتب...' : 'Processing Deduction...',
                    text: isAr ? 'يرجى الانتظار لحين تحويل المبلغ لسجل المصاريف' : 'Please wait while recording salary expense...',
                    allowOutsideClick: false,
                    didOpen: () => { Swal.showLoading(); }
                });
                setTimeout(function () {
                    if (typeof form.submit === 'function') {
                        form.submit();
                    } else {
                        HTMLFormElement.prototype.submit.call(form);
                    }
                }, 100);
            }
        });
    } else {
        if (confirm(isAr ? 'هل تريد خصم الراتب الآن وتسجيله كمصروف؟' : 'Deduct salary now and log it as an expense?')) {
            form.submit();
        }
    }
    return false;
};

window.copyNetworkUrlToClipboard = function () {
    const input = document.getElementById('local-network-url-input');
    if (!input) return;

    input.select();
    input.setSelectionRange(0, 99999);

    let copied = false;
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(input.value);
            copied = true;
        }
    } catch (e) { }

    if (!copied) {
        try {
            document.execCommand('copy');
            copied = true;
        } catch (err) { }
    }

    const btnText = document.getElementById('copy-btn-text');
    if (btnText) {
        const isAr = getIsArabic();
        const original = btnText.textContent;
        btnText.textContent = isAr ? 'تم النسخ!' : 'Copied!';
        setTimeout(() => { btnText.textContent = original; }, 2000);
    }
};

// ── Master Settings Initialization ─────────────────────────────────────────
window.initSettingsPage = function (config) {
    window.settingsConfig = config || {};
    const mainForm = document.getElementById("main-settings-form");
    const saveWrapper = document.getElementById("save-settings-btn-wrapper");

    // ── Toggle Save button visibility based on active tab ──
    function toggleSaveButton() {
        if (!saveWrapper) return;
        const usersTab = document.getElementById("tab-users");
        const appearanceTab = document.getElementById("tab-appearance");
        const updatesTab = document.getElementById("tab-updates");
        const backupsTab = document.getElementById("tab-backups");
        const notificationsTab = document.getElementById("tab-notifications");
        const notifLogsPane = document.getElementById("notif-logs-pane");

        const isUsersActive = usersTab && usersTab.classList.contains("show") && usersTab.classList.contains("active");
        const isAppearanceActive = appearanceTab && appearanceTab.classList.contains("show") && appearanceTab.classList.contains("active");
        const isUpdatesActive = updatesTab && updatesTab.classList.contains("show") && updatesTab.classList.contains("active");
        const isBackupsActive = backupsTab && backupsTab.classList.contains("show") && backupsTab.classList.contains("active");
        const isLogsActive = notificationsTab && notificationsTab.classList.contains("show") && notificationsTab.classList.contains("active") && notifLogsPane && notifLogsPane.classList.contains("show") && notifLogsPane.classList.contains("active");

        if (isUsersActive || isAppearanceActive || isUpdatesActive || isBackupsActive || isLogsActive) {
            saveWrapper.style.display = "none";
        } else {
            saveWrapper.style.display = "flex";
        }
    }

    // ── Notifications subtab hook ──
    const notifLogsTabBtn = document.getElementById("notif-logs-tab");
    const notifConfigTabBtn = document.getElementById("notif-config-tab");
    if (notifLogsTabBtn && notifConfigTabBtn) {
        notifLogsTabBtn.addEventListener("shown.bs.tab", toggleSaveButton);
        notifConfigTabBtn.addEventListener("shown.bs.tab", toggleSaveButton);
    }

    // Initialize button states based on current theme and language
    const currentTheme = document.documentElement.getAttribute('data-bs-theme') || localStorage.getItem('theme') || 'light';
    updateThemeButtons(currentTheme);

    const currentLang = window.settingsConfig.currentLang || 'ar';
    updateLangButtons(currentLang);

    // ── Hash-based tab activation ──
    const hash = window.location.hash;
    if (hash) {
        const tabTriggerEl = document.querySelector(`button[data-bs-target="${hash}"]`);
        if (tabTriggerEl) {
            const tab = new bootstrap.Tab(tabTriggerEl);
            tab.show();
        }
    }

    // Listen for tab changes
    document.querySelectorAll('#settings-tabs button[data-bs-toggle="pill"]').forEach(function (btn) {
        btn.addEventListener("shown.bs.tab", function (e) {
            const targetHash = e.target.getAttribute("data-bs-target");
            const activeTabInput = document.getElementById("active-tab-input");
            if (activeTabInput) {
                activeTabInput.value = targetHash;
            }
            if (mainForm && targetHash) {
                mainForm.action = window.settingsConfig.settingsPageUrl + targetHash;
            }
            toggleSaveButton();
        });
    });
    toggleSaveButton();

    // ── Defensive Form Submit Verification with Custom Validation ──
    if (mainForm) {
        mainForm.addEventListener("submit", function (event) {
            const nameInput = document.getElementById("clinic_name");
            const currencyInput = document.getElementById("currency_symbol");
            const bookingDaysInput = document.getElementById("booking_window_days");

            if (nameInput && !nameInput.value.trim()) {
                nameInput.value = "عيادة الأسنان";
            }
            if (currencyInput && !currencyInput.value.trim()) {
                currencyInput.value = "SP";
            }
            if (bookingDaysInput && (isNaN(parseInt(bookingDaysInput.value, 10)) || parseInt(bookingDaysInput.value, 10) <= 0)) {
                bookingDaysInput.value = "30";
            }
        });
    }

    // ── Edit User Modal population ──
    document.querySelectorAll(".edit-user-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            const userId = this.dataset.userId;
            const username = this.dataset.username;
            const firstName = this.dataset.firstName;
            const lastName = this.dataset.lastName;
            const role = this.dataset.role;

            document.getElementById("edit_username").value = username;
            document.getElementById("edit_first_name").value = firstName;
            document.getElementById("edit_last_name").value = lastName;
            document.getElementById("edit_password").value = "";

            const roleWrapper = document.getElementById("edit_role_wrapper");
            const roleSelect = document.getElementById("edit_role");
            const patientRoleInfo = document.getElementById("edit_patient_role_info");

            if (role === 'patient') {
                if (roleWrapper) roleWrapper.style.display = 'none';
                if (patientRoleInfo) patientRoleInfo.style.display = 'block';
                if (roleSelect) roleSelect.value = 'patient';
            } else {
                if (roleWrapper) roleWrapper.style.display = 'block';
                if (patientRoleInfo) patientRoleInfo.style.display = 'none';
                if (roleSelect) roleSelect.value = role;
            }

            const form = document.getElementById("editUserForm");
            form.action = `/settings/users/${userId}/edit`;
        });
    });

    // ── Test Buttons Event Listeners ──
    const getCsrfToken = () => {
        const el = document.querySelector('input[name="csrf_token"]');
        return el ? el.value : (window.settingsConfig ? window.settingsConfig.csrfToken : '');
    };

    function sendTestRequest(url, data, btn, resultDiv) {
        const isAr = getIsArabic();
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> ${isAr ? 'جاري الإرسال...' : 'Sending...'}`;
        resultDiv.style.display = 'block';
        resultDiv.className = 'col-md-12 mt-1 alert alert-info py-2';
        resultDiv.textContent = isAr ? 'جاري الإرسال...' : 'Sending...';

        const formData = new FormData();
        for (const key in data) {
            formData.append(key, data[key]);
        }
        formData.append('csrf_token', getCsrfToken());

        fetch(url, {
            method: 'POST',
            body: formData
        })
            .then(res => {
                if (!res.ok) {
                    return res.text().then(text => {
                        throw new Error(text || 'HTTP ' + res.status);
                    });
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    resultDiv.className = 'col-md-12 mt-1 alert alert-success py-2';
                    resultDiv.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i> ' + data.message;
                } else {
                    resultDiv.className = 'col-md-12 mt-1 alert alert-danger py-2';
                    resultDiv.innerHTML = '<i class="bi bi-exclamation-triangle-fill me-1"></i> ' + data.message;
                }
            })
            .catch(err => {
                resultDiv.className = 'col-md-12 mt-1 alert alert-danger py-2';
                resultDiv.textContent = (isAr ? 'حدث خطأ: ' : 'Error: ') + err.message;
            })
            .finally(() => {
                btn.disabled = false;
                const isAr = getIsArabic();
                btn.innerHTML = btn.id === 'btn-test-sms' ? (isAr ? '<i class="bi bi-send-fill me-1"></i> اختبار SMS' : '<i class="bi bi-send-fill me-1"></i> Send Test SMS') :
                    btn.id === 'btn-test-telegram' ? (isAr ? '<i class="bi bi-send-fill me-1"></i> اختبار تيليغرام' : '<i class="bi bi-send-fill me-1"></i> Test Telegram') :
                        (isAr ? '<i class="bi bi-send-fill me-1"></i> اختبار البريد' : '<i class="bi bi-send-fill me-1"></i> Send Test Email');
            });
    }

    const btnTestSms = document.getElementById('btn-test-sms');
    if (btnTestSms) {
        btnTestSms.addEventListener('click', function () {
            const phone = document.getElementById('test_sms_phone').value.trim();
            const apiKey = document.getElementById('commpeak_api_key').value.trim();
            const streamId = document.getElementById('commpeak_stream_id').value.trim();
            const resultDiv = document.getElementById('test-sms-result');
            sendTestRequest('/settings/test-sms', {
                phone: phone,
                api_key: apiKey,
                stream_id: streamId
            }, btnTestSms, resultDiv);
        });
    }

    const btnTestTelegram = document.getElementById('btn-test-telegram');
    if (btnTestTelegram) {
        btnTestTelegram.addEventListener('click', function () {
            const chatId = document.getElementById('test_telegram_chat_id').value.trim();
            const botToken = document.getElementById('telegram_bot_token').value.trim();
            const resultDiv = document.getElementById('test-telegram-result');
            sendTestRequest('/settings/test-telegram', {
                chat_id: chatId,
                bot_token: botToken
            }, btnTestTelegram, resultDiv);
        });
    }

    const btnTestEmail = document.getElementById('btn-test-email');
    if (btnTestEmail) {
        btnTestEmail.addEventListener('click', function () {
            const email = document.getElementById('test_email_address').value.trim();
            const smtpHost = document.getElementById('smtp_host').value.trim();
            const smtpPort = document.getElementById('smtp_port').value.trim();
            const smtpUser = document.getElementById('smtp_user').value.trim();
            const smtpPassword = document.getElementById('smtp_password').value.trim();
            const smtpFromEmail = document.getElementById('smtp_from_email').value.trim();
            const resultDiv = document.getElementById('test-email-result');
            sendTestRequest('/settings/test-email', {
                email: email,
                smtp_host: smtpHost,
                smtp_port: smtpPort,
                smtp_user: smtpUser,
                smtp_password: smtpPassword,
                smtp_from_email: smtpFromEmail
            }, btnTestEmail, resultDiv);
        });
    }

    // System update event listener
    const btnCheckUpdate = document.getElementById('check-update-btn');
    if (btnCheckUpdate) {
        btnCheckUpdate.addEventListener('click', function (e) {
            e.preventDefault();
            const btn = btnCheckUpdate;
            const box = document.getElementById('update-result-box');
            const alert = document.getElementById('update-result-alert');
            const isAr = getIsArabic();

            if (!btn || !box || !alert) return;

            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> ${isAr ? 'جاري الفحص والتحديث...' : 'Checking updates...'}`;

            box.classList.remove('d-none');
            alert.className = 'alert alert-info mb-0';
            alert.innerHTML = `<i class="bi bi-hourglass-split me-2"></i>${isAr ? 'جاري سحب أحدث نسخة وتحديث الملفات...' : 'Fetching latest version and updating files...'}`;

            const formData = new FormData();
            const csrfEl = document.querySelector('input[name="csrf_token"]');
            if (csrfEl) formData.append('csrf_token', csrfEl.value);

            fetch('/settings/check-update', {
                method: 'POST',
                body: formData
            })
                .then(res => {
                    if (!res.ok) {
                        return res.text().then(text => { throw new Error(text || 'HTTP ' + res.status); });
                    }
                    return res.json();
                })
                .then(data => {
                    btn.disabled = false;
                    btn.innerHTML = `<i class="bi bi-arrow-clockwise me-1"></i> ${isAr ? 'تحديث النظام الآن' : 'Update System Now'}`;

                    if (data.success) {
                        alert.className = 'alert alert-success mb-0';
                        alert.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> ${data.message.replace(/\n/g, '<br>')}`;
                        if (data.updated) {
                            setTimeout(() => { window.location.reload(); }, 2500);
                        }
                    } else {
                        alert.className = 'alert alert-danger mb-0';
                        alert.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i> ${data.message}`;
                    }
                });
        });
    }

    // Modal submit loading states
    const resetForm = document.querySelector('#resetClinicModal form');
    if (resetForm) {
        resetForm.addEventListener('submit', function () {
            const btn = resetForm.querySelector('button[type="submit"]');
            if (btn) {
                const isAr = getIsArabic();
                btn.disabled = true;
                btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> ${isAr ? 'جاري تصفير البيانات...' : 'Resetting data...'}`;
            }
        });
    }

    const restoreForm = document.querySelector('#restoreBackupModal form');
    if (restoreForm) {
        restoreForm.addEventListener('submit', function () {
            const btn = restoreForm.querySelector('button[type="submit"]');
            if (btn) {
                const isAr = getIsArabic();
                btn.disabled = true;
                btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> ${isAr ? 'جاري استعادة البيانات...' : 'Restoring data...'}`;
            }
        });
    }

    const restoreBackupSelect = document.getElementById('restore_backup_filename');
    const manualFileContainer = document.getElementById('manual_backup_file_container');
    const manualFileInput = document.getElementById('manual_backup_file');
    if (restoreBackupSelect && manualFileContainer && manualFileInput) {
        const handleBackupSelectChange = function () {
            if (restoreBackupSelect.value === '__upload__') {
                manualFileContainer.classList.remove('d-none');
                manualFileInput.required = true;
            } else {
                manualFileContainer.classList.add('d-none');
                manualFileInput.required = false;
                manualFileInput.value = '';
            }
        };
        restoreBackupSelect.addEventListener('change', handleBackupSelectChange);
        handleBackupSelectChange();
    }

    // ── Salary Cards Logic ──
    document.querySelectorAll(".salary-active-toggle").forEach(function (toggle) {
        toggle.addEventListener("change", function () {
            const card = toggle.closest(".salary-staff-card");
            if (!card) return;
            const hiddenInput = card.querySelector(".salary-is-active-input");
            if (hiddenInput) hiddenInput.value = toggle.checked ? "1" : "0";
            card.style.opacity = toggle.checked ? "1" : "0.5";
        });
        const card = toggle.closest(".salary-staff-card");
        if (card && !toggle.checked) card.style.opacity = "0.5";
    });

    document.querySelectorAll(".salary-form").forEach(function (form) {
        form.addEventListener("submit", function (e) {
            const isAr = getIsArabic();
            const amountInput = form.querySelector('input[name="amount"]');
            const val = amountInput ? parseFloat(amountInput.value) : 0;
            if (!amountInput || isNaN(val) || val <= 0) {
                e.preventDefault();
                amountInput.focus();
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        title: isAr ? 'تنبيه' : 'Warning',
                        text: isAr ? 'يرجى كتابة قيمة الراتب أو النسبة المئوية أولاً في الخانة المخصصة قبل الضغط على حفظ!' : 'Please enter a valid salary amount or percentage first!',
                        icon: 'warning',
                        confirmButtonColor: '#0ea5e9',
                        confirmButtonText: isAr ? 'حسناً' : 'OK'
                    });
                } else {
                    alert(isAr ? 'يرجى كتابة قيمة الراتب أو النسبة المئوية أولاً!' : 'Please enter a valid salary amount or percentage!');
                }
            }
        });
    });

    document.querySelectorAll(".salary-type-btn").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const card = btn.closest(".salary-staff-card");
            if (!card) return;
            const hiddenInput = card.querySelector(".salary-type-input");
            const type = btn.getAttribute("data-type");
            if (hiddenInput && type) {
                hiddenInput.value = type;
            }
            updateSalaryTypeUI(card);
        });
    });

    document.querySelectorAll(".salary-staff-card").forEach(function (card) {
        updateSalaryTypeUI(card);
    });

    function updateSalaryTypeUI(card) {
        const hiddenInput = card.querySelector(".salary-type-input");
        const selectedType = hiddenInput ? hiddenInput.value : "fixed";
        const btns = card.querySelectorAll(".salary-type-btn");
        const unitLabel = card.querySelector(".salary-unit-label");
        const labelFixed = card.querySelector(".label-fixed");
        const labelPct = card.querySelector(".label-pct");

        btns.forEach(function (btn) {
            const t = btn.getAttribute("data-type");
            if (t === selectedType) {
                btn.classList.add("btn-primary", "text-white", "border-primary");
                btn.classList.remove("btn-outline-secondary");
            } else {
                btn.classList.remove("btn-primary", "text-white", "border-primary");
                btn.classList.add("btn-outline-secondary");
            }
        });

        if (unitLabel) {
            unitLabel.innerHTML = selectedType === "percentage"
                ? '<i class="bi bi-percent"></i>'
                : (unitLabel.dataset.currency || (window.settingsConfig ? window.settingsConfig.currencySymbol : "SP"));
        }
        if (labelFixed) labelFixed.classList.toggle("d-none", selectedType === "percentage");
        if (labelPct) labelPct.classList.toggle("d-none", selectedType !== "percentage");
    }
};
