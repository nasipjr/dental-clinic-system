(function () {
    function setupCustomYearSelect(instance, isDob) {
        if (!instance || !instance.calendarContainer) return;
        const calendarContainer = instance.calendarContainer;
        const monthContainers = calendarContainer.querySelectorAll(".flatpickr-current-month");

        monthContainers.forEach(container => {
            let yearSelect = container.querySelector(".flatpickr-year-dropdown");
            const numWrapper = container.querySelector(".numInputWrapper");
            const curYearInput = container.querySelector(".cur-year");

            const currentYear = new Date().getFullYear();
            const minYear = isDob ? 1920 : 1940;
            const maxYear = isDob ? currentYear : currentYear + 10;

            if (!yearSelect) {
                yearSelect = document.createElement("select");
                yearSelect.className = "flatpickr-monthDropdown-months flatpickr-year-dropdown";
                yearSelect.setAttribute("aria-label", "Year");

                for (let y = maxYear; y >= minYear; y--) {
                    const opt = document.createElement("option");
                    opt.value = y;
                    opt.textContent = y;
                    yearSelect.appendChild(opt);
                }

                yearSelect.addEventListener("change", function (e) {
                    e.stopPropagation();
                    const chosenYear = parseInt(e.target.value, 10);
                    instance.changeYear(chosenYear);
                });

                if (numWrapper) {
                    numWrapper.style.setProperty("display", "none", "important");
                }
                if (curYearInput) {
                    curYearInput.style.setProperty("display", "none", "important");
                }

                container.appendChild(yearSelect);
            }

            if (yearSelect) {
                if (numWrapper) numWrapper.style.setProperty("display", "none", "important");
                if (curYearInput) curYearInput.style.setProperty("display", "none", "important");
                yearSelect.value = instance.currentYear;
            }
        });
    }

    function initGlobalDatePickers() {
        if (typeof flatpickr === "undefined") {
            setTimeout(initGlobalDatePickers, 100);
            return;
        }

        const isAr = document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en');

        // Select all date inputs across the app
        const dateInputs = document.querySelectorAll(
            'input[type="date"], input[name="date_of_birth"], input#date_of_birth, input.dob-picker, input[name="history_date"], input#edit-history-date'
        );

        dateInputs.forEach(input => {
            if (input.dataset.flatpickrBound) return;
            input.dataset.flatpickrBound = "true";

            // Preserve value & bounds
            const initialVal = input.value;
            let inputMax = input.getAttribute("max");
            let inputMin = input.getAttribute("min");

            const isDob = (input.name === "date_of_birth" || input.id === "date_of_birth" || input.classList.contains("dob-picker"));

            // Birth dates & prior tooth history dates MUST be past/today dates (cannot be future dates!)
            if (isDob || input.name === "history_date" || input.id === "edit-history-date") {
                inputMax = "today";
            }

            input.setAttribute("type", "text");
            input.setAttribute("autocomplete", "off");

            const levantineMonths = ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"];

            const fpConfig = {
                enableTime: false,
                dateFormat: "Y-m-d",
                allowInput: true,
                locale: isAr && typeof flatpickr.l10ns !== "undefined" && typeof flatpickr.l10ns.ar !== "undefined" ? {
                    ...flatpickr.l10ns.ar,
                    months: {
                        shorthand: levantineMonths,
                        longhand: levantineMonths
                    },
                    firstDayOfWeek: 0
                } : {
                    firstDayOfWeek: 0
                },
                onReady: function (selectedDates, dateStr, instance) {
                    setupCustomYearSelect(instance, isDob);
                },
                onMonthChange: function (selectedDates, dateStr, instance) {
                    setupCustomYearSelect(instance, isDob);
                },
                onYearChange: function (selectedDates, dateStr, instance) {
                    setupCustomYearSelect(instance, isDob);
                },
                onOpen: function (selectedDates, dateStr, instance) {
                    setupCustomYearSelect(instance, isDob);
                },
                onValueUpdate: function (selectedDates, dateStr, instance) {
                    setupCustomYearSelect(instance, isDob);
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
