/**
 * Dental Clinic Management System - Base Layout Core Controller
 * Handles WhatsApp reminder triggers, SweetAlert2 delete dialogs, and instant theme/language switching.
 */

function sendWhatsAppReminder(phone, patientName, dateTimeStr, clinicName, appointmentId) {
    if (!phone || phone.trim() === '' || phone === 'No phone' || phone === 'No phone number') {
        const isAr = document.documentElement.getAttribute('lang') === 'ar';
        alert(isAr ? 'خطأ: المريض لا يملك رقم هاتف مسجل!' : 'Error: Patient has no registered phone number!');
        return;
    }

    let cleanedPhone = phone.replace(/[^0-9]/g, '');

    const isArabic = document.documentElement.getAttribute('lang') === 'ar';
    let message = "";
    if (isArabic) {
        message = `مرحباً ${patientName}، نود تذكيركم بموعدكم القادم في عيادة ${clinicName} بتاريخ ${dateTimeStr}. نتطلع لرؤيتكم!`;
    } else {
        message = `Hello ${patientName}, this is a reminder for your upcoming appointment at ${clinicName} on ${dateTimeStr}. We look forward to seeing you!`;
    }

    let encodedText = encodeURIComponent(message);
    let url = `https://wa.me/${cleanedPhone}?text=${encodedText}`;
    window.open(url, '_blank');

    if (appointmentId) {
        localStorage.setItem('reminded_appt_' + appointmentId, 'true');
        const isAr = document.documentElement.getAttribute('lang') === 'ar';
        const badgeHtml = `<span class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1 small align-middle" style="font-size: 0.72rem; font-weight: 700; margin-left: 4px; margin-right: 4px;">
                  <i class="bi bi-check-all fs-6"></i> ${isAr ? 'تم التذكير' : 'Reminded'}
              </span>`;

        document.querySelectorAll(`.reminded-status-placeholder[data-appointment-id="${appointmentId}"]`).forEach(el => {
            el.innerHTML = badgeHtml;
        });

        const modalStatus = document.getElementById('modal-reminded-status');
        if (modalStatus) {
            modalStatus.innerHTML = badgeHtml;
        }
    }
}

function confirmDelete(event, customMsg, customTitle) {
    if (event) event.preventDefault();
    const isAr = document.documentElement.getAttribute('lang') === 'ar' || document.documentElement.lang === 'ar';
    const target = (event && (event.currentTarget || event.target)) || null;

    const title = customTitle || (isAr ? 'تأكيد الحذف' : 'Confirm Deletion');
    const text = customMsg || (isAr ? 'هل أنت متأكد من عملية الحذف؟' : 'Are you sure you want to delete this item?');

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: title,
            text: text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: isAr ? 'نعم، احذف الآن' : 'Yes, Delete Now',
            cancelButtonText: isAr ? 'إلغاء' : 'Cancel',
            buttonsStyling: false,
            customClass: {
                popup: 'rounded-4 shadow-lg swal2-custom-glass-popup',
                confirmButton: 'btn-modal-submit-danger px-4 py-2 mx-1',
                cancelButton: 'btn-modal-cancel px-4 py-2 mx-1'
            }
        }).then((result) => {
            if (result.isConfirmed && target) {
                if (target.tagName === 'FORM') {
                    target.submit();
                } else if (target.tagName === 'A' && target.href) {
                    window.location.href = target.href;
                } else {
                    const form = target.closest('form');
                    if (form) {
                        form.submit();
                    } else if (target.href) {
                        window.location.href = target.href;
                    } else if (target.getAttribute('href')) {
                        window.location.href = target.getAttribute('href');
                    }
                }
            }
        });
    } else {
        if (confirm(text) && target) {
            if (target.tagName === 'FORM') target.submit();
            else if (target.href) window.location.href = target.href;
            else {
                const form = target.closest('form');
                if (form) form.submit();
            }
        }
    }
    return false;
}

function toggleAppTheme() {
    const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-bs-theme', next);
    localStorage.setItem('theme', next);
    document.cookie = "theme=" + next + ";path=/;max-age=31536000;SameSite=Lax";
    updateQuickThemeIcon(next);
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: next } }));
}

function updateQuickThemeIcon(theme) {
    const icon = document.getElementById('quickThemeIcon');
    if (!icon) return;
    if (theme === 'dark') {
        icon.className = 'bi bi-sun-fill text-warning';
    } else {
        icon.className = 'bi bi-moon-stars-fill text-white';
    }
}

function toggleAppLanguage() {
    const current = document.documentElement.getAttribute('lang') || 'ar';
    const next = current === 'ar' ? 'en' : 'ar';
    document.cookie = "lang=" + next + ";path=/;max-age=31536000;SameSite=Lax";
    localStorage.setItem('lang', next);
    window.location.reload();
}

document.addEventListener('DOMContentLoaded', function () {
    const theme = document.documentElement.getAttribute('data-bs-theme') || localStorage.getItem('theme') || 'light';
    updateQuickThemeIcon(theme);

    document.querySelectorAll('.reminded-status-placeholder').forEach(el => {
        const apptId = el.getAttribute('data-appointment-id');
        if (apptId && localStorage.getItem('reminded_appt_' + apptId) === 'true') {
            const isAr = document.documentElement.getAttribute('lang') === 'ar';
            el.innerHTML = `<span class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1 small align-middle" style="font-size: 0.72rem; font-weight: 700; margin-left: 4px; margin-right: 4px;">
                        <i class="bi bi-check-all fs-6"></i> ${isAr ? 'تم التذكير' : 'Reminded'}
                    </span>`;
        }
    });
});
