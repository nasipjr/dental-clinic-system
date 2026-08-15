/**
 * Dental Clinic Management System - Invoices Master List Controller
 * AJAX table pagination, status filtering, live search, and sorting.
 */

window.initInvoicesList = function (config) {
    const tableContainer = document.getElementById("invoices-table-container");
    const filterForm = document.getElementById("invoices-filter-form");

    function loadInvoicesTable(url) {
        // Rewrite the URL path from '/invoices' to '/invoices/table' to fetch only the partial HTML table
        const fetchUrl = url.replace("/invoices", "/invoices/table");

        if (tableContainer) tableContainer.style.opacity = '0.5';

        fetch(fetchUrl, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("Failed to load invoices table.");
            }
            return response.text();
        })
        .then(function (html) {
            if (tableContainer) {
                tableContainer.innerHTML = html;
                tableContainer.style.opacity = '1';
            }
            window.history.pushState(null, "", url);
            if (window.initCustomTooltips) {
                window.initCustomTooltips();
            }
            if (window.scrollToTableTop && tableContainer) {
                window.scrollToTableTop(tableContainer);
            }
        })
        .catch(function (error) {
            console.error(error);
            if (tableContainer) tableContainer.style.opacity = '1';
            window.location.href = url;
        });
    }

    if (filterForm) {
        filterForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const formData = new FormData(filterForm);
            const queryString = new URLSearchParams(formData).toString();
            const url = filterForm.getAttribute("action") + "?" + queryString;
            loadInvoicesTable(url);
        });

        filterForm.addEventListener("change", function (event) {
            if (event.target && event.target.name === "status") {
                filterForm.requestSubmit();
            }
        });
    }

    document.addEventListener("click", function (event) {
        const link = event.target.closest(".invoices-ajax-link");
        if (!link) return;
        event.preventDefault();
        loadInvoicesTable(link.href);
    });

    window.changeTablePerPage = function (val, module) {
        if (module === 'invoices') {
            const input = document.getElementById('invoices-per-page-input');
            if (input) input.value = val;
            if (filterForm) {
                const formData = new FormData(filterForm);
                const queryString = new URLSearchParams(formData).toString();
                loadInvoicesTable(filterForm.getAttribute("action") + "?" + queryString);
            }
        }
    };
};
