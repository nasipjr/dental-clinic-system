/**
 * Dental Clinic Management System - Auth Login Controller
 * Handles client-side language switching, cookie storage, and tab focus management.
 */

window.initAuthLogin = function (config) {
    const currentLang = config.currentLang || 'ar';
    const langBtn = document.getElementById('lang-toggle-btn');

    if (langBtn) {
        langBtn.addEventListener('click', () => {
            const newLang = currentLang === 'ar' ? 'en' : 'ar';
            document.cookie = "lang=" + newLang + ";path=/;max-age=31536000";
            window.location.reload();
        });
    }
};
