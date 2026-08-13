document.addEventListener("DOMContentLoaded", function () {
    const appointmentInput = document.getElementById("appointment_date");
    if (!appointmentInput) return;

    // Fallback: If Flatpickr library is not loaded from CDN, keep native HTML5 input
    if (typeof flatpickr === 'undefined') {
        console.warn("Flatpickr library not loaded, using native datetime-local picker.");
        return;
    }

    const isAr = !document.cookie.includes('lang=en') || document.documentElement.getAttribute('lang') === 'ar';
    const currentLang = isAr ? 'ar' : 'en';

    function getCleanAttr(el, attrName, defaultVal) {
        let val = el.dataset[attrName] || el.getAttribute("data-" + attrName);
        if (!val || val === "None" || val === "undefined" || val === "null" || val.trim() === "") {
            return defaultVal;
        }
        return val.trim();
    }

    const durationAttr = parseInt(getCleanAttr(appointmentInput, "duration", "30"), 10) || 30;
    const minTimeAttr = getCleanAttr(appointmentInput, "minTime", "08:00");
    const maxTimeAttr = getCleanAttr(appointmentInput, "maxTime", "18:00");
    const workingDaysAttr = getCleanAttr(appointmentInput, "workingDays", "0,1,2,3,4,6");
    
    let workingDaysList = workingDaysAttr.split(',').map(d => parseInt(d.trim(), 10)).filter(n => !isNaN(n));
    if (workingDaysList.length === 0) {
        workingDaysList = [0, 1, 2, 3, 4, 6];
    }

    // Check for existing value
    let rawInitialValue = appointmentInput.value ? appointmentInput.value.trim() : "";
    let initialDateObj = null;
    if (rawInitialValue) {
        let isoStr = rawInitialValue.includes('T') ? rawInitialValue : rawInitialValue.replace(' ', 'T');
        let parsedTs = Date.parse(isoStr);
        if (!isNaN(parsedTs)) {
            initialDateObj = new Date(parsedTs);
        }
    }

    // Remove native HTML5 picker
    appointmentInput.setAttribute("type", "text");
    appointmentInput.setAttribute("placeholder", isAr ? "اختر التاريخ والوقت..." : "Select Date & Time...");

    const currentAppointmentId = typeof appointmentIdForEdit !== 'undefined' ? appointmentIdForEdit : "";
    let bookedSlotsList = [];

    function updateConfirmedBadge(dateObj, dateStr) {
        const valStr = dateStr || (appointmentInput ? appointmentInput.value : "");
        if (!valStr) return;
        let badge = document.getElementById("appointment_date_confirm_badge");
        if (!badge) {
            badge = document.createElement("div");
            badge.id = "appointment_date_confirm_badge";
            badge.className = "mt-2 p-2.5 rounded-3 fw-bold small d-flex align-items-center gap-2";
            const parent = appointmentInput.closest(".col-md-6") || appointmentInput.closest(".col-md-12") || appointmentInput.parentElement;
            if (parent) {
                parent.appendChild(badge);
            }
        }

        const doctorSelect = document.getElementById("doctor_id");
        const doctorId = doctorSelect ? doctorSelect.value : "";
        const apptId = appointmentInput.dataset.appointmentId || currentAppointmentId || "";

        let checkDateParam = valStr;
        if (dateObj instanceof Date && !isNaN(dateObj)) {
            const year = dateObj.getFullYear();
            const month = String(dateObj.getMonth() + 1).padStart(2, '0');
            const day = String(dateObj.getDate()).padStart(2, '0');
            const hours = String(dateObj.getHours()).padStart(2, '0');
            const minutes = String(dateObj.getMinutes()).padStart(2, '0');
            checkDateParam = `${year}-${month}-${day} ${hours}:${minutes}`;
        }

        const checkingLabel = currentLang === 'ar' ? 'جاري التحقق من توفر الموعد...' : 'Checking availability...';
        badge.className = "mt-2 p-2.5 rounded-3 fw-bold small d-flex align-items-center gap-2 text-info bg-info bg-opacity-10 border border-info border-opacity-25";
        badge.style.boxShadow = "0 2px 10px rgba(14, 165, 233, 0.15)";
        badge.innerHTML = `<span class="spinner-border spinner-border-sm text-info" role="status"></span> <span>${checkingLabel}</span>`;
        badge.style.display = "flex";

        fetch(`/api/check-appointment-conflict?date=${encodeURIComponent(checkDateParam)}&doctor_id=${encodeURIComponent(doctorId)}&appointment_id=${encodeURIComponent(apptId)}`)
            .then(res => res.json())
            .then(data => {
                if (data.available) {
                    const textLabel = currentLang === 'ar' ? 'الموعد المحدد متاح:' : 'Selected Time Available:';
                    badge.className = "mt-2 p-2.5 rounded-3 fw-bold small d-flex align-items-center gap-2 text-success bg-success bg-opacity-10 border border-success border-opacity-25";
                    badge.style.boxShadow = "0 2px 10px rgba(16, 185, 129, 0.15)";
                    badge.innerHTML = `<i class="bi bi-check-circle-fill fs-5 text-success"></i> <span>${textLabel} <strong class="text-light fs-6 ms-1" style="direction: ltr; display: inline-block;">${valStr}</strong></span>`;
                } else {
                    const errorMsg = data.message || (currentLang === 'ar' ? 'تعارض في الموعد: هذا الوقت محجوز مسبقاً!' : 'Conflict with another appointment!');
                    badge.className = "mt-2 p-2.5 rounded-3 fw-bold small d-flex align-items-center gap-2 text-danger bg-danger bg-opacity-10 border border-danger border-opacity-25";
                    badge.style.boxShadow = "0 2px 10px rgba(239, 68, 68, 0.15)";
                    badge.innerHTML = `<i class="bi bi-exclamation-triangle-fill fs-5 text-danger"></i> <span>${errorMsg}</span>`;
                }
            })
            .catch(() => {
                const textLabel = currentLang === 'ar' ? 'الموعد المحدد:' : 'Selected Date & Time:';
                badge.className = "mt-2 p-2.5 rounded-3 fw-bold small d-flex align-items-center gap-2 text-primary bg-primary bg-opacity-10 border border-primary border-opacity-25";
                badge.style.boxShadow = "0 2px 10px rgba(37, 99, 235, 0.15)";
                badge.innerHTML = `<i class="bi bi-calendar-check fs-5 text-primary"></i> <span>${textLabel} <strong class="text-light fs-6 ms-1" style="direction: ltr; display: inline-block;">${valStr}</strong></span>`;
            });
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

    function isPastTime(dateObj) {
        if (!dateObj) return false;
        const now = new Date();
        return dateObj.getTime() < (now.getTime() - 60000);
    }

    let minDateVal = "today";
    if (initialDateObj) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (initialDateObj < today) {
            minDateVal = initialDateObj;
        }
    }

    const config = {
        enableTime: true,
        dateFormat: "Y-m-d h:i K",
        time_24hr: false,
        minDate: minDateVal,
        maxDate: new Date().fp_incr(60),
        minuteIncrement: durationAttr > 0 ? durationAttr : 15,
        minTime: minTimeAttr,
        maxTime: maxTimeAttr,
        disable: [
            function (date) {
                if (!workingDaysList.includes(date.getDay())) {
                    return true;
                }
                return false;
            }
        ],
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
                btn.innerHTML = `<i class="bi bi-check-circle-fill fs-6"></i> <span>${currentLang === 'ar' ? 'تأكيد اختيار الموعد' : 'Confirm Selection'}</span>`;
                
                btn.addEventListener('click', function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    if (instance.selectedDates.length > 0) {
                        if (isPastTime(instance.selectedDates[0]) && !currentAppointmentId) {
                            showAlert(
                                currentLang === 'ar' ? 'تنبيه وقت الموعد' : 'Invalid Time',
                                currentLang === 'ar' ? 'لا يمكن اختيار موعد في الماضي. يرجى اختيار تاريخ ووقت قادم.' : 'Cannot select a past time. Please select a future date and time.',
                                'warning'
                            );
                            instance.clear();
                            const badge = document.getElementById("appointment_date_confirm_badge");
                            if (badge) badge.style.display = "none";
                            return;
                        }
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
            if (instance.input.value && instance.selectedDates.length > 0) {
                updateConfirmedBadge(instance.selectedDates[0], instance.input.value);
            }
        },
        onChange: function (selectedDates, dateStr, instance) {
            if (selectedDates.length > 0 && isPastTime(selectedDates[0]) && !currentAppointmentId) {
                showAlert(
                    currentLang === 'ar' ? 'تنبيه وقت الموعد' : 'Invalid Time',
                    currentLang === 'ar' ? 'لا يمكن اختيار موعد في الماضي. يرجى اختيار تاريخ ووقت قادم.' : 'Cannot select a past time. Please select a future date and time.',
                    'warning'
                );
                instance.clear();
                const badge = document.getElementById("appointment_date_confirm_badge");
                if (badge) badge.style.display = "none";
                return;
            }
            if (bookedSlotsList && bookedSlotsList.includes(dateStr)) {
                showAlert(
                    currentLang === 'ar' ? 'الوقت محجوز' : 'Slot Reserved',
                    currentLang === 'ar' ? 'هذا الوقت محجوز بالفعل، يرجى اختيار وقت آخر.' : 'This slot is already reserved. Please select another time.',
                    'error'
                );
                instance.clear();
                const badge = document.getElementById("appointment_date_confirm_badge");
                if (badge) badge.style.display = "none";
            } else if (dateStr) {
                updateConfirmedBadge(selectedDates[0], dateStr);
            }
        },
        onClose: function (selectedDates, dateStr, instance) {
            if (selectedDates.length > 0 && isPastTime(selectedDates[0]) && !currentAppointmentId) {
                instance.clear();
                const badge = document.getElementById("appointment_date_confirm_badge");
                if (badge) badge.style.display = "none";
            } else if (dateStr) {
                updateConfirmedBadge(dateStr);
            }
        },
        locale: currentLang === 'ar' && typeof flatpickr !== 'undefined' && typeof flatpickr.l10ns !== 'undefined' && typeof flatpickr.l10ns.ar !== 'undefined' ? {
            ...flatpickr.l10ns.ar,
            months: {
                shorthand: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"],
                longhand: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين تاني", "كانون الأول"]
            },
            firstDayOfWeek: 0
        } : {
            firstDayOfWeek: 0
        }
    };

    if (initialDateObj) {
        config.defaultDate = initialDateObj;
    }

    // INITIALIZE FLATPICKR IMMEDIATELY (SYNCHRONOUSLY) SO IT IS INSTANTLY CLICKABLE
    const fpInstance = flatpickr(appointmentInput, config);

    // Open Flatpickr when input is clicked or focused
    appointmentInput.addEventListener("click", function() {
        if (fpInstance) fpInstance.open();
    });

    // Fetch booked slots asynchronously in the background and update bookedSlotsList
    const url = "/appointments/booked-slots" + (currentAppointmentId ? "?exclude_id=" + currentAppointmentId : "");
    fetch(url)
        .then(res => res.json())
        .then(bookedSlots => {
            if (Array.isArray(bookedSlots)) {
                bookedSlotsList = bookedSlots;
            }
        })
        .catch(err => {
            console.error("Failed to load booked slots", err);
        });

    const doctorSelectEl = document.getElementById("doctor_id");
    if (doctorSelectEl) {
        doctorSelectEl.addEventListener("change", function() {
            if (appointmentInput && appointmentInput.value) {
                updateConfirmedBadge(fpInstance ? fpInstance.selectedDates[0] : null, appointmentInput.value);
            }
        });
    }
});

