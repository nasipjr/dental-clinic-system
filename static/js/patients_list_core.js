/**
 * Dental Clinic Management System - Patients List Core Controller
 * Handles asynchronous table pagination, live search filters, and items-per-page updates.
 */

window.initPatientsList = function () {
    const tableContainer = document.getElementById("patients-table-container");
    const filterForm = document.getElementById("patients-filter-form");

    function loadPatientsTable(url) {
        if (!tableContainer) return;
        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Failed to load patients table.");
            }
            return response.text();
        })
        .then(function (html) {
            tableContainer.innerHTML = html;
            if (window.initCustomTooltips) {
                window.initCustomTooltips();
            }
            if (window.scrollToTableTop) {
                window.scrollToTableTop(tableContainer);
            }
        })
        .catch(function (error) {
            console.error(error);
            window.location.href = url;
        });
    }

    if (filterForm) {
        filterForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const formData = new FormData(filterForm);
            const queryString = new URLSearchParams(formData).toString();
            const url = filterForm.getAttribute("action") + "?" + queryString;

            loadPatientsTable(url);
        });
    }

    document.addEventListener("click", function (event) {
        const link = event.target.closest(".patients-ajax-link");

        if (!link) {
            return;
        }

        event.preventDefault();
        loadPatientsTable(link.href);
    });

    window.changeTablePerPage = function (val, module) {
        if (module === 'patients') {
            const input = document.getElementById('patient-per-page-input');
            if (input) input.value = val;
            if (filterForm) {
                const formData = new FormData(filterForm);
                const queryString = new URLSearchParams(formData).toString();
                loadPatientsTable(filterForm.getAttribute("action") + "?" + queryString);
            }
        }
    };
};
