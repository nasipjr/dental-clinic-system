
# -*- coding: utf-8 -*-
# Generates install_guide.html - Full USB installation guide for Dental Clinic MS

parts = []

parts.append("""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>دليل التثبيت الكامل - من الفلاشة للتشغيل</title>
<style>
@import url("https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&display=swap");
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:"Cairo",sans-serif;background:#0f172a;color:#e2e8f0;line-height:1.75;font-size:14px;}
.hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0d6efd 100%);padding:70px 40px;text-align:center;position:relative;overflow:hidden;border-bottom:3px solid #0d6efd;}
.hero::before{content:'';position:absolute;width:600px;height:600px;background:radial-gradient(circle,rgba(13,110,253,0.2) 0%,transparent 70%);top:-100px;right:-100px;border-radius:50%;}
.hero-badge{display:inline-block;background:rgba(13,110,253,0.3);border:1px solid rgba(13,110,253,0.6);border-radius:50px;padding:6px 20px;font-size:12px;font-weight:700;color:#60d0ff;margin-bottom:20px;letter-spacing:1px;}
.hero h1{font-size:2.8rem;font-weight:900;margin-bottom:12px;color:#fff;text-shadow:0 2px 20px rgba(0,0,0,0.5);}
.hero h2{font-size:1.1rem;font-weight:400;color:rgba(255,255,255,0.7);max-width:600px;margin:0 auto 30px;}
.hero-steps{display:flex;justify-content:center;gap:0;margin-top:30px;flex-wrap:wrap;}
.hs{background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);padding:12px 20px;font-size:12px;font-weight:700;color:rgba(255,255,255,0.9);}
.hs:first-child{border-radius:10px 0 0 10px;}
.hs:last-child{border-radius:0 10px 10px 0;}
.hs-arrow{background:rgba(13,110,253,0.4);padding:12px 8px;color:#60d0ff;font-size:16px;display:flex;align-items:center;}
.container{max-width:960px;margin:0 auto;padding:50px 40px;}

/* Progress nav */
.progress-nav{background:#1e293b;border-bottom:1px solid #334155;padding:15px 40px;position:sticky;top:0;z-index:100;display:flex;gap:6px;flex-wrap:wrap;justify-content:center;}
.pn{padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;cursor:pointer;border:1px solid #334155;color:#94a3b8;background:#0f172a;transition:all 0.2s;}
.pn:hover,.pn.active{background:#0d6efd;color:#fff;border-color:#0d6efd;}

/* Section */
.section{margin-bottom:60px;}
.sec-header{display:flex;align-items:center;gap:15px;margin-bottom:25px;padding-bottom:15px;border-bottom:2px solid #334155;}
.sec-icon{width:50px;height:50px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;}
.sec-icon.blue{background:linear-gradient(135deg,#0d6efd,#0066cc);}
.sec-icon.green{background:linear-gradient(135deg,#16a34a,#15803d);}
.sec-icon.orange{background:linear-gradient(135deg,#f59e0b,#d97706);}
.sec-icon.purple{background:linear-gradient(135deg,#7c3aed,#6d28d9);}
.sec-icon.red{background:linear-gradient(135deg,#dc2626,#b91c1c);}
.sec-icon.teal{background:linear-gradient(135deg,#0f9488,#0d8080);}
.sec-header h2{font-size:1.5rem;font-weight:800;color:#f1f5f9;}
.sec-header p{font-size:13px;color:#64748b;margin-top:3px;}
.sec-num{font-size:11px;font-weight:700;color:#0d6efd;letter-spacing:2px;margin-bottom:3px;}

/* Steps */
.steps{position:relative;padding-right:55px;}
.steps::before{content:'';position:absolute;right:22px;top:30px;bottom:30px;width:2px;background:linear-gradient(to bottom,#0d6efd,#7c3aed,#16a34a);opacity:0.4;}
.step{position:relative;margin-bottom:30px;}
.step-num{position:absolute;right:-55px;top:0;width:44px;height:44px;background:linear-gradient(135deg,#0d6efd,#0066cc);border-radius:50%;color:#fff;font-weight:900;font-size:16px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 4px #0f172a,0 0 0 6px rgba(13,110,253,0.4);}
.step-body{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:22px 25px;}
.step-body h3{font-size:1.05rem;font-weight:800;color:#f1f5f9;margin-bottom:10px;}
.step-body p{font-size:13px;color:#94a3b8;margin-bottom:10px;}
.step-body ul{padding-right:20px;margin-bottom:10px;}
.step-body ul li{font-size:13px;color:#94a3b8;margin-bottom:6px;}
.step-body ul li strong{color:#e2e8f0;}
.step-body.success{border-color:#16a34a;background:linear-gradient(135deg,#1e293b,#14532d22);}
.step-body.warning{border-color:#f59e0b;background:linear-gradient(135deg,#1e293b,#78350f22);}
.step-body.info{border-color:#0d6efd;background:linear-gradient(135deg,#1e293b,#1e3a5f44);}

/* CMD */
.cmd{background:#020617;border:1px solid #1e293b;border-radius:10px;padding:16px 20px;margin:12px 0;font-family:'Courier New',monospace;font-size:13px;direction:ltr;text-align:left;overflow-x:auto;position:relative;}
.cmd-label{font-size:10px;color:#475569;font-family:'Cairo',sans-serif;margin-bottom:8px;direction:rtl;text-align:right;font-weight:700;}
.cmd .c{color:#475569;}
.cmd .k{color:#60d0ff;}
.cmd .s{color:#a3e635;}
.cmd .p{color:#f59e0b;}
.cmd .ok{color:#4ade80;}

/* Cards */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px;margin:20px 0;}
.card{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:18px;}
.card h4{font-size:0.95rem;font-weight:700;color:#f1f5f9;margin-bottom:6px;}
.card p{font-size:12.5px;color:#64748b;}
.card.featured{border-color:#0d6efd;background:linear-gradient(135deg,#1e293b,#1e3a5f);}
.card.green{border-color:#16a34a;background:linear-gradient(135deg,#1e293b,#14532d22);}
.card.orange{border-color:#f59e0b;background:linear-gradient(135deg,#1e293b,#78350f22);}

/* Download buttons */
.dl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:15px;margin:20px 0;}
.dl-card{background:#1e293b;border:1px solid #334155;border-radius:14px;padding:20px;display:flex;align-items:center;gap:15px;}
.dl-icon{width:50px;height:50px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;}
.dl-icon.python{background:linear-gradient(135deg,#3b82f6,#1d4ed8);}
.dl-icon.xampp{background:linear-gradient(135deg,#f97316,#c2410c);}
.dl-icon.git{background:linear-gradient(135deg,#f43f5e,#be123c);}
.dl-icon.browser{background:linear-gradient(135deg,#10b981,#059669);}
.dl-info h4{font-size:0.95rem;font-weight:800;color:#f1f5f9;margin-bottom:3px;}
.dl-info p{font-size:12px;color:#64748b;}
.dl-info .size{font-size:11px;color:#0d6efd;font-weight:700;margin-top:4px;}
.dl-info .required{font-size:10px;font-weight:800;color:#f43f5e;background:rgba(244,63,94,0.15);padding:1px 8px;border-radius:10px;}
.dl-info .optional{font-size:10px;font-weight:800;color:#64748b;background:rgba(100,116,139,0.15);padding:1px 8px;border-radius:10px;}

/* USB visual */
.usb-layout{background:#020617;border:2px solid #1e293b;border-radius:16px;padding:25px;margin:20px 0;}
.usb-title{font-size:12px;font-weight:700;color:#64748b;margin-bottom:15px;display:flex;align-items:center;gap:8px;}
.folder{margin-bottom:8px;}
.folder-name{font-size:13px;font-weight:700;color:#f59e0b;font-family:'Courier New',monospace;display:flex;align-items:center;gap:8px;}
.folder-name::before{content:'📁';}
.folder-files{margin-right:25px;margin-top:5px;}
.file-item{font-size:12px;color:#64748b;font-family:'Courier New',monospace;padding:3px 0;display:flex;align-items:center;gap:8px;}
.file-item.green{color:#4ade80;}
.file-item.blue{color:#60a5fa;}
.file-item.yellow{color:#fbbf24;}

/* Alert boxes */
.alert{border-radius:14px;padding:18px 22px;margin:18px 0;border-right:4px solid;display:flex;gap:15px;align-items:flex-start;}
.alert-icon{font-size:22px;flex-shrink:0;margin-top:2px;}
.alert-body h4{font-weight:700;margin-bottom:5px;font-size:0.95rem;}
.alert-body p,.alert-body li{font-size:13px;}
.alert.danger{background:rgba(220,38,38,0.1);border-color:#dc2626;}.alert.danger h4{color:#fca5a5;}
.alert.success{background:rgba(22,163,74,0.1);border-color:#16a34a;}.alert.success h4{color:#86efac;}
.alert.warning{background:rgba(245,158,11,0.1);border-color:#f59e0b;}.alert.warning h4{color:#fcd34d;}
.alert.info{background:rgba(13,110,253,0.1);border-color:#0d6efd;}.alert.info h4{color:#93c5fd;}
.alert ul{padding-right:20px;margin-top:5px;}
.alert ul li{margin-bottom:4px;color:#94a3b8;}

/* Table */
table{width:100%;border-collapse:collapse;margin:20px 0;font-size:13px;}
th{background:#1e293b;color:#f1f5f9;padding:12px 16px;text-align:right;font-weight:700;border-bottom:2px solid #0d6efd;}
td{padding:10px 16px;border-bottom:1px solid #1e293b;color:#94a3b8;}
tr:hover td{background:#1e293b44;}

/* Badge */
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700;}
.badge.green{background:#14532d;color:#4ade80;}
.badge.red{background:#450a0a;color:#f87171;}
.badge.blue{background:#1e3a5f;color:#60a5fa;}
.badge.orange{background:#431407;color:#fb923c;}

/* Final success */
.success-final{background:linear-gradient(135deg,#14532d,#15803d22);border:2px solid #16a34a;border-radius:20px;padding:35px;text-align:center;margin-top:40px;}
.success-final h2{font-size:2rem;font-weight:900;color:#4ade80;margin-bottom:10px;}
.success-final p{color:#86efac;font-size:15px;}

/* Divider */
.divider{height:1px;background:linear-gradient(to right,transparent,#334155,transparent);margin:50px 0;}

footer{background:#020617;border-top:1px solid #1e293b;text-align:center;padding:25px;color:#475569;font-size:12px;}

@media print{body{background:#fff;color:#000;}.hero{background:#0f172a!important;-webkit-print-color-adjust:exact;print-color-adjust:exact;}.progress-nav{display:none;}}
</style>
</head>
<body>""")

parts.append("""
<div class="hero">
  <div class="hero-badge">💾 دليل التثبيت الكامل من الفلاشة</div>
  <h1>🖥️ من لابتوب فارغ إلى عيادة جاهزة</h1>
  <h2>دليل خطوة بخطوة لتثبيت نظام إدارة العيادة من صفر كامل</h2>
  <div class="hero-steps">
    <div class="hs">📋 تجهيز الفلاشة</div>
    <div class="hs-arrow">→</div>
    <div class="hs">⬇️ تثبيت البرامج</div>
    <div class="hs-arrow">→</div>
    <div class="hs">🗄️ إعداد قاعدة البيانات</div>
    <div class="hs-arrow">→</div>
    <div class="hs">⚙️ تهيئة النظام</div>
    <div class="hs-arrow">→</div>
    <div class="hs">🚀 أول تشغيل</div>
  </div>
</div>

<nav class="progress-nav">
  <div class="pn">💾 الفلاشة</div>
  <div class="pn">⬇️ البرامج</div>
  <div class="pn">🗄️ MySQL</div>
  <div class="pn">🐍 Python</div>
  <div class="pn">⚙️ إعداد .env</div>
  <div class="pn">🚀 التشغيل</div>
  <div class="pn">👤 Admin</div>
  <div class="pn">✅ تأكيد</div>
</nav>""")

parts.append("""
<div class="container">

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 0 — ما تحتاجه قبل البدء                  -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon orange">📋</div>
    <div><div class="sec-num">قبل البدء</div><h2>ما تحتاجه لهذه العملية</h2><p>تجهيز كل شيء قبل الذهاب للعيادة</p></div>
  </div>

  <div class="cards">
    <div class="card green">
      <h4>💾 فلاشة 8 GB+</h4>
      <p>لنسخ ملفات البرامج والمشروع عليها مسبقاً قبل الذهاب للعيادة.</p>
    </div>
    <div class="card featured">
      <h4>💻 لابتوب العيادة</h4>
      <p>Windows 10 أو 11. لا يحتاج أي شيء مثبت مسبقاً.</p>
    </div>
    <div class="card orange">
      <h4>🌐 اتصال إنترنت (اختياري)</h4>
      <p>لو ما عندك إنترنت في العيادة، حمّل كل البرامج على الفلاشة مسبقاً من بيتك.</p>
    </div>
  </div>

  <div class="alert info">
    <div class="alert-icon">💡</div>
    <div class="alert-body">
      <h4>الخطة الذكية — حمّل كل شيء على الفلاشة مسبقاً</h4>
      <ul>
        <li>من بيتك، حمّل كل ملفات التثبيت المطلوبة</li>
        <li>انسخ مجلد المشروع على الفلاشة</li>
        <li>اذهب للعيادة والفلاشة عندك كل شيء — لا تحتاج إنترنت</li>
      </ul>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 1 — تجهيز الفلاشة                        -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon orange">💾</div>
    <div><div class="sec-num">الخطوة الأولى</div><h2>تجهيز الفلاشة — من جهازك قبل الذهاب</h2><p>ما تحمّله وكيف ترتب الفلاشة</p></div>
  </div>

  <div class="alert success">
    <div class="alert-icon">✅</div>
    <div class="alert-body">
      <h4>البرامج التي ستحملها على الفلاشة (من بيتك)</h4>
      <ul>
        <li><strong>Python 3.12</strong> — python.org/downloads — ملف .exe حجمه ~27 MB</li>
        <li><strong>XAMPP</strong> — apachefriends.org — ملف .exe حجمه ~170 MB</li>
        <li><strong>مجلد المشروع كاملاً</strong> — Dental Clinic MS Flask</li>
        <li><strong>هذا الملف HTML</strong> — دليل التثبيت معك</li>
      </ul>
    </div>
  </div>

  <div class="dl-grid">
    <div class="dl-card">
      <div class="dl-icon python">🐍</div>
      <div class="dl-info">
        <h4>Python 3.12.x</h4>
        <p>اللغة الأساسية للنظام</p>
        <div class="size">python.org/downloads — ~27 MB</div>
        <span class="required">مطلوب</span>
      </div>
    </div>
    <div class="dl-card">
      <div class="dl-icon xampp">🐬</div>
      <div class="dl-info">
        <h4>XAMPP (MySQL + phpMyAdmin)</h4>
        <p>قاعدة البيانات وأداة إدارتها</p>
        <div class="size">apachefriends.org — ~170 MB</div>
        <span class="required">مطلوب</span>
      </div>
    </div>
    <div class="dl-card">
      <div class="dl-icon git">📁</div>
      <div class="dl-info">
        <h4>مجلد المشروع (Dental Clinic MS Flask)</h4>
        <p>انسخ المجلد كاملاً من جهازك على الفلاشة</p>
        <div class="size">مجلد المشروع كاملاً</div>
        <span class="required">مطلوب</span>
      </div>
    </div>
    <div class="dl-card">
      <div class="dl-icon browser">📋</div>
      <div class="dl-info">
        <h4>هذا الدليل (install_guide.html)</h4>
        <p>اجعله معك على الفلاشة للمرجعية</p>
        <div class="size">ملف HTML واحد</div>
        <span class="optional">اختياري لكن مفيد</span>
      </div>
    </div>
  </div>

  <h3 style="color:#f1f5f9;margin-bottom:15px;margin-top:25px;">📁 هيكل الفلاشة المقترح</h3>
  <div class="usb-layout">
    <div class="usb-title">💾 USB Flash Drive (F:\\)</div>

    <div class="folder">
      <div class="folder-name" style="color:#fbbf24;font-size:14px;">USB_Flash (F:\\)</div>
      <div class="folder-files">

        <div class="folder" style="margin-top:8px;">
          <div class="folder-name">01_برامج_التثبيت</div>
          <div class="folder-files">
            <div class="file-item green">📄 python-3.12.x-amd64.exe</div>
            <div class="file-item orange">📄 xampp-windows-x64-8.x.x-installer.exe</div>
          </div>
        </div>

        <div class="folder" style="margin-top:8px;">
          <div class="folder-name">02_المشروع</div>
          <div class="folder-files">
            <div class="folder-name" style="color:#60a5fa;font-size:13px;">📁 Dental Clinic MS Flask</div>
            <div class="folder-files" style="margin-right:20px;">
              <div class="file-item blue">📄 app.py</div>
              <div class="file-item blue">📄 models.py</div>
              <div class="file-item blue">📄 settings.py</div>
              <div class="file-item blue">📄 requirements.txt</div>
              <div class="file-item yellow">📄 .env.example</div>
              <div class="file-item green">📁 routes/</div>
              <div class="file-item green">📁 templates/</div>
              <div class="file-item green">📁 static/</div>
              <div class="file-item green">📁 utils/</div>
            </div>
          </div>
        </div>

        <div class="folder" style="margin-top:8px;">
          <div class="folder-name">03_الدليل</div>
          <div class="folder-files">
            <div class="file-item green">📄 install_guide.html ← هذا الملف</div>
            <div class="file-item green">📄 dental_clinic_guide.html</div>
          </div>
        </div>

      </div>
    </div>
  </div>

  <div class="alert warning">
    <div class="alert-icon">⚠️</div>
    <div class="alert-body">
      <h4>ملاحظة مهمة عند نسخ المشروع</h4>
      <ul>
        <li>انسخ مجلد المشروع كاملاً بما فيه: app.py, models.py, routes/, templates/, static/, utils/, requirements.txt</li>
        <li>لا تنسخ مجلد <strong>venv/</strong> (البيئة الافتراضية) — سنعيد إنشاءها في العيادة</li>
        <li>لا تنسخ مجلد <strong>instance/</strong> — فيه قاعدة البيانات القديمة</li>
        <li>انسخ ملف <strong>.env.example</strong> وستعدّله في العيادة</li>
      </ul>
    </div>
  </div>

  <h3 style="color:#f1f5f9;margin:20px 0 12px;">📦 كيف تنسخ المشروع على الفلاشة</h3>
  <div class="cmd">
    <div class="cmd-label">من جهازك (Windows Explorer أو Command Prompt)</div>
<span class="c"># افتح File Explorer</span>
<span class="c"># اذهب لمجلد المشروع:</span>
<span class="s">C:\\Users\\Windows.11\\Desktop\\Dental Clinic MS Flask</span>

<span class="c"># انقر بزر اليمين على المجلد → Copy</span>
<span class="c"># افتح الفلاشة → مجلد 02_المشروع → Paste</span>

<span class="c"># أو بالأوامر (PowerShell):</span>
<span class="k">xcopy</span> <span class="s">"C:\\Users\\Windows.11\\Desktop\\Dental Clinic MS Flask"</span> <span class="s">"F:\\02_المشروع\\Dental Clinic MS Flask"</span> /E /I /EXCLUDE:exclude.txt
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 2 — في العيادة: تثبيت Python             -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon blue">🐍</div>
    <div><div class="sec-num">خطوة 1 من 6</div><h2>تثبيت Python</h2><p>اللغة الأساسية للنظام — أول شيء تثبته</p></div>
  </div>

  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body info">
        <h3>🔌 صل الفلاشة بلابتوب العيادة</h3>
        <p>افتح الفلاشة من File Explorer. اذهب لمجلد <strong>01_برامج_التثبيت</strong></p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body">
        <h3>📦 شغّل ملف Python</h3>
        <p>انقر مزدوج على: <code style="color:#60d0ff;background:#020617;padding:2px 8px;border-radius:4px;">python-3.12.x-amd64.exe</code></p>
        <p>ستظهر نافذة التثبيت. <strong style="color:#f43f5e;">قبل أي شيء</strong> افعل التالي:</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body warning">
        <h3>☑️ ضع علامة على "Add Python to PATH" — مهم جداً!</h3>
        <p>في أسفل نافذة التثبيت ستجد خيارين:</p>
        <ul>
          <li>☑️ <strong>"Add Python 3.12 to PATH"</strong> ← ضع علامة هنا أولاً</li>
          <li>☑️ <strong>"Use admin privileges when installing py.exe"</strong></li>
        </ul>
        <p style="margin-top:10px;color:#fcd34d;font-weight:700;">⚠️ إذا نسيت هذا الخيار، Python لن يعمل من Command Prompt وستحتاج إعادة التثبيت!</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">4</div>
      <div class="step-body">
        <h3>▶️ اضغط "Install Now"</h3>
        <p>انتظر اكتمال التثبيت (~2 دقيقة). اضغط "Close" عند الانتهاء.</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">5</div>
      <div class="step-body success">
        <h3>✅ تحقق من نجاح التثبيت</h3>
        <p>افتح Command Prompt: اضغط <strong>Win+R</strong> ← اكتب <strong>cmd</strong> ← Enter</p>
        <div class="cmd">
<span class="k">python</span> --version
<span class="ok"># النتيجة المتوقعة: Python 3.12.x</span>

<span class="k">pip</span> --version
<span class="ok"># النتيجة المتوقعة: pip 24.x.x from ...</span>
        </div>
        <p style="color:#86efac;">إذا ظهرت الأرقام = Python مثبت بنجاح ✅</p>
      </div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 3 — تثبيت XAMPP                          -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon orange">🗄️</div>
    <div><div class="sec-num">خطوة 2 من 6</div><h2>تثبيت XAMPP (قاعدة البيانات)</h2><p>يحتوي على MySQL و phpMyAdmin</p></div>
  </div>

  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body">
        <h3>📦 شغّل ملف XAMPP</h3>
        <p>انقر مزدوج على: <code style="color:#fb923c;background:#020617;padding:2px 8px;border-radius:4px;">xampp-windows-x64-8.x.x-installer.exe</code></p>
        <p>اقبل كل الإعدادات الافتراضية. اضغط Next → Next → Next → Install</p>
        <p style="color:#64748b;">مجلد التثبيت الافتراضي: <strong style="color:#fb923c;">C:\\xampp</strong> — ابقه كما هو</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body">
        <h3>⏳ انتظر اكتمال التثبيت</h3>
        <p>يأخذ 3-5 دقائق. عند الانتهاء سيسألك "Do you want to start XAMPP Control Panel now?" → اضغط <strong>Yes</strong></p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body info">
        <h3>▶️ تشغيل MySQL من XAMPP Control Panel</h3>
        <p>في نافذة XAMPP Control Panel:</p>
        <ul>
          <li>ابحث عن سطر <strong>"MySQL"</strong></li>
          <li>اضغط زر <strong>"Start"</strong> بجانبه</li>
          <li>انتظر حتى يتحول لون المربع للأخضر ✅</li>
          <li>لا تشغل Apache — النظام لا يحتاجه</li>
        </ul>
        <p style="color:#93c5fd;margin-top:10px;">💡 MySQL الآن يعمل على البورت 3306 أو 3308</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">4</div>
      <div class="step-body success">
        <h3>✅ تحقق من تشغيل MySQL</h3>
        <p>افتح المتصفح (Chrome أو Edge) واكتب:</p>
        <div class="cmd">
http://localhost/phpmyadmin
        </div>
        <p style="color:#86efac;">إذا فتحت صفحة phpMyAdmin زرقاء = MySQL يعمل بنجاح ✅</p>
        <p style="color:#64748b;margin-top:8px;">اسم المستخدم الافتراضي: <strong style="color:#fbbf24;">root</strong> / كلمة المرور: <strong style="color:#fbbf24;">فارغة</strong></p>
      </div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 4 — إنشاء قاعدة البيانات                 -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon green">🏗️</div>
    <div><div class="sec-num">خطوة 3 من 6</div><h2>إنشاء قاعدة البيانات</h2><p>في phpMyAdmin — يستغرق دقيقة واحدة</p></div>
  </div>

  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body">
        <h3>🌐 افتح phpMyAdmin في المتصفح</h3>
        <div class="cmd">http://localhost/phpmyadmin</div>
        <p>اضغط Enter وستفتح الصفحة الزرقاء</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body">
        <h3>➕ إنشاء قاعدة بيانات جديدة</h3>
        <ul>
          <li>في القائمة اليسرى اضغط <strong>"New"</strong> (باللون الأزرق)</li>
          <li>في حقل "Database name" اكتب بالضبط: <code style="color:#4ade80;background:#020617;padding:2px 8px;border-radius:4px;font-size:14px;">dental_clinic</code></li>
          <li>من القائمة المنسدلة بجانبه اختر: <strong>utf8mb4_unicode_ci</strong></li>
          <li>اضغط زر <strong>"Create"</strong></li>
        </ul>
      </div>
    </div>

    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body success">
        <h3>✅ النجاح</h3>
        <p>ستظهر رسالة "Database dental_clinic has been created" ← ممتاز!</p>
        <p style="color:#86efac;">قاعدة البيانات جاهزة الآن. الجداول ستُنشأ تلقائياً عند أول تشغيل للبرنامج.</p>
      </div>
    </div>
  </div>

  <div class="alert warning">
    <div class="alert-icon">⚠️</div>
    <div class="alert-body">
      <h4>تحقق من رقم بورت MySQL</h4>
      <ul>
        <li>في XAMPP Control Panel اضغط "Config" بجانب MySQL</li>
        <li>افتح my.ini وابحث عن: <strong>port=</strong></li>
        <li>إذا كانت القيمة <strong>3306</strong> → ستضع 3306 في ملف .env</li>
        <li>إذا كانت <strong>3308</strong> → ستضع 3308 في ملف .env</li>
        <li>الافتراضي في XAMPP هو <strong>3306</strong></li>
      </ul>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 5 — نسخ المشروع وإعداده                  -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon purple">📁</div>
    <div><div class="sec-num">خطوة 4 من 6</div><h2>نسخ المشروع وإعداد البيئة</h2><p>من الفلاشة للابتوب وتثبيت المكتبات</p></div>
  </div>

  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body">
        <h3>📋 انسخ مجلد المشروع من الفلاشة</h3>
        <ul>
          <li>افتح الفلاشة → مجلد <strong>02_المشروع</strong></li>
          <li>انقر بزر اليمين على مجلد <strong>"Dental Clinic MS Flask"</strong> → Copy</li>
          <li>اذهب لـ <strong>C:\\</strong> أو سطح المكتب</li>
          <li>انقر بزر اليمين → Paste</li>
        </ul>
        <p style="color:#64748b;margin-top:8px;">📌 مثال: ضعه في <code style="color:#60d0ff;background:#020617;padding:2px 6px;border-radius:4px;">C:\\ClinicApp\\</code></p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body info">
        <h3>⚙️ إنشاء ملف .env من المثال</h3>
        <ul>
          <li>داخل مجلد المشروع ابحث عن ملف <strong>.env.example</strong></li>
          <li>انقر بزر اليمين عليه → Copy</li>
          <li>Paste في نفس المجلد</li>
          <li>انقر بزر اليمين على النسخة الجديدة → Rename → اسمه: <strong>.env</strong> (بدون example)</li>
        </ul>
        <p style="color:#64748b;margin-top:8px;">💡 إذا Windows يرفض الاسم بدون امتداد: افتحه بـ Notepad وسمّيه .env عند الحفظ</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body warning">
        <h3>✏️ تعديل ملف .env</h3>
        <p>افتح ملف .env بـ Notepad (انقر بزر اليمين → Open with → Notepad)</p>
        <p>عدّل هذه القيم:</p>
        <div class="cmd">
<span class="c"># بيانات قاعدة البيانات</span>
<span class="k">DB_USER</span>=root
<span class="k">DB_PASSWORD</span>=          <span class="c"># اتركها فارغة إذا XAMPP بدون كلمة مرور</span>
<span class="k">DB_HOST</span>=127.0.0.1
<span class="k">DB_PORT</span>=<span class="s">3306</span>          <span class="c"># أو 3308 حسب ما وجدت في my.ini</span>
<span class="k">DB_NAME</span>=dental_clinic

<span class="c"># مفتاح الأمان — عدّله لأي نص عشوائي طويل</span>
<span class="k">SECRET_KEY</span>=<span class="s">clinic-secret-key-2025-change-this-now</span>
        </div>
        <p style="color:#fcd34d;margin-top:8px;">احفظ الملف: Ctrl+S</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">4</div>
      <div class="step-body">
        <h3>💻 افتح Command Prompt في مجلد المشروع</h3>
        <p>الطريقة السهلة:</p>
        <ul>
          <li>افتح مجلد المشروع في File Explorer</li>
          <li>في شريط العنوان (address bar) أعلى النافذة — امسح النص واكتب: <code style="color:#60d0ff;background:#020617;padding:2px 8px;border-radius:4px;">cmd</code></li>
          <li>اضغط Enter — سيفتح Command Prompt في نفس المجلد مباشرة ✅</li>
        </ul>
      </div>
    </div>

    <div class="step">
      <div class="step-num">5</div>
      <div class="step-body">
        <h3>🌐 إنشاء البيئة الافتراضية</h3>
        <div class="cmd">
<span class="c"># تأكد إنك داخل مجلد المشروع</span>
<span class="k">python</span> -m venv venv

<span class="ok"># ستظهر رسالة وسيُنشأ مجلد venv/</span>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-num">6</div>
      <div class="step-body">
        <h3>⚡ تفعيل البيئة الافتراضية</h3>
        <div class="cmd">
<span class="c"># على Windows:</span>
venv<span class="p">\\</span>Scripts<span class="p">\\</span>activate

<span class="ok"># ستظهر (venv) في بداية السطر — هذا يعني إنها فعّالة</span>
<span class="ok"># مثال: (venv) C:\\ClinicApp\\Dental Clinic MS Flask></span>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-num">7</div>
      <div class="step-body info">
        <h3>📦 تثبيت مكتبات Python</h3>
        <p>هذا قد يستغرق 5-10 دقائق حسب سرعة الإنترنت (أو من الفلاشة إذا حملتها مسبقاً)</p>
        <div class="cmd">
pip install -r requirements.txt

<span class="ok"># ستبدأ تظهر رسائل التثبيت...</span>
<span class="ok"># Successfully installed Flask... SQLAlchemy... PyMySQL...</span>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-num">8</div>
      <div class="step-body success">
        <h3>✅ تحقق من نجاح التثبيت</h3>
        <div class="cmd">
<span class="k">python</span> -m py_compile app.py
<span class="ok"># لا يجب أن تظهر أي رسالة خطأ — هذا يعني إن الكود سليم</span>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 6 — أول تشغيل                            -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon green">🚀</div>
    <div><div class="sec-num">خطوة 5 من 6</div><h2>أول تشغيل للنظام</h2><p>اللحظة الكبيرة — إنشاء الجداول والتحقق</p></div>
  </div>

  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body">
        <h3>▶️ شغّل البرنامج</h3>
        <p>تأكد إن Command Prompt ما زال في مجلد المشروع وإن <strong>(venv)</strong> ظاهرة</p>
        <div class="cmd">
python app.py
        </div>
        <p>ستبدأ تظهر رسائل التشغيل...</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body success">
        <h3>✅ رسائل النجاح المتوقعة</h3>
        <div class="cmd">
<span class="ok">INFO - Application started successfully</span>
<span class="ok">* Running on http://127.0.0.1:5000</span>
<span class="ok">* Running on http://0.0.0.0:5000</span>
<span class="ok">Press CTRL+C to quit</span>
        </div>
        <p style="color:#86efac;">🎉 هذه الرسائل تعني إن كل شيء يعمل!</p>
        <p style="color:#64748b;margin-top:8px;">في أول تشغيل، البرنامج يُنشئ جميع الجداول في قاعدة البيانات تلقائياً.</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body">
        <h3>🌐 افتح البرنامج في المتصفح</h3>
        <p>افتح Chrome أو Edge واكتب:</p>
        <div class="cmd">
http://127.0.0.1:5000
        </div>
        <p>ستظهر صفحة تسجيل الدخول للنظام ✅</p>
      </div>
    </div>
  </div>

  <div class="alert danger">
    <div class="alert-icon">🔴</div>
    <div class="alert-body">
      <h4>إذا ظهرت رسالة خطأ عند التشغيل</h4>
      <ul>
        <li><strong>"Can't connect to MySQL server"</strong> → MySQL في XAMPP غير مشغل. افتح XAMPP Control Panel وشغّل MySQL</li>
        <li><strong>"Unknown database 'dental_clinic'"</strong> → لم تُنشئ قاعدة البيانات. ارجع لـ phpMyAdmin وأنشئها</li>
        <li><strong>"ModuleNotFoundError"</strong> → المكتبات لم تُثبَّت. نفّذ: pip install -r requirements.txt</li>
        <li><strong>"Port already in use"</strong> → هناك برنامج آخر يستخدم البورت 5000. أغلقه أو أعد تشغيل الكمبيوتر</li>
      </ul>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 7 — إعداد حساب Admin                     -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon red">👤</div>
    <div><div class="sec-num">خطوة 6 من 6</div><h2>إعداد الحساب وأول دخول</h2><p>تسجيل الدخول وتخصيص بيانات العيادة</p></div>
  </div>

  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body info">
        <h3>🔑 بيانات الدخول الافتراضية</h3>
        <p>عند أول تشغيل، النظام يُنشئ حساب Admin تلقائياً:</p>
        <table>
          <thead><tr><th>الحقل</th><th>القيمة</th></tr></thead>
          <tbody>
            <tr><td>اسم المستخدم / الإيميل</td><td><span style="color:#60d0ff;font-family:monospace;">admin@clinic.com</span></td></tr>
            <tr><td>كلمة المرور</td><td><span style="color:#60d0ff;font-family:monospace;">admin123</span></td></tr>
          </tbody>
        </table>
        <p style="color:#fcd34d;margin-top:10px;">⚠️ غيّر كلمة المرور فوراً بعد أول دخول!</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body">
        <h3>⚙️ إعداد بيانات العيادة</h3>
        <p>بعد الدخول اذهب لـ <strong>Settings (الإعدادات)</strong> وعدّل:</p>
        <ul>
          <li>اسم العيادة</li>
          <li>رقم الهاتف والعنوان</li>
          <li>ساعات العمل وأيام الراحة</li>
          <li>العملة المستخدمة</li>
          <li>اللغة (عربي/إنجليزي)</li>
          <li>اسم الطبيب وبياناته</li>
        </ul>
      </div>
    </div>

    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body success">
        <h3>🎉 النظام جاهز للاستخدام!</h3>
        <p>يمكنك الآن:</p>
        <ul>
          <li>إضافة أول مريض من قسم "Patients"</li>
          <li>إنشاء حسابات للطاقم الطبي من "Settings → Users"</li>
          <li>حجز أول موعد من "Calendar"</li>
          <li>استكشاف لوحة التحكم الرئيسية</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 8 — بدء تلقائي مع Windows               -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon teal">⚡</div>
    <div><div class="sec-num">إعداد إضافي مهم</div><h2>تشغيل النظام تلقائياً عند بدء Windows</h2><p>حتى لا تحتاج كتابة أوامر كل مرة</p></div>
  </div>

  <div class="alert info">
    <div class="alert-icon">💡</div>
    <div class="alert-body">
      <h4>الهدف</h4>
      <p>بدلاً من فتح Command Prompt وكتابة أوامر كل يوم، نصنع ملف .bat يشغّل كل شيء بنقرة مزدوجة واحدة.</p>
    </div>
  </div>

  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body">
        <h3>📝 إنشاء ملف تشغيل سريع (start_clinic.bat)</h3>
        <p>افتح Notepad وانسخ هذا النص:</p>
        <div class="cmd" style="direction:ltr;text-align:left;">
@echo off
title Dental Clinic MS - Starting...
echo.
echo ============================================
echo    Dental Clinic MS - Loading...
echo ============================================
echo.

<span class="c">:: Change to project directory (عدّل المسار حسب مكان المشروع)</span>
<span class="k">cd</span> /d <span class="s">"C:\\ClinicApp\\Dental Clinic MS Flask"</span>

<span class="c">:: Activate virtual environment</span>
<span class="k">call</span> venv\Scripts\activate.bat

<span class="c">:: Open browser after 3 seconds</span>
start /min timeout /t 3 /nobreak >nul
start chrome http://127.0.0.1:5000

<span class="c">:: Start Flask app</span>
echo Starting server... Open browser on http://127.0.0.1:5000
<span class="k">python</span> app.py

pause
        </div>
        <p>احفظ الملف على سطح المكتب باسم: <strong style="color:#4ade80;">start_clinic.bat</strong></p>
        <p style="color:#64748b;margin-top:6px;">⚠️ عند الحفظ: غيّر "Save as type" لـ "All Files" و"Encoding" لـ UTF-8</p>
      </div>
    </div>

    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body success">
        <h3>✅ الآن لتشغيل البرنامج كل يوم</h3>
        <ul>
          <li>1. شغّل XAMPP وابدأ MySQL (مرة واحدة)</li>
          <li>2. انقر مزدوج على <strong>start_clinic.bat</strong></li>
          <li>3. ستفتح نافذة سوداء ثم يفتح المتصفح تلقائياً</li>
          <li>4. النظام جاهز! 🎉</li>
        </ul>
      </div>
    </div>

    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body info">
        <h3>💡 تشغيل XAMPP تلقائياً مع Windows</h3>
        <ul>
          <li>افتح XAMPP Control Panel</li>
          <li>اضغط "Config" (الزر الأحمر في الزاوية)</li>
          <li>ضع علامة على "Start Control Panel Minimized"</li>
          <li>ضع اختصار XAMPP Control Panel في مجلد Startup:<br>
            <code style="color:#60d0ff;background:#020617;padding:2px 8px;border-radius:4px;font-size:12px;">C:\\Users\\USERNAME\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup</code>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 9 — الوصول من أجهزة أخرى                -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon purple">🌐</div>
    <div><div class="sec-num">إعداد اختياري</div><h2>الوصول للنظام من أجهزة أخرى في العيادة</h2><p>الطبيب من تابلته والاستقبال من لابتوبه</p></div>
  </div>

  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body">
        <h3>🔍 معرفة IP لابتوب الاستقبال (الـ Server)</h3>
        <div class="cmd">
<span class="c"># في Command Prompt على لابتوب الاستقبال:</span>
<span class="k">ipconfig</span>

<span class="ok"># ابحث عن "IPv4 Address" تحت "Wireless LAN adapter"</span>
<span class="ok"># مثال: 192.168.1.105</span>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body warning">
        <h3>⚙️ تعديل ملف start_clinic.bat للشبكة</h3>
        <p>في ملف .bat عدّل السطر الأخير ليقبل اتصالات خارجية:</p>
        <div class="cmd">
<span class="c"># بدلاً من:</span>
python app.py

<span class="c"># اكتب:</span>
<span class="k">python</span> -c <span class="s">"from app import app; app.run(host='0.0.0.0', port=5000, debug=False)"</span>
        </div>
      </div>
    </div>

    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body success">
        <h3>✅ الوصول من الأجهزة الأخرى</h3>
        <p>من أي جهاز على نفس الشبكة (Wi-Fi العيادة):</p>
        <div class="cmd">
http://192.168.1.105:5000
<span class="c"># استبدل 192.168.1.105 بـ IP لابتوب الاستقبال</span>
        </div>
        <ul style="margin-top:10px;">
          <li>الطبيب يفتح هذا الرابط من تابلته أو لابتوبه</li>
          <li>الاستقبال يفتح من لابتوبه الخاص</li>
          <li>جميعهم على نفس قاعدة البيانات في نفس الوقت</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════════════ -->
<!--  SECTION 10 — ملخص كامل                           -->
<!-- ═══════════════════════════════════════════════════ -->
<div class="section">
  <div class="sec-header">
    <div class="sec-icon blue">📋</div>
    <div><div class="sec-num">ملخص كامل</div><h2>قائمة التحقق النهائية</h2><p>تأكد من كل خطوة قبل تسليم العيادة</p></div>
  </div>

  <table>
    <thead><tr><th>#</th><th>الخطوة</th><th>ملاحظة</th><th>الحالة</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>Python 3.12 مثبت مع PATH</td><td>python --version تعطي رقم الإصدار</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>2</td><td>XAMPP مثبت</td><td>في C:\\xampp</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>3</td><td>MySQL يعمل في XAMPP</td><td>المربع أخضر في Control Panel</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>4</td><td>phpMyAdmin يفتح</td><td>http://localhost/phpmyadmin</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>5</td><td>قاعدة بيانات dental_clinic موجودة</td><td>ظاهرة في القائمة اليسرى</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>6</td><td>مجلد المشروع منسوخ على الجهاز</td><td>في C:\\ClinicApp أو سطح المكتب</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>7</td><td>ملف .env معدّل بالبيانات الصحيحة</td><td>DB_PORT و DB_NAME محددين</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>8</td><td>البيئة الافتراضية venv منشأة</td><td>مجلد venv موجود في المشروع</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>9</td><td>المكتبات مثبتة</td><td>pip install -r requirements.txt نجحت</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>10</td><td>البرنامج يشتغل</td><td>python app.py تعطي "Running on http://..."</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>11</td><td>صفحة الدخول تظهر في المتصفح</td><td>http://127.0.0.1:5000</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>12</td><td>تسجيل الدخول يعمل</td><td>admin@clinic.com / admin123</td><td><span class="badge green">✅</span></td></tr>
      <tr><td>13</td><td>بيانات العيادة معدّلة في الإعدادات</td><td>الاسم والهاتف وساعات العمل</td><td><span class="badge orange">⏳</span></td></tr>
      <tr><td>14</td><td>ملف start_clinic.bat على سطح المكتب</td><td>للتشغيل اليومي السهل</td><td><span class="badge orange">⏳</span></td></tr>
    </tbody>
  </table>
</div>

<div class="success-final">
  <h2>🎉 العيادة جاهزة!</h2>
  <p>إذا أكملت كل الخطوات، النظام يعمل بشكل كامل<br>وجاهز لاستقبال أول مريض وحجز أول موعد.</p>
  <p style="margin-top:15px;font-size:13px;opacity:0.7;">في حال أي مشكلة — راجع قسم رسائل الخطأ أعلاه أو تواصل مع مطوّر النظام</p>
</div>

</div><!-- end container -->

<footer>
  <p>🦷 Dental Clinic MS — دليل التثبيت الكامل | من الفلاشة للتشغيل</p>
  <p style="margin-top:8px;opacity:0.6;">احتفظ بهذا الملف على الفلاشة دائماً كمرجع للتثبيت</p>
</footer>
</body>
</html>""")

final_html = ''.join(parts)

with open('install_guide.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f'SUCCESS! install_guide.html written: {len(final_html)} bytes')
print('Open: install_guide.html')
