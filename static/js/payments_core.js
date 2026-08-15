/**
 * Dental Clinic Management System - Payments Master List Controller
 * AJAX table pagination, live filtering, and table per-page switching.
 */

window.initPaymentsList = function (config) {
    const tableContainer = document.getElementById("payments-table-container");
    const filterForm = document.getElementById("payments-filter-form");

    function loadPaymentsTable(url) {
        if (!tableContainer) return;
        tableContainer.style.opacity = '0.5';

        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Failed to load payments table.");
            }
            return response.text();
        })
        .then(function (html) {
            tableContainer.innerHTML = html;
            tableContainer.style.opacity = '1';
            if (window.initCustomTooltips) {
                window.initCustomTooltips();
            }
            if (window.scrollToTableTop) {
                window.scrollToTableTop(tableContainer);
            }
        })
        .catch(function (error) {
            console.error(error);
            tableContainer.style.opacity = '1';
            window.location.href = url;
        });
    }

    if (filterForm) {
        filterForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const formData = new FormData(filterForm);
            const queryString = new URLSearchParams(formData).toString();
            const url = filterForm.getAttribute("action") + "?" + queryString;
            loadPaymentsTable(url);
        });
    }

    document.addEventListener("click", function (event) {
        const link = event.target.closest(".payments-ajax-link");
        if (!link) return;
        event.preventDefault();
        loadPaymentsTable(link.href);
    });

    window.changeTablePerPage = function (val, module) {
        if (module === 'payments') {
            const input = document.getElementById('payments-per-page-input');
            if (input) input.value = val;
            if (filterForm) {
                const formData = new FormData(filterForm);
                const queryString = new URLSearchParams(formData).toString();
                loadPaymentsTable(filterForm.getAttribute("action") + "?" + queryString);
            }
        }
    };
};
