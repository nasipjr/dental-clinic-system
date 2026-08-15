/**
 * Dental Clinic Management System - Patient Portal Dashboard JavaScript Controller
 * Client-side logic for FullCalendar appointment booking, slot time availability generation, cancellation confirmation, and AJAX table pagination.
 */

window.confirmCancel = function (event) {
    event.preventDefault();
    const form = event.currentTarget;
    const isArabic = document.documentElement.getAttribute('lang') === 'ar' || document.dir === 'rtl';

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: isArabic ? 'تأكيد إلغاء الموعد' : 'Cancel Appointment',
            text: isArabic ? 'هل أنت متأكد من رغبتك في إلغاء هذا الموعد؟' : 'Are you sure you want to cancel this appointment?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: isArabic ? 'نعم، إلغاء' : 'Yes, cancel it',
            cancelButtonText: isArabic ? 'تراجع' : 'No, keep it'
        }).then((result) => {
            if (result.isConfirmed) {
                form.submit();
            }
        });
    } else {
        if (confirm(isArabic ? 'هل أنت متأكد من رغبتك في إلغاء هذا الموعد؟' : 'Are you sure you want to cancel this appointment?')) {
            form.submit();
        }
    }
    return false;
};

window.loadPortalPage = function (targetPage) {
    const tbody = document.getElementById('portalAppointmentsTbody');
    if (!tbody) return;

    tbody.style.opacity = '0.3';
    tbody.style.transition = 'opacity 0.15s ease-in-out';

    const baseUrl = window.portalDashboardUrl || '/portal';

    fetch(`${baseUrl}?page=${targetPage}&ajax=1`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                tbody.innerHTML = data.html_rows;

                const pageIndicator = document.getElementById('portalPageIndicator');
                if (pageIndicator) {
                    const isAr = document.documentElement.lang === 'ar' || document.documentElement.dir === 'rtl';
                    pageIndicator.textContent = isAr ? `${data.page} من ${data.pages}` : `${data.page} / ${data.pages}`;
                }

                const prevBtn = document.getElementById('portalPrevBtn');
                const nextBtn = document.getElementById('portalNextBtn');

                if (prevBtn) {
                    const prevPage = Math.max(1, data.page - 1);
                    prevBtn.setAttribute('onclick', `loadPortalPage(${prevPage})`);
                    if (data.page === 1) {
                        prevBtn.classList.add('disabled', 'opacity-50');
                        prevBtn.setAttribute('disabled', 'disabled');
                    } else {
                        prevBtn.classList.remove('disabled', 'opacity-50');
                        prevBtn.removeAttribute('disabled');
                    }
                }

                if (nextBtn) {
                    const nextPage = Math.min(data.pages, data.page + 1);
                    nextBtn.setAttribute('onclick', `loadPortalPage(${nextPage})`);
                    if (data.page === data.pages) {
                        nextBtn.classList.add('disabled', 'opacity-50');
                        nextBtn.setAttribute('disabled', 'disabled');
                    } else {
                        nextBtn.classList.remove('disabled', 'opacity-50');
                        nextBtn.removeAttribute('disabled');
                    }
                }
            }
        })
        .catch(err => console.error('Error fetching portal page:', err))
        .finally(() => {
            tbody.style.opacity = '1';
        });
};

window.initPortalDashboard = function (config) {
    window.portalDashboardUrl = config.portalDashboardUrl || '/portal';
    const calendarEl = document.getElementById("calendar");
    if (!calendarEl || typeof FullCalendar === 'undefined') return;

    const bookingWindowDays = parseInt(config.bookingWindowDays, 10) || 30;
    const workingHoursStart = config.workingHoursStart || "09:00";
    const workingHoursEnd = config.workingHoursEnd || "17:00";
    const workingDays = (config.workingDays || "0,1,2,3,4,6").split(",").map(Number);

    const startParts = workingHoursStart.split(':');
    const endParts = workingHoursEnd.split(':');
    const startHrs = isNaN(parseInt(startParts[0], 10)) ? 9 : parseInt(startParts[0], 10);
    const startMins = isNaN(parseInt(startParts[1], 10)) ? 0 : parseInt(startParts[1], 10);
    const endHrs = isNaN(parseInt(endParts[0], 10)) ? 17 : parseInt(endParts[0], 10);
    const endMins = isNaN(parseInt(endParts[1], 10)) ? 0 : parseInt(endParts[1], 10);

    const defaultDuration = parseInt(config.defaultDuration, 10) || 30;
    const slotDurHrs = Math.floor(defaultDuration / 60);
    const slotDurMins = defaultDuration % 60;
    const slotDurationStr = `${String(slotDurHrs).padStart(2, '0')}:${String(slotDurMins).padStart(2, '0')}:00`;

    const slotMinTime = `${String(startHrs).padStart(2, '0')}:${String(startMins).padStart(2, '0')}:00`;
    let maxHrs = endHrs;
    let maxMins = endMins + defaultDuration;
    if (maxMins >= 60) {
        maxHrs += Math.floor(maxMins / 60);
        maxMins = maxMins % 60;
    }
    const slotMaxTime = `${String(maxHrs).padStart(2, '0')}:${String(maxMins).padStart(2, '0')}:00`;

    const currentLang = config.currentLang || (document.documentElement.getAttribute('lang') || 'en');
    const isArabic = config.isArabic !== undefined ? config.isArabic : (currentLang === 'ar');

    const arabicTranslations = {
        "Check-up": "فحص طبي",
        "Cleaning": "تنظيف أسنان",
        "Filling": "حشوة أسنان",
        "Root Canal": "علاج عصب السن",
        "Extraction": "قلع سن",
        "Crown / Bridge": "تاج / جسر",
        "Braces / Orthodontics": "تقويم الأسنان",
        "Whitening": "تبييض الأسنان",
        "Emergency Pain": "ألم طارئ",
        "Follow-up": "متابعة ودورية"
    };

    const reasons = config.reasons || [];
    const doctorsList = config.doctorsList || [];
    const eventsUrl = config.eventsUrl || '/portal/events';
    const bookAppointmentUrl = config.bookAppointmentUrl || '/portal/book';

    const calendar = new FullCalendar.Calendar(calendarEl, {
        locale: isArabic ? 'ar' : 'en',
        direction: isArabic ? 'rtl' : 'ltr',
        buttonText: {
            today: isArabic ? 'اليوم' : 'Today',
            month: isArabic ? 'شهر' : 'Month',
            week: isArabic ? 'أسبوع' : 'Week',
            day: isArabic ? 'يوم' : 'Day',
            list: isArabic ? 'قائمة' : 'List'
        },
        initialView: window.innerWidth < 768 ? 'timeGridDay' : 'timeGridWeek',
        allDaySlot: false,
        slotMinTime: slotMinTime,
        slotMaxTime: slotMaxTime,
        slotDuration: slotDurationStr,
        eventTimeFormat: {
            hour: 'numeric',
            minute: '2-digit',
            meridiem: 'short',
            hour12: true
        },
        headerToolbar: {
            left: window.innerWidth < 768 ? 'prev,next' : 'prev,next today',
            center: 'title',
            right: window.innerWidth < 768 ? 'timeGridDay,dayGridMonth' : 'timeGridWeek,dayGridMonth'
        },
        windowResize: function () {
            if (window.innerWidth < 768) {
                calendar.setOption('headerToolbar', {
                    left: 'prev,next',
                    center: 'title',
                    right: 'timeGridDay,dayGridMonth'
                });
                if (calendar.view.type === 'timeGridWeek') {
                    calendar.changeView('timeGridDay');
                }
            } else {
                calendar.setOption('headerToolbar', {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'timeGridWeek,dayGridMonth'
                });
            }
        },
        events: eventsUrl,
        eventDataTransform: function (eventData) {
            if (isArabic && eventData.title === 'Reserved') {
                eventData.title = 'محجوز';
            }
            return eventData;
        },
        datesSet: function (info) {
            const now = new Date();
            const calInstance = info.view.calendar;
            const currentFocused = calInstance.getDate();

            if ((info.view.type === 'timeGridDay' || info.view.type === 'timeGridWeek') &&
                currentFocused.getDate() === 1 &&
                currentFocused.getMonth() === now.getMonth() &&
                currentFocused.getFullYear() === now.getFullYear()) {
                setTimeout(() => {
                    calInstance.gotoDate(now);
                }, 0);
                return;
            }

            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const maxDate = new Date(todayStart);
            maxDate.setDate(maxDate.getDate() + bookingWindowDays);

            const dateEls = document.querySelectorAll('[data-date]');
            dateEls.forEach(el => {
                const dateStr = el.getAttribute('data-date');
                if (!dateStr) return;

                const parts = dateStr.split('-');
                if (parts.length !== 3) return;
                const date = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
                const dateStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());

                const dayOfWeek = date.getDay();
                const isHoliday = !workingDays.includes(dayOfWeek);
                const isPast = dateStart < todayStart;
                const isFutureLimit = dateStart > maxDate;

                if (isHoliday || isPast || isFutureLimit) {
                    el.classList.add('fc-day-disabled');
                    document.querySelectorAll(`.fc-timegrid-col[data-date="${dateStr}"]`).forEach(col => {
                        col.classList.add('fc-day-disabled');
                    });
                } else {
                    el.classList.remove('fc-day-disabled');
                    document.querySelectorAll(`.fc-timegrid-col[data-date="${dateStr}"]`).forEach(col => {
                        col.classList.remove('fc-day-disabled');
                    });
                }
            });
        },
        dateClick: function (info) {
            const now = new Date();
            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

            const datePartStr = info.dateStr.split('T')[0];
            const [yStr, mStr, dStr] = datePartStr.split('-');
            const selYear = parseInt(yStr, 10);
            const selMonth = parseInt(mStr, 10) - 1;
            const selDay = parseInt(dStr, 10);

            const clickedDateStart = new Date(selYear, selMonth, selDay);
            const dayOfWeek = clickedDateStart.getDay();

            if (!workingDays.includes(dayOfWeek)) {
                Swal.fire({
                    icon: 'error',
                    title: isArabic ? 'العيادة مغلقة' : 'Clinic Closed',
                    text: isArabic ? 'لا يمكن حجز مواعيد في أيام العطل الرسمية.' : 'Appointments cannot be booked on holidays.',
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            if (clickedDateStart < todayStart) {
                Swal.fire({
                    icon: 'error',
                    title: isArabic ? 'تاريخ غير صالح' : 'Invalid Date',
                    text: isArabic ? 'لا يمكن حجز مواعيد في الماضي.' : 'Appointments cannot be booked in the past.',
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            const hasTime = info.dateStr.includes('T') || info.dateStr.includes(' ');
            let clickedDate = info.date;

            if (hasTime && clickedDate < now) {
                Swal.fire({
                    icon: 'error',
                    title: isArabic ? 'وقت غير صالح' : 'Invalid Time',
                    text: isArabic ? 'الوقت المحدد في الماضي. يرجى اختيار وقت مستقبلي.' : 'Selected time is in the past. Please choose a future time.',
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            const startVal = startHrs * 60 + startMins;
            const endVal = endHrs * 60 + endMins;
            const events = calendar.getEvents();
            const availableSlots = [];

            const maxDate = new Date(todayStart);
            maxDate.setDate(maxDate.getDate() + bookingWindowDays);
            maxDate.setHours(23, 59, 59, 999);
            if (clickedDateStart > maxDate) {
                Swal.fire({
                    icon: 'error',
                    title: isArabic ? 'تجاوز فترة الحجز' : 'Booking Period Exceeded',
                    text: isArabic ? `لا يمكن حجز المواعيد قبل أكثر من ${bookingWindowDays} يوماً.` : `Appointments cannot be booked more than ${bookingWindowDays} days in advance.`,
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            for (let mins = startVal; mins + defaultDuration <= endVal; mins += defaultDuration) {
                const slotH = Math.floor(mins / 60);
                const slotM = mins % 60;
                const testDate = new Date(selYear, selMonth, selDay, slotH, slotM);

                if (testDate > now) {
                    let isOcc = false;
                    events.forEach(evt => {
                        if (evt.start && evt.end && testDate >= evt.start && testDate < evt.end) {
                            isOcc = true;
                        }
                    });
                    if (!isOcc) {
                        const timeValStr = (slotH < 10 ? '0' : '') + slotH + ':' + (slotM < 10 ? '0' : '') + slotM;
                        const timeLabel = testDate.toLocaleTimeString(isArabic ? 'ar' : undefined, { hour: '2-digit', minute: '2-digit', hour12: true });
                        availableSlots.push({ val: timeValStr, label: timeLabel });
                    }
                }
            }

            if (availableSlots.length === 0) {
                Swal.fire({
                    icon: 'warning',
                    title: isArabic ? 'لا توجد أوقات متاحة' : 'No Available Slots',
                    text: isArabic ? 'عفواً، لا توجد أوقات متاحة للحجز في هذا اليوم. يرجى اختيار يوم آخر.' : 'Sorry, no available slots for this day. Please pick another day.',
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            let defaultTimeVal = availableSlots[0].val;
            if (hasTime) {
                const clickedH = clickedDate.getHours();
                const clickedM = clickedDate.getMinutes();
                const clickedValStr = (clickedH < 10 ? '0' : '') + clickedH + ':' + (clickedM < 10 ? '0' : '') + clickedM;
                if (availableSlots.some(s => s.val === clickedValStr)) {
                    defaultTimeVal = clickedValStr;
                }
            }

            let timeSelectHtml = `<div class="mt-3 text-start"><label class="form-label swal-custom-label fw-bold mb-1">${isArabic ? 'اختر وقت الموعد' : 'Select Time Slot'}</label><select id="swal-time-slot" class="form-select">`;
            availableSlots.forEach(s => {
                const isSelected = s.val === defaultTimeVal ? 'selected' : '';
                timeSelectHtml += `<option value="${s.val}" ${isSelected}>${s.label}</option>`;
            });
            timeSelectHtml += `</select></div>`;

            const selectOptions = {};
            reasons.forEach(r => {
                selectOptions[r] = arabicTranslations[r] || r;
            });

            const formattedDate = clickedDateStart.toLocaleDateString(isArabic ? 'ar' : undefined);

            let doctorSelectHtml = `<div class="mt-3 text-start"><label class="form-label swal-custom-label fw-bold mb-1">${isArabic ? 'اختر الطبيب المفضل (اختياري)' : 'Select Preferred Doctor (Optional)'}</label><select id="swal-doctor-id" class="form-select"><option value="">${isArabic ? 'أي طبيب متاح' : 'Any Available Doctor'}</option>`;
            doctorsList.forEach(d => {
                doctorSelectHtml += `<option value="${d.id}">${d.name}</option>`;
            });
            doctorSelectHtml += `</select></div>`;

            Swal.fire({
                title: isArabic ? 'طلب حجز موعد جديد' : 'Request Appointment',
                html: `<p class="mb-2">${isArabic ? 'اختر تفاصيل الموعد المطلوبة:' : 'Select your preferred appointment details:'}</p>
                       <div class="text-primary fw-bold mb-3 fs-5">${formattedDate}</div>
                       ${timeSelectHtml}
                       ${doctorSelectHtml}`,
                input: 'select',
                inputOptions: selectOptions,
                inputPlaceholder: isArabic ? 'اختر سبب الحجز' : 'Select a Reason',
                showCancelButton: true,
                confirmButtonText: isArabic ? 'تقديم الطلب' : 'Submit Request',
                cancelButtonText: isArabic ? 'إلغاء' : 'Cancel',
                confirmButtonColor: '#175cdd',
                preConfirm: () => {
                    const reasonSelect = Swal.getInput();
                    const reasonVal = reasonSelect ? reasonSelect.value : '';
                    if (!reasonVal) {
                        Swal.showValidationMessage(isArabic ? 'يجب اختيار سبب الحجز' : 'You must select a reason');
                        return false;
                    }
                    const timeEl = document.getElementById('swal-time-slot');
                    const docEl = document.getElementById('swal-doctor-id');
                    return {
                        reason: reasonVal,
                        timeSlot: timeEl ? timeEl.value : '',
                        doctorId: docEl ? docEl.value : ''
                    };
                }
            }).then((result) => {
                if (result.isConfirmed && result.value) {
                    const { reason, timeSlot, doctorId } = result.value;

                    Swal.fire({
                        title: isArabic ? 'جاري إرسال الطلب...' : 'Submitting Request...',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });

                    const finalDateParam = `${datePartStr}T${timeSlot}`;
                    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
                    const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

                    const formData = new URLSearchParams();
                    formData.append('appointment_date', finalDateParam);
                    formData.append('reason', reason);
                    if (doctorId) formData.append('doctor_id', doctorId);
                    formData.append('csrf_token', csrfToken);

                    fetch(bookAppointmentUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: formData.toString()
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.success) {
                                Swal.fire({
                                    icon: 'success',
                                    title: isArabic ? 'تم تقديم الطلب' : 'Request Submitted',
                                    text: data.message || (isArabic ? 'تم إرسال طلب الموعد بنجاح، وهو الآن قيد التثبيت.' : 'Request submitted successfully.'),
                                    confirmButtonColor: '#175cdd'
                                }).then(() => {
                                    window.location.href = window.portalDashboardUrl;
                                });
                            } else {
                                Swal.fire({
                                    icon: 'error',
                                    title: isArabic ? 'تنبيه' : 'Notice',
                                    text: data.message || (isArabic ? 'فشل تقديم الطلب. يرجى المحاولة مرة أخرى.' : 'Failed to request appointment.'),
                                    confirmButtonColor: '#175cdd'
                                });
                            }
                        })
                        .catch(err => {
                            console.error(err);
                            window.location.href = window.portalDashboardUrl;
                        });
                }
            });
        }
    });

    calendar.render();

    // 30-minute slot hover highlight in Week/Day views
    if (!window.matchMedia("(pointer: coarse)").matches) {
        const hoverHighlight = document.createElement('div');
        hoverHighlight.className = 'fc-timegrid-hover-highlight';

        document.addEventListener('mousemove', function (e) {
            if (!e.target || typeof e.target.closest !== 'function') return;
            const timegridBody = e.target.closest('.fc-timegrid-body');
            if (!timegridBody) {
                hoverHighlight.style.display = 'none';
                return;
            }

            if (hoverHighlight.parentElement !== timegridBody) {
                timegridBody.appendChild(hoverHighlight);
            }

            const rect = timegridBody.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const cols = timegridBody.querySelectorAll('.fc-timegrid-col');
            let hoveredCol = null;
            let colLeft = 0;
            let colWidth = 0;

            cols.forEach(col => {
                const colRect = col.getBoundingClientRect();
                const left = colRect.left - rect.left;
                if (x >= left && x <= left + colRect.width) {
                    hoveredCol = col;
                    colLeft = left;
                    colWidth = colRect.width;
                }
            });

            if (!hoveredCol) {
                hoverHighlight.style.display = 'none';
                timegridBody.style.cursor = 'default';
                return;
            }

            const slotLanes = timegridBody.querySelectorAll('.fc-timegrid-slots tr');
            let hoveredSlotRow = null;
            let slotTop = 0;
            let slotHeight = 0;

            slotLanes.forEach(lane => {
                const laneRect = lane.getBoundingClientRect();
                const top = laneRect.top - rect.top;
                if (y >= top && y <= top + laneRect.height) {
                    hoveredSlotRow = lane;
                    slotTop = top;
                    slotHeight = laneRect.height;
                }
            });

            if (!hoveredSlotRow) {
                hoverHighlight.style.display = 'none';
                timegridBody.style.cursor = 'default';
                return;
            }

            const dateStr = hoveredCol.getAttribute('data-date');
            const timeStr = hoveredSlotRow.getAttribute('data-time');

            let isAllowed = true;
            if (dateStr && timeStr) {
                const slotDate = new Date(dateStr + 'T' + timeStr);
                const now = new Date();
                const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

                const dayOfWeek = slotDate.getDay();
                const isHoliday = !workingDays.includes(dayOfWeek);
                const isPast = slotDate < now;

                const maxDate = new Date(todayStart);
                maxDate.setDate(maxDate.getDate() + bookingWindowDays);
                maxDate.setHours(23, 59, 59, 999);
                const isFutureLimit = slotDate > maxDate;

                let isOccupied = false;
                const events = calendar.getEvents();
                events.forEach(evt => {
                    if (evt.start && evt.end && slotDate >= evt.start && slotDate < evt.end) {
                        isOccupied = true;
                    }
                });

                if (isHoliday || isPast || isFutureLimit || isOccupied) {
                    isAllowed = false;
                }
            } else if (hoveredCol.classList.contains('fc-day-disabled') || hoveredCol.classList.contains('fc-day-past')) {
                isAllowed = false;
            }

            const isOverEvent = e.target.closest('.fc-event');

            if (isOverEvent || !isAllowed) {
                timegridBody.style.cursor = 'not-allowed';
                hoverHighlight.style.display = 'none';
            } else {
                timegridBody.style.cursor = 'pointer';
                hoverHighlight.style.left = (colLeft + 2) + 'px';
                hoverHighlight.style.width = (colWidth - 4) + 'px';
                hoverHighlight.style.top = (slotTop + 1) + 'px';
                hoverHighlight.style.height = (slotHeight - 2) + 'px';
                hoverHighlight.style.display = 'block';
            }
        });

        document.addEventListener('mouseleave', function (e) {
            if (e.target && e.target.classList && typeof e.target.classList.contains === 'function' && e.target.classList.contains('fc-timegrid-body')) {
                hoverHighlight.style.display = 'none';
                e.target.style.cursor = 'default';
            }
        }, true);
    }
};
