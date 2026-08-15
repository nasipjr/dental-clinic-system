/**
 * Dental Clinic Management System - Appointment Archive Core Controller
 * Handles AJAX table loading, live search debounce, status filtering, and SweetAlert2 confirmation dialogs.
 */

window.initAppointmentArchive = function (config) {
    const tableContainer = document.getElementById("archive-table-container");
    const filterForm = document.getElementById("archive-filter-form");
    const searchInput = document.getElementById("archive-search-input");
    const statusSelect = document.getElementById("archive-status-select");
    const isAr = config.isArabic !== undefined ? config.isArabic : (document.cookie.includes('lang=ar') || !document.cookie.includes('lang=en'));
    const restoreAllUrl = config.restoreAllUrl || '';
    const permDeleteAllUrl = config.permDeleteAllUrl || '';
    const csrfTokenDefault = config.csrfToken || '';

    function loadArchiveTable(url) {
        if (!tableContainer) return;
        tableContainer.style.opacity = "0.5";

        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => {
            if (!res.ok) throw new Error("Failed to load archive table");
            return res.text();
        })
        .then(html => {
            tableContainer.innerHTML = html;
            tableContainer.style.opacity = "1";
            if (window.initCustomTooltips) window.initCustomTooltips();
        })
        .catch(err => {
            console.error(err);
            tableContainer.style.opacity = "1";
        });
    }

    function refreshArchive() {
        if (filterForm) {
            const formData = new FormData(filterForm);
            const queryString = new URLSearchParams(formData).toString();
            loadArchiveTable(filterForm.action + "?" + queryString);
        } else {
            location.reload();
        }
    }

    // Delegate AJAX clicks for sorting headers & pagination links
    document.addEventListener("click", function (e) {
        const link = e.target.closest(".archive-ajax-link");
        if (link) {
            e.preventDefault();
            loadArchiveTable(link.href);
        }
    });

    // Handle Restore All Button
    const restoreAllBtn = document.getElementById('restore-all-btn');
    if (restoreAllBtn && restoreAllUrl) {
        restoreAllBtn.addEventListener('click', function () {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: isAr ? 'استعادة كل المواعيد القابلة للاستعادة' : 'Restore All Restorable Appointments',
                    text: isAr ? 'هل ترغب في استعادة جميع المواعيد المستقبلية المؤرشفة وإعادتها فوراً إلى جدول المواعيد؟' : 'Are you sure you want to restore all future archived appointments back to the appointments schedule?',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#10b981',
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: isAr ? 'نعم، استعادة الكل الآن' : 'Yes, Restore All',
                    cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
                }).then((result) => {
                    if (result.isConfirmed) {
                        Swal.fire({
                            title: isAr ? 'جاري استعادة المواعيد...' : 'Restoring Appointments...',
                            allowOutsideClick: false,
                            didOpen: () => { Swal.showLoading(); }
                        });
                        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || csrfTokenDefault;
                        const fd = new FormData();
                        fd.append('csrf_token', csrfToken);

                        fetch(restoreAllUrl, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-CSRFToken': csrfToken
                            },
                            body: fd
                        })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                Swal.fire({
                                    title: isAr ? 'تمت الاستعادة بنجاح!' : 'Restored Successfully!',
                                    text: res.message,
                                    icon: 'success',
                                    confirmButtonText: isAr ? 'حسناً' : 'OK'
                                }).then(() => refreshArchive());
                            } else {
                                Swal.fire({
                                    title: isAr ? 'تنبيه' : 'Notice',
                                    text: res.message || (isAr ? 'لم يتم استعادة المواعيد' : 'Failed to restore appointments'),
                                    icon: 'warning',
                                    confirmButtonText: isAr ? 'حسناً' : 'OK'
                                });
                            }
                        })
                        .catch(() => {
                            Swal.fire({
                                title: isAr ? 'خطأ' : 'Error',
                                text: isAr ? 'حدث خطأ أثناء تنفيذ عملية الاستعادة' : 'An error occurred during restoration',
                                icon: 'error',
                                confirmButtonText: isAr ? 'حسناً' : 'OK'
                            });
                        });
                    }
                });
            }
        });
    }

    // Handle Permanent Delete All Button
    const permDeleteAllBtn = document.getElementById('permanent-delete-all-btn');
    if (permDeleteAllBtn && permDeleteAllUrl) {
        permDeleteAllBtn.addEventListener('click', function () {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: isAr ? 'حذف نهائي لجميع المواعيد المؤرشفة' : 'Permanently Delete All Archived Appointments',
                    text: isAr ? 'تحذير: هل أنت متأكد تماماً من رغبتك في حذف جميع المواعيد المؤرشفة (الملغاة والمحذوفة) نهائياً من قاعدة البيانات؟ لا يمكن التراجع عن هذا الإجراء إطلاقاً.' : 'Warning: Are you sure you want to permanently delete all archived appointments from the database? This action cannot be undone!',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#ef4444',
                    cancelButtonColor: '#6c757d',
                    confirmButtonText: isAr ? 'نعم، حذف الكل نهائياً' : 'Yes, Delete All',
                    cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
                }).then((result) => {
                    if (result.isConfirmed) {
                        Swal.fire({
                            title: isAr ? 'جاري الحذف النهائي للمواعيد...' : 'Deleting Appointments...',
                            allowOutsideClick: false,
                            didOpen: () => { Swal.showLoading(); }
                        });
                        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || csrfTokenDefault;
                        const fd = new FormData();
                        fd.append('csrf_token', csrfToken);

                        fetch(permDeleteAllUrl, {
                            method: 'POST',
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-CSRFToken': csrfToken
                            },
                            body: fd
                        })
                        .then(r => r.json())
                        .then(res => {
                            if (res.success) {
                                Swal.fire({
                                    title: isAr ? 'تم الحذف النهائي بنجاح!' : 'Deleted Successfully!',
                                    text: res.message,
                                    icon: 'success',
                                    confirmButtonText: isAr ? 'حسناً' : 'OK'
                                }).then(() => refreshArchive());
                            } else {
                                Swal.fire({
                                    title: isAr ? 'تنبيه' : 'Notice',
                                    text: res.message || (isAr ? 'لم يتم الحذف' : 'Failed to delete appointments'),
                                    icon: 'warning',
                                    confirmButtonText: isAr ? 'حسناً' : 'OK'
                                });
                            }
                        })
                        .catch(() => {
                            Swal.fire({
                                title: isAr ? 'خطأ' : 'Error',
                                text: isAr ? 'حدث خطأ أثناء عملية الحذف' : 'An error occurred during deletion',
                                icon: 'error',
                                confirmButtonText: isAr ? 'حسناً' : 'OK'
                            });
                        });
                    }
                });
            }
        });
    }

    // Single Restore & Permanent Delete Form Handling
    document.addEventListener("submit", function (e) {
        const form = e.target;
        if (form && form.action.includes("/restore") && !form.action.includes("/restore-all")) {
            e.preventDefault();
            Swal.fire({
                title: isAr ? 'استعادة الموعد' : 'Restore Appointment',
                text: isAr ? 'هل تريد استعادة هذا الموعد وإعادته إلى جدول المواعيد؟' : 'Restore this appointment back to the active schedule?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#10b981',
                cancelButtonColor: '#6c757d',
                confirmButtonText: isAr ? 'نعم، استعادة' : 'Yes, Restore',
                cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
            }).then((res) => {
                if (res.isConfirmed) {
                    const fd = new FormData(form);
                    const csrfToken = fd.get('csrf_token') || csrfTokenDefault;
                    fetch(form.action, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrfToken
                        },
                        body: fd
                    })
                    .then(r => r.json())
                    .then(r => {
                        if (r.success) {
                            Swal.fire({ title: isAr ? 'تمت الاستعادة' : 'Restored', text: r.message, icon: 'success', confirmButtonText: isAr ? 'حسناً' : 'OK' })
                            .then(() => refreshArchive());
                        } else {
                            Swal.fire({ title: isAr ? 'تنبيه' : 'Notice', text: r.message, icon: 'warning', confirmButtonText: isAr ? 'حسناً' : 'OK' });
                        }
                    })
                    .catch(() => {
                        form.submit();
                    });
                }
            });
        } else if (form && form.action.includes("/permanent-delete") && !form.action.includes("/permanent-delete-all")) {
            e.preventDefault();
            Swal.fire({
                title: isAr ? 'حذف نهائي للموعد' : 'Permanently Delete Appointment',
                text: isAr ? 'هل أنت متأكد من حذف هذا الموعد نهائياً من قاعدة البيانات؟ لا يمكن التراجع عن هذا الإجراء.' : 'Are you sure you want to permanently delete this appointment from the database?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#ef4444',
                cancelButtonColor: '#6c757d',
                confirmButtonText: isAr ? 'نعم، حذف نهائي' : 'Yes, Delete',
                cancelButtonText: isAr ? 'إلغاء' : 'Cancel'
            }).then((res) => {
                if (res.isConfirmed) {
                    const fd = new FormData(form);
                    const csrfToken = fd.get('csrf_token') || csrfTokenDefault;
                    fetch(form.action, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrfToken
                        },
                        body: fd
                    })
                    .then(r => r.json())
                    .then(r => {
                        if (r.success) {
                            Swal.fire({ title: isAr ? 'تم الحذف' : 'Deleted', text: r.message, icon: 'success', confirmButtonText: isAr ? 'حسناً' : 'OK' })
                            .then(() => refreshArchive());
                        } else {
                            Swal.fire({ title: isAr ? 'تنبيه' : 'Notice', text: r.message, icon: 'warning', confirmButtonText: isAr ? 'حسناً' : 'OK' });
                        }
                    })
                    .catch(() => {
                        form.submit();
                    });
                }
            });
        }
    });

    // Handle Live Input Search with debounce
    let searchTimeout = null;
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function () {
                refreshArchive();
            }, 350);
        });
    }

    // Handle Status Select Filter Change
    if (statusSelect) {
        statusSelect.addEventListener("change", function () {
            refreshArchive();
        });
    }

    window.changeTablePerPage = function (val, module) {
        if (module === 'archive') {
            const input = document.getElementById('archive-per-page-input');
            if (input) input.value = val;
            refreshArchive();
        }
    };
};
