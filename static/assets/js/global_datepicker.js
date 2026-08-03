(function () {
    function initGlobalDatePickers() {
        if (typeof flatpickr === "undefined") {
            setTimeout(initGlobalDatePickers, 100);
            return;
        }

        const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');

        // Select all date inputs across the app
        const dateInputs = document.querySelectorAll('input[type="date"]');

        dateInputs.forEach(input => {
            if (input.dataset.flatpickrBound) return;
            input.dataset.flatpickrBound = "true";

            // Preserve value & bounds
            const initialVal = input.value;
            let inputMax = input.getAttribute("max");
            let inputMin = input.getAttribute("min");

            // Prior tooth history dates MUST be past/today dates (cannot be future dates!)
            if (input.name === "history_date" || input.id === "edit-history-date") {
                inputMax = "today";
            }

            input.setAttribute("type", "text");
            input.setAttribute("autocomplete", "off");

            const fpConfig = {
                enableTime: false,
                dateFormat: "Y-m-d",
                allowInput: true,
                locale: isAr && typeof flatpickr.l10ns !== "undefined" && typeof flatpickr.l10ns.ar !== "undefined" ? {
                    ...flatpickr.l10ns.ar,
                    firstDayOfWeek: 0
                } : {
                    firstDayOfWeek: 0
                }
            };

            if (inputMax) {
                fpConfig.maxDate = inputMax === "today" ? "today" : inputMax;
            }
            if (inputMin) {
                fpConfig.minDate = inputMin === "today" ? "today" : inputMin;
            }

            const fp = flatpickr(input, fpConfig);
            if (initialVal) {
                fp.setDate(initialVal, false);
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initGlobalDatePickers);
    } else {
        initGlobalDatePickers();
    }

    // Re-initialize when bootstrap modals open
    document.addEventListener("shown.bs.modal", function () {
        initGlobalDatePickers();
    });
})();
