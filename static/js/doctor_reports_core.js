/**
 * Dental Clinic Management System - Doctor Reports JavaScript Controller
 * Client-side logic for Doctor KPI Charts, dynamic Dark/Light theme updating, and live sort/filter/pagination of treatments.
 */

window.initDoctorReports = function (config) {
    const isAr = config.isArabic !== undefined ? config.isArabic : (document.documentElement.getAttribute('lang') === 'ar' || document.dir === 'rtl');
    const currencySymbol = config.currencySymbol || 'SP';
    const monthNames = config.monthNames || [];
    const monthlyRevenueData = config.monthlyRevenueData || [];
    const monthlyEarnedData = config.monthlyEarnedData || [];
    const statusCounts = config.statusCounts || {};
    const totalRevenueLabel = config.totalRevenueLabel || (isAr ? 'إجمالي تكلفة العلاج' : 'Total Billed Revenue');
    const doctorEarningsLabel = config.doctorEarningsLabel || (isAr ? 'مستحق/أرباح الطبيب' : 'Doctor Earnings');

    function getChartColors() {
        const attr = document.documentElement.getAttribute('data-bs-theme');
        const local = localStorage.getItem('theme');
        const isDark = attr === 'dark' || (!attr && local === 'dark');
        return {
            textColor: isDark ? '#f1f5f9' : '#1e293b',
            gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)'
        };
    }

    let initialColors = getChartColors();
    const textColor = initialColors.textColor;
    const gridColor = initialColors.gridColor;

    // ── 1. Doctor Monthly Bar Chart ─────────────────────────────────────────
    const monthlyCanvas = document.getElementById('doctorMonthlyChart');
    if (monthlyCanvas && typeof Chart !== 'undefined') {
        new Chart(monthlyCanvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: monthNames,
                datasets: [
                    {
                        label: totalRevenueLabel,
                        data: monthlyRevenueData,
                        backgroundColor: 'rgba(13, 110, 253, 0.75)',
                        borderColor: 'rgb(13, 110, 253)',
                        borderWidth: 1,
                        borderRadius: 6
                    },
                    {
                        label: doctorEarningsLabel,
                        data: monthlyEarnedData,
                        backgroundColor: 'rgba(25, 135, 84, 0.85)',
                        borderColor: 'rgb(25, 135, 84)',
                        borderWidth: 1,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            callback: function (value) { return value.toLocaleString('de-DE') + ' ' + currencySymbol; }
                        }
                    },
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: textColor }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.dataset.label + ': ' + context.raw.toLocaleString('de-DE') + ' ' + currencySymbol;
                            }
                        }
                    }
                }
            }
        });
    }

    // ── 2. Doctor Status Doughnut Chart ─────────────────────────────────────
    const statusCanvas = document.getElementById('doctorStatusChart');
    if (statusCanvas && typeof Chart !== 'undefined') {
        new Chart(statusCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusCounts),
                datasets: [{
                    data: Object.values(statusCounts),
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.8)',   // Scheduled - Blue
                        'rgba(25, 135, 84, 0.8)',    // Done - Green
                        'rgba(220, 53, 69, 0.8)'     // Cancelled - Red
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor }
                    }
                }
            }
        });
    }

    // ── 3. AJAX Table Sorting & Pagination Engine ───────────────────────────
    let currentPage = 1;
    let currentSortCol = 'date';
    let currentSortOrder = 'desc';

    const tbody = document.getElementById('doctor-treatments-tbody');
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('.treatment-row'));

    function updateDoctorTable() {
        const searchTerm = (document.getElementById('doctor-treatments-search')?.value || '').toLowerCase().trim();
        const pageSizeVal = document.getElementById('doctor-page-size')?.value || '10';

        // Filter
        let filtered = rows.filter(row => {
            if (!searchTerm) return true;
            const patient = row.getAttribute('data-patient') || '';
            const procedure = row.getAttribute('data-procedure') || '';
            return patient.includes(searchTerm) || procedure.includes(searchTerm);
        });

        // Sort
        filtered.sort((a, b) => {
            let valA = a.getAttribute(`data-${currentSortCol}`) || '';
            let valB = b.getAttribute(`data-${currentSortCol}`) || '';

            if (currentSortCol === 'cost' || currentSortCol === 'share') {
                valA = parseFloat(valA) || 0;
                valB = parseFloat(valB) || 0;
            }

            if (valA < valB) return currentSortOrder === 'asc' ? -1 : 1;
            if (valA > valB) return currentSortOrder === 'asc' ? 1 : -1;
            return 0;
        });

        // Paginate
        const totalItems = filtered.length;
        let pageSize = pageSizeVal === 'all' ? totalItems : parseInt(pageSizeVal, 10);
        if (isNaN(pageSize) || pageSize < 1) pageSize = 10;

        const totalPages = Math.ceil(totalItems / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;

        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = startIndex + pageSize;

        rows.forEach(r => r.style.display = 'none');
        const pageRows = filtered.slice(startIndex, endIndex);

        pageRows.forEach((row, idx) => {
            row.style.display = '';
            const indexTd = row.querySelector('.row-index');
            if (indexTd) indexTd.textContent = startIndex + idx + 1;
            tbody.appendChild(row);
        });

        // Recalculate Footer Sums for Filtered Data
        let sumRevenue = 0;
        let sumEarned = 0;
        filtered.forEach(r => {
            sumRevenue += parseFloat(r.getAttribute('data-cost')) || 0;
            sumEarned += parseFloat(r.getAttribute('data-share')) || 0;
        });

        const footRev = document.getElementById('foot-total-revenue');
        const footEarned = document.getElementById('foot-total-earned');
        if (footRev) footRev.textContent = sumRevenue.toLocaleString('de-DE') + ' ' + currencySymbol;
        if (footEarned) footEarned.textContent = sumEarned.toLocaleString('de-DE') + ' ' + currencySymbol;

        // Render Pagination Controls & Info
        const infoSpan = document.getElementById('doctor-pagination-info');
        if (infoSpan) {
            if (totalItems === 0) {
                infoSpan.textContent = isAr ? 'لا توجد نتائج لعرضها' : 'No results to display';
            } else {
                const fromNum = startIndex + 1;
                const toNum = Math.min(endIndex, totalItems);
                infoSpan.textContent = isAr
                    ? `عرض ${fromNum} إلى ${toNum} من أصل ${totalItems} إجراء`
                    : `Showing ${fromNum} to ${toNum} of ${totalItems} items`;
            }
        }

        renderPaginationControls(totalPages);
    }

    function renderPaginationControls(totalPages) {
        const controlsUl = document.getElementById('doctor-pagination-controls');
        if (!controlsUl) return;
        controlsUl.innerHTML = '';

        if (totalPages <= 1) return;

        // Previous Button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link shadow-xs rounded-2 px-2.5 py-1" href="#" aria-label="Previous">${isAr ? 'السابق' : 'Prev'}</a>`;
        prevLi.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage > 1) { currentPage--; updateDoctorTable(); }
        });
        controlsUl.appendChild(prevLi);

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (totalPages > 7 && Math.abs(i - currentPage) > 2 && i !== 1 && i !== totalPages) {
                if (i === 2 || i === totalPages - 1) {
                    const dots = document.createElement('li');
                    dots.className = 'page-item disabled';
                    dots.innerHTML = '<span class="page-link border-0 px-2">...</span>';
                    controlsUl.appendChild(dots);
                }
                continue;
            }
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link shadow-xs rounded-2 px-3 py-1" href="#">${i}</a>`;
            li.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = i;
                updateDoctorTable();
            });
            controlsUl.appendChild(li);
        }

        // Next Button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link shadow-xs rounded-2 px-2.5 py-1" href="#" aria-label="Next">${isAr ? 'التالي' : 'Next'}</a>`;
        nextLi.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage < totalPages) { currentPage++; updateDoctorTable(); }
        });
        controlsUl.appendChild(nextLi);
    }

    // Event Listeners
    document.getElementById('doctor-treatments-search')?.addEventListener('input', () => {
        currentPage = 1;
        updateDoctorTable();
    });

    document.getElementById('doctor-page-size')?.addEventListener('change', () => {
        currentPage = 1;
        updateDoctorTable();
    });

    document.querySelectorAll('.sortable-col').forEach(th => {
        th.addEventListener('click', function () {
            const col = this.getAttribute('data-sort');
            if (currentSortCol === col) {
                currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortCol = col;
                currentSortOrder = 'asc';
            }

            document.querySelectorAll('.sortable-col .sort-icon').forEach(icon => {
                icon.className = 'bi bi-arrow-down-up ms-1 text-muted opacity-50 sort-icon';
            });
            const activeIcon = this.querySelector('.sort-icon');
            if (activeIcon) {
                activeIcon.className = currentSortOrder === 'asc'
                    ? 'bi bi-sort-down-alt ms-1 text-primary sort-icon'
                    : 'bi bi-sort-up ms-1 text-primary sort-icon';
            }

            updateDoctorTable();
        });
    });

    updateDoctorTable();

    // ── 4. Theme Switch Observer ────────────────────────────────────────────
    window.updateAllDoctorChartsTheme = function () {
        if (typeof Chart === 'undefined' || !Chart.instances) return;
        const colors = getChartColors();
        Object.values(Chart.instances).forEach(chart => {
            if (chart.options.scales) {
                if (chart.options.scales.x && chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = colors.textColor;
                if (chart.options.scales.y && chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = colors.textColor;
            }
            if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                chart.options.plugins.legend.labels.color = colors.textColor;
            }
            chart.update('none');
        });
    };

    const docThemeObserver = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-bs-theme') {
                window.updateAllDoctorChartsTheme();
            }
        });
    });
    docThemeObserver.observe(document.documentElement, { attributes: true });
};
