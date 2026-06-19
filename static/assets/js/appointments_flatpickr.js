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
    const workingDaysList = workingDaysAttr.split(",").map(d => parseInt(d.trim(), 10));

    // Fetch booked slots
    const currentAppointmentId = typeof appointmentIdForEdit !== 'undefined' ? appointmentIdForEdit : "";
    const url = "/appointments/booked-slots" + (currentAppointmentId ? "?exclude_id=" + currentAppointmentId : "");

    fetch(url)
        .then(res => res.json())
        .then(bookedSlots => {
            // Flatpickr expects bookedSlots to be parsed as Date objects
            const disabledDates = bookedSlots.map(slotStr => {
                // Parse 'YYYY-MM-DD HH:MM' into date
                const parts = slotStr.split(' ');
                const dateParts = parts[0].split('-');
                const timeParts = parts[1].split(':');
                return new Date(
                    parseInt(dateParts[0]),
                    parseInt(dateParts[1]) - 1,
                    parseInt(dateParts[2]),
                    parseInt(timeParts[0]),
                    parseInt(timeParts[1])
                );
            });
            
            // Add closed days disable function
            disabledDates.push(function(date) {
                return !workingDaysList.includes(date.getDay());
            });

            flatpickr(appointmentInput, {
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                minDate: "today",
                maxDate: new Date().fp_incr(30),
                minuteIncrement: 30,
                minTime: minTimeAttr,
                maxTime: maxTimeAttr,
                disable: disabledDates,
                locale: {
                    firstDayOfWeek: 0 // Sunday
                }
            });
        })
        .catch(err => {
            console.error("Failed to load booked slots", err);
            // Initialize flatpickr anyway without booked slots if API fails
            flatpickr(appointmentInput, {
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                minDate: "today",
                maxDate: new Date().fp_incr(30),
                minuteIncrement: 30,
                minTime: minTimeAttr,
                maxTime: maxTimeAttr,
                disable: [
                    function(date) {
                        return !workingDaysList.includes(date.getDay());
                    }
                ],
                locale: {
                    firstDayOfWeek: 0
                }
            });
        });
});
