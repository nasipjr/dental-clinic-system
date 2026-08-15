/**
 * Dental Clinic Management System - Dashboard JavaScript Controller
 * Isolated client-side logic for charts, clinic open/close status, quick cancellation, and auto-refresh polling.
 */

window.initDashboard = function (config) {
    const currencySymbol = config.currencySymbol || 'SP';
    const isArabic = config.isArabic !== undefined ? config.isArabic : (document.documentElement.getAttribute('lang') === 'ar' || document.dir === 'rtl');
    const csrfToken = config.csrfToken || '';

    const scheduled = parseInt(config.scheduled, 10) || 0;
    const completed = parseInt(config.completed, 10) || 0;
    const cancelled = parseInt(config.cancelled, 10) || 0;
    const paid = parseFloat(config.paid) || 0;
    const debt = parseFloat(config.debt) || 0;

    const workingDaysStr = config.workingDays || '0,1,2,3,4,6';
    const minTimeStr = config.minTime || '08:00';
    const maxTimeStr = config.maxTime || '18:00';

    const statusLabels = isArabic ? ['مجدول', 'منجز', 'ملغى'] : ['Scheduled', 'Completed', 'Cancelled'];
    const financialLabels = isArabic ? ['المدفوعات المسددة', 'الديون المستحقة'] : ['Paid Payments', 'Outstanding Debt'];

    const chartCanvas = document.getElementById('dashboardOverviewChart');
    const todayContainer = document.getElementById('todayStatusContainer');
    let currentChart = null;

    function getChartTheme() {
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        return {
            legendColor: isDark ? '#e2e8f0' : '#475569'
        };
    }

    function renderStatusChart() {
        if (!chartCanvas || typeof Chart === 'undefined') return;
        if (currentChart) currentChart.destroy();

        const ctx = chartCanvas.getContext('2d');
        const theme = getChartTheme();

        currentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: statusLabels,
                datasets: [{
                    data: [scheduled, completed, cancelled],
                    backgroundColor: [
                        '#175cdd',   // Scheduled - Royal Blue
                        '#10b981',   // Completed - Green
                        '#f43f5e'    // Cancelled - Rose Red
                    ],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: theme.legendColor,
                            font: { weight: '700', size: 14 },
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                const unit = isArabic ? ' جلسات' : ' sessions';
                                return ' ' + context.label + ': ' + context.raw + unit;
                            }
                        }
                    }
                }
            }
        });
    }

    function renderFinancialsChart() {
        if (!chartCanvas || typeof Chart === 'undefined') return;
        if (currentChart) currentChart.destroy();

        const ctx = chartCanvas.getContext('2d');
        const theme = getChartTheme();

        currentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: financialLabels,
                datasets: [{
                    data: [paid, debt],
                    backgroundColor: [
                        '#10b981',   // Paid - Green
                        '#f43f5e'    // Debt - Rose Red
                    ],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: theme.legendColor,
                            font: { weight: '700', size: 14 },
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return ' ' + context.label + ': ' + context.raw.toLocaleString('de-DE') + ' ' + currencySymbol;
                            }
                        }
                    }
                }
            }
        });
    }

    function updateClinicStatus() {
        if (!todayContainer) return;
        const workingDays = workingDaysStr.split(',').map(Number);
        const now = new Date();
        const currentDay = now.getDay();

        const dot = document.getElementById('clinicStatusDot');
        const text = document.getElementById('clinicStatusText');
        if (!dot || !text) return;

        if (!workingDays.includes(currentDay)) {
            dot.className = 'spinner-grow spinner-grow-sm text-danger';
            dot.style.animation = 'none';
            dot.style.background = '#dc3545';
            if (isArabic) {
                text.innerHTML = 'مغلق <span class="text-muted fw-normal" style="font-size: 0.7rem;">(عطلة نهاية الأسبوع / يوم عطلة)</span>';
            } else {
                text.innerHTML = 'Closed <span class="text-muted fw-normal" style="font-size: 0.7rem;">(Weekend / Day Off)</span>';
            }
            return;
        }

        const [minH, minM] = minTimeStr.split(':').map(Number);
        const [maxH, maxM] = maxTimeStr.split(':').map(Number);

        const currentMinutes = now.getHours() * 60 + now.getMinutes();
        const minMinutes = minH * 60 + minM;
        const maxMinutes = maxH * 60 + maxM;

        if (currentMinutes >= minMinutes && currentMinutes < maxMinutes) {
            dot.className = 'spinner-grow spinner-grow-sm text-success';
            dot.style.animation = 'spinner-grow 1.5s linear infinite';
            dot.style.background = '#198754';
            if (isArabic) {
                text.innerHTML = 'مفتوح الآن <span class="text-muted fw-normal" style="font-size: 0.7rem;">(ساعات العمل)</span>';
            } else {
                text.innerHTML = 'Open Now <span class="text-muted fw-normal" style="font-size: 0.7rem;">(Operating Hours)</span>';
            }
        } else {
            dot.className = 'spinner-grow spinner-grow-sm text-warning';
            dot.style.animation = 'none';
            dot.style.background = '#ffc107';
            if (isArabic) {
                text.innerHTML = 'مغلق <span class="text-muted fw-normal" style="font-size: 0.7rem;">(خارج أوقات العمل)</span>';
            } else {
                text.innerHTML = 'Closed <span class="text-muted fw-normal" style="font-size: 0.7rem;">(Off Hours)</span>';
            }
        }
    }

    function setActiveTab(activeBtn, inactiveBtn1, inactiveBtn2) {
        activeBtn.className = 'btn btn-primary btn-sm rounded-pill px-3 py-1 fw-bold border-0';
        activeBtn.style.background = 'var(--accent-color, #0d6efd)';
        activeBtn.style.color = '#ffffff';
        activeBtn.style.boxShadow = '0 2px 6px rgba(13, 110, 253, 0.15)';

        [inactiveBtn1, inactiveBtn2].forEach(btn => {
            if (btn) {
                btn.className = 'btn btn-outline-secondary btn-sm rounded-pill px-3 py-1 fw-bold border-0 text-secondary';
                btn.style.background = 'transparent';
                btn.style.color = '';
                btn.style.boxShadow = 'none';
            }
        });
    }

    const btnStatus = document.getElementById('btn-show-status');
    const btnFinancials = document.getElementById('btn-show-financials');
    const btnToday = document.getElementById('btn-show-today');

    if (btnStatus) {
        btnStatus.addEventListener('click', function () {
            setActiveTab(btnStatus, btnFinancials, btnToday);
            if (todayContainer) todayContainer.style.display = 'none';
            if (chartCanvas) chartCanvas.style.display = 'block';
            renderStatusChart();
        });
    }

    if (btnFinancials) {
        btnFinancials.addEventListener('click', function () {
            setActiveTab(btnFinancials, btnStatus, btnToday);
            if (todayContainer) todayContainer.style.display = 'none';
            if (chartCanvas) chartCanvas.style.display = 'block';
            renderFinancialsChart();
        });
    }

    if (btnToday) {
        btnToday.addEventListener('click', function () {
            setActiveTab(btnToday, btnStatus, btnFinancials);
            if (chartCanvas) chartCanvas.style.display = 'none';
            if (todayContainer) todayContainer.style.display = 'block';
            updateClinicStatus();
        });
    }

    // Cancellation helper
    window.confirmCancelAppointment = function (apptId) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: isArabic ? "تأكيد إلغاء الموعد" : "Confirm Cancellation",
                text: isArabic ? "هل أنت متأكد من رغبتك في إلغاء هذا الموعد؟" : "Are you sure you want to cancel this appointment?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#6c757d',
                confirmButtonText: isArabic ? "نعم، إلغاء الموعد" : "Yes, cancel appointment",
                cancelButtonText: isArabic ? "إلغاء" : "Cancel"
            }).then((result) => {
                if (result.isConfirmed) {
                    window.changeFlowStatus(apptId, 'Cancelled');
                }
            });
        } else {
            if (confirm(isArabic ? "هل أنت متأكد من إلغاء هذا الموعد؟" : "Are you sure you want to cancel this appointment?")) {
                window.changeFlowStatus(apptId, 'Cancelled');
            }
        }
    };

    window.changeFlowStatus = function (apptId, newStatus) {
        const url = `/appointments/${apptId}/update-status`;
        const currentCsrf = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || csrfToken;

        const Toast = (typeof Swal !== 'undefined') ? Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        }) : null;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': currentCsrf
            },
            body: JSON.stringify({ status: newStatus })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (Toast) {
                        Toast.fire({
                            icon: 'success',
                            title: isArabic ? "تم تحديث حالة المريض بنجاح!" : "Patient status updated successfully!"
                        });
                    }
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            icon: 'error',
                            title: isArabic ? 'خطأ' : 'Error',
                            text: data.message || (isArabic ? 'فشل تحديث الحالة' : 'Failed to update status.')
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error updating status:', error);
                if (typeof Swal !== 'undefined') {
                    Swal.fire({
                        icon: 'error',
                        title: isArabic ? 'خطأ' : 'Error',
                        text: isArabic ? 'حدث خطأ أثناء الاتصال بالخادم.' : 'Network error or server failed.'
                    });
                }
            });
    };

    renderStatusChart();
    updateClinicStatus();

    // Auto-refresh polling for today's appointment statuses
    let currentStatusesString = "";

    function checkStatuses() {
        if (document.hidden) return;

        fetch("/appointments/today-statuses")
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const keys = Object.keys(data.statuses).sort();
                    const statusesStr = keys.map(k => `${k}:${data.statuses[k]}`).join(',');

                    if (currentStatusesString === "") {
                        currentStatusesString = statusesStr;
                    } else if (currentStatusesString !== statusesStr) {
                        console.log("[Auto-Refresh] Status change detected! Reloading page...");
                        window.location.reload();
                    }
                }
            })
            .catch(err => console.error("[Auto-Refresh] Error polling statuses:", err));
    }

    checkStatuses();
    setInterval(checkStatuses, 10000);

    document.addEventListener("visibilitychange", function () {
        if (!document.hidden) {
            checkStatuses();
        }
    });
};
