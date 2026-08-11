document.addEventListener("DOMContentLoaded", function () {
    const appointmentInput = document.getElementById("appointment_date");
    if (!appointmentInput) return;

    const isAr = !document.cookie.includes('lang=en') || document.documentElement.getAttribute('lang') === 'ar';
    const currentLang = isAr ? 'ar' : 'en';

    // Remove the native HTML5 constraint validation script if present
    appointmentInput.setAttribute("type", "text");
    appointmentInput.setAttribute("placeholder", isAr ? "اختر التاريخ والوقت..." : "Select Date & Time...");

    // Fetch booked slots
    const currentAppointmentId = typeof appointmentIdForEdit !== 'undefined' ? appointmentIdForEdit : "";
    const url = "/appointments/booked-slots" + (currentAppointmentId ? "?exclude_id=" + currentAppointmentId : "");

    function updateConfirmedBadge(dateStr) {
        if (!dateStr) return;
        let badge = document.getElementById("appointment_date_confirm_badge");
        if (!badge) {
            badge = document.createElement("div");
            badge.id = "appointment_date_confirm_badge";
            badge.className = "mt-2 p-2.5 rounded-3 fw-bold small d-flex align-items-center gap-2";
            badge.style.background = "rgba(16, 185, 129, 0.15)";
            badge.style.color = "#10b981";
            badge.style.border = "1px solid rgba(16, 185, 129, 0.35)";
            badge.style.boxShadow = "0 2px 10px rgba(16, 185, 129, 0.15)";

            const parent = appointmentInput.closest(".col-md-6") || appointmentInput.parentElement;
            if (parent) {
                parent.appendChild(badge);
            }
        }
        const textLabel = currentLang === 'ar' ? 'تم تأكيد الموعد المحجوز:' : 'Confirmed Date & Time:';
        badge.innerHTML = `<i class="bi bi-check-circle-fill fs-5 text-success"></i> <span>${textLabel} <strong class="text-light fs-6 ms-1" style="direction: ltr; display: inline-block;">${dateStr}</strong></span>`;
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

    function isPastTime(dateObj) {
        if (!dateObj) return false;
        const now = new Date();
        // Allow 60-second grace period for exact current minute selection
        return dateObj.getTime() < (now.getTime() - 60000);
    }

    function createFlatpickrConfig(bookedSlots) {
        return {
            enableTime: true,
            dateFormat: "Y-m-d h:i K",
            time_24hr: false,
            minDate: "today",
            maxDate: new Date().fp_incr(30),
            minuteIncrement: durationAttr,
            minTime: minTimeAttr,
            maxTime: maxTimeAttr,
            disable: [
                function (date) {
                    return !workingDaysList.includes(date.getDay());
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
                            if (isPastTime(instance.selectedDates[0])) {
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
                            updateConfirmedBadge(instance.input.value);
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
                    if (isPastTime(instance.selectedDates[0])) {
                        instance.clear();
                        const badge = document.getElementById("appointment_date_confirm_badge");
                        if (badge) badge.style.display = "none";
                    } else {
                        updateConfirmedBadge(instance.input.value);
                    }
                }
            },
            onChange: function (selectedDates, dateStr, instance) {
                if (selectedDates.length > 0 && isPastTime(selectedDates[0])) {
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
                if (bookedSlots && bookedSlots.includes(dateStr)) {
                    showAlert(
                        currentLang === 'ar' ? 'الوقت محجوز' : 'Slot Reserved',
                        currentLang === 'ar' ? 'هذا الوقت محجوز بالفعل، يرجى اختيار وقت آخر.' : 'This slot is already reserved. Please select another time.',
                        'error'
                    );
                    instance.clear();
                    const badge = document.getElementById("appointment_date_confirm_badge");
                    if (badge) badge.style.display = "none";
                } else if (dateStr) {
                    updateConfirmedBadge(dateStr);
                }
            },
            onClose: function (selectedDates, dateStr, instance) {
                if (selectedDates.length > 0 && isPastTime(selectedDates[0])) {
                    instance.clear();
                    const badge = document.getElementById("appointment_date_confirm_badge");
                    if (badge) badge.style.display = "none";
                } else if (dateStr) {
                    updateConfirmedBadge(dateStr);
                }
            },
            locale: currentLang === 'ar' && typeof flatpickr.l10ns.ar !== 'undefined' ? {
                ...flatpickr.l10ns.ar,
                months: {
                    shorthand: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"],
                    longhand: ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"]
                },
                firstDayOfWeek: 0
            } : {
                firstDayOfWeek: 0
            }
        };
    }

    fetch(url)
        .then(res => res.json())
        .then(bookedSlots => {
            flatpickr(appointmentInput, createFlatpickrConfig(bookedSlots));
        })
        .catch(err => {
            console.error("Failed to load booked slots", err);
            flatpickr(appointmentInput, createFlatpickrConfig([]));
        });
});
