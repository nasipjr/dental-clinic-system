/**
* Template Name: Clinic
* Template URL: https://bootstrapmade.com/clinic-bootstrap-template/
* Updated: Jul 23 2025 with Bootstrap v5.3.7
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }
  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  scrollTop.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    AOS.init({
      duration: 600,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  window.addEventListener('load', aosInit);

  /**
   * Initiate glightbox
   */
  const glightbox = GLightbox({
    selector: '.glightbox'
  });

  /**
   * Initiate Pure Counter
   */
  new PureCounter();

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Frequently Asked Questions Toggle
   */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle, .faq-item .faq-header').forEach((faqItem) => {
    faqItem.addEventListener('click', () => {
      faqItem.parentNode.classList.toggle('faq-active');
    });
  });

})();

document.addEventListener("DOMContentLoaded", function () {
  async function loadDashboardPartial(url, targetId) {
    const target = document.getElementById(targetId);

    if (!target) {
      return;
    }

    try {
      target.classList.add("dashboard-loading");

      const response = await fetch(url, {
        headers: {
          "X-Requested-With": "XMLHttpRequest"
        }
      });

      if (!response.ok) {
        throw new Error("Failed to load dashboard partial");
      }

      const html = await response.text();
      target.innerHTML = html;
      if (window.initCustomTooltips) {
        window.initCustomTooltips();
      }
    } catch (error) {
      console.error(error);
    } finally {
      target.classList.remove("dashboard-loading");
    }
  }

  document.addEventListener("submit", function (event) {
    const form = event.target.closest(".dashboard-ajax-form");

    if (!form) {
      return;
    }

    event.preventDefault();

    const targetId = form.dataset.target;
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    const url = `${form.action}?${params.toString()}`;

    loadDashboardPartial(url, targetId);
  });

  document.addEventListener("click", function (event) {
    const link = event.target.closest(".dashboard-ajax-link");

    if (!link) {
      return;
    }

    event.preventDefault();

    const targetId = link.dataset.target;
    const url = link.href;

    loadDashboardPartial(url, targetId);
  });

  document.addEventListener("click", function (event) {
    const btn = event.target.closest(".quick-action-btn");
    if (!btn) {
      return;
    }

    event.preventDefault();
    const url = btn.getAttribute("data-action-url");
    const rawMsg = btn.getAttribute("data-confirm-msg") || "";
    const rawTitle = btn.getAttribute("data-confirm-title") || "";
    const isArabic = document.documentElement.getAttribute("lang") === "ar";

    const isDecline = url && url.includes("/decline");
    const isCancel = url && (url.includes("/cancel") || url.includes("/quick-cancel"));
    const isDone = url && (url.includes("/done") || url.includes("/quick-done"));

    let titleText = "";
    let confirmBtnText = "";
    let confirmBtnColor = "#198754";
    let alertMsg = "";

    if (isDecline) {
      titleText = isArabic ? "تأكيد رفض طلب الموعد" : "Decline Booking Request";
      confirmBtnText = isArabic ? "نعم، إرفض الموعد" : "Yes, Decline";
      confirmBtnColor = "#dc3545";
      alertMsg = isArabic ? "هل أنت تأكد من إغلاق ورفض هذا الموعد؟" : (rawMsg || "Decline this booking?");
    } else if (isCancel) {
      titleText = isArabic ? "تأكيد إلغاء الموعد" : "Cancel Appointment";
      confirmBtnText = isArabic ? "نعم، إلغاء الموعد" : "Yes, Cancel";
      confirmBtnColor = "#dc3545";
      alertMsg = isArabic ? "هل أنت تأكد من إلغاء هذا الموعد؟" : (rawMsg || "Are you sure you want to cancel this appointment?");
    } else if (isDone) {
      titleText = isArabic ? "تأكيد إتمام الموعد" : "Complete Appointment";
      confirmBtnText = isArabic ? "نعم، إتمام الموعد" : "Yes, Complete";
      confirmBtnColor = "#198754";
      alertMsg = isArabic ? "هل أنت تأكد من إتمام هذا الموعد؟" : (rawMsg || "Mark this appointment as completed?");
    } else {
      titleText = isArabic ? "تأكيد قبول الموعد" : "Confirm Booking Request";
      confirmBtnText = isArabic ? "نعم، أكد الموعد" : "Yes, Confirm";
      confirmBtnColor = "#198754";
      alertMsg = isArabic ? "هل أنت تأكد من قبول وتأكيد حجز هذا الموعد؟" : (rawMsg || "Confirm this booking?");
    }

    if (rawTitle) titleText = rawTitle;

    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfMeta ? csrfMeta.getAttribute("content") : "";

    const performAction = function () {
      fetch(url, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "Content-Type": "application/json",
          "X-CSRF-Token": csrfToken
        }
      })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        if (data.success) {
          if (typeof Swal !== "undefined") {
            Swal.fire({
              icon: "success",
              title: isArabic ? "تم الإجراء" : "Completed",
              text: data.message || (isArabic ? "تم تنفيذ الإجراء بنجاح." : "Action completed successfully."),
              timer: 1500,
              showConfirmButton: false
            }).then(function () {
              reloadTableOrPage();
            });
          } else {
            reloadTableOrPage();
          }
        } else {
          if (typeof Swal !== "undefined") {
            Swal.fire({
              icon: "error",
              title: isArabic ? "تنبيه" : "Notice",
              text: data.message || (isArabic ? "حدث خطأ أثناء تنفيذ الطلب." : "An error occurred."),
              confirmButtonColor: "#175cdd"
            });
          } else {
            alert(data.message || "An error occurred.");
          }
        }
      })
      .catch(function (error) {
        console.error(error);
        if (typeof Swal !== "undefined") {
          Swal.fire({
            icon: "error",
            title: isArabic ? "خطأ" : "Error",
            text: isArabic ? "حدث خطأ في الاتصال بالخادم." : "Connection error.",
            confirmButtonColor: "#175cdd"
          });
        } else {
          alert("An error occurred.");
        }
      });
    };

    function reloadTableOrPage() {
      const apptsContainer = document.getElementById("appointments-table-container");
      if (apptsContainer) {
        const activeLink = document.querySelector(".appointments-ajax-link");
        const fetchUrl = activeLink ? activeLink.href : window.location.href;
        fetch(fetchUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } })
          .then(function (res) { return res.text(); })
          .then(function (html) { apptsContainer.innerHTML = html; });
      } else {
        const patientApptsContainer = document.getElementById("patient-appointments-container");
        if (patientApptsContainer) {
          const activeLink = patientApptsContainer.querySelector(".dashboard-ajax-link");
          const fetchUrl = activeLink ? activeLink.href : window.location.href;
          fetch(fetchUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } })
            .then(function (res) { return res.text(); })
            .then(function (html) { patientApptsContainer.innerHTML = html; });
        } else {
          window.location.reload();
        }
      }
    }

    if (typeof Swal !== "undefined") {
      Swal.fire({
        title: titleText,
        text: alertMsg,
        icon: isDecline ? "warning" : "question",
        showCancelButton: true,
        confirmButtonColor: confirmBtnColor,
        cancelButtonColor: "#6c757d",
        confirmButtonText: confirmBtnText,
        cancelButtonText: isArabic ? "إلغاء" : "Cancel"
      }).then(function (result) {
        if (result.isConfirmed) {
          performAction();
        }
      });
    } else {
      if (confirm(alertMsg)) {
        performAction();
      }
    }
  });

  // ════════════════════════════════════════════════════════════
  // لوحة التلميح القياسية — STANDARD GLASSMORPHIC TOOLTIP SYSTEM
  // ════════════════════════════════════════════════════════════
  
  // 1. Floating Glass Tooltip Container (For SVG and Special Elements)
  let floatingTooltipEl = document.getElementById('app-global-glass-tooltip');
  if (!floatingTooltipEl) {
    floatingTooltipEl = document.createElement('div');
    floatingTooltipEl.id = 'app-global-glass-tooltip';
    document.body.appendChild(floatingTooltipEl);
  }

  // 2. Scan and convert HTML title attributes to standard CSS data-tooltip
  window.initCustomTooltips = function(root) {
    const scope = root || document;
    const elements = scope.querySelectorAll('[title]');
    elements.forEach(function (el) {
      // If inside SVG, we handle via floating tooltip
      if (el.ownerSVGElement || el.tagName.toLowerCase() === 'svg' || el.closest('svg')) {
        const title = el.getAttribute('title');
        if (title && title.trim()) {
          el.setAttribute('data-glass-tooltip', title.trim());
          el.removeAttribute('title');
        }
        return;
      }
      const title = el.getAttribute('title');
      if (title && title.trim()) {
        el.setAttribute('data-tooltip', title.trim());
        el.removeAttribute('title');
      }
    });

    // Strip SVG <title> child tags to eliminate OS native black tooltips
    scope.querySelectorAll('svg title').forEach(function(titleTag) {
      const parent = titleTag.parentElement;
      if (parent) {
        const txt = titleTag.textContent.trim();
        if (txt && !parent.getAttribute('data-glass-tooltip')) {
          parent.setAttribute('data-glass-tooltip', txt);
        }
      }
      titleTag.remove();
    });
  };

  // Run initial tooltips parsing
  window.initCustomTooltips();

  const toothTypeMapAr = {
    'Third Molar': 'ضرس العقل',
    'Second Molar': 'رحى ثانية',
    'First Molar': 'رحى أولى',
    'Second Premolar': 'ضاحك ثاني',
    'First Premolar': 'ضاحك أول',
    'Canine': 'ناب',
    'Lateral Incisor': 'قاطع جانبي',
    'Central Incisor': 'قاطع مركزي'
  };

  function getLocalizedToothTitle(rawText) {
    if (!rawText) return '';
    let text = rawText.trim();
    const isArabic = document.documentElement.lang === 'ar' || document.documentElement.dir === 'rtl' || !document.body.classList.contains('lang-en');
    if (isArabic) {
      text = text.replace(/^Tooth\s+/i, 'السن ');
      for (const [en, ar] of Object.entries(toothTypeMapAr)) {
        text = text.replace(new RegExp(en, 'g'), ar);
      }
    }
    return text;
  }

  // 3. Universal Dynamic Delegation for both HTML elements and SVG Teeth
  document.addEventListener('mouseover', function (e) {
    // A. Check for SVG tooth or element with data-glass-tooltip
    const svgTarget = e.target.closest('svg .vector-tooth-item, svg .tooth-wrapper, svg .p-tooth-item, svg .tooth-btn, svg [data-tooth], svg [data-fdi], [data-glass-tooltip]');
    if (svgTarget) {
      // Check if there's any stray <title> tag
      const titleTag = svgTarget.querySelector('title');
      if (titleTag) {
        svgTarget.setAttribute('data-glass-tooltip', titleTag.textContent.trim());
        titleTag.remove();
      }
      const rawText = svgTarget.getAttribute('data-glass-tooltip') || svgTarget.getAttribute('data-tooltip');
      if (rawText && floatingTooltipEl) {
        floatingTooltipEl.textContent = getLocalizedToothTitle(rawText);
        const rect = svgTarget.getBoundingClientRect();
        const top = rect.top;
        const left = rect.left + rect.width / 2;
        floatingTooltipEl.style.top = `${top}px`;
        floatingTooltipEl.style.left = `${left}px`;
        floatingTooltipEl.classList.add('show');
        return;
      }
    }


    // B. Check for standard HTML element with title
    const htmlTarget = e.target.closest('[title]');
    if (htmlTarget) {
      const title = htmlTarget.getAttribute('title');
      if (title && title.trim()) {
        htmlTarget.setAttribute('data-tooltip', title.trim());
        htmlTarget.removeAttribute('title');
      }
    }
  }, { passive: true });

  document.addEventListener('mouseout', function (e) {
    const svgTarget = e.target.closest('svg .vector-tooth-item, svg .tooth-wrapper, svg .p-tooth-item, svg .tooth-btn, svg [data-tooth], svg [data-fdi], [data-glass-tooltip]');
    if (svgTarget && floatingTooltipEl) {
      floatingTooltipEl.classList.remove('show');
    }
  }, { passive: true });


  // Universal Smooth Scroll to Top of Table on Pagination Click
  window.scrollToTableTop = function(triggerEl) {
    let target = null;
    if (triggerEl) {
      target = triggerEl.closest('#appointments-table-container, #patients-table-container, #invoices-table-container, #payments-table-container, #patient-appointments-container, #patient-invoices-container, #patient-payments-table-container, #patient-treatments-table-container, .appointments-table-wrapper, .table-responsive, .table-card, section, table');
    }
    if (!target) {
      target = document.querySelector('.appointments-table-wrapper, .table-responsive, table');
    }
    if (target) {
      const yOffset = -90;
      const y = target.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    }
  };

  document.addEventListener('click', function(e) {
    const pageLink = e.target.closest('.page-link, .pagination a, [class*="-pagination"] a, .appointments-ajax-link, .patients-ajax-link, .invoices-ajax-link, .payments-ajax-link, .dashboard-ajax-link');
    if (pageLink && (pageLink.classList.contains('page-link') || pageLink.closest('.pagination') || (pageLink.href && pageLink.href.includes('page=')))) {
      window.scrollToTableTop(pageLink);
    }
  });
});