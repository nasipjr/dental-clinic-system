/**
 * Dental Clinic Management System - License Activation Controller
 * Handles HWID clipboard copy and license key uppercase auto-formatting.
 */

window.initAuthActivate = function (config) {
    const copyBtn = document.getElementById('btnCopyHwid');
    const copyText = document.getElementById('copyHwidText');
    const keyInput = document.getElementById('license_key');

    if (copyBtn && copyText) {
        copyBtn.addEventListener('click', function () {
            const hwid = copyBtn.getAttribute('data-hwid') || '';
            if (navigator.clipboard && hwid) {
                navigator.clipboard.writeText(hwid).then(() => {
                    const original = copyText.innerText;
                    copyText.innerText = (config.currentLang === 'ar') ? '✓ تم النسخ' : '✓ Copied';
                    setTimeout(() => {
                        copyText.innerText = original;
                    }, 2000);
                });
            }
        });
    }

    if (keyInput) {
        keyInput.addEventListener('input', function () {
            this.value = this.value.toUpperCase();
        });
    }
};
