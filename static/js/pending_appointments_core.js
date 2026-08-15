/**
 * Dental Clinic Management System - Pending Appointments Controller
 * Handles auto-clean expired requests and appointment confirm/decline quick actions via SweetAlert2.
 */

window.initPendingAppointments = function (config) {
    const cleanUrl = config.cleanUrl || '';
    const cleanBtn = document.getElementById("btn-clean-expired");

    if (cleanBtn && cleanUrl) {
        cleanBtn.addEventListener("click", function () {
            if (typeof Swal !== "undefined") {
                Swal.fire({
                    title: config.langCleanTitle || "تنظيف الطلبات المنتهية",
                    text: config.langCleanText || "سيتم إلغاء كافة طلبات الحجز التي فات تاريخها الميعادي تلقائياً.",
                    icon: "question",
                    showCancelButton: true,
                    confirmButtonText: config.langCleanConfirm || "نعم، تنظيف الآن",
                    cancelButtonText: config.langCancel || "إلغاء"
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch(cleanUrl, {
                            method: "POST",
                            headers: { "X-Requested-With": "XMLHttpRequest" }
                        }).then(res => res.json()).then(data => {
                            if (data.success) {
                                Swal.fire({
                                    icon: "success",
                                    title: config.langSuccess || "تم التنظيف بنجاح",
                                    text: data.message,
                                    timer: 1500,
                                    showConfirmButton: false
                                }).then(() => window.location.reload());
                            }
                        }).catch(() => {
                            window.location.reload();
                        });
                    }
                });
            } else {
                if (confirm(config.langCleanConfirmDirect || "هل تريد إلغاء وتنظيف الطلبات المنتهية التارخ؟")) {
                    fetch(cleanUrl, {
                        method: "POST",
                        headers: { "X-Requested-With": "XMLHttpRequest" }
                    }).then(res => res.json()).then(data => {
                        if (data.success) {
                            window.location.reload();
                        }
                    }).catch(() => {
                        window.location.reload();
                    });
                }
            }
        });
    }

    // Quick action buttons for confirm/decline
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const url = this.getAttribute('data-action-url');
            const msg = this.getAttribute('data-confirm-msg') || 'هل أنت متأكد؟';
            if (!url) return;

            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: msg,
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonText: config.langYes || 'نعم، متابعة',
                    cancelButtonText: config.langCancel || 'إلغاء'
                }).then((res) => {
                    if (res.isConfirmed) {
                        window.location.href = url;
                    }
                });
            } else {
                if (confirm(msg)) {
                    window.location.href = url;
                }
            }
        });
    });
};
