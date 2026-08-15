/**
 * Dental Clinic - Invoice Date/Time Flatpickr Controller
 * Mirrors the appointment form Flatpickr for the manual invoice visit datetime field.
 * No conflict-checking against appointments (direct walk-in visits).
 */
document.addEventListener("DOMContentLoaded", function () {
    const invoiceDateInput = document.getElementById("invoice-visit-datetime");
    if (!invoiceDateInput) return;

    // Fallback: If Flatpickr library is not loaded from CDN, keep native input
    if (typeof flatpickr === 'undefined') {
        console.warn("Flatpickr not loaded, using native datetime-local picker.");
        return;
    }

    const isAr = !document.cookie.includes('lang=en') || document.documentElement.getAttribute('lang') === 'ar';
    const currentLang = isAr ? 'ar' : 'en';

    // Parse any existing default value
    let rawInitialValue = invoiceDateInput.value ? invoiceDateInput.value.trim() : "";
    let initialDateObj = null;
    if (rawInitialValue) {
        // Handle both "YYYY-MM-DDThh:mm" and "YYYY-MM-DD hh:mm" formats
        let isoStr = rawInitialValue.includes('T') ? rawInitialValue : rawInitialValue.replace(' ', 'T');
        let parsedTs = Date.parse(isoStr);
        if (!isNaN(parsedTs)) {
            initialDateObj = new Date(parsedTs);
        }
    }
    if (!initialDateObj) {
        initialDateObj = new Date(); // Default: now
    }

    // Switch input type from datetime-local to text so Flatpickr takes over
    invoiceDateInput.setAttribute("type", "text");
    invoiceDateInput.setAttribute("placeholder", isAr ? "اختر تاريخ ووقت الزيارة..." : "Select Visit Date & Time...");

    function updateConfirmedBadge(dateObj, dateStr) {
        const valStr = dateStr || (invoiceDateInput ? invoiceDateInput.value : "");
        if (!valStr) return;

        let badge = document.getElementById("invoice_date_confirm_badge");
        if (!badge) {
            badge = document.createElement("div");
            badge.id = "invoice_date_confirm_badge";
            badge.className = "mt-2 p-2 rounded-3 fw-bold small d-flex align-items-center gap-2";
            const parent = invoiceDateInput.closest(".patient-info-box") || invoiceDateInput.parentElement;
            if (parent) parent.appendChild(badge);
        }

        // Use Bootstrap text classes (have !important) — guaranteed contrast on mint badge background
        const dateClass = document.documentElement.getAttribute('data-bs-theme') === 'light'
            ? 'text-dark fw-bold fs-6 ms-1'
            : 'text-white fw-bold fs-6 ms-1';

        const textLabel = currentLang === 'ar' ? 'تاريخ ووقت الزيارة:' : 'Visit Date & Time:';
        badge.className = "mt-2 p-2 rounded-3 fw-bold small d-flex align-items-center gap-2 text-success bg-success bg-opacity-10 border border-success border-opacity-25";
        badge.style.boxShadow = "0 2px 10px rgba(16, 185, 129, 0.15)";
        badge.innerHTML = `<i class="bi bi-calendar-check-fill fs-5 text-success"></i> <span>${textLabel} <strong class="${dateClass}" style="direction: ltr; display: inline-block;">${valStr}</strong></span>`;
        badge.style.display = "flex";
    }

    function showAlert(title, message, icon = 'warning') {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: icon,
                title: title,
                text: message,
                confirmButtonText: currentLang === 'ar' ? 'حسناً، فهمت' : 'Got it',
                confirmButtonColor: '#0ea5e9',
                background: '#1e293b',
                color: '#f8fafc',
                customClass: {
                    popup: 'rounded-4 shadow-lg border border-secondary border-opacity-25'
                }
            });
        } else {
            alert(message);
        }
    }

    const config = {
        enableTime: true,
        dateFormat: "Y-m-d h:i K",
        time_24hr: false,
        // Allow any date including past (invoices can be back-dated)
        minDate: null,
        maxDate: null,
        minuteIncrement: 15,
        onReady: function (selectedDates, dateStr, instance) {
            const calendarContainer = instance.calendarContainer;
            if (calendarContainer && !calendarContainer.querySelector('.flatpickr-confirm-btn')) {
                const btnContainer = document.createElement('div');
                btnContainer.className = 'p-2 border-top border-secondary border-opacity-25 w-100 mt-1';

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'flatpickr-confirm-btn btn btn-primary w-100 fw-bold py-2 shadow-sm d-flex align-items-center justify-content-center gap-2';
                btn.style.borderRadius = '10px';
                btn.style.background = 'linear-gradient(135deg, #0ea5e9, #2563eb)';
                btn.style.border = 'none';
                btn.style.fontSize = '0.9rem';
                btn.innerHTML = `<i class="bi bi-check-circle-fill fs-6"></i> <span>${currentLang === 'ar' ? 'تأكيد تاريخ الزيارة' : 'Confirm Visit Date'}</span>`;

                btn.addEventListener('click', function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    if (instance.selectedDates.length > 0) {
                        updateConfirmedBadge(instance.selectedDates[0], instance.input.value);
                        instance.close();
                    } else {
                        showAlert(
                            currentLang === 'ar' ? 'تنبيه' : 'Notice',
                            currentLang === 'ar' ? 'يرجى اختيار التاريخ والوقت أولاً.' : 'Please select a date and time first.',
                            'info'
                        );
                    }
                });

                btnContainer.appendChild(btn);
                calendarContainer.appendChild(btnContainer);
            }

            // Show initial badge if value already set
            if (instance.input.value && instance.selectedDates.length > 0) {
                updateConfirmedBadge(instance.selectedDates[0], instance.input.value);
            }
        },
        onChange: function (selectedDates, dateStr, instance) {
            if (dateStr) {
                updateConfirmedBadge(selectedDates[0], dateStr);
            }
        },
        onClose: function (selectedDates, dateStr, instance) {
            if (dateStr) {
                updateConfirmedBadge(selectedDates[0], dateStr);
            }
        },
        locale: currentLang === 'ar' && typeof flatpickr !== 'undefined' && typeof flatpickr.l10ns !== 'undefined' && typeof flatpickr.l10ns.ar !== 'undefined' ? {
            ...flatpickr.l10ns.ar,
            months: {
                shorthand: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"],
                longhand: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين ثاني", "كانون الأول"]
            },
            firstDayOfWeek: 0
        } : {
            firstDayOfWeek: 0
        },
        defaultDate: initialDateObj
    };

    const fpInstance = flatpickr(invoiceDateInput, config);

    // Open Flatpickr when input is clicked or focused
    invoiceDateInput.addEventListener("click", function () {
        if (fpInstance) fpInstance.open();
    });

    // Show initial badge for the default date
    if (initialDateObj && invoiceDateInput.value) {
        updateConfirmedBadge(initialDateObj, invoiceDateInput.value);
    }
});
