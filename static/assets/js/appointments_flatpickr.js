document.addEventListener("DOMContentLoaded", function () {
    const appointmentInput = document.getElementById("appointment_date");
    if (!appointmentInput) return;

    // Remove the native HTML5 constraint validation script if present
    appointmentInput.setAttribute("type", "text");
    appointmentInput.setAttribute("placeholder", "Select Date & Time");

    // Retrieve settings parameters from data attributes
    const workingDaysAttr = appointmentInput.getAttribute("data-working-days") || "0,1,2,3,4,6";
    const minTimeAttr = appointmentInput.getAttribute("data-min-time") || "08:00";
    const maxTimeAttr = appointmentInput.getAttribute("data-max-time") || "18:00";
    const durationAttr = parseInt(appointmentInput.getAttribute("data-duration") || "30", 10);
    const workingDaysList = workingDaysAttr.split(",").map(d => parseInt(d.trim(), 10));
    const currentLang = document.documentElement.getAttribute('lang') || 'en';

    // Fetch booked slots
    const currentAppointmentId = typeof appointmentIdForEdit !== 'undefined' ? appointmentIdForEdit : "";
    const url = "/appointments/booked-slots" + (currentAppointmentId ? "?exclude_id=" + currentAppointmentId : "");

    fetch(url)
        .then(res => res.json())
        .then(bookedSlots => {
            flatpickr(appointmentInput, {
                enableTime: true,
                dateFormat: "Y-m-d h:i K",
                time_24hr: false,
                minDate: "today",
                maxDate: new Date().fp_incr(30),
                minuteIncrement: durationAttr,
                minTime: minTimeAttr,
                maxTime: maxTimeAttr,
                disable: [
                    function(date) {
                        return !workingDaysList.includes(date.getDay());
                    }
                ],
                onChange: function(selectedDates, dateStr, instance) {
                    if (bookedSlots.includes(dateStr)) {
                        const msg = currentLang === 'ar' 
                            ? "هذا الوقت محجوز بالفعل، يرجى اختيار وقت آخر." 
                            : "This slot is already reserved. Please select another time.";
                        alert(msg);
                        instance.clear();
                    }
                },
                locale: currentLang === 'ar' && typeof flatpickr.l10ns.ar !== 'undefined' ? {
                    ...flatpickr.l10ns.ar,
                    firstDayOfWeek: 0
                } : {
                    firstDayOfWeek: 0
                }
            });
        })
        .catch(err => {
            console.error("Failed to load booked slots", err);
            flatpickr(appointmentInput, {
                enableTime: true,
                dateFormat: "Y-m-d h:i K",
                time_24hr: false,
                minDate: "today",
                maxDate: new Date().fp_incr(30),
                minuteIncrement: durationAttr,
                minTime: minTimeAttr,
                maxTime: maxTimeAttr,
                disable: [
                    function(date) {
                        return !workingDaysList.includes(date.getDay());
                    }
                ],
                locale: currentLang === 'ar' && typeof flatpickr.l10ns.ar !== 'undefined' ? {
                    ...flatpickr.l10ns.ar,
                    firstDayOfWeek: 0
                } : {
                    firstDayOfWeek: 0
                }
            });
        });
});
