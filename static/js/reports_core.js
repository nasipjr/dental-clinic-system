/**
 * Dental Clinic Management System - Reports & BI Dashboard JavaScript Controller
 * Clean, isolated, modular client-side logic for charts, calendar, and AJAX data tables.
 */

window.initReportsDashboard = function (config) {
    const currencySymbol = config.currencySymbol || 'SP';
    const invoiceUrlTemplate = config.invoiceUrlTemplate || '/invoices/0';
    const paymentUrlTemplate = config.paymentUrlTemplate || '/payments/0';
    const rawSelectedYear = config.selectedYear || 'all';
    const csrfToken = config.csrfToken || '';
    const isArabic = config.isArabic !== undefined ? config.isArabic : (document.documentElement.getAttribute('lang') === 'ar' || document.dir === 'rtl');

    function formatPrice(val) {
        return Math.round(Number(val || 0)).toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    }

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

    // ── 1. Monthly Financials (Bar Chart) ───────────────────────────────────
    const monthlyCanvas = document.getElementById('monthlyFinancialsChart');
    if (monthlyCanvas && typeof Chart !== 'undefined') {
        const monthlyLabels = JSON.parse(monthlyCanvas.getAttribute('data-labels') || '[]');
        const monthlyBilled = JSON.parse(monthlyCanvas.getAttribute('data-billed') || '[]');
        const monthlyPaid = JSON.parse(monthlyCanvas.getAttribute('data-paid') || '[]');

        const monthsAr = {
            "January": "كانون الثاني", "February": "شباط", "March": "آذار",
            "April": "نيسان", "May": "أيار", "June": "حزيران",
            "July": "تموز", "August": "آب", "September": "أيلول",
            "October": "تشرين الأول", "November": "تشرين الثاني", "December": "كانون الأول"
        };
        const monthlyLabelsMapped = monthlyLabels.map(l => {
            const parts = l.split(' ');
            if (parts.length === 2) {
                const monthEng = parts[0];
                const year = parts[1];
                if (monthsAr[monthEng]) {
                    return monthsAr[monthEng] + ' ' + year;
                }
            }
            return l;
        });

        const monthlyCtx = monthlyCanvas.getContext('2d');
        new Chart(monthlyCtx, {
            type: 'bar',
            data: {
                labels: monthlyLabelsMapped,
                datasets: [
                    {
                        label: isArabic ? 'المبلغ المفوتر' : 'Invoiced Amount',
                        data: monthlyBilled,
                        backgroundColor: 'rgba(13, 110, 253, 0.75)',
                        borderColor: 'rgb(13, 110, 253)',
                        borderWidth: 1,
                        borderRadius: 6
                    },
                    {
                        label: isArabic ? 'المدفوعات المستلمة' : 'Payments Received',
                        data: monthlyPaid,
                        backgroundColor: 'rgba(25, 135, 84, 0.75)',
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

    // ── 2. Appointment Status (Doughnut Chart) ──────────────────────────────
    const statusCanvas = document.getElementById('appointmentStatusChart');
    if (statusCanvas && typeof Chart !== 'undefined') {
        const statusLabels = JSON.parse(statusCanvas.getAttribute('data-labels') || '[]');
        const statusValues = JSON.parse(statusCanvas.getAttribute('data-values') || '[]');

        const statusLabelsMapped = statusLabels.map(l => {
            if (l === 'Scheduled') return isArabic ? 'مجدول' : 'Scheduled';
            if (l === 'Done') return isArabic ? 'منجز' : 'Done';
            if (l === 'Cancelled') return isArabic ? 'ملغى' : 'Cancelled';
            return l;
        });

        const statusCtx = statusCanvas.getContext('2d');
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: statusLabelsMapped,
                datasets: [{
                    data: statusValues,
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

    // ── 3. Top Procedures (Horizontal Bar Chart) ────────────────────────────
    const proceduresCanvas = document.getElementById('topProceduresChart');
    if (proceduresCanvas && typeof Chart !== 'undefined') {
        const proceduresLabels = JSON.parse(proceduresCanvas.getAttribute('data-labels') || '[]');
        const proceduresCounts = JSON.parse(proceduresCanvas.getAttribute('data-counts') || '[]');

        const proceduresCtx = proceduresCanvas.getContext('2d');
        new Chart(proceduresCtx, {
            type: 'bar',
            data: {
                labels: proceduresLabels,
                datasets: [{
                    label: isArabic ? 'عدد الإجراءات المعالجة' : 'Procedure Count',
                    data: proceduresCounts,
                    backgroundColor: 'rgba(13, 202, 240, 0.8)',
                    borderColor: 'rgb(13, 202, 240)',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            stepSize: 1
                        }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: textColor }
                    }
                }
            }
        });
    }

    // ── 4. Gender Demographics (Pie Chart) ──────────────────────────────────
    const genderCanvas = document.getElementById('genderDemographicsChart');
    if (genderCanvas && typeof Chart !== 'undefined') {
        const genderLabels = JSON.parse(genderCanvas.getAttribute('data-labels') || '[]');
        const genderValues = JSON.parse(genderCanvas.getAttribute('data-values') || '[]');

        const genderLabelsMapped = genderLabels.map(g => {
            if (g === 'Male') return isArabic ? 'ذكر' : 'Male';
            if (g === 'Female') return isArabic ? 'أنثى' : 'Female';
            if (g === 'Not specified') return isArabic ? 'غير محدد' : 'Not specified';
            return g;
        });

        const genderCtx = genderCanvas.getContext('2d');
        new Chart(genderCtx, {
            type: 'pie',
            data: {
                labels: genderLabelsMapped,
                datasets: [{
                    data: genderValues,
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.75)',  // Male - Blue
                        'rgba(244, 63, 94, 0.75)',   // Female - Pink
                        'rgba(108, 117, 125, 0.75)'  // Not specified
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

    // ── 5. Year Financials Chart (Combo Bar/Line Chart) ─────────────────────
    const yearCanvas = document.getElementById('yearFinancialsChart');
    if (yearCanvas && typeof Chart !== 'undefined') {
        const yearLabels = JSON.parse(yearCanvas.getAttribute('data-labels') || '[]');
        const yearBilled = JSON.parse(yearCanvas.getAttribute('data-billed') || '[]');
        const yearPaid = JSON.parse(yearCanvas.getAttribute('data-paid') || '[]');
        const yearExpenses = JSON.parse(yearCanvas.getAttribute('data-expenses') || '[]');
        const yearNetProfit = JSON.parse(yearCanvas.getAttribute('data-net-profit') || '[]');
        const yearAccrualProfit = JSON.parse(yearCanvas.getAttribute('data-accrual-profit') || '[]');

        const monthsAr = {
            "January": "كانون الثاني", "February": "شباط", "March": "آذار",
            "April": "نيسان", "May": "أيار", "June": "حزيران",
            "July": "تموز", "August": "آب", "September": "أيلول",
            "October": "تشرين الأول", "November": "تشرين الثاني", "December": "كانون الأول"
        };

        const yearLabelsMapped = yearLabels.map(l => {
            const parts = l.split(' ');
            if (parts.length === 2) {
                const monthEng = parts[0];
                const year = parts[1];
                if (monthsAr[monthEng]) {
                    return monthsAr[monthEng] + ' ' + year;
                }
            }
            return l;
        });

        const datasetsConfig = {
            billed: {
                label: isArabic ? 'إجمالي المفوتر (تراكمي)' : 'Total Billed (Accrual)',
                data: yearBilled,
                backgroundColor: 'rgba(13, 110, 253, 0.65)',
                borderColor: 'rgb(13, 110, 253)',
                borderWidth: 1.5,
                borderRadius: 5,
                type: 'bar',
                order: 3
            },
            paid: {
                label: isArabic ? 'إجمالي المقبوضات (نقدي)' : 'Total Paid (Cash)',
                data: yearPaid,
                backgroundColor: 'rgba(25, 135, 84, 0.65)',
                borderColor: 'rgb(25, 135, 84)',
                borderWidth: 1.5,
                borderRadius: 5,
                type: 'bar',
                order: 3
            },
            expenses: {
                label: isArabic ? 'المصاريف' : 'Expenses',
                data: yearExpenses,
                backgroundColor: 'rgba(220, 53, 69, 0.65)',
                borderColor: 'rgb(220, 53, 69)',
                borderWidth: 1.5,
                borderRadius: 5,
                type: 'bar',
                order: 3
            },
            netProfit: {
                label: isArabic ? 'صافي الربح (نقدي)' : 'Net Profit (Cash)',
                data: yearNetProfit,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.35,
                type: 'line',
                pointBackgroundColor: '#10b981',
                pointHoverRadius: 7,
                order: 1
            },
            accrualProfit: {
                label: isArabic ? 'صافي الربح (تراكمي)' : 'Net Profit (Accrual)',
                data: yearAccrualProfit,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.35,
                type: 'line',
                pointBackgroundColor: '#8b5cf6',
                pointHoverRadius: 7,
                order: 2
            }
        };

        const yearCtx = yearCanvas.getContext('2d');
        let currentChartStyle = 'bar';

        function getDatasets(style, view) {
            const list = [];
            if (view === 'all' || view === 'income-expense') {
                const b = { ...datasetsConfig.billed };
                const p = { ...datasetsConfig.paid };
                const e = { ...datasetsConfig.expenses };
                if (style === 'line') {
                    b.type = 'line'; b.fill = false;
                    p.type = 'line'; p.fill = false;
                    e.type = 'line'; e.fill = false;
                } else {
                    b.type = 'bar'; p.type = 'bar'; e.type = 'bar';
                }
                list.push(b, p, e);
            }
            if (view === 'all' || view === 'profits') {
                const np = { ...datasetsConfig.netProfit };
                const ap = { ...datasetsConfig.accrualProfit };
                np.type = 'line';
                ap.type = 'line';
                list.push(np, ap);
            }
            return list;
        }

        let activeView = 'all';
        let yearChart = new Chart(yearCtx, {
            type: 'bar',
            data: {
                labels: yearLabelsMapped,
                datasets: getDatasets(currentChartStyle, activeView)
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
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
                        labels: { color: textColor },
                        position: 'bottom'
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

        // View Filtering Event Listeners
        const viewButtons = document.querySelectorAll('#chart-view-filter button');
        viewButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                viewButtons.forEach(b => {
                    b.classList.remove('btn-primary', 'active');
                    b.classList.add('text-secondary');
                });
                this.classList.add('btn-primary', 'active');
                this.classList.remove('text-secondary');

                activeView = this.getAttribute('data-view');
                yearChart.data.datasets = getDatasets(currentChartStyle, activeView);
                yearChart.update();
            });
        });

        // Style Filtering Event Listeners
        const styleButtons = document.querySelectorAll('#chart-style-filter button');
        styleButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                styleButtons.forEach(b => {
                    b.classList.remove('btn-primary', 'active');
                    b.classList.add('text-secondary');
                });
                this.classList.add('btn-primary', 'active');
                this.classList.remove('text-secondary');

                currentChartStyle = this.getAttribute('data-style');
                yearChart.data.datasets = getDatasets(currentChartStyle, activeView);
                yearChart.update();
            });
        });
    }

    // ── Tab Switching Fix for Canvas Charts & Live Tables ────────────────────
    document.querySelectorAll('button[data-bs-toggle="pill"], button[data-bs-toggle="tab"]').forEach(tabBtn => {
        tabBtn.addEventListener('shown.bs.tab', function () {
            if (typeof Chart !== 'undefined' && Chart.instances) {
                Object.values(Chart.instances).forEach(chart => {
                    chart.resize();
                    chart.update('none');
                });
            }
            if (typeof window.filterAndSortDebtors === 'function') {
                window.filterAndSortDebtors();
            }
            if (typeof window.filterAndSortCredits === 'function') {
                window.filterAndSortCredits();
            }
        });
    });

    // ── Print Mode Theme Adjustments ────────────────────────────────────────
    window.addEventListener('beforeprint', function () {
        if (typeof Chart !== 'undefined' && Chart.instances) {
            Object.values(Chart.instances).forEach(chart => {
                if (chart.options.scales) {
                    if (chart.options.scales.x && chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = '#000000';
                    if (chart.options.scales.y && chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = '#000000';
                }
                if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                    chart.options.plugins.legend.labels.color = '#000000';
                }
                chart.resize();
                chart.update('none');
            });
        }
    });

    window.addEventListener('afterprint', function () {
        if (typeof window.updateAllChartsTheme === 'function') {
            window.updateAllChartsTheme();
        }
    });

    window.updateAllChartsTheme = function () {
        if (typeof Chart === 'undefined' || !Chart.instances) return;
        const colors = getChartColors();
        Object.values(Chart.instances).forEach(chart => {
            if (chart.options.scales) {
                if (chart.options.scales.x) {
                    if (chart.options.scales.x.grid) chart.options.scales.x.grid.color = colors.gridColor;
                    if (chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = colors.textColor;
                }
                if (chart.options.scales.y) {
                    if (chart.options.scales.y.grid) chart.options.scales.y.grid.color = colors.gridColor;
                    if (chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = colors.textColor;
                }
            }
            if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                chart.options.plugins.legend.labels.color = colors.textColor;
            }
            chart.resize();
            chart.update('none');
        });
    };

    const chartThemeObserver = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-bs-theme') {
                window.updateAllChartsTheme();
            }
        });
    });
    chartThemeObserver.observe(document.documentElement, { attributes: true });

    // ── Daily Financial Calendar Logic ─────────────────────────────────────
    let parsedYearNum = parseInt(rawSelectedYear, 10);
    let currentCalYear = (!isNaN(parsedYearNum) && rawSelectedYear !== "all") ? parsedYearNum : new Date().getFullYear();
    let currentCalMonth = (new Date().getFullYear() === currentCalYear || rawSelectedYear === "all") ? (new Date().getMonth() + 1) : 1;

    function openDayDetailsModal(year, month, day, dayInfo) {
        const dateStr = `${day}/${month}/${year}`;
        const modalTitle = document.getElementById("modal-day-title");
        if (modalTitle) modalTitle.innerText = dateStr;

        const summaryBanner = document.getElementById("modal-day-summary-banner");
        if (summaryBanner) {
            const netColorClass = dayInfo.net_profit >= 0 ? "text-success" : "text-danger";
            summaryBanner.innerHTML = `
                <div class="col-6 col-md-3">
                    <div class="p-2 border rounded-3" style="background-color: var(--surface-color);">
                        <small class="text-secondary d-block">${isArabic ? 'إجمالي المفوتر' : 'Total Billed'}</small>
                        <strong class="text-primary">${formatPrice(dayInfo.billed)} ${currencySymbol}</strong>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="p-2 border rounded-3" style="background-color: var(--surface-color);">
                        <small class="text-secondary d-block">${isArabic ? 'إجمالي المقبوض' : 'Total Paid'}</small>
                        <strong class="text-success">+${formatPrice(dayInfo.paid)} ${currencySymbol}</strong>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="p-2 border rounded-3" style="background-color: var(--surface-color);">
                        <small class="text-secondary d-block">${isArabic ? 'المصاريف' : 'Expenses'}</small>
                        <strong class="text-danger">-${formatPrice(dayInfo.expenses)} ${currencySymbol}</strong>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="p-2 border rounded-3" style="background-color: var(--surface-color);">
                        <small class="text-secondary d-block">${isArabic ? 'صافي الربح' : 'Net Profit'}</small>
                        <strong class="${netColorClass}">${formatPrice(dayInfo.net_profit)} ${currencySymbol}</strong>
                    </div>
                </div>
            `;
        }

        const invoicesList = document.getElementById("modal-invoices-list");
        if (invoicesList) {
            invoicesList.innerHTML = "";
            if (dayInfo.invoices && dayInfo.invoices.length > 0) {
                dayInfo.invoices.forEach(inv => {
                    const invoiceUrl = invoiceUrlTemplate.replace('0', inv.id);
                    invoicesList.innerHTML += `
                        <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                            <div>
                                <a href="${invoiceUrl}" class="fw-bold text-primary">${inv.invoice_number}</a><br>
                                <span class="text-secondary small">${inv.patient_name}</span>
                            </div>
                            <span class="fw-bold">${formatPrice(inv.total_amount)} ${currencySymbol}</span>
                        </div>
                    `;
                });
            } else {
                invoicesList.innerHTML = `<div class="text-muted small py-2 text-center">${isArabic ? 'لا توجد فواتير صادرة' : 'No invoices issued.'}</div>`;
            }
        }

        const paymentsList = document.getElementById("modal-payments-list");
        if (paymentsList) {
            paymentsList.innerHTML = "";
            if (dayInfo.payments && dayInfo.payments.length > 0) {
                dayInfo.payments.forEach(pay => {
                    const paymentUrl = paymentUrlTemplate.replace('0', pay.id);
                    paymentsList.innerHTML += `
                        <div class="d-flex justify-content-between align-items-start py-2 border-bottom">
                            <div>
                                <a href="${paymentUrl}" class="fw-bold text-success">PAY-${pay.id.toString().padStart(4, '0')}</a><br>
                                <span class="text-secondary small">${pay.patient_name}</span>
                                ${pay.notes ? `<br><small class="text-muted">${pay.notes}</small>` : ''}
                            </div>
                            <span class="fw-bold text-success">+${formatPrice(pay.amount)} ${currencySymbol}</span>
                        </div>
                    `;
                });
            } else {
                paymentsList.innerHTML = `<div class="text-muted small py-2 text-center">${isArabic ? 'لا توجد مقبوضات مستلمة' : 'No payments received.'}</div>`;
            }
        }

        const expensesList = document.getElementById("modal-expenses-list");
        if (expensesList) {
            expensesList.innerHTML = "";
            if (dayInfo.expenses_list && dayInfo.expenses_list.length > 0) {
                dayInfo.expenses_list.forEach(exp => {
                    expensesList.innerHTML += `
                        <div class="d-flex justify-content-between align-items-start py-2 border-bottom">
                            <div>
                                <span class="fw-bold text-danger">${exp.category}</span>
                                ${exp.notes ? `<br><small class="text-muted">${exp.notes}</small>` : ''}
                            </div>
                            <span class="fw-bold text-danger">-${formatPrice(exp.amount)} ${currencySymbol}</span>
                        </div>
                    `;
                });
            } else {
                expensesList.innerHTML = `<div class="text-muted small py-2 text-center">${isArabic ? 'لا توجد مصاريف مدفوعة' : 'No expenses logged.'}</div>`;
            }
        }

        const modalEl = document.getElementById("dayDetailsModal");
        if (modalEl) {
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        }
    }

    function generateFinancialCalendar(year, month) {
        const container = document.getElementById("calendar-days-container");
        if (!container) return;

        container.innerHTML = `<div class="w-100 text-center py-5" style="grid-column: span 7;"><div class="spinner-border text-primary" role="status"></div></div>`;

        fetch(`/reports/financial-calendar-data?year=${year}&month=${month}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    container.innerHTML = `<div class="alert alert-danger text-center" style="grid-column: span 7;">${data.error}</div>`;
                    return;
                }

                container.innerHTML = "";
                const firstDayIndex = new Date(year, month - 1, 1).getDay();
                const daysInMonth = data.days_in_month;

                for (let i = 0; i < firstDayIndex; i++) {
                    const emptyCell = document.createElement("div");
                    emptyCell.className = "calendar-day-cell empty-cell";
                    container.appendChild(emptyCell);
                }

                for (let day = 1; day <= daysInMonth; day++) {
                    const dayInfo = data.day_data[day];
                    const cell = document.createElement("div");
                    cell.className = "calendar-day-cell card p-2 rounded-3";

                    if (dayInfo.paid > 0 || dayInfo.expenses > 0 || dayInfo.billed > 0) {
                        const netColor = dayInfo.net_profit >= 0 ? "#198754" : "#dc3545";
                        cell.style.borderTop = `3px solid ${netColor}`;
                        cell.onclick = () => openDayDetailsModal(year, month, day, dayInfo);
                    } else {
                        cell.style.cursor = "default";
                        cell.style.pointerEvents = "none";
                    }

                    let statsHtml = "";
                    if (dayInfo.paid > 0 || dayInfo.expenses > 0 || dayInfo.billed > 0) {
                        statsHtml = `
                            <div class="cal-day-stats mt-1 text-start" style="font-size: 0.68rem; line-height: 1.25;">
                                ${dayInfo.billed > 0 ? `<div class="text-secondary d-flex justify-content-between"><span>${isArabic ? 'مفوتر:' : 'Billed:'}</span><strong>${formatPrice(dayInfo.billed)}</strong></div>` : ''}
                                ${dayInfo.paid > 0 ? `<div class="text-success d-flex justify-content-between"><span>${isArabic ? 'مقبوض:' : 'Paid:'}</span><strong>+${formatPrice(dayInfo.paid)}</strong></div>` : ''}
                                ${dayInfo.expenses > 0 ? `<div class="text-danger d-flex justify-content-between"><span>${isArabic ? 'مصروف:' : 'Exp:'}</span><strong>-${formatPrice(dayInfo.expenses)}</strong></div>` : ''}
                                ${(dayInfo.paid > 0 || dayInfo.expenses > 0) ? `
                                    <div class="border-top my-1"></div>
                                    <div class="d-flex justify-content-between font-bold ${dayInfo.net_profit >= 0 ? 'text-success' : 'text-danger'}">
                                        <span>${isArabic ? 'صافي:' : 'Net:'}</span><strong>${formatPrice(dayInfo.net_profit)}</strong>
                                    </div>
                                ` : ''}
                            </div>
                        `;
                    }

                    cell.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="fw-bold cal-day-number">${day}</span>
                            ${(dayInfo.invoices.length > 0 || dayInfo.payments.length > 0 || dayInfo.expenses_list.length > 0) ? `
                                <span class="badge bg-primary bg-opacity-10 text-primary rounded-circle p-1" style="font-size: 0.62rem; min-width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center;">
                                    ${dayInfo.invoices.length + dayInfo.payments.length + dayInfo.expenses_list.length}
                                </span>
                            ` : ''}
                        </div>
                        ${statsHtml}
                    `;
                    container.appendChild(cell);
                }

                // Calculate month-wide totals
                let monthBilled = 0, monthPaid = 0, monthExpenses = 0;
                for (let day = 1; day <= daysInMonth; day++) {
                    const dayInfo = data.day_data[day];
                    monthBilled += dayInfo.billed;
                    monthPaid += dayInfo.paid;
                    monthExpenses += dayInfo.expenses;
                }
                const monthNet = monthPaid - monthExpenses;
                const netColorClass = monthNet >= 0 ? "text-success" : "text-danger";

                const totalsContainer = document.getElementById("calendar-month-totals");
                if (totalsContainer) {
                    totalsContainer.innerHTML = `
                        <div class="small">
                            <span class="text-secondary">${isArabic ? 'مفوتر الشهر:' : 'Month Billed:'}</span> 
                            <strong class="text-primary">${formatPrice(monthBilled)} ${currencySymbol}</strong>
                        </div>
                        <div class="small">
                            <span class="text-secondary">${isArabic ? 'مقبوض الشهر:' : 'Month Paid:'}</span> 
                            <strong class="text-success">+${formatPrice(monthPaid)} ${currencySymbol}</strong>
                        </div>
                        <div class="small">
                            <span class="text-secondary">${isArabic ? 'مصاريف الشهر:' : 'Month Expenses:'}</span> 
                            <strong class="text-danger">-${formatPrice(monthExpenses)} ${currencySymbol}</strong>
                        </div>
                        <div class="small border-start ps-3">
                            <span class="text-secondary font-bold">${isArabic ? 'صافي الشهر:' : 'Month Net:'}</span> 
                            <strong class="font-bold ${netColorClass}">${formatPrice(monthNet)} ${currencySymbol}</strong>
                        </div>
                    `;
                }

                const monthNamesAr = ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"];
                const monthNamesEn = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
                const mNameDisplay = isArabic ? monthNamesAr[month - 1] : monthNamesEn[month - 1];
                const displayEl = document.getElementById("calendar-month-display");
                if (displayEl) displayEl.innerText = mNameDisplay;

                const calYearSelect = document.getElementById("cal-year-select");
                if (calYearSelect) calYearSelect.value = year;
            })
            .catch(err => {
                console.error(err);
                container.innerHTML = `<div class="alert alert-danger text-center" style="grid-column: span 7;">Failed to load calendar data.</div>`;
            });
    }

    const prevBtn = document.getElementById("cal-prev-month-btn");
    const nextBtn = document.getElementById("cal-next-month-btn");
    if (prevBtn && nextBtn) {
        prevBtn.onclick = () => {
            currentCalMonth--;
            if (currentCalMonth <= 0) {
                currentCalMonth = 12;
                currentCalYear--;
            }
            generateFinancialCalendar(currentCalYear, currentCalMonth);
        };
        nextBtn.onclick = () => {
            currentCalMonth++;
            if (currentCalMonth > 12) {
                currentCalMonth = 1;
                currentCalYear++;
            }
            generateFinancialCalendar(currentCalYear, currentCalMonth);
        };
        const yearSelect = document.getElementById("cal-year-select");
        if (yearSelect) {
            yearSelect.onchange = () => {
                currentCalYear = parseInt(yearSelect.value, 10);
                generateFinancialCalendar(currentCalYear, currentCalMonth);
            };
        }
        generateFinancialCalendar(currentCalYear, currentCalMonth);
    }

    // ── 6. Debtors Table Live Filter, Sort & Pagination ─────────────────────
    const debtorsSearch = document.getElementById('debtors-search-input');
    const debtorsPageSizeSelect = document.getElementById('debtors-page-size');
    const debtorsTbody = document.getElementById('debtors-table-body');
    const debtorsCountBadge = document.getElementById('debtors-count-badge');
    const debtorsPaginationInfo = document.getElementById('debtors-pagination-info');
    const debtorsPaginationControls = document.getElementById('debtors-pagination-controls');

    let debtorsSortKey = 'debt';
    let debtorsSortOrder = 'desc';
    window.debtorsCurrentPage = 1;

    window.filterAndSortDebtors = function () {
        if (!debtorsTbody) return;
        const rows = Array.from(debtorsTbody.querySelectorAll('.debtor-row'));
        const query = debtorsSearch ? debtorsSearch.value.trim().toLowerCase() : '';

        let matchingRows = [];
        rows.forEach(row => {
            const name = row.getAttribute('data-name') || '';
            const phone = row.getAttribute('data-phone') || '';
            const matches = name.includes(query) || phone.includes(query);
            if (matches) {
                matchingRows.push(row);
            } else {
                row.style.display = 'none';
            }
        });

        if (debtorsCountBadge) debtorsCountBadge.textContent = matchingRows.length;

        let totalBilled = 0, totalPaid = 0, totalDebt = 0;
        matchingRows.forEach(row => {
            totalBilled += parseFloat(row.getAttribute('data-billed')) || 0;
            totalPaid += parseFloat(row.getAttribute('data-paid')) || 0;
            totalDebt += parseFloat(row.getAttribute('data-debt')) || 0;
        });
        const tbEl = document.getElementById('debtors-total-billed');
        const tpEl = document.getElementById('debtors-total-paid');
        const tdEl = document.getElementById('debtors-total-debt');
        if (tbEl) tbEl.textContent = Number(totalBilled).toLocaleString('de-DE') + ' ' + currencySymbol;
        if (tpEl) tpEl.textContent = Number(totalPaid).toLocaleString('de-DE') + ' ' + currencySymbol;
        if (tdEl) tdEl.textContent = Number(totalDebt).toLocaleString('de-DE') + ' ' + currencySymbol;

        matchingRows.sort((a, b) => {
            let valA, valB;
            if (debtorsSortKey === 'name') {
                valA = a.getAttribute('data-name') || '';
                valB = b.getAttribute('data-name') || '';
                return debtorsSortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
            } else if (debtorsSortKey === 'phone') {
                valA = a.getAttribute('data-phone') || '';
                valB = b.getAttribute('data-phone') || '';
                return debtorsSortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
            } else if (debtorsSortKey === 'paid') {
                valA = parseFloat(a.getAttribute('data-paid')) || 0;
                valB = parseFloat(b.getAttribute('data-paid')) || 0;
            } else if (debtorsSortKey === 'billed') {
                valA = parseFloat(a.getAttribute('data-billed')) || 0;
                valB = parseFloat(b.getAttribute('data-billed')) || 0;
            } else if (debtorsSortKey === 'ratio') {
                valA = parseFloat(a.getAttribute('data-ratio')) || 0;
                valB = parseFloat(b.getAttribute('data-ratio')) || 0;
            } else {
                valA = parseFloat(a.getAttribute('data-debt')) || 0;
                valB = parseFloat(b.getAttribute('data-debt')) || 0;
            }
            return debtorsSortOrder === 'asc' ? valA - valB : valB - valA;
        });

        const pageSizeVal = debtorsPageSizeSelect ? debtorsPageSizeSelect.value : '10';
        const pageSize = pageSizeVal === 'all' ? matchingRows.length : parseInt(pageSizeVal, 10);
        const totalPages = (pageSize > 0 && matchingRows.length > 0) ? Math.ceil(matchingRows.length / pageSize) : 1;

        if (window.debtorsCurrentPage > totalPages) window.debtorsCurrentPage = totalPages || 1;
        if (window.debtorsCurrentPage < 1) window.debtorsCurrentPage = 1;

        const startIndex = matchingRows.length > 0 ? (window.debtorsCurrentPage - 1) * pageSize : 0;
        const endIndex = pageSizeVal === 'all' ? matchingRows.length : Math.min(startIndex + pageSize, matchingRows.length);

        matchingRows.forEach((row, idx) => {
            if (pageSizeVal === 'all' || (idx >= startIndex && idx < endIndex)) {
                row.style.display = '';
                const firstTd = row.querySelector('td');
                if (firstTd) firstTd.textContent = idx + 1;
            } else {
                row.style.display = 'none';
            }
            debtorsTbody.appendChild(row);
        });

        if (debtorsPaginationInfo) {
            if (matchingRows.length === 0) {
                debtorsPaginationInfo.textContent = isArabic ? "لا توجد نتائج مطابقة" : "No matching results";
            } else {
                debtorsPaginationInfo.textContent = isArabic
                    ? `عرض ${startIndex + 1} إلى ${endIndex} من أصل ${matchingRows.length} مدين`
                    : `Showing ${startIndex + 1} to ${endIndex} of ${matchingRows.length} debtors`;
            }
        }

        if (debtorsPaginationControls) {
            debtorsPaginationControls.innerHTML = '';
            if (totalPages <= 1 || pageSizeVal === 'all') return;

            const prevLi = document.createElement('li');
            prevLi.className = `page-item ${window.debtorsCurrentPage === 1 ? 'disabled' : ''}`;
            prevLi.innerHTML = `<a class="page-link" href="#"><i class="bi bi-chevron-right"></i></a>`;
            prevLi.addEventListener('click', (e) => {
                e.preventDefault();
                if (window.debtorsCurrentPage > 1) {
                    window.debtorsCurrentPage--;
                    window.filterAndSortDebtors();
                }
            });
            debtorsPaginationControls.appendChild(prevLi);

            for (let p = 1; p <= totalPages; p++) {
                if (totalPages > 7 && Math.abs(p - window.debtorsCurrentPage) > 2 && p !== 1 && p !== totalPages) {
                    if (p === 2 || p === totalPages - 1) {
                        const ellipsisLi = document.createElement('li');
                        ellipsisLi.className = 'page-item disabled';
                        ellipsisLi.innerHTML = `<span class="page-link">...</span>`;
                        debtorsPaginationControls.appendChild(ellipsisLi);
                    }
                    continue;
                }

                const pageLi = document.createElement('li');
                pageLi.className = `page-item ${p === window.debtorsCurrentPage ? 'active' : ''}`;
                pageLi.innerHTML = `<a class="page-link" href="#">${p}</a>`;
                pageLi.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.debtorsCurrentPage = p;
                    window.filterAndSortDebtors();
                });
                debtorsPaginationControls.appendChild(pageLi);
            }

            const nextLi = document.createElement('li');
            nextLi.className = `page-item ${window.debtorsCurrentPage === totalPages ? 'disabled' : ''}`;
            nextLi.innerHTML = `<a class="page-link" href="#"><i class="bi bi-chevron-left"></i></a>`;
            nextLi.addEventListener('click', (e) => {
                e.preventDefault();
                if (window.debtorsCurrentPage < totalPages) {
                    window.debtorsCurrentPage++;
                    window.filterAndSortDebtors();
                }
            });
            debtorsPaginationControls.appendChild(nextLi);
        }
    };

    if (debtorsSearch) {
        debtorsSearch.addEventListener('input', () => {
            window.debtorsCurrentPage = 1;
            window.filterAndSortDebtors();
        });
    }
    if (debtorsPageSizeSelect) {
        debtorsPageSizeSelect.addEventListener('change', () => {
            window.debtorsCurrentPage = 1;
            window.filterAndSortDebtors();
        });
    }

    // Quick Settle Debt Handler
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.quick-settle-debt-btn');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const pId = btn.dataset.patientId;
        const pName = btn.dataset.patientName;
        const pDebt = parseFloat(btn.dataset.debt) || 0;
        const debtFmt = Number(pDebt).toLocaleString('de-DE') + ' ' + currencySymbol;

        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: isArabic ? `تسديد سريع للدين (${pName})` : `Quick Debt Settlement (${pName})`,
                text: isArabic ? `هل تريد تسديد كامل الدين المتبقي وقدره (${debtFmt}) للمريض تلقائياً وتوثيقه بسجل المدفوعات؟` : `Instantly settle full debt of (${debtFmt}) for this patient?`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#10b981',
                cancelButtonColor: '#6c757d',
                confirmButtonText: isArabic ? 'نعم، تسديد كامل الدين الآن' : 'Yes, settle debt now',
                cancelButtonText: isArabic ? 'إلغاء' : 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: isArabic ? 'جاري تسجيل الدفعة وتسديد الدين...' : 'Processing Payment...',
                        allowOutsideClick: false,
                        didOpen: () => { Swal.showLoading(); }
                    });
                    const currentCsrf = document.querySelector('input[name="csrf_token"]')?.value || csrfToken;
                    const fd = new FormData();
                    fd.append('amount', pDebt);
                    fd.append('csrf_token', currentCsrf);

                    fetch(`/payments/quick-settle/${pId}`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': currentCsrf
                        },
                        body: fd
                    })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                Swal.fire({
                                    title: isArabic ? 'تم التسديد بنجاح' : 'Debt Settled',
                                    text: res.message,
                                    icon: 'success',
                                    confirmButtonText: isArabic ? 'حسناً' : 'OK'
                                });
                                const row = btn.closest('.debtor-row');
                                if (row) row.remove();
                                if (typeof window.filterAndSortDebtors === 'function') window.filterAndSortDebtors();
                                if (typeof window.loadExpenses === 'function') window.loadExpenses();
                            } else {
                                Swal.fire({
                                    title: isArabic ? 'تنبيه' : 'Notice',
                                    text: res.message || (isArabic ? 'فشل تسديد الدين' : 'Failed to settle debt'),
                                    icon: 'warning',
                                    confirmButtonText: isArabic ? 'حسناً' : 'OK'
                                });
                            }
                        })
                        .catch(() => {
                            Swal.fire({
                                title: isArabic ? 'خطأ' : 'Error',
                                text: isArabic ? 'حدث خطأ غير متوقع أثناء تسديد الدين' : 'Unexpected error',
                                icon: 'error',
                                confirmButtonText: isArabic ? 'حسناً' : 'OK'
                            });
                        });
                }
            });
        }
    });

    window.filterAndSortDebtors();

    // ── 7. Credits Table Live Filter, Sort & Pagination ─────────────────────
    const creditsSearch = document.getElementById('credits-search-input');
    const creditsPageSizeSelect = document.getElementById('credits-page-size');
    const creditsTbody = document.getElementById('credits-table-body');
    const creditsCountBadge = document.getElementById('credits-count-badge');
    const creditsPaginationInfo = document.getElementById('credits-pagination-info');
    const creditsPaginationControls = document.getElementById('credits-pagination-controls');

    let creditsSortKey = 'credit';
    let creditsSortOrder = 'desc';
    window.creditsCurrentPage = 1;

    window.filterAndSortCredits = function () {
        if (!creditsTbody) return;
        const rows = Array.from(creditsTbody.querySelectorAll('.credit-row'));
        const query = creditsSearch ? creditsSearch.value.trim().toLowerCase() : '';

        let matchingRows = [];
        rows.forEach(row => {
            const name = row.getAttribute('data-name') || '';
            const phone = row.getAttribute('data-phone') || '';
            const matches = name.includes(query) || phone.includes(query);
            if (matches) {
                matchingRows.push(row);
            } else {
                row.style.display = 'none';
            }
        });

        if (creditsCountBadge) creditsCountBadge.textContent = matchingRows.length;

        matchingRows.sort((a, b) => {
            let valA, valB;
            if (creditsSortKey === 'name') {
                valA = a.getAttribute('data-name') || '';
                valB = b.getAttribute('data-name') || '';
                return creditsSortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
            } else if (creditsSortKey === 'phone') {
                valA = a.getAttribute('data-phone') || '';
                valB = b.getAttribute('data-phone') || '';
                return creditsSortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
            } else if (creditsSortKey === 'paid') {
                valA = parseFloat(a.getAttribute('data-paid')) || 0;
                valB = parseFloat(b.getAttribute('data-paid')) || 0;
            } else if (creditsSortKey === 'billed') {
                valA = parseFloat(a.getAttribute('data-billed')) || 0;
                valB = parseFloat(b.getAttribute('data-billed')) || 0;
            } else {
                valA = parseFloat(a.getAttribute('data-credit')) || 0;
                valB = parseFloat(b.getAttribute('data-credit')) || 0;
            }
            return creditsSortOrder === 'asc' ? valA - valB : valB - valA;
        });

        const pageSizeVal = creditsPageSizeSelect ? creditsPageSizeSelect.value : '10';
        const pageSize = pageSizeVal === 'all' ? matchingRows.length : parseInt(pageSizeVal, 10);
        const totalPages = (pageSize > 0 && matchingRows.length > 0) ? Math.ceil(matchingRows.length / pageSize) : 1;

        if (window.creditsCurrentPage > totalPages) window.creditsCurrentPage = totalPages || 1;
        if (window.creditsCurrentPage < 1) window.creditsCurrentPage = 1;

        const startIndex = matchingRows.length > 0 ? (window.creditsCurrentPage - 1) * pageSize : 0;
        const endIndex = pageSizeVal === 'all' ? matchingRows.length : Math.min(startIndex + pageSize, matchingRows.length);

        matchingRows.forEach((row, idx) => {
            if (pageSizeVal === 'all' || (idx >= startIndex && idx < endIndex)) {
                row.style.display = '';
                const firstTd = row.querySelector('td');
                if (firstTd) firstTd.textContent = idx + 1;
            } else {
                row.style.display = 'none';
            }
            creditsTbody.appendChild(row);
        });

        if (creditsPaginationInfo) {
            if (matchingRows.length === 0) {
                creditsPaginationInfo.textContent = isArabic ? "لا توجد نتائج مطابقة" : "No matching results";
            } else {
                creditsPaginationInfo.textContent = isArabic
                    ? `عرض ${startIndex + 1} إلى ${endIndex} من أصل ${matchingRows.length} مريض دائن`
                    : `Showing ${startIndex + 1} to ${endIndex} of ${matchingRows.length} credited patients`;
            }
        }

        if (creditsPaginationControls) {
            creditsPaginationControls.innerHTML = '';
            if (totalPages <= 1 || pageSizeVal === 'all') return;

            const prevLi = document.createElement('li');
            prevLi.className = `page-item ${window.creditsCurrentPage === 1 ? 'disabled' : ''}`;
            prevLi.innerHTML = `<a class="page-link" href="#"><i class="bi bi-chevron-right"></i></a>`;
            prevLi.addEventListener('click', (e) => {
                e.preventDefault();
                if (window.creditsCurrentPage > 1) {
                    window.creditsCurrentPage--;
                    window.filterAndSortCredits();
                }
            });
            creditsPaginationControls.appendChild(prevLi);

            for (let p = 1; p <= totalPages; p++) {
                if (totalPages > 7 && Math.abs(p - window.creditsCurrentPage) > 2 && p !== 1 && p !== totalPages) {
                    if (p === 2 || p === totalPages - 1) {
                        const ellipsisLi = document.createElement('li');
                        ellipsisLi.className = 'page-item disabled';
                        ellipsisLi.innerHTML = `<span class="page-link">...</span>`;
                        creditsPaginationControls.appendChild(ellipsisLi);
                    }
                    continue;
                }

                const pageLi = document.createElement('li');
                pageLi.className = `page-item ${p === window.creditsCurrentPage ? 'active' : ''}`;
                pageLi.innerHTML = `<a class="page-link" href="#">${p}</a>`;
                pageLi.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.creditsCurrentPage = p;
                    window.filterAndSortCredits();
                });
                creditsPaginationControls.appendChild(pageLi);
            }

            const nextLi = document.createElement('li');
            nextLi.className = `page-item ${window.creditsCurrentPage === totalPages ? 'disabled' : ''}`;
            nextLi.innerHTML = `<a class="page-link" href="#"><i class="bi bi-chevron-left"></i></a>`;
            nextLi.addEventListener('click', (e) => {
                e.preventDefault();
                if (window.creditsCurrentPage < totalPages) {
                    window.creditsCurrentPage++;
                    window.filterAndSortCredits();
                }
            });
            creditsPaginationControls.appendChild(nextLi);
        }
    };

    if (creditsSearch) {
        creditsSearch.addEventListener('input', () => {
            window.creditsCurrentPage = 1;
            window.filterAndSortCredits();
        });
    }
    if (creditsPageSizeSelect) {
        creditsPageSizeSelect.addEventListener('change', () => {
            window.creditsCurrentPage = 1;
            window.filterAndSortCredits();
        });
    }

    window.filterAndSortCredits();

    // Sorting column header click listener
    document.querySelectorAll('.reports-sort-link').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const tableType = this.getAttribute('data-table');
            const sortKey = this.getAttribute('data-sort');
            let currentOrder = this.getAttribute('data-order') || 'none';
            let newOrder = (currentOrder === 'desc') ? 'asc' : 'desc';

            const parentTable = this.closest('table');
            parentTable.querySelectorAll('.reports-sort-link').forEach(l => {
                l.setAttribute('data-order', 'none');
                const holder = l.querySelector('.sort-icon');
                if (holder) holder.innerHTML = '';
            });

            this.setAttribute('data-order', newOrder);
            const activeHolder = this.querySelector('.sort-icon');
            if (activeHolder) {
                const arrowClass = (newOrder === 'asc') ? 'bi-arrow-up' : 'bi-arrow-down';
                activeHolder.innerHTML = `<i class="bi ${arrowClass} ms-1"></i>`;
            }

            if (tableType === 'debtors') {
                debtorsSortKey = sortKey;
                debtorsSortOrder = newOrder;
                window.filterAndSortDebtors();
            } else if (tableType === 'credits') {
                creditsSortKey = sortKey;
                creditsSortOrder = newOrder;
                window.filterAndSortCredits();
            }
        });
    });

    // ── 8. Expenses AJAX Table ──────────────────────────────────────────────
    let expPage = 1, expSort = 'date', expOrder = 'desc';
    const CAT_BADGES = {
        'Materials': `<span class="badge bg-info bg-opacity-10 text-info px-3 py-1 rounded-pill fw-semibold">${isArabic ? 'مواد طبية' : 'Materials'}</span>`,
        'Rent': `<span class="badge bg-warning bg-opacity-10 text-warning px-3 py-1 rounded-pill fw-semibold">${isArabic ? 'إيجار' : 'Rent'}</span>`,
        'Salaries': `<span class="badge bg-primary bg-opacity-10 text-primary px-3 py-1 rounded-pill fw-semibold">${isArabic ? 'رواتب' : 'Salaries'}</span>`,
        'Other': `<span class="badge bg-secondary bg-opacity-10 text-secondary px-3 py-1 rounded-pill fw-semibold">${isArabic ? 'أخرى' : 'Other'}</span>`,
    };

    window.confirmDeleteExpense = function (form, e) {
        if (e) e.preventDefault();
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: isArabic ? 'حذف المصروف' : 'Delete Expense',
                text: isArabic ? 'هل أنت متأكد من رغبتك في حذف هذا المصروف نهائياً؟' : 'Are you sure you want to delete this expense?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: isArabic ? 'نعم، حذف' : 'Yes, delete',
                cancelButtonText: isArabic ? 'إلغاء' : 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    HTMLFormElement.prototype.submit.call(form);
                }
            });
        } else {
            if (confirm(isArabic ? 'هل تريد حذف هذا المصروف؟' : 'Delete this expense?')) {
                HTMLFormElement.prototype.submit.call(form);
            }
        }
        return false;
    };

    function loadExpenses() {
        const cat = document.getElementById('exp-filter-category')?.value || '';
        const yr = document.getElementById('exp-filter-year')?.value || '';
        const mon = document.getElementById('exp-filter-month')?.value || '';
        const search = document.getElementById('exp-filter-search')?.value || '';
        const perPage = document.getElementById('exp-per-page')?.value || 10;
        const tbody = document.getElementById('expenses-table-body');
        if (!tbody) return;

        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted"><div class="spinner-border spinner-border-sm"></div></td></tr>';

        const params = new URLSearchParams({ page: expPage, per_page: perPage, sort: expSort, order: expOrder });
        if (cat) params.set('category', cat);
        if (yr) params.set('year', yr);
        if (mon && mon !== 'all') params.set('month', mon);
        if (search) params.set('search', search);

        fetch('/reports/expenses/list?' + params)
            .then(r => r.json())
            .then(data => {
                if (data.error) { tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">${data.error}</td></tr>`; return; }

                const totalAmtEl = document.getElementById('exp-total-amount');
                if (totalAmtEl) totalAmtEl.textContent = formatPrice(data.total_filtered_amount || 0);

                if (!data.rows || data.rows.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="5" class="text-center py-5 text-muted"><i class="bi bi-journal-x fs-1 opacity-50 d-block mb-2"></i>${isArabic ? 'لا توجد مصاريف' : 'No expenses found'}</td></tr>`;
                } else {
                    const currentCsrf = document.querySelector('input[name="csrf_token"]')?.value || csrfToken;
                    tbody.innerHTML = data.rows.map(e => `
                        <tr>
                            <td>${CAT_BADGES[e.category] || CAT_BADGES['Other']}</td>
                            <td class="text-end fw-bold text-danger">${formatPrice(e.amount)}</td>
                            <td class="text-center text-secondary small">${e.date}</td>
                            <td class="text-secondary small">${e.notes || '—'}</td>
                            <td class="text-center">
                                <div class="d-flex gap-2 justify-content-center align-items-center">
                                    <button type="button" class="btn btn-sm btn-link text-primary p-0 edit-expense-btn"
                                            data-id="${e.id}" data-category="${e.category}" data-amount="${e.amount}"
                                            data-date="${e.date}" data-notes="${e.notes || ''}"
                                            title="${isArabic ? 'تعديل' : 'Edit'}">
                                        <i class="bi bi-pencil-square fs-5"></i>
                                    </button>
                                    <form method="POST" action="/reports/expenses/${e.id}/delete"
                                          onsubmit="return window.confirmDeleteExpense(this, event);"
                                          style="display:inline;">
                                        <input type="hidden" name="csrf_token" value="${currentCsrf}">
                                        <button type="submit" class="btn btn-sm btn-link text-danger p-0" title="${isArabic ? 'حذف' : 'Delete'}">
                                            <i class="bi bi-trash fs-5"></i>
                                        </button>
                                    </form>
                                </div>
                            </td>
                        </tr>`).join('');
                    attachEditExpenseListeners();
                }

                renderExpPagination(data.current_page, data.pages, data.total);
            })
            .catch(() => { tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">${isArabic ? 'خطأ في التحميل' : 'Load error'}</td></tr>`; });
    }

    function attachEditExpenseListeners() {
        document.querySelectorAll('.edit-expense-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const expId = this.dataset.id;
                const category = this.dataset.category;
                const amount = this.dataset.amount;
                const date = this.dataset.date;
                const notes = this.dataset.notes;

                const form = document.getElementById('edit-expense-form');
                if (form) form.action = `/reports/expenses/${expId}/edit`;

                const catEl = document.getElementById('edit-expense-category');
                if (catEl) catEl.value = category;

                const amtEl = document.getElementById('edit-expense-amount');
                if (amtEl) amtEl.value = amount;

                const dateEl = document.getElementById('edit-expense-date');
                if (dateEl) dateEl.value = date;

                const notesEl = document.getElementById('edit-expense-notes');
                if (notesEl) notesEl.value = notes;

                const modalEl = document.getElementById('editExpenseModal');
                if (modalEl) {
                    const modal = new bootstrap.Modal(modalEl);
                    modal.show();
                }
            });
        });
    }

    function renderExpPagination(current, pages, total) {
        const info = document.getElementById('exp-pagination-info');
        const links = document.getElementById('exp-pagination-links');
        if (info) info.textContent = isArabic ? `الصفحة ${current} من ${pages} (${total} سجل)` : `Page ${current} of ${pages} (${total} records)`;
        if (!links) return;
        let html = '';
        const prevIcon = isArabic ? 'bi-chevron-right' : 'bi-chevron-left';
        const nextIcon = isArabic ? 'bi-chevron-left' : 'bi-chevron-right';
        if (current > 1) html += `<li class="page-item"><button type="button" class="page-link rounded-3" data-exp-page="${current - 1}"><i class="bi ${prevIcon}"></i></button></li>`;
        for (let p = Math.max(1, current - 2); p <= Math.min(pages, current + 2); p++) {
            html += `<li class="page-item ${p === current ? 'active' : ''}"><button type="button" class="page-link rounded-3" data-exp-page="${p}">${p}</button></li>`;
        }
        if (current < pages) html += `<li class="page-item"><button type="button" class="page-link rounded-3" data-exp-page="${current + 1}"><i class="bi ${nextIcon}"></i></button></li>`;
        links.innerHTML = html;
        links.querySelectorAll('[data-exp-page]').forEach(btn => btn.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();
            expPage = +btn.dataset.expPage;
            loadExpenses();
        }));
    }

    window.loadExpenses = loadExpenses;
    loadExpenses();

    ['exp-filter-category', 'exp-filter-year', 'exp-filter-month', 'exp-per-page'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', () => { expPage = 1; loadExpenses(); });
    });
    const search = document.getElementById('exp-filter-search');
    let searchTimer;
    if (search) search.addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(() => { expPage = 1; loadExpenses(); }, 400); });

    document.getElementById('exp-reset-btn')?.addEventListener('click', () => {
        const catEl = document.getElementById('exp-filter-category');
        const yrEl = document.getElementById('exp-filter-year');
        const moEl = document.getElementById('exp-filter-month');
        const sEl = document.getElementById('exp-filter-search');
        if (catEl) catEl.value = '';
        if (yrEl) yrEl.value = 'all';
        if (moEl) moEl.value = 'all';
        if (sEl) sEl.value = '';
        expPage = 1; loadExpenses();
    });

    document.querySelectorAll('.exp-sort-th').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.dataset.col;
            if (expSort === col) expOrder = expOrder === 'asc' ? 'desc' : 'asc';
            else { expSort = col; expOrder = 'desc'; }
            expPage = 1; loadExpenses();
        });
    });

    const addForm = document.getElementById('add-expense-form');
    if (addForm) {
        addForm.addEventListener('submit', function () {
            setTimeout(() => { expPage = 1; loadExpenses(); }, 600);
        });
    }

    // ── 9. Doctors Revenue Share AJAX Table ─────────────────────────────────
    let sharePage = 1, shareSort = 'revenue', shareOrder = 'desc', shareDoctorId = '';

    function loadDoctorRevenueShare() {
        const monthVal = document.getElementById('doc-share-filter-month')?.value || '';
        const tbody = document.getElementById('doc-share-table-body');
        if (!tbody) return;

        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted"><div class="spinner-border spinner-border-sm"></div></td></tr>';

        const params = new URLSearchParams({ page: sharePage, per_page: 10, sort: shareSort, order: shareOrder });
        if (shareDoctorId) params.set('doctor_id', shareDoctorId);
        if (monthVal) params.set('month', monthVal);
        else if (rawSelectedYear && rawSelectedYear !== 'all') params.set('year', rawSelectedYear);

        fetch('/reports/doctor-revenue-share?' + params)
            .then(r => r.json())
            .then(data => {
                if (data.error) { tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">${data.error}</td></tr>`; return; }

                if (data.active_month && (rawSelectedYear === 'all' || !rawSelectedYear)) {
                    const mEl = document.getElementById('doc-share-filter-month');
                    if (mEl && !mEl.value) {
                        mEl.value = data.active_month;
                        updateMonthPickerBtnText(data.active_month);
                    }
                } else if (monthVal) {
                    updateMonthPickerBtnText(monthVal);
                }

                const revEl = document.getElementById('doc-share-total-revenue');
                const earnEl = document.getElementById('doc-share-total-earned');
                const netEl = document.getElementById('doc-share-total-net');
                const revLbl = document.getElementById('doc-share-revenue-label');
                const earnLbl = document.getElementById('doc-share-earned-label');
                const netLbl = document.getElementById('doc-share-net-label');

                if (revEl) revEl.textContent = formatPrice(data.total_revenue_sum || 0);
                if (earnEl) earnEl.textContent = formatPrice(data.total_earned_sum || 0);
                if (netEl) netEl.textContent = formatPrice(data.total_net_sum || 0);

                let selectedDocName = '';
                if (shareDoctorId) {
                    const activeItem = document.querySelector(`.doc-share-filter-item[data-doc-id="${shareDoctorId}"]`);
                    if (activeItem) selectedDocName = activeItem.textContent.trim();
                }

                if (shareDoctorId && selectedDocName) {
                    if (revLbl) revLbl.textContent = isArabic ? `دخل الطبيب (${selectedDocName}):` : `Doctor Revenue (${selectedDocName}):`;
                    if (earnLbl) earnLbl.textContent = isArabic ? `مستحقات الربح (${selectedDocName}):` : `Doctor Share (${selectedDocName}):`;
                    if (netLbl) netLbl.textContent = isArabic ? `صافي العيادة من (${selectedDocName}):` : `Clinic Net (${selectedDocName}):`;
                } else {
                    if (revLbl) revLbl.textContent = isArabic ? 'إجمالي دخل العيادة:' : 'Total Revenue:';
                    if (earnLbl) earnLbl.textContent = isArabic ? 'أرباح الأطباء:' : 'Doctors Earned:';
                    if (netLbl) netLbl.textContent = isArabic ? 'صافي العيادة:' : 'Clinic Net:';
                }

                const menu = document.getElementById('doc-share-filter-menu');
                if (menu && data.doctors && menu.children.length <= 2) {
                    data.doctors.forEach(d => {
                        const li = document.createElement('li');
                        li.innerHTML = `<a class="dropdown-item rounded-3 d-flex align-items-center gap-2 py-2 px-3 doc-share-filter-item" href="#" data-doc-id="${d.id}"><i class="bi bi-person text-primary"></i>${d.name}</a>`;
                        menu.appendChild(li);
                    });
                    attachDocShareDropdownListeners();
                }

                if (!data.rows || data.rows.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-5 text-muted"><i class="bi bi-person-x fs-1 opacity-50 d-block mb-2"></i>${isArabic ? 'لا يوجد أطباء مساعدين مطابقين للشهر المحدد' : 'No matching assistant doctors found for this month'}</td></tr>`;
                } else {
                    tbody.innerHTML = data.rows.map(d => {
                        const schemeBadge = d.salary_type === 'percentage'
                            ? `<span class="badge rounded-pill bg-success bg-opacity-10 text-success border border-success border-opacity-25 px-3 py-1"><i class="bi bi-percent me-1"></i>${isArabic ? 'نسبة ' + d.salary_amount + '%' : d.salary_amount + '% Percentage'}</span>`
                            : `<span class="badge rounded-pill bg-info bg-opacity-10 text-info border border-info border-opacity-25 px-3 py-1"><i class="bi bi-cash me-1"></i>${isArabic ? 'راتب ثابت: ' + Number(d.salary_amount).toLocaleString() + ' ' + currencySymbol : 'Fixed: ' + d.salary_amount}</span>`;

                        const pendingDropdown = (d.pending_months && d.pending_months.length > 0) ? `
                            <div class="dropdown d-inline-block position-relative">
                                <span class="text-warning fw-bold cursor-pointer dropdown-toggle text-decoration-none"
                                      data-bs-toggle="dropdown" data-bs-display="static" aria-expanded="false"
                                      style="font-size:0.75rem;">
                                    <i class="bi bi-hourglass-split me-1"></i>${d.pending_count} ${isArabic ? 'معلقة' : 'pending'}
                                </span>
                                <ul class="dropdown-menu shadow-lg border rounded-3 p-2 text-start" style="font-size:0.82rem; min-width:180px; z-index: 1050;">
                                    <li class="dropdown-header small text-muted px-2 py-1 border-bottom mb-1 fw-bold">
                                        <i class="bi bi-calendar-range me-1 text-warning"></i>${isArabic ? 'الأشهر المعلقة:' : 'Pending Months:'}
                                    </li>
                                    ${d.pending_months.map(m => `
                                        <li>
                                            <a class="dropdown-item rounded-2 py-1.5 px-2 d-flex justify-content-between align-items-center doc-filter-pending-month-btn"
                                               href="#" data-ym="${m.ym}">
                                                <span><i class="bi bi-calendar3 me-1.5 text-warning"></i>${isArabic ? m.label_ar : m.label_en}</span>
                                                <span class="badge bg-warning bg-opacity-20 text-warning rounded-pill ms-2">${m.count}</span>
                                            </a>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : `
                            <span class="text-warning fw-bold" style="font-size:0.75rem;">
                                <i class="bi bi-hourglass-split me-1"></i>${d.pending_count} ${isArabic ? 'معلقة' : 'pending'}
                            </span>
                        `;

                        return `
                        <tr style="font-size: 0.88rem;">
                            <td style="padding: 10px 8px;">
                                <div class="d-flex align-items-center gap-2">
                                    <div class="rounded-circle bg-primary bg-opacity-10 text-primary d-flex align-items-center justify-content-center fw-bold" style="width:34px; height:34px; font-size:.9rem;">
                                        ${d.first_name ? d.first_name[0] : 'D'}
                                    </div>
                                    <div>
                                        <div class="fw-bold text-main">${d.first_name} ${d.last_name}</div>
                                        <small class="text-muted" style="font-size:0.75rem;">@${d.username}</small>
                                    </div>
                                </div>
                            </td>
                            <td class="text-center" style="padding: 10px 8px;">${schemeBadge}</td>
                            <td class="text-center" style="padding: 10px 8px;">
                                <span class="badge bg-secondary bg-opacity-10 text-secondary px-2.5 py-1 rounded-pill mb-1 fw-bold">
                                    ${d.appointment_count} ${isArabic ? 'موعد' : 'appts'}
                                </span>
                                <div class="small" style="font-size:0.75rem;">
                                    <span class="text-success fw-bold" data-tooltip="${isArabic ? 'معالجات مخصومة' : 'Deducted treatments'}">
                                        <i class="bi bi-check-circle-fill me-1"></i>${d.deducted_count} ${isArabic ? 'مخصومة' : 'deducted'}
                                    </span>
                                    ${d.pending_count > 0 ? `
                                        <span class="text-secondary mx-1">|</span>
                                        ${pendingDropdown}
                                    ` : ''}
                                </div>
                            </td>
                            <td class="text-end fw-bold text-primary" style="padding: 10px 8px;">${formatPrice(d.total_revenue)} ${currencySymbol}</td>
                            <td class="text-end fw-bold text-success" style="padding: 10px 8px;">${formatPrice(d.doctor_earned)} ${currencySymbol}</td>
                            <td class="text-end fw-bold text-info" style="padding: 10px 8px;">${formatPrice(d.clinic_net)} ${currencySymbol}</td>
                            <td class="text-center" style="padding: 10px 8px;">
                                ${(d.is_deducted || d.deducted_this_month)
                                ? `<button type="button" class="btn btn-sm btn-link text-danger p-0 doc-undo-btn"
                                            data-tooltip="${isArabic ? 'تراجع عن الخصم لهذا الشهر' : 'Undo Deduction for this Month'}"
                                            data-doc-id="${d.id}" data-doc-name="${d.first_name} ${d.last_name}">
                                        <i class="bi bi-arrow-counterclockwise fs-5"></i>
                                     </button>`
                                : `<button type="button" class="btn btn-sm btn-link text-warning p-0 doc-deduct-btn"
                                            data-tooltip="${isArabic ? 'خصم الراتب الآن' : 'Deduct Salary Now'}"
                                            data-doc-id="${d.id}" data-doc-name="${d.first_name} ${d.last_name}">
                                        <i class="bi bi-arrow-down-circle fs-5"></i>
                                     </button>`}
                            </td>
                        </tr>`;
                    }).join('');

                    attachDeductBtnListeners();
                    attachUndoBtnListeners();
                    attachPendingMonthBtnListeners();
                }

                renderSharePagination(data.current_page, data.pages, data.total);
            })
            .catch(() => { tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">${isArabic ? 'خطأ في التحميل' : 'Load error'}</td></tr>`; });
    }

    function attachPendingMonthBtnListeners() {
        document.querySelectorAll('.doc-filter-pending-month-btn').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const ym = this.dataset.ym;
                const monthInput = document.getElementById('doc-share-filter-month');
                if (monthInput && ym) {
                    monthInput.value = ym;
                    updateMonthPickerBtnText(ym);
                    sharePage = 1;
                    loadDoctorRevenueShare();
                }
            });
        });
    }

    function attachDeductBtnListeners() {
        document.querySelectorAll('.doc-deduct-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const docId = this.dataset.docId;
                const docName = this.dataset.docName;
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        title: isArabic ? `خصم راتب/مستحقات (${docName})` : `Deduct Salary (${docName})`,
                        text: isArabic ? 'هل تريد خصم الراتب الآن وتسجيله كمصروف في سجل المصاريف؟' : 'Deduct salary now and log it as an expense?',
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#ffc107',
                        cancelButtonColor: '#6c757d',
                        confirmButtonText: isArabic ? 'نعم، الخصم الآن' : 'Yes, deduct now',
                        cancelButtonText: isArabic ? 'إلغاء' : 'Cancel'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            Swal.fire({
                                title: isArabic ? 'جاري خصم وتسجيل الراتب...' : 'Processing Deduction...',
                                text: isArabic ? 'يرجى الانتظار لحين تحويل المبلغ لسجل المصاريف' : 'Please wait while recording salary expense...',
                                allowOutsideClick: false,
                                didOpen: () => { Swal.showLoading(); }
                            });
                            const fd = new FormData();
                            const currentCsrf = document.querySelector('input[name="csrf_token"]')?.value || csrfToken;
                            if (currentCsrf) fd.append('csrf_token', currentCsrf);
                            const monthVal = document.getElementById('doc-share-filter-month')?.value || '';
                            if (monthVal) fd.append('month', monthVal);
                            fetch(`/settings/salary/deduct/${docId}`, {
                                method: 'POST',
                                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                                body: fd
                            })
                                .then(r => r.json())
                                .then(res => {
                                    if (res.success) {
                                        Swal.fire({
                                            title: isArabic ? 'تم الخصم بنجاح' : 'Deducted Successfully',
                                            text: res.message,
                                            icon: 'success',
                                            confirmButtonText: isArabic ? 'حسناً' : 'OK'
                                        });
                                        const mInput = document.getElementById('doc-share-filter-month');
                                        if (mInput) mInput.value = '';
                                        updateMonthPickerBtnText('');
                                        loadDoctorRevenueShare();
                                        if (typeof window.loadExpenses === 'function') window.loadExpenses();
                                    } else {
                                        Swal.fire({
                                            title: isArabic ? 'تنبيه' : 'Warning',
                                            text: res.message || (isArabic ? 'فشل خصم الراتب' : 'Failed to deduct salary'),
                                            icon: 'warning',
                                            confirmButtonText: isArabic ? 'حسناً' : 'OK'
                                        });
                                    }
                                })
                                .catch(() => {
                                    Swal.fire({
                                        title: isArabic ? 'خطأ' : 'Error',
                                        text: isArabic ? 'حدث خطأ غير متوقع أثناء خصم الراتب' : 'Unexpected error during deduction',
                                        icon: 'error',
                                        confirmButtonText: isArabic ? 'حسناً' : 'OK'
                                    });
                                });
                        }
                    });
                }
            });
        });
    }

    function attachUndoBtnListeners() {
        document.querySelectorAll('.doc-undo-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const docId = this.dataset.docId;
                const docName = this.dataset.docName;
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        title: isArabic ? `تراجع عن الخصم (${docName})` : `Undo Deduction (${docName})`,
                        text: isArabic ? 'هل تريد التراجع عن خصم راتب هذا الشهر وإلغاء المصروف المسجل؟' : 'Undo this month salary deduction and remove the logged expense?',
                        icon: 'question',
                        showCancelButton: true,
                        confirmButtonColor: '#ef4444',
                        cancelButtonColor: '#6c757d',
                        confirmButtonText: isArabic ? 'نعم، تراجع عن الخصم' : 'Yes, undo deduction',
                        cancelButtonText: isArabic ? 'إلغاء' : 'Cancel'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            Swal.fire({
                                title: isArabic ? 'جاري التراجع...' : 'Undoing Deduction...',
                                allowOutsideClick: false,
                                didOpen: () => { Swal.showLoading(); }
                            });
                            const fd = new FormData();
                            const currentCsrf = document.querySelector('input[name="csrf_token"]')?.value || csrfToken;
                            if (currentCsrf) fd.append('csrf_token', currentCsrf);
                            const mVal = document.getElementById('doc-share-filter-month')?.value || '';
                            if (mVal) fd.append('month', mVal);
                            fetch(`/settings/salary/undo/${docId}`, {
                                method: 'POST',
                                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                                body: fd
                            })
                                .then(r => r.json())
                                .then(res => {
                                    if (res.success) {
                                        Swal.fire({
                                            title: isArabic ? 'تم التراجع بنجاح' : 'Deduction Reversed',
                                            text: res.message,
                                            icon: 'success',
                                            confirmButtonText: isArabic ? 'حسناً' : 'OK'
                                        });
                                        loadDoctorRevenueShare();
                                        if (typeof window.loadExpenses === 'function') window.loadExpenses();
                                    } else {
                                        Swal.fire({
                                            title: isArabic ? 'تنبيه' : 'Notice',
                                            text: res.message || (isArabic ? 'فشل التراجع عن الخصم' : 'Failed to undo deduction'),
                                            icon: 'warning',
                                            confirmButtonText: isArabic ? 'حسناً' : 'OK'
                                        });
                                    }
                                })
                                .catch(() => {
                                    Swal.fire({
                                        title: isArabic ? 'خطأ' : 'Error',
                                        text: isArabic ? 'حدث خطأ غير متوقع' : 'Unexpected error',
                                        icon: 'error',
                                        confirmButtonText: isArabic ? 'حسناً' : 'OK'
                                    });
                                });
                        }
                    });
                }
            });
        });
    }

    function renderSharePagination(current, pages, total) {
        const info = document.getElementById('doc-share-pagination-info');
        const links = document.getElementById('doc-share-pagination-links');
        if (info) info.textContent = isArabic ? `الصفحة ${current} من ${pages} (${total} أطباء)` : `Page ${current} of ${pages} (${total} doctors)`;
        if (!links) return;
        let html = '';
        const prevIcon = isArabic ? 'bi-chevron-right' : 'bi-chevron-left';
        const nextIcon = isArabic ? 'bi-chevron-left' : 'bi-chevron-right';
        if (current > 1) html += `<li class="page-item"><button type="button" class="page-link rounded-3" data-share-page="${current - 1}"><i class="bi ${prevIcon}"></i></button></li>`;
        for (let p = Math.max(1, current - 2); p <= Math.min(pages, current + 2); p++) {
            html += `<li class="page-item ${p === current ? 'active' : ''}"><button type="button" class="page-link rounded-3" data-share-page="${p}">${p}</button></li>`;
        }
        if (current < pages) html += `<li class="page-item"><button type="button" class="page-link rounded-3" data-share-page="${current + 1}"><i class="bi ${nextIcon}"></i></button></li>`;
        links.innerHTML = html;
        links.querySelectorAll('[data-share-page]').forEach(btn => btn.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();
            sharePage = +btn.dataset.sharePage;
            loadDoctorRevenueShare();
        }));
    }

    function attachDocShareDropdownListeners() {
        document.querySelectorAll('.doc-share-filter-item').forEach(item => {
            item.addEventListener('click', e => {
                e.preventDefault();
                document.querySelectorAll('.doc-share-filter-item').forEach(i => i.classList.remove('active', 'fw-bold'));
                item.classList.add('active', 'fw-bold');
                shareDoctorId = item.getAttribute('data-doc-id') || '';
                const label = document.getElementById('doc-share-filter-label');
                if (label) label.textContent = item.textContent.trim();
                sharePage = 1;
                loadDoctorRevenueShare();
            });
        });
    }

    function updateMonthPickerBtnText(val) {
        const textEl = document.getElementById('doc-share-month-picker-text');
        if (!textEl) return;
        if (!val || val === 'all') {
            textEl.textContent = isArabic ? 'كافة الأشهر / كافة السنين' : 'All Months / All Years';
            return;
        }
        if (val.length === 4 && !isNaN(val)) {
            textEl.textContent = isArabic ? `سنة ${val} كاملة` : `Full Year ${val}`;
            return;
        }
        const parts = val.split('-');
        if (parts.length === 2) {
            const yr = parts[0];
            const mInt = parseInt(parts[1], 10);
            const monthsAr = ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"];
            const monthsEn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const mName = isArabic ? monthsAr[mInt - 1] : monthsEn[mInt - 1];
            textEl.textContent = `${mName} (${parts[1]}) ${yr}`;
        }
    }

    function initCustomMonthPicker() {
        const monthsAr = ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"];
        const monthsEn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        let currentYearSelected = '2026';

        function renderMonthGrid() {
            const grid = document.getElementById('month-picker-grid');
            if (!grid) return;
            grid.innerHTML = '';
            const hiddenVal = document.getElementById('doc-share-filter-month')?.value || '';

            for (let m = 1; m <= 12; m++) {
                const mStr = String(m).padStart(2, '0');
                const mName = isArabic ? monthsAr[m - 1] : monthsEn[m - 1];
                const val = `${currentYearSelected}-${mStr}`;
                const isActive = hiddenVal === val;

                const col = document.createElement('div');
                col.className = 'col-3';
                col.innerHTML = `
                    <button type="button" class="btn btn-sm w-100 rounded-3 py-1 px-1 fw-semibold transition-all month-card-btn ${isActive ? 'btn-primary text-white shadow-xs' : 'btn-outline-secondary border-0 text-body opacity-85'}"
                            data-val="${val}" data-month="${mStr}" data-mname="${mName}" style="font-size:0.72rem;">
                        <div style="font-size:0.72rem; line-height: 1.1;">${mName}</div>
                        <small class="${isActive ? 'text-white-50' : 'text-muted'}" style="font-size:0.62rem;">${mStr}</small>
                    </button>
                `;
                grid.appendChild(col);
            }

            grid.querySelectorAll('.month-card-btn').forEach(btn => {
                btn.addEventListener('click', function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const val = this.dataset.val;
                    const hiddenInput = document.getElementById('doc-share-filter-month');
                    if (hiddenInput) hiddenInput.value = val;

                    updateMonthPickerBtnText(val);
                    renderMonthGrid();

                    sharePage = 1;
                    loadDoctorRevenueShare();
                });
            });
        }

        document.querySelectorAll('#month-picker-year-pills .year-pill-btn').forEach(pill => {
            pill.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                document.querySelectorAll('#month-picker-year-pills .year-pill-btn').forEach(b => {
                    b.classList.remove('active', 'btn-primary', 'text-white');
                    b.classList.add('btn-outline-secondary', 'border-0', 'text-body');
                });
                this.classList.add('active', 'btn-primary', 'text-white');
                this.classList.remove('btn-outline-secondary', 'border-0', 'text-body');
                currentYearSelected = this.dataset.year;

                const hiddenInput = document.getElementById('doc-share-filter-month');
                if (hiddenInput) hiddenInput.value = currentYearSelected;

                updateMonthPickerBtnText(currentYearSelected);
                renderMonthGrid();

                sharePage = 1;
                loadDoctorRevenueShare();
            });
        });

        document.getElementById('month-picker-clear-btn')?.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            const hiddenInput = document.getElementById('doc-share-filter-month');
            if (hiddenInput) hiddenInput.value = 'all';
            updateMonthPickerBtnText('all');
            renderMonthGrid();
            sharePage = 1;
            loadDoctorRevenueShare();
        });

        document.getElementById('month-picker-apply-btn')?.addEventListener('click', function (e) {
            e.preventDefault();
            const dropdownEl = document.getElementById('doc-share-month-picker-btn');
            if (dropdownEl) {
                const bsDropdown = bootstrap.Dropdown.getInstance(dropdownEl);
                if (bsDropdown) bsDropdown.hide();
            }
        });

        renderMonthGrid();
    }

    document.getElementById('doc-share-reset-btn')?.addEventListener('click', () => {
        const mInput = document.getElementById('doc-share-filter-month');
        if (mInput) mInput.value = '';
        shareDoctorId = '';
        const label = document.getElementById('doc-share-filter-label');
        if (label) label.textContent = isArabic ? 'كل الأطباء المساعدين' : 'All Doctors';
        document.querySelectorAll('.doc-share-filter-item').forEach(i => i.classList.remove('active', 'fw-bold'));
        const allItem = document.querySelector('.doc-share-filter-item[data-doc-id=""]');
        if (allItem) allItem.classList.add('active', 'fw-bold');

        updateMonthPickerBtnText('');
        sharePage = 1;
        loadDoctorRevenueShare();
    });

    document.querySelectorAll('.doc-share-sort-th').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.dataset.col;
            if (shareSort === col) shareOrder = shareOrder === 'asc' ? 'desc' : 'asc';
            else { shareSort = col; shareOrder = 'desc'; }
            sharePage = 1;
            loadDoctorRevenueShare();
        });
    });

    initCustomMonthPicker();
    loadDoctorRevenueShare();

    // ── Hash navigation support ─────────────────────────────────────────────
    const hash = window.location.hash;
    if (hash) {
        const triggerEl = document.querySelector(`button[data-bs-target="${hash}"]`);
        if (triggerEl) {
            const tab = new bootstrap.Tab(triggerEl);
            tab.show();
        }
    }
};
