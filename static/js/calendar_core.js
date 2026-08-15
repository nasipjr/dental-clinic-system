/**
 * Dental Clinic Management System - Interactive Appointment Calendar Controller
 * Isolated client-side logic for FullCalendar, drag-and-drop rescheduling, interactive filters, and quick session triggers.
 */

window.initAppointmentCalendar = function (config) {
    window.addEventListener('pageshow', function () {
        if (typeof Swal !== 'undefined') {
            Swal.close();
        }
    });

    const calendarEl = document.getElementById('calendar');
    if (!calendarEl || typeof FullCalendar === 'undefined') return;

    const workingHoursStart = config.workingHoursStart || "09:00";
    const workingHoursEnd = config.workingHoursEnd || "17:00";
    const bookingWindowDays = parseInt(config.bookingWindowDays, 10) || 30;
    const defaultDuration = parseInt(config.defaultDuration, 10) || 30;
    const workingDaysList = config.workingDaysList || [0, 1, 2, 3, 4, 6];
    const currentLang = config.currentLang || (document.documentElement.getAttribute('lang') || 'en');
    const canSeeWhatsApp = config.canSeeWhatsApp || false;
    const clinicName = config.clinicName || '';
    const csrfToken = config.csrfToken || '';
    const patientsListApiUrl = config.patientsListApiUrl || '/appointments/api/patients-list';

    const startParts = workingHoursStart ? workingHoursStart.split(':') : ["09", "00"];
    const endParts = workingHoursEnd ? workingHoursEnd.split(':') : ["17", "00"];
    const startHrs = isNaN(parseInt(startParts[0], 10)) ? 9 : parseInt(startParts[0], 10);
    const startMins = isNaN(parseInt(startParts[1], 10)) ? 0 : parseInt(startParts[1], 10);
    const endHrs = isNaN(parseInt(endParts[0], 10)) ? 17 : parseInt(endParts[0], 10);
    const endMins = isNaN(parseInt(endParts[1], 10)) ? 0 : parseInt(endParts[1], 10);

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

    const calendar = new FullCalendar.Calendar(calendarEl, {
        locale: currentLang === 'ar' ? 'ar' : 'en',
        direction: currentLang === 'ar' ? 'rtl' : 'ltr',
        editable: true,
        eventStartEditable: true,
        eventDurationEditable: false,
        buttonText: {
            today: currentLang === 'ar' ? 'اليوم' : 'Today',
            month: currentLang === 'ar' ? 'شهر' : 'Month',
            week: currentLang === 'ar' ? 'أسبوع' : 'Week',
            day: currentLang === 'ar' ? 'يوم' : 'Day',
            list: currentLang === 'ar' ? 'قائمة' : 'List',
            dayGridMonth: currentLang === 'ar' ? 'شهر' : 'Month',
            timeGridWeek: currentLang === 'ar' ? 'أسبوع' : 'Week',
            listMonth: currentLang === 'ar' ? 'قائمة' : 'List'
        },
        buttonHints: {
            today: (buttonText) => currentLang === 'ar' ? 'اليوم الحالي' : `This ${buttonText}`,
            month: (buttonText) => currentLang === 'ar' ? 'الشهر الحالي' : `This ${buttonText}`,
            week: (buttonText) => currentLang === 'ar' ? 'الأسبوع الحالي' : `This ${buttonText}`,
            day: (buttonText) => currentLang === 'ar' ? 'اليوم الحالي' : `This ${buttonText}`,
            list: (buttonText) => currentLang === 'ar' ? 'قائمة المواعيد' : `This ${buttonText}`,
            prev: (buttonText) => currentLang === 'ar' ? 'السابق' : `Previous ${buttonText}`,
            next: (buttonText) => currentLang === 'ar' ? 'التالي' : `Next ${buttonText}`
        },
        titleFormatter: function (dateInfo) {
            const monthsAr = [
                "كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران",
                "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"
            ];
            const monthsEn = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ];
            const d = dateInfo.date;
            const mName = currentLang === 'ar' ? monthsAr[d.month] : monthsEn[d.month];
            return `${mName} ${d.year}`;
        },
        initialView: window.innerWidth < 768 ? 'listMonth' : 'dayGridMonth',
        allDaySlot: false,
        slotLabelFormat: {
            hour: 'numeric',
            minute: '2-digit',
            meridiem: 'short',
            hour12: true
        },
        slotEventOverlap: false,
        slotMinTime: slotMinTime,
        slotMaxTime: slotMaxTime,
        slotDuration: slotDurationStr,
        eventTimeFormat: {
            hour: 'numeric',
            minute: '2-digit',
            meridiem: 'short',
            hour12: true
        },
        eventDisplay: 'block',
        contentHeight: 'auto',
        headerToolbar: {
            left: window.innerWidth < 768 ? 'prev,next' : 'prev,next today',
            center: 'title',
            right: window.innerWidth < 768 ? 'dayGridMonth,timeGridDay,listMonth' : 'dayGridMonth,timeGridWeek,listMonth'
        },
        windowResize: function () {
            if (window.innerWidth < 768) {
                calendar.setOption('headerToolbar', {
                    left: 'prev,next',
                    center: 'title',
                    right: 'dayGridMonth,timeGridDay,listMonth'
                });
                if (calendar.view.type === 'timeGridWeek') {
                    calendar.changeView('timeGridDay');
                }
            } else {
                calendar.setOption('headerToolbar', {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,listMonth'
                });
            }
        },
        events: function (info, successCallback, failureCallback) {
            fetch('/appointments/events')
                .then(response => response.json())
                .then(data => {
                    const showScheduled = document.getElementById('filter-scheduled')?.checked ?? true;
                    const showDone = document.getElementById('filter-done')?.checked ?? true;
                    const showCancelled = document.getElementById('filter-cancelled')?.checked ?? true;

                    const filtered = data.filter(event => {
                        const status = event.extendedProps.status;
                        if (status === 'Scheduled' && !showScheduled) return false;
                        if (status === 'Done' && !showDone) return false;
                        if (status === 'Cancelled' && !showCancelled) return false;
                        return true;
                    });
                    successCallback(filtered);
                })
                .catch(err => {
                    console.error('Failed to fetch calendar events:', err);
                    failureCallback(err);
                });
        },
        eventClassNames: function (arg) {
            const status = arg.event.extendedProps.status;
            return ['event-status-' + (status ? status.toLowerCase() : 'scheduled')];
        },
        eventContent: function (arg) {
            if (arg.view && arg.view.type && arg.view.type.startsWith('list')) {
                return;
            }
            const start = arg.event.start;
            if (!start) return { html: arg.event.title };

            let hours = start.getHours();
            const minutes = String(start.getMinutes()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            const timeText = `${hours}:${minutes} ${ampm}`;

            return {
                html: `<div class="fc-event-main-frame" style="display: flex; flex-wrap: wrap; align-items: baseline;">
                         <div class="fc-event-time" style="font-weight: 800; margin-right: 6px; white-space: nowrap; color: #ffffff !important;">${timeText}</div>
                         <div class="fc-event-title" style="font-weight: 600; color: #ffffff !important;">${arg.event.title}</div>
                       </div>`
            };
        },
        datesSet: function (info) {
            const now = new Date();
            const calInstance = info.view.calendar;
            const currentFocused = calInstance.getDate();

            const monthSelectEl = document.getElementById('calendar-month-select');
            const yearSelectEl = document.getElementById('calendar-year-select');
            if (monthSelectEl) monthSelectEl.value = currentFocused.getMonth();
            if (yearSelectEl) yearSelectEl.value = currentFocused.getFullYear();

            if (currentLang === 'ar') {
                const monthsAr = [
                    "كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران",
                    "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"
                ];
                const titleEl = document.querySelector('.fc-toolbar-title');
                if (titleEl) {
                    const mName = monthsAr[currentFocused.getMonth()];
                    const yearVal = currentFocused.getFullYear();
                    titleEl.textContent = `${mName} ${yearVal}`;
                }
            }

            document.querySelectorAll('.fc-button').forEach(btn => {
                const title = btn.getAttribute('title') || '';
                if (title.includes('This') || title.includes('Previous') || title.includes('Next')) {
                    if (btn.classList.contains('fc-dayGridMonth-button') || btn.classList.contains('fc-month-button')) {
                        btn.setAttribute('title', currentLang === 'ar' ? 'الشهر الحالي' : 'This Month');
                    } else if (btn.classList.contains('fc-timeGridWeek-button') || btn.classList.contains('fc-week-button')) {
                        btn.setAttribute('title', currentLang === 'ar' ? 'الأسبوع الحالي' : 'This Week');
                    } else if (btn.classList.contains('fc-timeGridDay-button') || btn.classList.contains('fc-day-button')) {
                        btn.setAttribute('title', currentLang === 'ar' ? 'اليوم الحالي' : 'This Day');
                    } else if (btn.classList.contains('fc-listMonth-button') || btn.classList.contains('fc-list-button')) {
                        btn.setAttribute('title', currentLang === 'ar' ? 'قائمة المواعيد' : 'List View');
                    } else if (btn.classList.contains('fc-today-button')) {
                        btn.setAttribute('title', currentLang === 'ar' ? 'اليوم' : 'Today');
                    } else if (btn.classList.contains('fc-prev-button')) {
                        btn.setAttribute('title', currentLang === 'ar' ? 'السابق' : 'Previous');
                    } else if (btn.classList.contains('fc-next-button')) {
                        btn.setAttribute('title', currentLang === 'ar' ? 'التالي' : 'Next');
                    }
                }
            });

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

            const workingDays = workingDaysList || [0, 1, 2, 3, 4, 6];

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
            const clickedDate = info.date;
            const now = new Date();
            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const clickedDateStart = new Date(clickedDate.getFullYear(), clickedDate.getMonth(), clickedDate.getDate());

            const workingDays = workingDaysList || [0, 1, 2, 3, 4, 6];
            const dayOfWeek = clickedDate.getDay();

            if (!workingDays.includes(dayOfWeek)) {
                Swal.fire({
                    icon: 'error',
                    title: currentLang === 'ar' ? 'العيادة مغلقة' : 'Clinic Closed',
                    text: currentLang === 'ar' ? 'لا يمكن حجز مواعيد في أيام العطل الرسمية.' : 'Appointments cannot be booked on holidays (Clinic is closed).',
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            if (clickedDateStart < todayStart) {
                Swal.fire({
                    icon: 'error',
                    title: currentLang === 'ar' ? 'تاريخ غير صالح' : 'Invalid Date',
                    text: currentLang === 'ar' ? 'لا يمكن حجز مواعيد في الماضي.' : 'Appointments cannot be booked in the past.',
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            const hasTime = info.dateStr.includes('T') || info.dateStr.includes(' ');
            if (hasTime && clickedDate < now) {
                Swal.fire({
                    icon: 'error',
                    title: currentLang === 'ar' ? 'وقت غير صالح' : 'Invalid Time',
                    text: currentLang === 'ar' ? 'الوقت المحدد في الماضي. يرجى اختيار وقت مستقبلي.' : 'Selected time is in the past. Please choose a future time.',
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            if (hasTime) {
                const hours = clickedDate.getHours();
                const minutes = clickedDate.getMinutes();
                const timeVal = hours * 60 + minutes;
                const startVal = startHrs * 60 + startMins;
                const endVal = endHrs * 60 + endMins;
                if (timeVal < startVal || timeVal > endVal) {
                    Swal.fire({
                        icon: 'error',
                        title: currentLang === 'ar' ? 'خارج ساعات العمل' : 'Outside Business Hours',
                        text: currentLang === 'ar' ? `يجب جدولة المواعيد بين ${workingHoursStart} و ${workingHoursEnd}.` : `Appointments must be scheduled between ${workingHoursStart} and ${workingHoursEnd}.`,
                        confirmButtonColor: '#175cdd'
                    });
                    return;
                }
            }

            const maxDate = new Date(todayStart);
            maxDate.setDate(maxDate.getDate() + bookingWindowDays);
            maxDate.setHours(23, 59, 59, 999);
            if (clickedDate > maxDate) {
                Swal.fire({
                    icon: 'error',
                    title: currentLang === 'ar' ? 'تجاوز فترة الحجز' : 'Booking Period Exceeded',
                    text: currentLang === 'ar' ? `لا يمكن حجز المواعيد قبل أكثر من ${bookingWindowDays} يوماً.` : `Appointments cannot be booked more than ${bookingWindowDays} days in advance.`,
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            let dateParam = info.dateStr;
            if (!hasTime) {
                if (clickedDateStart.getTime() === todayStart.getTime()) {
                    const nextSlot = new Date(now);
                    const mins = nextSlot.getMinutes();
                    const remainder = mins % defaultDuration;
                    if (remainder === 0) {
                        nextSlot.setSeconds(0, 0);
                    } else {
                        nextSlot.setMinutes(mins + (defaultDuration - remainder), 0, 0);
                    }

                    if (nextSlot.getHours() * 60 + nextSlot.getMinutes() >= endHrs * 60 + endMins) {
                        Swal.fire({
                            icon: 'warning',
                            title: currentLang === 'ar' ? 'العيادة على وشك الإغلاق' : 'Clinic Closing Soon',
                            text: currentLang === 'ar' ? 'لا توجد فترات حجز متبقية لليوم. يرجى اختيار تاريخ مستقبلي.' : 'There are no remaining booking slots for today. Please select a future date.',
                            confirmButtonColor: '#175cdd'
                        });
                        return;
                    } else {
                        const hoursStr = String(nextSlot.getHours()).padStart(2, '0');
                        const minsStr = String(nextSlot.getMinutes()).padStart(2, '0');
                        dateParam += `T${hoursStr}:${minsStr}`;
                    }
                } else {
                    dateParam += `T${workingHoursStart}`;
                }
            } else {
                dateParam = dateParam.substring(0, 16);
            }

            Swal.fire({
                title: currentLang === 'ar' ? 'جارٍ إنشاء الموعد...' : 'Creating Appointment...',
                text: currentLang === 'ar' ? 'جارٍ التحويل إلى نموذج الموعد' : 'Redirecting to appointment form',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                    window.location.href = `/appointments/add?date=${encodeURIComponent(dateParam)}`;
                }
            });
        },
        eventClick: function (info) {
            const props = info.event.extendedProps;

            const nameEl = document.getElementById('modal-patient-name');
            if (nameEl) nameEl.textContent = props.patientName;

            const patientLinkEl = document.getElementById('modal-patient-link');
            if (patientLinkEl && props.patientUrl) {
                patientLinkEl.href = props.patientUrl;
            }

            const phoneEl = document.getElementById('modal-phone');
            if (phoneEl) phoneEl.textContent = props.phone;

            const start = info.event.start;
            const formattedDate = start.toLocaleDateString() + ' ' + start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
            const dtEl = document.getElementById('modal-date-time');
            if (dtEl) dtEl.textContent = formattedDate;

            const reasonEl = document.getElementById('modal-reason');
            if (reasonEl) reasonEl.textContent = props.reason;

            const statusBadge = document.getElementById('modal-status');
            let displayStatus = props.status;
            if (currentLang === 'ar') {
                if (props.status === 'Done') displayStatus = 'منجز';
                else if (props.status === 'Scheduled') displayStatus = 'مجدول';
                else if (props.status === 'Cancelled') displayStatus = 'ملغي';
                else if (props.status === 'Pending') displayStatus = 'قيد التثبيت';
                else if (props.status === 'Rejected') displayStatus = 'تم الرفض';
            }
            if (statusBadge) {
                statusBadge.textContent = displayStatus;
                statusBadge.className = 'badge';
                if (props.status === 'Done' || props.status === 'منجز') {
                    statusBadge.classList.add('bg-success');
                } else if (props.status === 'Cancelled' || props.status === 'ملغي') {
                    statusBadge.classList.add('bg-danger');
                } else {
                    statusBadge.classList.add('bg-primary');
                }
            }

            const isClosed = (props.isClosed === true || props.status === 'Done' || props.status === 'Cancelled' || props.status === 'منجز' || props.status === 'ملغي');

            const sessionBtn = document.getElementById('modal-session-link');
            if (sessionBtn) {
                if (props.canOpenSession === true && props.sessionUrl) {
                    sessionBtn.style.setProperty('display', 'inline-block', 'important');
                    if (props.status === 'Done' || props.status === 'منجز') {
                        sessionBtn.innerHTML = `<i class="bi bi-arrow-counterclockwise me-1"></i> ${currentLang === 'ar' ? 'إعادة فتح الجلسة' : 'Reopen Session'}`;
                        sessionBtn.removeAttribute('href');
                        sessionBtn.onclick = function (e) {
                            e.preventDefault();
                            Swal.fire({
                                title: currentLang === 'ar' ? 'إعادة فتح الجلسة؟' : 'Reopen Session?',
                                text: currentLang === 'ar'
                                    ? 'هل أنت متأكد من إعادة فتح هذه الجلسة؟ سيتم تفعيل إمكانية إضافة وتعديل المعالجات.'
                                    : 'Are you sure you want to reopen this session? This will enable adding and editing treatments.',
                                icon: 'question',
                                showCancelButton: true,
                                confirmButtonText: currentLang === 'ar' ? 'نعم، أعد فتح الجلسة' : 'Yes, reopen',
                                cancelButtonText: currentLang === 'ar' ? 'إلغاء' : 'Cancel',
                                confirmButtonColor: '#175cdd',
                                cancelButtonColor: '#64748b'
                            }).then((result) => {
                                if (result.isConfirmed) {
                                    const form = document.createElement('form');
                                    form.method = 'POST';
                                    form.action = `/appointments/${info.event.id}/reopen-session`;
                                    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || csrfToken;
                                    if (token) {
                                        const csrfInput = document.createElement('input');
                                        csrfInput.type = 'hidden';
                                        csrfInput.name = 'csrf_token';
                                        csrfInput.value = token;
                                        form.appendChild(csrfInput);
                                    }
                                    document.body.appendChild(form);
                                    form.submit();
                                }
                            });
                        };
                    } else {
                        sessionBtn.href = props.sessionUrl;
                        sessionBtn.onclick = null;
                        sessionBtn.innerHTML = `<i class="bi bi-clipboard2-pulse me-1"></i> ${currentLang === 'ar' ? 'فتح الجلسة' : 'Open Session'}`;
                    }
                } else {
                    sessionBtn.style.setProperty('display', 'none', 'important');
                    sessionBtn.removeAttribute('href');
                    sessionBtn.onclick = null;
                }
            }

            const viewLink = document.getElementById('modal-view-link');
            if (viewLink) viewLink.href = props.viewUrl;

            const editBtn = document.getElementById('modal-edit-link');
            const isEditable = !isClosed && props.status !== 'Done' && props.status !== 'Cancelled' && props.status !== 'منجز' && props.status !== 'ملغي';
            if (editBtn) {
                if (props.canEdit === true && props.editUrl && isEditable) {
                    editBtn.href = props.editUrl;
                    editBtn.style.setProperty('display', 'inline-block', 'important');
                } else {
                    editBtn.style.setProperty('display', 'none', 'important');
                    editBtn.removeAttribute('href');
                }
            }

            const whatsappBtn = document.getElementById('modal-whatsapp-btn');
            const remindedRow = document.getElementById('modal-reminded-row');
            const remindedStatus = document.getElementById('modal-reminded-status');

            if (canSeeWhatsApp && !isClosed && props.canRemind === true && props.phone && props.phone !== 'No phone') {
                if (whatsappBtn) {
                    whatsappBtn.style.setProperty('display', 'inline-block', 'important');
                    whatsappBtn.onclick = function () {
                        if (typeof window.sendWhatsAppReminder === 'function') {
                            window.sendWhatsAppReminder(props.phone, props.patientName, formattedDate, clinicName, info.event.id);
                        }
                    };
                }
            } else {
                if (whatsappBtn) {
                    whatsappBtn.style.setProperty('display', 'none', 'important');
                    whatsappBtn.onclick = null;
                }
            }

            if (remindedRow && remindedStatus) {
                if (localStorage.getItem('reminded_appt_' + info.event.id) === 'true') {
                    remindedRow.style.display = 'block';
                    remindedStatus.innerHTML = `<span class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1 small align-middle" style="font-size: 0.72rem; font-weight: 700;">
                        <i class="bi bi-check-all fs-6"></i> ${currentLang === 'ar' ? 'تم التذكير' : 'Reminded'}
                    </span>`;
                } else {
                    remindedRow.style.display = 'none';
                    remindedStatus.innerHTML = '';
                }
            }

            const modalEl = document.getElementById('eventModal');
            if (modalEl) {
                const myModal = new bootstrap.Modal(modalEl);
                myModal.show();
            }
        },
        eventDrop: function (info) {
            const status = info.event.extendedProps.status;
            if (status !== 'Scheduled') {
                info.revert();
                Swal.fire({
                    icon: 'error',
                    title: currentLang === 'ar' ? 'غير مسموح' : 'Not Allowed',
                    text: currentLang === 'ar' ? 'يمكنك فقط سحب وتعديل المواعيد المجدولة.' : 'You can only reschedule scheduled appointments.',
                    confirmButtonColor: '#175cdd'
                });
                return;
            }

            Swal.fire({
                title: currentLang === 'ar' ? 'تعديل توقيت الموعد؟' : 'Reschedule Appointment?',
                text: currentLang === 'ar'
                    ? `هل أنت متأكد من نقل موعد المريض إلى ${info.event.start.toLocaleString([], { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' })}؟`
                    : `Are you sure you want to reschedule this appointment to ${info.event.start.toLocaleString()}?`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: currentLang === 'ar' ? 'نعم، انقل الموعد' : 'Yes, reschedule',
                cancelButtonText: currentLang === 'ar' ? 'إلغاء' : 'Cancel',
                confirmButtonColor: '#175cdd',
                cancelButtonColor: '#64748b'
            }).then((result) => {
                if (result.isConfirmed) {
                    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || csrfToken;
                    fetch(`/appointments/${info.event.id}/reschedule`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRF-Token': token
                        },
                        body: JSON.stringify({
                            start: new Date(info.event.start.getTime() - info.event.start.getTimezoneOffset() * 60000).toISOString().slice(0, 19)
                        })
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                localStorage.removeItem('reminded_appt_' + info.event.id);
                                document.querySelectorAll(`.reminded-status-placeholder[data-appointment-id="${info.event.id}"]`).forEach(el => {
                                    el.innerHTML = '';
                                });
                                const modalStatus = document.getElementById('modal-reminded-status');
                                if (modalStatus) modalStatus.innerHTML = '';
                                const remindedRow = document.getElementById('modal-reminded-row');
                                if (remindedRow) remindedRow.style.display = 'none';

                                Swal.fire({
                                    icon: 'success',
                                    title: currentLang === 'ar' ? 'تم النقل بنجاح!' : 'Rescheduled!',
                                    text: data.message,
                                    timer: 2000,
                                    showConfirmButton: false
                                });
                            } else {
                                info.revert();
                                Swal.fire({
                                    icon: 'error',
                                    title: currentLang === 'ar' ? 'خطأ' : 'Error',
                                    text: data.message,
                                    confirmButtonColor: '#175cdd'
                                });
                            }
                        })
                        .catch(() => {
                            info.revert();
                            Swal.fire({
                                icon: 'error',
                                title: currentLang === 'ar' ? 'خطأ' : 'Error',
                                text: currentLang === 'ar' ? 'حدث خطأ أثناء الاتصال بالخادم.' : 'An error occurred while contacting the server.',
                                confirmButtonColor: '#175cdd'
                            });
                        });
                } else {
                    info.revert();
                }
            });
        }
    });

    calendar.render();

    // Handle Quick Month & Year Jumpers
    const monthSelectEl = document.getElementById('calendar-month-select');
    const yearSelectEl = document.getElementById('calendar-year-select');

    function handleQuickJump() {
        if (!monthSelectEl || !yearSelectEl) return;
        const y = parseInt(yearSelectEl.value, 10);
        const m = parseInt(monthSelectEl.value, 10);
        calendar.gotoDate(new Date(y, m, 1));
    }

    if (monthSelectEl) monthSelectEl.addEventListener('change', handleQuickJump);
    if (yearSelectEl) yearSelectEl.addEventListener('change', handleQuickJump);

    // Register interactive status filter listeners
    const filters = ['filter-scheduled', 'filter-done', 'filter-cancelled'];
    filters.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => {
                calendar.refetchEvents();
            });
        }
    });

    // Set the dynamic filter header label based on language
    const filterTitleEl = document.getElementById('filter-title-span');
    if (filterTitleEl) {
        filterTitleEl.innerText = currentLang === 'ar' ? 'تصفية حسب الحالة:' : 'Filter Status:';
    }

    // 30-minute slot hover highlight in Week/Day views (Desktop only)
    if (!window.matchMedia("(pointer: coarse)").matches) {
        const hoverHighlight = document.createElement('div');
        hoverHighlight.className = 'fc-timegrid-hover-highlight';
        hoverHighlight.style.position = 'absolute';
        hoverHighlight.style.pointerEvents = 'none';
        hoverHighlight.style.display = 'none';
        hoverHighlight.style.backgroundColor = 'color-mix(in srgb, var(--accent-color), transparent 92%)';
        hoverHighlight.style.zIndex = '5';
        hoverHighlight.style.borderRadius = '4px';
        hoverHighlight.style.border = '1px solid color-mix(in srgb, var(--accent-color), transparent 75%)';
        hoverHighlight.style.transition = 'left 0.05s ease, top 0.05s ease, width 0.05s ease, height 0.05s ease';

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

                const workingDays = workingDaysList || [0, 1, 2, 3, 4, 6];
                const dayOfWeek = slotDate.getDay();
                const isHoliday = !workingDays.includes(dayOfWeek);
                const isPast = slotDate < now;

                const maxDate = new Date(todayStart);
                maxDate.setDate(maxDate.getDate() + bookingWindowDays);
                maxDate.setHours(23, 59, 59, 999);
                const isFutureLimit = slotDate > maxDate;

                if (isHoliday || isPast || isFutureLimit) {
                    isAllowed = false;
                }
            } else if (hoveredCol.classList.contains('fc-day-disabled') || hoveredCol.classList.contains('fc-day-past')) {
                isAllowed = false;
            }

            const isOverEvent = e.target.closest('.fc-event');

            if (isOverEvent) {
                timegridBody.style.cursor = 'pointer';
                hoverHighlight.style.display = 'none';
            } else if (!isAllowed) {
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

    // Quick Session Modal AJAX patient select loader
    const quickModal = document.getElementById("quickSessionModal");
    if (quickModal) {
        quickModal.addEventListener("show.bs.modal", function () {
            const select = document.getElementById("calendar-quick-session-patient-select");
            if (!select || select.dataset.loaded) return;
            fetch(patientsListApiUrl)
                .then(r => r.json())
                .then(data => {
                    select.innerHTML = `<option value="">${currentLang === "ar" ? "-- اختر المريض --" : "-- Select Patient --"}</option>`;
                    data.forEach(p => {
                        const opt = document.createElement("option");
                        opt.value = p.id;
                        opt.textContent = `${p.name} (${p.phone})`;
                        select.appendChild(opt);
                    });
                    select.dataset.loaded = "true";
                })
                .catch(err => console.error("Failed to load patients", err));
        });
    }
};
