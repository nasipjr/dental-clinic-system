/**
 * Dental Clinic Management System - Appointments Master List Controller
 * AJAX table pagination, filtering by date/doctor/status, live search, and quick session modal loader.
 */

window.initAppointmentsList = function (config) {
    const isAr = config.isArabic !== undefined ? config.isArabic : (document.documentElement.lang === 'ar' || document.dir === 'rtl');
    const patientsApiUrl = config.patientsApiUrl || '/api/patients/list';
    const mainContainer = document.getElementById("appointments-tab-content-container");

    // ── 1. Load Appointments Table via AJAX ─────────────────────────────────
    function loadAppointmentsTable(url) {
        const tableContainer = document.getElementById("appointments-table-container");
        if (!tableContainer) return;

        tableContainer.style.opacity = '0.5';
        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(function (response) {
            if (!response.ok) throw new Error("Failed to load appointments table.");
            return response.text();
        })
        .then(function (html) {
            tableContainer.innerHTML = html;
            tableContainer.style.opacity = '1';
            if (window.initCustomTooltips) window.initCustomTooltips();
            if (window.scrollToTableTop) window.scrollToTableTop(tableContainer);
        })
        .catch(function (error) {
            console.error(error);
            tableContainer.style.opacity = '1';
            window.location.href = url;
        });
    }

    // ── 2. Load Full Tab Content (Scheduled vs Pending) via AJAX ────────────
    function loadTabContent(url) {
        if (!mainContainer) return;
        mainContainer.style.opacity = '0.5';

        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(function (response) {
            if (!response.ok) throw new Error("Failed to load tab content.");
            return response.text();
        })
        .then(function (html) {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newContent = doc.getElementById('appointments-tab-content-container');
            const newTabs = doc.getElementById('appointmentsTabs');

            if (newContent && mainContainer) {
                mainContainer.innerHTML = newContent.innerHTML;
            }
            if (newTabs) {
                const currentTabs = document.getElementById('appointmentsTabs');
                if (currentTabs) currentTabs.innerHTML = newTabs.innerHTML;
            }
            mainContainer.style.opacity = '1';
            if (window.initCustomTooltips) window.initCustomTooltips();
            history.pushState(null, '', url);
        })
        .catch(function (error) {
            console.error(error);
            if (mainContainer) mainContainer.style.opacity = '1';
            window.location.href = url;
        });
    }

    // ── 3. Global Click Delegation ──────────────────────────────────────────
    document.addEventListener("click", function (event) {
        // Top tabs (Today, Tomorrow, All, Pending)
        const dateBtn = event.target.closest(".appointment-tab-btn");
        if (dateBtn) {
            event.preventDefault();
            document.querySelectorAll(".appointment-tab-btn").forEach(btn => btn.classList.remove("active"));
            document.querySelectorAll(".appointment-tab-card").forEach(card => card.classList.remove("active"));

            dateBtn.classList.add("active");
            const targetCard = dateBtn.querySelector(".appointment-tab-card");
            if (targetCard) targetCard.classList.add("active");

            loadTabContent(dateBtn.href);
            return;
        }

        // Sub tabs under All Appointments (Scheduled, Done, Cancelled, All)
        const subTabBtn = event.target.closest(".sub-tab-item");
        if (subTabBtn) {
            event.preventDefault();
            loadTabContent(subTabBtn.href);
            return;
        }

        // Reset Button
        const resetBtn = event.target.closest("#appointments-reset-btn");
        if (resetBtn) {
            event.preventDefault();
            const filterForm = document.getElementById("appointments-filter-form");
            if (filterForm) {
                const searchInp = filterForm.querySelector('input[name="search"]');
                const statusSel = filterForm.querySelector('select[name="status"]');
                if (searchInp) searchInp.value = '';
                if (statusSel) statusSel.value = '';

                const formData = new FormData(filterForm);
                const queryString = new URLSearchParams(formData).toString();
                const tableUrl = filterForm.getAttribute("action") + "?" + queryString;

                history.pushState(null, '', resetBtn.href);
                loadAppointmentsTable(tableUrl);
            }
            return;
        }

        // AJAX Table Links (sort, pagination)
        const link = event.target.closest(".appointments-ajax-link");
        if (link) {
            event.preventDefault();
            loadAppointmentsTable(link.href);
            return;
        }

        // Doctor Filter Dropdown Option
        const doctorOption = event.target.closest(".doctor-filter-option");
        if (doctorOption) {
            event.preventDefault();
            const doctorId = doctorOption.getAttribute("data-doctor-id");
            const doctorInput = document.getElementById("doctor-filter-input");
            const doctorLabel = document.getElementById("doctor-filter-label");
            const dropdownBtn = document.querySelector("#doctor-filter-dropdown > button");

            if (doctorInput) doctorInput.value = doctorId;

            if (doctorLabel) {
                doctorLabel.textContent = doctorId ? doctorOption.textContent.trim() : (isAr ? 'الطبيب المعالج' : 'Doctor');
            }

            if (dropdownBtn) {
                if (doctorId) {
                    dropdownBtn.classList.remove("btn-outline-secondary");
                    dropdownBtn.classList.add("btn-primary");
                } else {
                    dropdownBtn.classList.remove("btn-primary");
                    dropdownBtn.classList.add("btn-outline-secondary");
                }
            }

            document.querySelectorAll(".doctor-filter-option").forEach(el => el.classList.remove("active", "fw-bold"));
            doctorOption.classList.add("active", "fw-bold");

            const filterForm = document.getElementById("appointments-filter-form");
            if (filterForm) {
                const formData = new FormData(filterForm);
                const queryString = new URLSearchParams(formData).toString();
                const url = filterForm.getAttribute("action") + "?" + queryString;
                loadAppointmentsTable(url);
            }
            return;
        }
    });

    // ── 4. Form Submit & Dynamic Change Handlers ────────────────────────────
    document.addEventListener("submit", function (event) {
        if (event.target && event.target.id === "appointments-filter-form") {
            event.preventDefault();
            const filterForm = event.target;
            const formData = new FormData(filterForm);
            const queryString = new URLSearchParams(formData).toString();
            const url = filterForm.getAttribute("action") + "?" + queryString;
            loadAppointmentsTable(url);
        }
    });

    document.addEventListener("change", function (event) {
        if (event.target && event.target.name === "status" && event.target.closest("#appointments-filter-form")) {
            const filterForm = event.target.closest("#appointments-filter-form");
            const formData = new FormData(filterForm);
            const queryString = new URLSearchParams(formData).toString();
            const url = filterForm.getAttribute("action") + "?" + queryString;
            loadAppointmentsTable(url);
        }
    });

    window.addEventListener("popstate", function () {
        loadAppointmentsTable(window.location.href);
    });

    window.changeTablePerPage = function (val, module) {
        if (module === 'appointments') {
            const input = document.getElementById('appointments-per-page-input');
            if (input) input.value = val;
            const filterForm = document.getElementById('appointments-filter-form');
            if (filterForm) {
                const formData = new FormData(filterForm);
                const queryString = new URLSearchParams(formData).toString();
                loadAppointmentsTable(filterForm.getAttribute("action") + "?" + queryString);
            }
        }
    };

    // ── 5. Quick Session Modal Lazy Patient Loader ──────────────────────────
    const quickModal = document.getElementById("quickSessionModal");
    if (quickModal) {
        quickModal.addEventListener("show.bs.modal", function () {
            const select = document.getElementById("quick-session-patient-select");
            if (!select || select.dataset.loaded) return;
            fetch(patientsApiUrl)
                .then(r => r.json())
                .then(data => {
                    select.innerHTML = `<option value="">${isAr ? '-- اختر المريض --' : '-- Select Patient --'}</option>`;
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
