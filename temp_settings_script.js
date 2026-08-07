
    // ── Global Scope Helpers (Available Immediately) ──────────────────────
    window.addNewProcedureRow = function () {
        const list = document.getElementById("procedures-list");
        if (list) {
            const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
            const namePlaceholder = isAr ? 'اسم الإجراء (مثال: تنظيف وتلميع)' : 'Procedure Name (e.g., Cleaning)';
            const deleteTooltip = isAr ? 'حذف الإجراء' : 'Delete Procedure';
            const currencySymbol = "{{ currency_symbol }}";
            const row = document.createElement("tr");
            row.className = "procedure-row";
            row.innerHTML = `
            <td>
                <input type="text" name="procedure_names[]" form="main-settings-form" class="form-control settings-input" required placeholder="${namePlaceholder}">
            </td>
            <td>
                <div class="input-group settings-input-group">
                    <input type="text" name="procedure_prices[]" form="main-settings-form" class="form-control settings-input" required placeholder="0">
                    <span class="input-group-text">${currencySymbol}</span>
                </div>
            </td>
            <td class="text-center align-middle">
                <button type="button" class="btn btn-outline-danger btn-sm rounded-circle delete-row-btn" onclick="deleteProcedureRow(this)" data-tooltip="${deleteTooltip}" style="width:34px;height:34px;padding:0 !important;">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
            list.appendChild(row);
            if (typeof window.initCustomTooltips === "function") {
                window.initCustomTooltips();
            }
            const nameInput = row.querySelector('input[name="procedure_names[]"]');
            if (nameInput) {
                nameInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                setTimeout(() => nameInput.focus(), 150);
            }
        }
    };

    window.deleteProcedureRow = function (btn) {
        const row = btn ? btn.closest("tr") : null;
        if (!row) return;

        const nameInput = row.querySelector('input[name="procedure_names[]"]');
        const procName = nameInput ? nameInput.value.trim() : '';
        const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');

        const confirmText = procName
            ? (isAr ? `هل أنت متأكد من رغبتك في حذف الإجراء (${procName})؟` : `Are you sure you want to delete procedure "${procName}"?`)
            : (isAr ? 'هل أنت متأكد من رغبتك في حذف هذا الإجراء؟' : 'Are you sure you want to delete this procedure?');

        const doDelete = function() {
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
        csrfInput.value = "{{ csrf_token() }}";
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    };

    window.confirmDeleteUser = function (userId, username) {
        const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
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
        form.action = "{{ url_for('settings.create_backup') }}";
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = "{{ csrf_token() }}";
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
        csrfInput.value = "{{ csrf_token() }}";
        form.appendChild(csrfInput);
        document.body.appendChild(form);
        form.submit();
    };

    window.confirmDeleteBackup = function (filename) {
        const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
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

    function runSettingsInit() {
        const mainForm = document.getElementById("main-settings-form");
        const tbody = document.getElementById("procedures-list");
        const currencySymbol = "{{ currency_symbol }}";
        const saveWrapper = document.getElementById("save-settings-btn-wrapper");

        // ── Add new procedure row (Event Delegation) ──
        document.addEventListener("click", function (e) {
            const addBtn = e.target.closest("#add-procedure-btn");
            if (addBtn) {
                e.preventDefault();
                const list = document.getElementById("procedures-list");
                if (list) {
                    const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
                    const namePlaceholder = isAr ? 'اسم الإجراء (مثال: تنظيف وتلميع)' : 'Procedure Name (e.g., Cleaning)';
                    const deleteTooltip = isAr ? 'حذف الإجراء' : 'Delete Procedure';
                    const row = document.createElement("tr");
                    row.className = "procedure-row";
                    row.innerHTML = `
                    <td>
                        <input type="text" name="procedure_names[]" form="main-settings-form" class="form-control settings-input" required placeholder="${namePlaceholder}">
                    </td>
                    <td>
                        <div class="input-group settings-input-group">
                            <input type="text" name="procedure_prices[]" form="main-settings-form" class="form-control settings-input" required placeholder="0">
                            <span class="input-group-text">${currencySymbol}</span>
                        </div>
                    </td>
                    <td class="text-center align-middle">
                        <button type="button" class="btn btn-outline-danger btn-sm rounded-circle delete-row-btn" data-tooltip="${deleteTooltip}" style="width:34px;height:34px;padding:0 !important;">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                    list.appendChild(row);
                    if (typeof window.initCustomTooltips === "function") {
                        window.initCustomTooltips();
                    }
                    const nameInput = row.querySelector('input[name="procedure_names[]"]');
                    if (nameInput) {
                        nameInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        setTimeout(() => nameInput.focus(), 150);
                    }
                }
            }

            // ── Delete row from table with warning confirmation ──
            const deleteBtn = e.target.closest(".delete-row-btn");
            if (deleteBtn) {
                e.preventDefault();
                const row = deleteBtn.closest("tr");
                if (!row) return;

                const nameInput = row.querySelector('input[name="procedure_names[]"]');
                const procName = nameInput ? nameInput.value.trim() : '';
                const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');

                const confirmText = procName
                    ? (isAr ? `هل أنت متأكد من رغبتك في حذف الإجراء (${procName})؟` : `Are you sure you want to delete procedure "${procName}"?`)
                    : (isAr ? 'هل أنت متأكد من رغبتك في حذف هذا الإجراء؟' : 'Are you sure you want to delete this procedure?');

                const doDelete = function() {
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
            }
        });

        // ── Hash-based tab activation ──
        const hash = window.location.hash;
        if (hash) {
            const tabTriggerEl = document.querySelector(`button[data-bs-target="${hash}"]`);
            if (tabTriggerEl) {
                const tab = new bootstrap.Tab(tabTriggerEl);
                tab.show();
            }
        }

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

        const currentLang = "{{ current_lang }}";
        updateLangButtons(currentLang);

        // Listen for tab changes
        document.querySelectorAll('#settings-tabs button[data-bs-toggle="pill"]').forEach(function (btn) {
            btn.addEventListener("shown.bs.tab", function (e) {
                const targetHash = e.target.getAttribute("data-bs-target");
                const activeTabInput = document.getElementById("active-tab-input");
                if (activeTabInput) {
                    activeTabInput.value = targetHash;
                }
                if (mainForm && targetHash) {
                    mainForm.action = "{{ url_for('settings.settings_page') }}" + targetHash;
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
                
                let errors = [];
                if (nameInput && !nameInput.value.trim()) {
                    errors.push("Clinic Name is required.");
                }
                if (currencyInput && !currencyInput.value.trim()) {
                    errors.push("Currency Symbol is required.");
                }
                if (bookingDaysInput) {
                    const daysVal = parseInt(bookingDaysInput.value, 10);
                    if (isNaN(daysVal) || daysVal <= 0) {
                        errors.push("Booking Window Days must be a positive integer.");
                    }
                }
                
                if (errors.length > 0) {
                    event.preventDefault();
                    alert(errors.join("\n"));
                    
                    // Switch to the first tab with an error
                    if (nameInput && !nameInput.value.trim()) {
                        const tabButton = document.getElementById("tab-general-btn");
                        if (tabButton) {
                            const tab = new bootstrap.Tab(tabButton);
                            tab.show();
                        }
                    } else if (bookingDaysInput && (isNaN(parseInt(bookingDaysInput.value, 10)) || parseInt(bookingDaysInput.value, 10) <= 0)) {
                        const tabButton = document.getElementById("tab-calendar-btn");
                        if (tabButton) {
                            const tab = new bootstrap.Tab(tabButton);
                            tab.show();
                        }
                    } else if (currencyInput && !currencyInput.value.trim()) {
                        const tabButton = document.getElementById("tab-billing-btn");
                        if (tabButton) {
                            const tab = new bootstrap.Tab(tabButton);
                            tab.show();
                        }
                    }
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

        // Keep the hidden input in sync with the active tab & activate hash tab on load
        document.querySelectorAll('[data-bs-toggle="pill"]').forEach(function (btn) {
            btn.addEventListener('shown.bs.tab', function (e) {
                const target = e.target.getAttribute('data-bs-target');
                const inp = document.getElementById('active-tab-input');
                if (inp) inp.value = target;
            });
        });

        const hash = window.location.hash;
        if (hash) {
            const triggerEl = document.querySelector(`button[data-bs-target="${hash}"]`);
            if (triggerEl) {
                const tab = new bootstrap.Tab(triggerEl);
                tab.show();
            }
        }

        // ── Test Buttons Event Listeners ─────────────────────────────────
        // Read CSRF token dynamically from the injected form input
        const getCsrfToken = () => {
            const el = document.querySelector('input[name="csrf_token"]');
            return el ? el.value : '';
        };

        // Helper to send test request
        function sendTestRequest(url, data, btn, resultDiv) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Sending...';
            resultDiv.style.display = 'block';
            resultDiv.className = 'col-md-12 mt-1 alert alert-info py-2';
            resultDiv.textContent = 'جاري الإرسال...';

            // Add CSRF Token
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
                resultDiv.textContent = 'حدث خطأ: ' + err.message;
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = btn.id === 'btn-test-sms' ? '<i class="bi bi-send-fill me-1"></i> Send Test SMS' :
                               btn.id === 'btn-test-telegram' ? '<i class="bi bi-send-fill me-1"></i> Test Telegram' :
                               '<i class="bi bi-send-fill me-1"></i> Send Test Email';
            });
        }

        // Test SMS
        const btnTestSms = document.getElementById('btn-test-sms');
        if (btnTestSms) {
            btnTestSms.addEventListener('click', function() {
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

        // Test Telegram
        const btnTestTelegram = document.getElementById('btn-test-telegram');
        if (btnTestTelegram) {
            btnTestTelegram.addEventListener('click', function() {
                const chatId = document.getElementById('test_telegram_chat_id').value.trim();
                const botToken = document.getElementById('telegram_bot_token').value.trim();
                const resultDiv = document.getElementById('test-telegram-result');
                sendTestRequest('/settings/test-telegram', {
                    chat_id: chatId,
                    bot_token: botToken
                }, btnTestTelegram, resultDiv);
            });
        }

        // Test Email
        const btnTestEmail = document.getElementById('btn-test-email');
        if (btnTestEmail) {
            btnTestEmail.addEventListener('click', function() {
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

        window.normalizeArabicText = function(text) {
            if (!text) return '';
            return text.toString().toLowerCase()
                .replace(/[أإآ]/g, 'ا')
                .replace(/ة/g, 'ه')
                .replace(/ى/g, 'ي')
                .trim();
        };

        window.filterUserTable = function(tbodyId, query) {
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

        // System update event listener
        const btnCheckUpdate = document.getElementById('check-update-btn');
        if (btnCheckUpdate) {
            btnCheckUpdate.addEventListener('click', function(e) {
                e.preventDefault();
                
                const btn = btnCheckUpdate;
                const box = document.getElementById('update-result-box');
                const alert = document.getElementById('update-result-alert');
                const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');

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

        window.triggerResetClinicFlow = function() {
            const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
            
            const openModal = function() {
                const modalEl = document.getElementById('resetClinicModal');
                if (modalEl) {
                    const bsModal = new bootstrap.Modal(modalEl);
                    bsModal.show();
                }
            };

            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: isAr ? '⚠️ تحذير شديد الخطورة!' : '⚠️ CRITICAL WARNING!',
                    html: isAr ? `
                        <div class="text-end dir-rtl p-1" style="direction: rtl; text-align: right;">
                            <p class="fw-bold text-danger mb-2 fs-6">هل أنت متأكد تماماً من رغبتك في إعادة ضبط العيادة وتصفير كافة البيانات؟</p>
                            <div class="p-3 bg-danger bg-opacity-10 border border-danger border-opacity-25 rounded-3 mb-3 small">
                                <div class="fw-bold mb-1 text-danger"><i class="bi bi-x-circle-fill me-1"></i> سيتم حذف:</div>
                                <ul class="mb-0 pe-3 text-secondary" style="list-style-type: square;">
                                    <li>جميع المرضى والملفات الطبية</li>
                                    <li>جميع المواعيد والجلسات</li>
                                    <li>كافة الفواتير والمدفوعات والمصاريف</li>
                                </ul>
                            </div>
                            <div class="p-2.5 bg-success bg-opacity-10 border border-success border-opacity-25 rounded-3 small">
                                <div class="fw-bold text-success"><i class="bi bi-check-circle-fill me-1"></i> سيتم الحفاظ على:</div>
                                <span class="text-secondary small">إعدادات العيادة، توكنز الإشعارات، الأسعار، وحسابات المستخدمين والمدراء.</span>
                            </div>
                        </div>
                    ` : 'Are you sure you want to reset all clinic data?',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#dc3545',
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: isAr ? 'متابعة للتحقق الأمني ➔' : 'Proceed to Admin Verification ➔',
                    cancelButtonText: isAr ? 'إلغاء' : 'Cancel',
                    reverseButtons: true
                }).then((result) => {
                    if (result.isConfirmed) {
                        openModal();
                    }
                });
            } else {
                openModal();
            }
        };

        window.triggerRestoreLatestBackupFlow = function() {
            const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');

            const openModal = function() {
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
                            <p class="fw-bold text-warning text-dark-emphasis mb-2 fs-6">هل أنت متأكد من رغبتك في استعادة كافة بيانات العيادة؟</p>
                            <div class="p-3 bg-warning bg-opacity-10 border border-warning border-opacity-25 rounded-3 mb-2 small text-secondary">
                                <i class="bi bi-info-circle-fill text-warning me-1"></i>
                                سيتم استبدال واسترجاع كافة سجلات المرضى والمواعيد والفواتير الموجودة بأحدث نسخة احتياطية محفوظة تلقائياً في النظام.
                            </div>
                        </div>
                    ` : 'Are you sure you want to restore clinic database from the latest saved backup file?',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#ffc107',
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: isAr ? 'متابعة للتحقق الأمني ➔' : 'Proceed to Admin Verification ➔',
                    cancelButtonText: isAr ? 'إلغاء' : 'Cancel',
                    reverseButtons: true
                }).then((result) => {
                    if (result.isConfirmed) {
                        openModal();
                    }
                });
            } else {
                openModal();
            }
        };

        // Form submit loading states for reset and restore modals
        const resetForm = document.querySelector('#resetClinicModal form');
        if (resetForm) {
            resetForm.addEventListener('submit', function() {
                const btn = resetForm.querySelector('button[type="submit"]');
                if (btn) {
                    const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
                    btn.disabled = true;
                    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> ${isAr ? 'جاري تصفير البيانات...' : 'Resetting data...'}`;
                }
            });
        }

        const restoreForm = document.querySelector('#restoreBackupModal form');
        if (restoreForm) {
            restoreForm.addEventListener('submit', function() {
                const btn = restoreForm.querySelector('button[type="submit"]');
                if (btn) {
                    const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
                    btn.disabled = true;
                    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status"></span> ${isAr ? 'جاري استعادة البيانات...' : 'Restoring data...'}`;
                }
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", runSettingsInit);
    } else {
        runSettingsInit();
    }

    // ── Salary Cards JS ──────────────────────────────────────────────────────
    document.addEventListener("DOMContentLoaded", function () {
        const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');

        // Active toggle → hidden input sync
        document.querySelectorAll(".salary-active-toggle").forEach(function (toggle) {
            toggle.addEventListener("change", function () {
                const card = toggle.closest(".salary-staff-card");
                if (!card) return;
                const hiddenInput = card.querySelector(".salary-is-active-input");
                if (hiddenInput) hiddenInput.value = toggle.checked ? "1" : "0";
                card.style.opacity = toggle.checked ? "1" : "0.5";
            });
            // Initial state
            const card = toggle.closest(".salary-staff-card");
            if (card && !toggle.checked) card.style.opacity = "0.5";
        });

        // Salary form submit validation
        document.querySelectorAll(".salary-form").forEach(function (form) {
            form.addEventListener("submit", function (e) {
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

        // Salary type button click → update hidden input and UI
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

        // Style salary-type-btn active state on load
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
                    : (unitLabel.dataset.currency || "{{ currency_symbol }}");
            }
            if (labelFixed) labelFixed.classList.toggle("d-none", selectedType === "percentage");
            if (labelPct) labelPct.classList.toggle("d-none", selectedType !== "percentage");
        }
    });

    window.confirmDeductSalary = function (form, e) {
        if (e) e.preventDefault();
        const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
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
                    setTimeout(function() {
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

    window.copyNetworkUrlToClipboard = function() {
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
        } catch (e) {}

        if (!copied) {
            try {
                document.execCommand('copy');
                copied = true;
            } catch (err) {}
        }

        const btnText = document.getElementById('copy-btn-text');
        if (btnText) {
            const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');
            const original = btnText.textContent;
            btnText.textContent = isAr ? 'تم النسخ!' : 'Copied!';
            setTimeout(() => { btnText.textContent = original; }, 2000);
        }
    };
