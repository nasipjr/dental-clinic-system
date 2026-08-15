/**
 * Dental Clinic Management System - Nurse Appearance Settings Controller
 * Handles application theme selection (light/dark) and language selection with cookie/localStorage persistence.
 */

window.setAppTheme = function (theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    document.cookie = "theme=" + theme + ";path=/;max-age=31536000;SameSite=Lax";
    updateThemeButtons(theme);
};

function updateThemeButtons(theme) {
    const lightBtn = document.getElementById('theme-light-btn');
    const darkBtn = document.getElementById('theme-dark-btn');
    if (!lightBtn || !darkBtn) return;

    if (theme === 'dark') {
        darkBtn.classList.remove('btn-outline-secondary', 'border-secondary-subtle');
        darkBtn.classList.add('btn-primary', 'border-primary', 'shadow-sm');
        darkBtn.style.backgroundColor = 'var(--accent-color)';
        darkBtn.style.color = '#ffffff';

        lightBtn.classList.remove('btn-primary', 'border-primary', 'shadow-sm');
        lightBtn.classList.add('btn-outline-secondary', 'border-secondary-subtle');
        lightBtn.style.backgroundColor = 'transparent';
        lightBtn.style.color = 'var(--default-color)';
    } else {
        lightBtn.classList.remove('btn-outline-secondary', 'border-secondary-subtle');
        lightBtn.classList.add('btn-primary', 'border-primary', 'shadow-sm');
        lightBtn.style.backgroundColor = 'var(--accent-color)';
        lightBtn.style.color = '#ffffff';

        darkBtn.classList.remove('btn-primary', 'border-primary', 'shadow-sm');
        darkBtn.classList.add('btn-outline-secondary', 'border-secondary-subtle');
        darkBtn.style.backgroundColor = 'transparent';
        darkBtn.style.color = 'var(--default-color)';
    }
}

window.setAppLang = function (lang) {
    document.cookie = "lang=" + lang + ";path=/;max-age=31536000;SameSite=Lax";
    localStorage.setItem('lang', lang);
    updateLangButtons(lang);
    window.location.reload();
};

function updateLangButtons(lang) {
    const enBtn = document.getElementById('lang-en-btn');
    const arBtn = document.getElementById('lang-ar-btn');
    if (!enBtn || !arBtn) return;

    if (lang === 'ar') {
        arBtn.classList.remove('btn-outline-secondary', 'border-secondary-subtle');
        arBtn.classList.add('btn-primary', 'border-primary', 'shadow-sm');
        arBtn.style.backgroundColor = 'var(--accent-color)';
        arBtn.style.color = '#ffffff';

        enBtn.classList.remove('btn-primary', 'border-primary', 'shadow-sm');
        enBtn.classList.add('btn-outline-secondary', 'border-secondary-subtle');
        enBtn.style.backgroundColor = 'transparent';
        enBtn.style.color = 'var(--default-color)';
    } else {
        enBtn.classList.remove('btn-outline-secondary', 'border-secondary-subtle');
        enBtn.classList.add('btn-primary', 'border-primary', 'shadow-sm');
        enBtn.style.backgroundColor = 'var(--accent-color)';
        enBtn.style.color = '#ffffff';

        arBtn.classList.remove('btn-primary', 'border-primary', 'shadow-sm');
        arBtn.classList.add('btn-outline-secondary', 'border-secondary-subtle');
        arBtn.style.backgroundColor = 'transparent';
        arBtn.style.color = 'var(--default-color)';
    }
}

window.initNurseSettings = function () {
    const currentTheme = localStorage.getItem('theme') || 'light';
    updateThemeButtons(currentTheme);

    const savedLang = localStorage.getItem('lang') || 'en';
    updateLangButtons(savedLang);
};
