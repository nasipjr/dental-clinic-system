/**
 * Dental Clinic Management System - Add Treatment JavaScript Controller
 * Isolated client-side logic for dynamic procedure price calculation and anesthesia options.
 */

window.initTreatmentAdd = function (config) {
    const defaultNeedlePrice = parseFloat(config.needlePrice) || 50000;
    const currencySymbol = config.currencySymbol || 'SP';
    const isAr = config.isArabic !== undefined ? config.isArabic : (document.documentElement.lang === 'ar' || document.dir === 'rtl');

    const procedureSelect = document.getElementById('procedure_type');
    const priceDisplay = document.getElementById('procedure_price_display');
    const toothInput = document.getElementById('tooth_number');
    const useAnesthesiaCheckbox = document.getElementById('use_anesthesia');
    const needlesWrapper = document.getElementById('needles_wrapper');
    const anesthesiaTypeSelect = document.getElementById('anesthesia_type');
    const needlesInput = document.getElementById('anesthesia_needles');

    let prices = {};
    if (procedureSelect && procedureSelect.dataset.prices) {
        try { prices = JSON.parse(procedureSelect.dataset.prices); } catch (e) { }
    }

    function updateProcedurePrice() {
        if (!procedureSelect || !priceDisplay) return;

        const selectedProcedure = procedureSelect.value;
        if (!selectedProcedure || prices[selectedProcedure] === undefined) {
            priceDisplay.textContent = isAr ? 'اختر نوع الإجراء لعرض السعر' : 'Select a procedure type to show price';
            return;
        }

        let teethCount = 1;
        if (toothInput && toothInput.value.trim()) {
            const teethList = toothInput.value.split(',')
                .map(t => t.trim())
                .filter(t => t !== '');
            if (teethList.length > 0) {
                teethCount = teethList.length;
            }
        }

        const basePrice = parseFloat(prices[selectedProcedure]) || 0;
        const procTotal = basePrice * teethCount;

        const useAnesthesia = useAnesthesiaCheckbox ? useAnesthesiaCheckbox.checked : false;
        let currentNeedlePrice = defaultNeedlePrice;
        if (anesthesiaTypeSelect && anesthesiaTypeSelect.options.length > 0) {
            const selOpt = anesthesiaTypeSelect.options[anesthesiaTypeSelect.selectedIndex];
            if (selOpt && selOpt.dataset.price) {
                currentNeedlePrice = parseFloat(selOpt.dataset.price) || defaultNeedlePrice;
            }
        }

        const needlesCount = needlesInput ? (parseInt(needlesInput.value, 10) || 1) : 0;
        const anesthesiaCost = useAnesthesia ? needlesCount * currentNeedlePrice : 0;
        const totalPrice = procTotal + anesthesiaCost;

        const toothLabel = isAr ? 'أسنان' : 'teeth';
        const totalLabel = isAr ? 'المجموع' : 'Total';

        let displayVal = totalPrice.toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' ' + currencySymbol;
        if (teethCount > 1) {
            displayVal += ` (${totalLabel} لـ ${teethCount} ${toothLabel})`;
        }
        if (useAnesthesia) {
            const incAnesthLabel = isAr ? 'شامل التخدير' : 'inc. anesthesia';
            displayVal += ` (${incAnesthLabel})`;
        }
        priceDisplay.textContent = displayVal;
    }

    if (useAnesthesiaCheckbox && needlesWrapper) {
        useAnesthesiaCheckbox.addEventListener('change', function () {
            needlesWrapper.style.display = this.checked ? 'block' : 'none';
            updateProcedurePrice();
        });
    }

    if (anesthesiaTypeSelect) {
        anesthesiaTypeSelect.addEventListener('change', updateProcedurePrice);
    }

    if (needlesInput) {
        needlesInput.addEventListener('input', updateProcedurePrice);
    }

    if (procedureSelect) {
        procedureSelect.addEventListener('change', updateProcedurePrice);
    }

    if (toothInput) {
        toothInput.addEventListener('input', updateProcedurePrice);
    }

    updateProcedurePrice();
};
