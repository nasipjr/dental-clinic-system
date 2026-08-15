/**
 * Dental Clinic Management System - Patient Form JavaScript Controller
 * Client-side logic for Syrian phone prefix (+963), dual emergency contact mode (select / manual), and live duplicate patient detection.
 */

window.initPatientForm = function (config) {
    const isAr = config.isArabic !== undefined ? config.isArabic : (document.documentElement.lang === 'ar' || document.dir === 'rtl');
    const patientId = config.patientId || null;

    const phoneInputLocal = document.getElementById("phone_input");
    const phoneHidden = document.getElementById("phone");
    const form = document.getElementById("add-patient-form");
    const firstNameInput = document.getElementById("first_name");
    const lastNameInput = document.getElementById("last_name");
    const liveAlert = document.getElementById("live-duplicate-alert");
    const liveList = document.getElementById("live-duplicate-list");

    // ── 1. Main Phone Prefix (+963) Sync & Validation ───────────────────────
    function syncPhone() {
        if (!phoneInputLocal || !phoneHidden) return true;
        let digits = phoneInputLocal.value.trim().replace(/\D/g, "");
        if (digits.startsWith("963")) digits = digits.slice(3);
        if (digits.startsWith("0")) digits = digits.slice(1);
        digits = digits.slice(0, 9);
        phoneInputLocal.value = digits;

        if (digits.length === 9) {
            phoneHidden.value = "+963" + digits;
            phoneInputLocal.classList.remove("is-invalid");
            return true;
        } else {
            phoneHidden.value = digits ? ("+963" + digits) : "";
            phoneInputLocal.classList.add("is-invalid");
            return false;
        }
    }

    if (phoneInputLocal) {
        phoneInputLocal.addEventListener("input", syncPhone);
        phoneInputLocal.addEventListener("blur", syncPhone);
        syncPhone();
    }

    // ── 2. Emergency Contact Dual-Mode Engine ───────────────────────────────
    const emergencySelectContainer = document.getElementById("emergency-select-container");
    const emergencyManualContainer = document.getElementById("emergency-manual-container");
    const emergencyPatientSelect = document.getElementById("emergency_patient_select");
    const emergencyPhoneInput = document.getElementById("emergency_phone_input");
    const emergencyHiddenInput = document.getElementById("emergency_contact");
    const btnEmergencySelect = document.getElementById("emergency-mode-select");
    const btnEmergencyManual = document.getElementById("emergency-mode-manual");

    const emergencyMatchBadge = document.getElementById("emergency-match-badge");
    const emergencyMatchText = document.getElementById("emergency-match-text");
    const emergencyMultiMatchBox = document.getElementById("emergency-multi-match-box");
    const emergencyMultiMatchList = document.getElementById("emergency-multi-match-list");

    const emergencyClearBtn = document.getElementById("emergency_clear_btn");
    const emergencyBadgeClearBtn = document.getElementById("emergency_badge_clear_btn");

    function toggleClearBtnVisibility() {
        const hasVal = !!(emergencyHiddenInput && emergencyHiddenInput.value.trim());
        if (emergencyClearBtn) {
            if (hasVal) {
                emergencyClearBtn.classList.remove("d-none");
                emergencyClearBtn.classList.add("d-flex", "align-items-center");
                if (emergencyPatientSelect) emergencyPatientSelect.classList.remove("rounded-end-3");
            } else {
                emergencyClearBtn.classList.add("d-none");
                emergencyClearBtn.classList.remove("d-flex", "align-items-center");
                if (emergencyPatientSelect) emergencyPatientSelect.classList.add("rounded-end-3");
            }
        }
    }

    function clearEmergencySelection() {
        if (emergencyPatientSelect) emergencyPatientSelect.selectedIndex = 0;
        if (emergencyPhoneInput) emergencyPhoneInput.value = "";
        if (emergencyHiddenInput) emergencyHiddenInput.value = "";
        hideMatchNotices();
        toggleClearBtnVisibility();
    }

    if (emergencyClearBtn) {
        emergencyClearBtn.addEventListener("click", function (e) { e.preventDefault(); clearEmergencySelection(); });
    }
    if (emergencyBadgeClearBtn) {
        emergencyBadgeClearBtn.addEventListener("click", function (e) { e.preventDefault(); clearEmergencySelection(); });
    }

    function setEmergencyMode(mode) {
        if (mode === "select") {
            if (btnEmergencySelect) {
                btnEmergencySelect.style.setProperty("background", "var(--accent-color, #0d6efd)", "important");
                btnEmergencySelect.style.setProperty("color", "#ffffff", "important");
                btnEmergencySelect.style.setProperty("box-shadow", "0 2px 6px rgba(13, 110, 253, 0.25)", "important");
            }
            if (btnEmergencyManual) {
                btnEmergencyManual.style.setProperty("background", "transparent", "important");
                btnEmergencyManual.style.setProperty("color", "var(--heading-color)", "important");
                btnEmergencyManual.style.setProperty("box-shadow", "none", "important");
            }
            emergencySelectContainer?.classList.remove("d-none");
            emergencyManualContainer?.classList.add("d-none");
            syncEmergencyFromSelect();
        } else {
            if (btnEmergencyManual) {
                btnEmergencyManual.style.setProperty("background", "var(--accent-color, #0d6efd)", "important");
                btnEmergencyManual.style.setProperty("color", "#ffffff", "important");
                btnEmergencyManual.style.setProperty("box-shadow", "0 2px 6px rgba(13, 110, 253, 0.25)", "important");
            }
            if (btnEmergencySelect) {
                btnEmergencySelect.style.setProperty("background", "transparent", "important");
                btnEmergencySelect.style.setProperty("color", "var(--heading-color)", "important");
                btnEmergencySelect.style.setProperty("box-shadow", "none", "important");
            }
            emergencyManualContainer?.classList.remove("d-none");
            emergencySelectContainer?.classList.add("d-none");
            syncEmergencyFromManual();
        }
        toggleClearBtnVisibility();
    }

    function hideMatchNotices() {
        if (emergencyMatchBadge) {
            emergencyMatchBadge.classList.add("d-none");
            emergencyMatchBadge.classList.remove("d-flex");
        }
        if (emergencyMultiMatchBox) {
            emergencyMultiMatchBox.classList.add("d-none");
        }
    }

    function syncEmergencyFromSelect() {
        if (!emergencyHiddenInput || !emergencyPatientSelect) return;
        const selVal = emergencyPatientSelect.value.trim();
        emergencyHiddenInput.value = selVal;

        if (selVal && emergencyPatientSelect.selectedIndex >= 0) {
            const selOpt = emergencyPatientSelect.options[emergencyPatientSelect.selectedIndex];
            const pPhone = selOpt.getAttribute("data-phone");
            if (pPhone && emergencyPhoneInput) {
                emergencyPhoneInput.value = pPhone;
            }
        }
        toggleClearBtnVisibility();
    }

    function syncEmergencyFromManual() {
        if (!emergencyPhoneInput || !emergencyHiddenInput) return;
        let digits = emergencyPhoneInput.value.trim().replace(/\D/g, "");
        if (digits.startsWith("963")) digits = digits.slice(3);
        if (digits.startsWith("0")) digits = digits.slice(1);
        digits = digits.slice(0, 9);
        emergencyPhoneInput.value = digits;

        hideMatchNotices();

        if (digits.length === 9) {
            emergencyHiddenInput.value = "+963" + digits;

            const matches = [];
            if (emergencyPatientSelect) {
                for (let i = 1; i < emergencyPatientSelect.options.length; i++) {
                    const opt = emergencyPatientSelect.options[i];
                    const pPhone = (opt.getAttribute("data-phone") || "").trim();
                    if (pPhone && pPhone === digits) {
                        matches.push({ index: i, option: opt });
                    }
                }
            }

            if (matches.length === 1) {
                emergencyPatientSelect.selectedIndex = matches[0].index;
                emergencyHiddenInput.value = matches[0].option.value.trim();
                setEmergencyMode("select");

                if (emergencyMatchBadge && emergencyMatchText) {
                    emergencyMatchText.textContent = isAr ? `تم الربط تلقائياً مع المريض: ${matches[0].option.text}` : `Linked with patient: ${matches[0].option.text}`;
                    emergencyMatchBadge.classList.remove("d-none");
                    emergencyMatchBadge.classList.add("d-flex");
                }
            } else if (matches.length > 1) {
                setEmergencyMode("select");
                if (emergencyMultiMatchBox && emergencyMultiMatchList) {
                    emergencyMultiMatchList.innerHTML = "";
                    matches.forEach(m => {
                        const btn = document.createElement("button");
                        btn.type = "button";
                        btn.className = "btn btn-sm btn-outline-primary rounded-pill px-2.5 py-1 text-nowrap";
                        btn.innerHTML = `<i class="bi bi-person-check me-1"></i>${m.option.text}`;
                        btn.addEventListener("click", function (e) {
                            e.preventDefault();
                            emergencyPatientSelect.selectedIndex = m.index;
                            syncEmergencyFromSelect();
                            hideMatchNotices();
                            if (emergencyMatchBadge && emergencyMatchText) {
                                emergencyMatchText.textContent = isAr ? `تم التطابق مع: ${m.option.text}` : `Matched with: ${m.option.text}`;
                                emergencyMatchBadge.classList.remove("d-none");
                                emergencyMatchBadge.classList.add("d-flex");
                            }
                        });
                        emergencyMultiMatchList.appendChild(btn);
                    });
                    emergencyMultiMatchBox.classList.remove("d-none");
                }
            }
        } else {
            emergencyHiddenInput.value = digits ? ("+963" + digits) : "";
        }
        toggleClearBtnVisibility();
    }

    if (btnEmergencySelect) {
        btnEmergencySelect.addEventListener("click", function (e) { e.preventDefault(); setEmergencyMode("select"); });
    }
    if (btnEmergencyManual) {
        btnEmergencyManual.addEventListener("click", function (e) { e.preventDefault(); setEmergencyMode("manual"); });
    }
    if (emergencyPatientSelect) {
        emergencyPatientSelect.addEventListener("change", function () {
            syncEmergencyFromSelect();
            hideMatchNotices();
        });
    }
    if (emergencyPhoneInput) {
        emergencyPhoneInput.addEventListener("input", syncEmergencyFromManual);
        emergencyPhoneInput.addEventListener("blur", syncEmergencyFromManual);
    }

    const initVal = emergencyHiddenInput ? (emergencyHiddenInput.value || "").trim() : "";
    if (initVal) {
        let foundInSelect = false;
        if (emergencyPatientSelect) {
            for (let opt of emergencyPatientSelect.options) {
                if (opt.value === initVal && initVal !== "") {
                    opt.selected = true;
                    foundInSelect = true;
                    break;
                }
            }
        }
        if (foundInSelect) {
            setEmergencyMode("select");
        } else if (initVal.startsWith("+963") || /^\+?\d{7,15}$/.test(initVal)) {
            setEmergencyMode("manual");
            let digits = initVal.replace(/\D/g, "");
            if (digits.startsWith("963")) digits = digits.slice(3);
            if (digits.startsWith("0")) digits = digits.slice(1);
            if (emergencyPhoneInput) emergencyPhoneInput.value = digits.slice(0, 9);
            syncEmergencyFromManual();
        } else {
            setEmergencyMode("select");
        }
    } else {
        setEmergencyMode("select");
    }
    toggleClearBtnVisibility();

    // ── 3. Live Duplicate Patient Check (AJAX Debounced) ─────────────────────
    let dupCheckTimer = null;

    function checkDuplicateLive() {
        const fn = firstNameInput ? firstNameInput.value.trim() : "";
        const ln = lastNameInput ? lastNameInput.value.trim() : "";

        if (!fn || !ln || fn.length < 3 || ln.length < 3) {
            if (liveAlert) liveAlert.style.display = "none";
            return;
        }

        clearTimeout(dupCheckTimer);
        dupCheckTimer = setTimeout(function () {
            const excludeParam = patientId ? `&exclude_id=${patientId}` : "";
            fetch(`/patients/check-duplicate?first_name=${encodeURIComponent(fn)}&last_name=${encodeURIComponent(ln)}${excludeParam}`)
                .then(r => r.json())
                .then(data => {
                    if (data.duplicates && data.duplicates.length > 0) {
                        const items = data.duplicates.map(p => {
                            const dob = p.date_of_birth ? `<span class="badge border px-2.5 py-1.5 rounded-pill shadow-sm" style="background-color: rgba(241, 245, 249, 0.08); color: #e2e8f0; border-color: rgba(255, 255, 255, 0.15) !important;"><i class="bi bi-calendar-event me-1"></i>${p.date_of_birth}</span>` : "";
                            const phone = p.phone ? `<span class="badge border px-2.5 py-1.5 rounded-pill shadow-sm" style="background-color: rgba(14, 165, 233, 0.15); color: #38bdf8; border-color: rgba(56, 189, 248, 0.35) !important;"><i class="bi bi-telephone-fill me-1"></i><span dir="ltr">${p.phone}</span></span>` : "";
                            return `
                                <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 p-2.5 rounded-3" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);">
                                    <div class="d-flex align-items-center gap-2">
                                        <i class="bi bi-person-fill text-warning fs-5"></i>
                                        <a href="${p.url}" target="_blank" class="fw-bold text-info text-decoration-none fs-6">${p.name}</a>
                                    </div>
                                    <div class="d-flex align-items-center gap-2 flex-wrap">
                                        ${phone}
                                        ${dob}
                                    </div>
                                </div>
                            `;
                        }).join("");
                        if (liveList) liveList.innerHTML = items;
                        if (liveAlert) liveAlert.style.display = "block";
                    } else {
                        if (liveAlert) liveAlert.style.display = "none";
                    }
                })
                .catch(() => { if (liveAlert) liveAlert.style.display = "none"; });
        }, 500);
    }

    if (firstNameInput) firstNameInput.addEventListener("input", checkDuplicateLive);
    if (lastNameInput) lastNameInput.addEventListener("input", checkDuplicateLive);

    if (form) {
        form.addEventListener("submit", function (e) {
            if (phoneInputLocal && !syncPhone()) {
                e.preventDefault();
                e.stopPropagation();
                phoneInputLocal.focus();
            }
        });
    }
};
