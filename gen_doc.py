# -*- coding: utf-8 -*-
"""Generates documentation.html for Dental Clinic MS"""

HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>توثيق تقني شامل - Dental Clinic MS</title>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet"/>
<style>
:root{--pr:#1e40af;--ac:#0ea5e9;--bg:#f8fafc;--bd:#e2e8f0;--tx:#1e293b;--mu:#64748b;--cb:#0f172a;--ct:#e2e8f0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Tajawal,sans-serif;background:var(--bg);color:var(--tx);line-height:1.8;font-size:15px}
.cover{background:linear-gradient(135deg,#1e3a8a,#1e40af 40%,#0ea5e9);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:60px 40px}
.ci{width:90px;height:90px;background:rgba(255,255,255,.15);border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:46px;border:1px solid rgba(255,255,255,.2)}
.cover h1{font-size:40px;font-weight:900;color:#fff;margin:22px 0 10px}
.cover h2{font-size:18px;color:rgba(255,255,255,.8);margin-bottom:36px}
.bgs{display:flex;gap:12px;flex-wrap:wrap;justify-content:center;margin-bottom:40px}
.bg{background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);color:#fff;padding:5px 16px;border-radius:999px;font-size:13px}
.cm{color:rgba(255,255,255,.6);font-size:12px;border-top:1px solid rgba(255,255,255,.15);padding-top:20px;max-width:480px}
.lay{display:flex;min-height:100vh}
.sb{width:268px;min-width:268px;background:#fff;border-left:1px solid var(--bd);position:sticky;top:0;height:100vh;overflow-y:auto;padding:22px 0}
.sbt{font-size:11px;font-weight:700;color:var(--mu);text-transform:uppercase;letter-spacing:1.5px;padding:0 16px 13px;border-bottom:1px solid var(--bd);margin-bottom:9px}
.ti{display:flex;align-items:center;gap:8px;padding:7px 16px;font-size:13px;color:var(--mu);text-decoration:none;border-right:3px solid transparent;transition:all .15s}
.ti:hover{color:var(--pr);background:#eff6ff;border-right-color:var(--pr)}
.tn{font-size:10px;font-weight:700;color:#3b82f6;background:#eff6ff;width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.mn{flex:1;padding:48px 56px;max-width:920px}
.sc{margin-bottom:56px}
.sh{display:flex;align-items:center;gap:13px;margin-bottom:22px;padding-bottom:13px;border-bottom:2px solid var(--bd)}
.sn{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,var(--pr),var(--ac));color:#fff;font-size:14px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.st{font-size:21px;font-weight:800}
h3{font-size:16px;font-weight:700;color:var(--pr);margin:22px 0 11px;display:flex;align-items:center;gap:7px}
h3::before{content:"";display:block;width:4px;height:15px;background:var(--ac);border-radius:2px}
p{margin-bottom:12px}
.tw{overflow-x:auto;margin:12px 0 20px;border-radius:10px;border:1px solid var(--bd);box-shadow:0 1px 3px rgba(0,0,0,.06)}
table{width:100%;border-collapse:collapse;font-size:13px}
thead{background:linear-gradient(90deg,#1e40af,#3b82f6)}
thead th{color:#fff;font-weight:600;padding:10px 13px;text-align:right;white-space:nowrap}
tbody tr:nth-child(even){background:#f8fafc}
tbody tr:hover{background:#eff6ff}
tbody td{padding:9px 13px;border-bottom:1px solid var(--bd);vertical-align:top}
tbody tr:last-child td{border-bottom:none}
code{background:#f1f5f9;padding:2px 5px;border-radius:4px;font-family:"JetBrains Mono",monospace;font-size:12px}
.tg{display:inline-block;font-size:11px;font-weight:600;padding:2px 7px;border-radius:5px;font-family:"JetBrains Mono",monospace}
.pk{background:#fef3c7;color:#92400e}.fk{background:#ede9fe;color:#5b21b6}
.gr{background:#d1fae5;color:#065f46}.bl{background:#dbeafe;color:#1e40af}.rd{background:#fee2e2;color:#991b1b}
pre{background:var(--cb);color:var(--ct);border-radius:10px;padding:18px 20px;font-family:"JetBrains Mono",monospace;font-size:12.5px;line-height:1.7;overflow-x:auto;margin:12px 0 20px;direction:ltr;text-align:left}
.fl{background:var(--cb);color:var(--ct);border-radius:10px;padding:20px 22px;font-family:"JetBrains Mono",monospace;font-size:12.5px;line-height:2.1;margin:12px 0 20px;direction:ltr;text-align:left;white-space:pre-wrap}
.cds{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:13px;margin:12px 0 20px}
.cd{background:#fff;border:1px solid var(--bd);border-radius:12px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.05)}
.cdi{font-size:24px;margin-bottom:7px}.cdt{font-size:13px;font-weight:700;margin-bottom:4px}.cdd{font-size:12px;color:var(--mu);line-height:1.5}
.al{border-radius:9px;padding:12px 15px;margin:12px 0;display:flex;gap:10px;align-items:flex-start;font-size:13px}
.ali{font-size:16px;flex-shrink:0;margin-top:1px}
.ai2{background:#eff6ff;border:1px solid #bfdbfe;color:#1e40af}
.aw{background:#fffbeb;border:1px solid #fed7aa;color:#92400e}
.as{background:#f0fdf4;border:1px solid #bbf7d0;color:#166534}
.ad{background:#fff1f2;border:1px solid #fecdd3;color:#9f1239}
.rg{display:grid;grid-template-columns:repeat(2,1fr);gap:11px;margin:12px 0}
.rc{border-radius:10px;padding:13px 17px;font-size:13px}
.ra{background:#fef3c7;border:1px solid #fde68a}
.rd2{background:#d1fae5;border:1px solid #a7f3d0}
.rr{background:#dbeafe;border:1px solid #bfdbfe}
.rp{background:#ede9fe;border:1px solid #ddd6fe}
.rn{font-weight:700;font-size:14px;margin-bottom:3px}
.lk{background:#0f172a;border-radius:10px;padding:20px;margin:12px 0;direction:ltr;text-align:left;font-family:"JetBrains Mono",monospace}
.ls1{color:#ff79c6}.ls2{color:#50fa7b}.ls3{color:#f1fa8c}.ls4{color:#bd93f9}.lsp{color:#6272a4;font-size:18px}
.lkey{font-size:20px;font-weight:700;letter-spacing:1px}
.llb{font-size:11px;color:#6272a4;display:flex;gap:0;margin-top:8px}
.llbi{padding:0 8px;text-align:center}
.nd{background:#0f172a;border-radius:10px;padding:24px;margin:12px 0 20px;text-align:center}
.nr{display:inline-flex;align-items:center;background:#1e40af;color:#fff;font-weight:700;font-size:13px;border-radius:10px;padding:8px 20px;margin-bottom:16px}
.nds{display:flex;justify-content:center;gap:18px;flex-wrap:wrap;align-items:center}
.ndc{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:11px 16px;text-align:center;font-size:12px;color:#e2e8f0;min-width:125px}
.nds2{border-color:#3b82f6;box-shadow:0 0 0 1px #3b82f6}
.ndi{font-size:24px;margin-bottom:5px}
.ni{font-family:"JetBrains Mono",monospace;font-size:11px;color:#50fa7b;margin-top:3px}
.na{color:#475569;font-size:18px;display:flex;align-items:center}
@media print{.sb{display:none}.mn{padding:18px;max-width:100%}}
@media(max-width:840px){.sb{display:none}.mn{padding:24px 16px}}
</style>
</head>
<body>

<div class="cover">
  <div class="ci">🦷</div>
  <h1>Dental Clinic MS</h1>
  <h2>التوثيق التقني الشامل — من الألف إلى الياء</h2>
  <div class="bgs">
    <span class="bg">Python / Flask</span>
    <span class="bg">SQLAlchemy ORM</span>
    <span class="bg">MySQL / SQLite</span>
    <span class="bg">PyInstaller</span>
    <span class="bg">Telegram Bot</span>
    <span class="bg">HMAC License</span>
  </div>
  <div class="cm">
    <strong>المطوّر:</strong> خالد ناصيف &nbsp;|&nbsp; <strong>الإصدار:</strong> 1.0 &nbsp;|&nbsp; <strong>التاريخ:</strong> يوليو 2026<br/>
    هذا المستند للمهندسين والمطورين الراغبين في فهم البنية الكاملة للنظام
  </div>
</div>

<div class="lay">
<nav class="sb">
  <div class="sbt">فهرس المحتويات</div>
  <a href="#s1"  class="ti"><span class="tn">1</span>نظرة عامة</a>
  <a href="#s2"  class="ti"><span class="tn">2</span>Tech Stack</a>
  <a href="#s3"  class="ti"><span class="tn">3</span>بنية المشروع</a>
  <a href="#s4"  class="ti"><span class="tn">4</span>قاعدة البيانات</a>
  <a href="#s5"  class="ti"><span class="tn">5</span>علاقات الجداول</a>
  <a href="#s6"  class="ti"><span class="tn">6</span>دورة حياة الطلب</a>
  <a href="#s7"  class="ti"><span class="tn">7</span>المصادقة والترخيص</a>
  <a href="#s8"  class="ti"><span class="tn">8</span>الـ Blueprints</a>
  <a href="#s9"  class="ti"><span class="tn">9</span>نظام الإشعارات</a>
  <a href="#s10" class="ti"><span class="tn">10</span>واجهات المستخدم</a>
  <a href="#s11" class="ti"><span class="tn">11</span>تطبيق سطح المكتب</a>
  <a href="#s12" class="ti"><span class="tn">12</span>النسخ الاحتياطي</a>
  <a href="#s13" class="ti"><span class="tn">13</span>الأمان</a>
  <a href="#s14" class="ti"><span class="tn">14</span>مفاتيح الترخيص</a>
  <a href="#s15" class="ti"><span class="tn">15</span>شبكة LAN</a>
  <a href="#s16" class="ti"><span class="tn">16</span>تدفق العمل اليومي</a>
</nav>
<main class="mn">

<!-- 1 -->
<section class="sc" id="s1">
<div class="sh"><div class="sn">1</div><div class="st">نظرة عامة على النظام</div></div>
<p><strong>Dental Clinic MS</strong> هو نظام إدارة عيادة أسنان متكامل مبني بـ Python/Flask، يعمل كـ:</p>
<div class="cds">
  <div class="cd"><div class="cdi">🌐</div><div class="cdt">تطبيق ويب</div><div class="cdd">يُشغَّل من أي متصفح على الشبكة المحلية</div></div>
  <div class="cd"><div class="cdi">🖥️</div><div class="cdt">تطبيق سطح مكتب</div><div class="cdd">ملف .exe يعمل مثل أي برنامج عادي على Windows</div></div>
  <div class="cd"><div class="cdi">🔗</div><div class="cdt">متعدد المستخدمين</div><div class="cdd">3 أجهزة أو أكثر تشترك بنفس قاعدة البيانات</div></div>
  <div class="cd"><div class="cdi">🔒</div><div class="cdt">محمي بترخيص</div><div class="cdd">مفاتيح HMAC-SHA256 لا يمكن تزويرها</div></div>
</div>
<h3>أدوار المستخدمين</h3>
<div class="rg">
  <div class="rc ra"><div class="rn">👑 Admin</div>صلاحيات كاملة: إدارة المستخدمين والإعدادات والتقارير وكل شيء</div>
  <div class="rc rd2"><div class="rn">🩺 Doctor</div>رؤية مرضاه، فتح/إغلاق الجلسات، إضافة العلاجات</div>
  <div class="rc rr"><div class="rn">📋 Receptionist</div>حجز المواعيد، إدارة المرضى، الفواتير والمدفوعات</div>
  <div class="rc rp"><div class="rn">👤 Patient</div>بوابة خاصة: مواعيده وفواتيره وطلب مواعيد جديدة فقط</div>
</div>
</section>

<!-- 2 -->
<section class="sc" id="s2">
<div class="sh"><div class="sn">2</div><div class="st">التقنيات المستخدمة (Tech Stack)</div></div>
<div class="tw"><table>
<thead><tr><th>المكوّن</th><th>التقنية</th><th>الدور</th></tr></thead>
<tbody>
<tr><td><strong>Backend</strong></td><td><span class="tg bl">Python 3 + Flask</span></td><td>معالجة الطلبات والـ Routes والمنطق الأساسي</td></tr>
<tr><td><strong>ORM</strong></td><td><span class="tg bl">SQLAlchemy</span></td><td>التواصل مع قاعدة البيانات بدون SQL مباشر</td></tr>
<tr><td><strong>قاعدة البيانات</strong></td><td><span class="tg gr">MySQL / SQLite</span></td><td>MySQL للإنتاج، SQLite تلقائي عند غيابه</td></tr>
<tr><td><strong>Frontend</strong></td><td><span class="tg bl">Jinja2 + Bootstrap + JS</span></td><td>قوالب HTML الديناميكية والتصميم</td></tr>
<tr><td><strong>Packaging</strong></td><td><span class="tg pk">PyInstaller</span></td><td>تحويل التطبيق لملف .exe قابل للتوزيع</td></tr>
<tr><td><strong>Desktop Wrapper</strong></td><td><span class="tg bl">pywebview</span></td><td>نافذة Windows تشغّل Flask بداخلها</td></tr>
<tr><td><strong>الإشعارات</strong></td><td><span class="tg bl">Telegram + SMS + SMTP</span></td><td>تذكيرات المواعيد للمرضى</td></tr>
<tr><td><strong>الأمان</strong></td><td><span class="tg pk">CSRF + HMAC-SHA256 + bcrypt</span></td><td>حماية الطلبات + التراخيص + كلمات المرور</td></tr>
</tbody>
</table></div>
</section>

<!-- 3 -->
<section class="sc" id="s3">
<div class="sh"><div class="sn">3</div><div class="st">بنية المشروع (Project Structure)</div></div>
<pre>Dental Clinic MS Flask/
│
├── app.py               ← نقطة الدخول الرئيسية للتطبيق
├── desktop_app.py       ← تشغيل التطبيق كبرنامج سطح مكتب
├── settings.py          ← إعدادات قاعدة البيانات والـ Config
├── models.py            ← تعريف جداول قاعدة البيانات
├── generate_license.py  ← أداة إنشاء مفاتيح الترخيص
│
├── routes/              ← الـ Blueprints (وحدات التوجيه)
│   ├── auth.py          ← تسجيل الدخول + تفعيل الترخيص
│   ├── dashboard.py     ← الصفحة الرئيسية + الإحصائيات
│   ├── patients.py      ← إدارة المرضى (CRUD كامل)
│   ├── appointments.py  ← إدارة المواعيد + الجلسات
│   ├── treatments.py    ← إدارة العلاجات داخل الجلسة
│   ├── invoices.py      ← إنشاء وعرض الفواتير
│   ├── payments.py      ← استلام المدفوعات وتوزيعها
│   ├── reports.py       ← التقارير المالية والإحصائية
│   ├── settings.py      ← إعدادات العيادة والمستخدمين
│   ├── portal.py        ← بوابة المريض الذاتية
│   └── deploy.py        ← Webhook للنشر التلقائي من GitHub
│
├── utils/               ← الأدوات المساعدة
│   ├── license_helper.py    ← توليد والتحقق من التراخيص
│   ├── notification_helper.py ← إرسال Telegram/SMS/Email
│   ├── settings_helper.py   ← قراءة/كتابة إعدادات النظام
│   ├── backup_helper.py     ← النسخ الاحتياطي التلقائي
│   └── validators.py        ← التحقق من صحة المدخلات
│
├── templates/           ← قوالب HTML (Jinja2)
├── static/              ← CSS, JS, الصور
├── instance/            ← قاعدة بيانات SQLite
├── logs/                ← ملفات السجلات clinic.log
└── backups/             ← النسخ الاحتياطية .sql</pre>
</section>

<!-- 4 -->
<section class="sc" id="s4">
<div class="sh"><div class="sn">4</div><div class="st">قاعدة البيانات والجداول</div></div>
<h3>🔌 كيف يختار النظام قاعدة البيانات؟</h3>
<div class="fl">build_database_uri() في settings.py:

1. هل في .env متغير DATABASE_URL؟
   نعم → استخدمه مباشرة
   لا  → انتقل للخطوة 2

2. هل MySQL شغّال على المنفذ 3308؟
   نعم → mysql+pymysql://root:1234@127.0.0.1:3308/dental_clinic
   لا  → انتقل للخطوة 3

3. الوضع الافتراضي:
   دائماً → sqlite:///instance/dental_clinic.db</div>

<h3>🏥 جدول patient — المرضى</h3>
<div class="tw"><table>
<thead><tr><th>الحقل</th><th>النوع</th><th>الوصف</th></tr></thead>
<tbody>
<tr><td><code>id</code></td><td><span class="tg pk">PK INT</span></td><td>معرّف المريض (يزداد تلقائياً)</td></tr>
<tr><td><code>first_name</code></td><td>VARCHAR(100)</td><td>الاسم الأول — مطلوب</td></tr>
<tr><td><code>last_name</code></td><td>VARCHAR(100)</td><td>اسم العائلة — مطلوب</td></tr>
<tr><td><code>phone</code></td><td>VARCHAR(20)</td><td>رقم الهاتف</td></tr>
<tr><td><code>email</code></td><td>VARCHAR(120)</td><td>البريد الإلكتروني</td></tr>
<tr><td><code>telegram_chat_id</code></td><td>VARCHAR(50)</td><td>معرّف تيليغرام للإشعارات التلقائية</td></tr>
<tr><td><code>reminders_enabled</code></td><td>BOOLEAN</td><td>هل يستلم تذكيرات؟ افتراضي: نعم</td></tr>
<tr><td><code>primary_doctor_id</code></td><td><span class="tg fk">FK → user</span></td><td>الدكتور المعالج الأساسي</td></tr>
<tr><td><code>medical_information</code></td><td>TEXT</td><td>المعلومات الطبية (حساسية، أمراض مزمنة...)</td></tr>
</tbody>
</table></div>

<h3>📅 جدول appointment — المواعيد</h3>
<div class="tw"><table>
<thead><tr><th>الحقل</th><th>النوع</th><th>الوصف</th></tr></thead>
<tbody>
<tr><td><code>id</code></td><td><span class="tg pk">PK INT</span></td><td>معرّف الموعد</td></tr>
<tr><td><code>patient_id</code></td><td><span class="tg fk">FK → patient</span></td><td>المريض المرتبط</td></tr>
<tr><td><code>doctor_id</code></td><td><span class="tg fk">FK → user</span></td><td>الدكتور المسؤول</td></tr>
<tr><td><code>appointment_date</code></td><td>DATETIME</td><td>تاريخ ووقت الموعد — مطلوب</td></tr>
<tr><td><code>reason</code></td><td>VARCHAR(255)</td><td>سبب الزيارة</td></tr>
<tr><td><code>status</code></td><td>VARCHAR(50)</td><td>Scheduled / Completed / Cancelled / Pending</td></tr>
<tr><td><code>session_opened_at</code></td><td>DATETIME</td><td>وقت فتح الجلسة (عند بدء العلاج)</td></tr>
</tbody>
</table></div>

<h3>🦷 جدول treatment — العلاجات</h3>
<div class="tw"><table>
<thead><tr><th>الحقل</th><th>النوع</th><th>الوصف</th></tr></thead>
<tbody>
<tr><td><code>id</code></td><td><span class="tg pk">PK INT</span></td><td>معرّف العلاج</td></tr>
<tr><td><code>appointment_id</code></td><td><span class="tg fk">FK → appointment</span></td><td>الموعد المرتبط (cascade delete)</td></tr>
<tr><td><code>doctor_id</code></td><td><span class="tg fk">FK → user</span></td><td>الدكتور المنفّذ</td></tr>
<tr><td><code>procedure_type</code></td><td>VARCHAR(200)</td><td>نوع الإجراء (حشوة، خلع، تقويم...)</td></tr>
<tr><td><code>tooth_number</code></td><td>VARCHAR(50)</td><td>رقم السن المعالج</td></tr>
<tr><td><code>total_cost</code></td><td>DECIMAL(10,2)</td><td>تكلفة هذا العلاج</td></tr>
<tr><td><code>use_anesthesia</code></td><td>BOOLEAN</td><td>هل استُخدم تخدير؟</td></tr>
<tr><td><code>anesthesia_needles</code></td><td>INT</td><td>عدد إبر التخدير</td></tr>
<tr><td><code>anesthesia_cost</code></td><td>DECIMAL(10,2)</td><td>تكلفة التخدير</td></tr>
</tbody>
</table></div>

<h3>🧾 جدول invoice — الفواتير</h3>
<div class="tw"><table>
<thead><tr><th>الحقل</th><th>النوع</th><th>الوصف</th></tr></thead>
<tbody>
<tr><td><code>id</code></td><td><span class="tg pk">PK INT</span></td><td>رقم الفاتورة (يُعرض كـ INV-{id})</td></tr>
<tr><td><code>appointment_id</code></td><td><span class="tg fk">FK UNIQUE</span></td><td>موعد واحد = فاتورة واحدة فقط</td></tr>
<tr><td><code>patient_id</code></td><td><span class="tg fk">FK → patient</span></td><td>المريض</td></tr>
<tr><td><code>discount</code></td><td>DECIMAL(10,2)</td><td>قيمة الخصم</td></tr>
<tr><td><code>discount_type</code></td><td>VARCHAR(20)</td><td>value أو percentage</td></tr>
</tbody>
</table></div>
<div class="al ai2"><div class="ali">💡</div><div><strong>الحسابات التلقائية (لا تُخزَّن في DB):</strong><br/>subtotal = مجموع تكاليف العلاجات | total_amount = subtotal − discount | status = Unpaid / Partially Paid / Paid / Credit</div></div>

<h3>💰 جداول payment و payment_allocation — المدفوعات</h3>
<div class="fl">مريض يدفع 100,000 S.P  →  سجل في جدول payment
                    │
                    ├── 60,000 →  payment_allocation  →  Invoice #5
                    └── 40,000 →  payment_allocation  →  Invoice #7

الفكرة: دفعة واحدة يمكن توزيعها على عدة فواتير</div>

<h3>👤 جدول user — المستخدمون</h3>
<div class="tw"><table>
<thead><tr><th>الحقل</th><th>النوع</th><th>الوصف</th></tr></thead>
<tbody>
<tr><td><code>id</code></td><td><span class="tg pk">PK INT</span></td><td>معرّف المستخدم</td></tr>
<tr><td><code>username</code></td><td>VARCHAR(80) UNIQUE</td><td>اسم الدخول (لا يتكرر)</td></tr>
<tr><td><code>password_hash</code></td><td>VARCHAR(255)</td><td>كلمة المرور مُشفَّرة بـ bcrypt</td></tr>
<tr><td><code>plain_password</code></td><td>VARCHAR(255)</td><td>كلمة المرور الصريحة (للمدير فقط)</td></tr>
<tr><td><code>role</code></td><td>VARCHAR(20)</td><td>admin / doctor / receptionist / patient</td></tr>
<tr><td><code>patient_id</code></td><td><span class="tg fk">FK → patient</span></td><td>يُربط المستخدم بسجل مريض (للدور patient)</td></tr>
</tbody>
</table></div>

<h3>⚙️ جدول system_setting — إعدادات النظام</h3>
<div class="tw"><table>
<thead><tr><th>المفتاح</th><th>مثال</th><th>الوصف</th></tr></thead>
<tbody>
<tr><td><code>clinic_name</code></td><td>Dr Clinic</td><td>اسم العيادة يظهر في كل الصفحات</td></tr>
<tr><td><code>active_license_key</code></td><td>DCMS-LIFE-...</td><td>مفتاح الترخيص المفعّل حالياً</td></tr>
<tr><td><code>license_type</code></td><td>trial / annual / lifetime</td><td>نوع الترخيص</td></tr>
<tr><td><code>last_system_activity</code></td><td>2026-07-24 05:12:55</td><td>آخر نشاط (لكشف التلاعب بالتاريخ)</td></tr>
<tr><td><code>telegram_bot_token</code></td><td>8732677418:AAG...</td><td>توكن بوت تيليغرام</td></tr>
<tr><td><code>treatment_prices</code></td><td>{"Check-up": 25000}</td><td>أسعار العلاجات الافتراضية (JSON)</td></tr>
</tbody>
</table></div>
</section>

<!-- 5 -->
<section class="sc" id="s5">
<div class="sh"><div class="sn">5</div><div class="st">علاقات الجداول (ERD)</div></div>
<pre>     user
      |  └──(primary_doctor_id)──────────────────┐
      |                                           ▼
      |(doctor_id)                            patient
      ▼                                      |  |   |
  appointment ◄────────(patient_id)──────────┘  |   |
      |  |                                       |   |
      |  └──[1:1]──────► invoice            [1:N]| [1:N]
      |                      |                   ▼   ▼
      |[1:N]             [1:N]|               payment  patient_file
      ▼                       ▼
  treatment           payment_allocation ◄── payment
  (cascade delete)    (cascade delete)

القواعد:
  مريض واحد  →  مواعيد متعددة         [1:N]
  موعد واحد  →  علاجات متعددة         [1:N] cascade delete
  موعد واحد  →  فاتورة واحدة فقط      [1:1] cascade delete
  مريض واحد  →  دفعات متعددة          [1:N]
  دفعة واحدة →  توزيع على فواتير عدة  [1:N] عبر payment_allocation</pre>
</section>

<!-- 6 -->
<section class="sc" id="s6">
<div class="sh"><div class="sn">6</div><div class="st">دورة حياة الطلب (Request Lifecycle)</div></div>
<div class="fl">Browser Request  GET /patients
           │
           ▼
① enforce_system_license()      ← app.py before_request
   هل يوجد ترخيص نشط؟
   لا  → redirect /activate
   نعم → متابعة
           │
           ▼
② load_logged_in_user()         ← app.py before_request
   يقرأ user_id من الـ session
   يجلب بيانات المستخدم من DB → g.current_user
           │
           ▼
③ validate_csrf()               ← app.py before_request (POST فقط)
   يتحقق من csrf_token في الفورم
   فشل → 403 Forbidden  |  نجح → متابعة
           │
           ▼
④ check_login()                 ← app.py before_request
   هل المستخدم مسجّل الدخول؟
   لا  → redirect /login  |  نعم → متابعة
           │
           ▼
⑤ Blueprint Route Handler       ← routes/patients.py
   تنفيذ الكود الفعلي
   جلب البيانات من قاعدة البيانات
   render_template() → HTML
           │
           ▼
⑥ process_html_response()       ← app.py after_request
   أ) حقن csrf_token في كل form تلقائياً
   ب) ترجمة الصفحة للعربية (إذا lang=ar)
           │
           ▼
Browser Response  200 OK</div>
</section>

<!-- 7 -->
<section class="sc" id="s7">
<div class="sh"><div class="sn">7</div><div class="st">نظام المصادقة والتراخيص</div></div>
<h3>🔐 تسجيل الدخول</h3>
<div class="tw"><table>
<thead><tr><th>الخطوة</th><th>التفاصيل</th></tr></thead>
<tbody>
<tr><td>1. استقبال البيانات</td><td>username + password + user_type من الفورم</td></tr>
<tr><td>2. البحث في DB</td><td>User.query.filter_by(username=...) حسب الدور</td></tr>
<tr><td>3. التحقق</td><td>werkzeug.check_password_hash(hash, input)</td></tr>
<tr><td>4. الـ Session</td><td>session["user_id"] = user.id + session["role"] = user.role</td></tr>
<tr><td>5. التوجيه</td><td>patient → /portal | باقي الأدوار → /dashboard</td></tr>
</tbody>
</table></div>

<h3>🔑 بنية مفتاح الترخيص</h3>
<div class="lk">
  <div class="lkey"><span class="ls1">DCMS</span><span class="lsp"> - </span><span class="ls2">T30</span><span class="lsp"> - </span><span class="ls3">20260822</span><span class="lsp"> - </span><span class="ls4">8F92A31B4C</span></div>
  <div class="llb">
    <span class="llbi">البادئة الثابتة</span>
    <span class="llbi">نوع الترخيص</span>
    <span class="llbi">تاريخ الانتهاء</span>
    <span class="llbi">توقيع HMAC-SHA256</span>
  </div>
</div>
<div class="tw"><table>
<thead><tr><th>الكود</th><th>النوع</th><th>المدة</th></tr></thead>
<tbody>
<tr><td><span class="tg pk">T14 / T30 / T60 / T90</span></td><td>تجريبي</td><td>14 / 30 / 60 / 90 يوم</td></tr>
<tr><td><span class="tg gr">A1Y / A2Y</span></td><td>سنوي</td><td>365 / 730 يوم</td></tr>
<tr><td><span class="tg bl">LIFE</span></td><td>مدى الحياة</td><td>~100 سنة</td></tr>
</tbody>
</table></div>
<div class="al aw"><div class="ali">⚠️</div><div><strong>حماية التلاعب بالتاريخ:</strong> النظام يحفظ آخر وقت نشاط في قاعدة البيانات. إذا رجع تاريخ الكمبيوتر للوراء بأكثر من 5 دقائق → يُحجب الوصول فوراً!</div></div>
</section>

<!-- 8 -->
<section class="sc" id="s8">
<div class="sh"><div class="sn">8</div><div class="st">الوحدات والـ Blueprints</div></div>
<div class="tw"><table>
<thead><tr><th>Blueprint</th><th>المسار الأساسي</th><th>الوظيفة</th></tr></thead>
<tbody>
<tr><td><code>auth_bp</code></td><td><code>/login, /logout, /activate</code></td><td>تسجيل الدخول + تفعيل الترخيص</td></tr>
<tr><td><code>dashboard_bp</code></td><td><code>/</code></td><td>الإحصائيات اليومية + التقويم</td></tr>
<tr><td><code>patients_bp</code></td><td><code>/patients</code></td><td>إضافة/تعديل/حذف/بحث المرضى + رفع ملفات</td></tr>
<tr><td><code>appointments_bp</code></td><td><code>/appointments</code></td><td>المواعيد + فتح/إغلاق الجلسات</td></tr>
<tr><td><code>treatments_bp</code></td><td><code>/treatments</code></td><td>إضافة/تعديل العلاجات داخل الجلسة</td></tr>
<tr><td><code>invoices_bp</code></td><td><code>/invoices</code></td><td>عرض/طباعة/تعديل الفواتير</td></tr>
<tr><td><code>payments_bp</code></td><td><code>/payments</code></td><td>استلام دفعة وتوزيعها على الفواتير</td></tr>
<tr><td><code>reports_bp</code></td><td><code>/reports</code></td><td>تقارير مالية + أداء الأطباء</td></tr>
<tr><td><code>settings_bp</code></td><td><code>/settings</code></td><td>بيانات العيادة + إعدادات الإشعارات + المستخدمين</td></tr>
<tr><td><code>portal_bp</code></td><td><code>/portal</code></td><td>بوابة المريض (مواعيده + فواتيره)</td></tr>
<tr><td><code>deploy_bp</code></td><td><code>/deploy</code></td><td>GitHub Webhook للنشر التلقائي</td></tr>
</tbody>
</table></div>
<h3>🔄 مسار فتح وإغلاق الجلسة</h3>
<div class="fl">1. مريض يصل → الاستقبال يضغط "فتح الجلسة"
   POST /appointments/{id}/open-session
   session_opened_at = datetime.now()

2. الدكتور يضيف العلاجات
   POST /treatments/add  (يمكن عدة علاجات)

3. الاستقبال يضغط "إغلاق الجلسة"
   POST /appointments/{id}/close-session
   status → "Completed"
   تُنشأ فاتورة تلقائياً = مجموع تكاليف العلاجات</div>
</section>

<!-- 9 -->
<section class="sc" id="s9">
<div class="sh"><div class="sn">9</div><div class="st">نظام الإشعارات</div></div>
<p>عند بدء التطبيق، تُشغَّل 3 Threads مستقلة في الخلفية:</p>
<div class="cds">
  <div class="cd"><div class="cdi">⏰</div><div class="cdt">مُجدِّل التذكيرات</div><div class="cdd">يفحص كل دقيقة مواعيد اليوم ويرسل تذكيرات قبل 24 ساعة و 2 ساعة</div></div>
  <div class="cd"><div class="cdi">🤖</div><div class="cdt">Telegram Listener</div><div class="cdd">يستمع لـ /start من المرضى ويحفظ chat_id في قاعدة البيانات تلقائياً</div></div>
  <div class="cd"><div class="cdi">💾</div><div class="cdt">مُجدِّل النسخ</div><div class="cdd">ينشئ نسخة احتياطية كل 24 ساعة في مجلد backups/</div></div>
</div>
<div class="tw"><table>
<thead><tr><th>القناة</th><th>الدالة</th><th>المزوّد</th></tr></thead>
<tbody>
<tr><td>🔵 Telegram</td><td><code>send_telegram_message()</code></td><td>Telegram Bot API (مجاني)</td></tr>
<tr><td>📱 SMS</td><td><code>send_commpeak_sms()</code></td><td>CommPeak TextPeak API</td></tr>
<tr><td>📱 SMS بديل</td><td><code>send_easysendsms()</code></td><td>EasySendSMS API</td></tr>
<tr><td>📧 Email</td><td><code>send_email()</code></td><td>SMTP (Gmail أو غيره)</td></tr>
</tbody>
</table></div>
</section>

<!-- 10 -->
<section class="sc" id="s10">
<div class="sh"><div class="sn">10</div><div class="st">واجهات المستخدم</div></div>
<h3>🏗️ القالب الأساسي base.html</h3>
<div class="tw"><table>
<thead><tr><th>المنطقة</th><th>المحتوى</th></tr></thead>
<tbody>
<tr><td>Sidebar يميناً</td><td>قائمة التنقل — تتغير حسب دور المستخدم</td></tr>
<tr><td>Header أعلى</td><td>اسم العيادة + اسم المستخدم + تغيير اللغة</td></tr>
<tr><td>Main Content</td><td>محتوى الصفحة الحالية (block content)</td></tr>
<tr><td>Flash Messages</td><td>رسائل النجاح (خضراء) والخطأ (حمراء)</td></tr>
</tbody>
</table></div>
<h3>🌐 الترجمة (عربي / إنجليزي)</h3>
<p>تعمل على مستوى الخادم. بعد كل استجابة HTML، يمر عليها <code>process_html_response()</code> ويترجمها باستخدام قاموس <code>utils/translations.py</code> (أكثر من 1000 مصطلح).</p>
<h3>⚡ البيانات المُحقنة في كل صفحة تلقائياً</h3>
<div class="tw"><table>
<thead><tr><th>المتغير</th><th>المصدر</th></tr></thead>
<tbody>
<tr><td><code>clinic_name</code></td><td>system_setting</td></tr>
<tr><td><code>currency_symbol</code></td><td>system_setting</td></tr>
<tr><td><code>current_user</code></td><td>g.current_user (session)</td></tr>
<tr><td><code>all_doctors</code></td><td>User.query (role=doctor/admin)</td></tr>
<tr><td><code>pending_count</code></td><td>Appointment.query (status=Pending)</td></tr>
<tr><td><code>operating_hours</code></td><td>system_setting (محوّل لـ 12h)</td></tr>
</tbody>
</table></div>
</section>

<!-- 11 -->
<section class="sc" id="s11">
<div class="sh"><div class="sn">11</div><div class="st">التشغيل كتطبيق سطح مكتب</div></div>
<div class="fl">التطبيق يُفتح (Clinic MS.exe)
           │
           ▼
① find_free_port(5000)
   يبحث عن منفذ حر بين 5000-6000
           │
           ▼
② Thread جديد في الخلفية
   app.run(host="0.0.0.0", port=PORT)
   host="0.0.0.0" = يستمع على كل واجهات الشبكة
           │
           ▼
③ time.sleep(1.5)  ← ينتظر Flask يجهز
           │
           ▼
④ webview.create_window()
   نافذة Windows 1280×800 تحمل: http://127.0.0.1:{PORT}</div>
<h3>📦 بناء ملف .exe</h3>
<pre>python -m PyInstaller "Clinic MS.spec" --noconfirm
# الناتج: dist/Clinic MS/Clinic MS.exe</pre>
</section>

<!-- 12 -->
<section class="sc" id="s12">
<div class="sh"><div class="sn">12</div><div class="st">نظام النسخ الاحتياطي</div></div>
<div class="tw"><table>
<thead><tr><th>الدالة</th><th>الوصف</th></tr></thead>
<tbody>
<tr><td><code>create_database_backup()</code></td><td>ينشئ نسخة .sql الآن</td></tr>
<tr><td><code>list_backups()</code></td><td>يُرجع قائمة بكل النسخ المتاحة</td></tr>
<tr><td><code>restore_database_backup(filename)</code></td><td>يستعيد قاعدة البيانات من نسخة محددة</td></tr>
<tr><td><code>schedule_daily_backups(app)</code></td><td>مجدول يومي في thread مستقل</td></tr>
</tbody>
</table></div>
<div class="al as"><div class="ali">✅</div><div>النسخ تعمل تلقائياً كل 24 ساعة. اسم الملف مثلاً: <code>backup_dental_clinic_20260724_051912.sql</code></div></div>
</section>

<!-- 13 -->
<section class="sc" id="s13">
<div class="sh"><div class="sn">13</div><div class="st">الأمان (Security)</div></div>
<div class="cds">
  <div class="cd"><div class="cdi">🛡️</div><div class="cdt">CSRF Protection</div><div class="cdd">كل فورم POST يحتوي token مخفي. لا يمكن إرسال طلبات من مواقع خارجية.</div></div>
  <div class="cd"><div class="cdi">🔐</div><div class="cdt">Password Hashing</div><div class="cdd">bcrypt. حتى لو سُرقت قاعدة البيانات لا يمكن معرفة كلمات المرور.</div></div>
  <div class="cd"><div class="cdi">✍️</div><div class="cdt">HMAC License</div><div class="cdd">مفاتيح موقّعة بـ HMAC-SHA256. لا يمكن توليد مفتاح بدون MASTER_SECRET.</div></div>
  <div class="cd"><div class="cdi">⏱️</div><div class="cdt">Clock Detection</div><div class="cdd">يكشف تغيير تاريخ الكمبيوتر للخلف ويحجب الوصول فوراً.</div></div>
</div>
</section>

<!-- 14 -->
<section class="sc" id="s14">
<div class="sh"><div class="sn">14</div><div class="st">كيفية إنشاء مفاتيح الترخيص</div></div>
<pre># مفتاح تجريبي 30 يوم
python generate_license.py 30

# مفتاح سنوي
python generate_license.py 365

# مفتاح مدى الحياة
python generate_license.py lifetime

# الناتج:
License Key:    DCMS-T30-20260822-8F92A31B4C
License Type:   TRIAL
Validity:       30 Days
Expiry:         2026-08-22 23:59:59</pre>
<div class="al ad"><div class="ali">🚫</div><div><strong>قبل التسليم لعميل جديد:</strong> احذف مجلد <code>instance/</code> لتجبر النظام على إنشاء قاعدة بيانات جديدة فارغة تطلب المفتاح فوراً.</div></div>
</section>

<!-- 15 -->
<section class="sc" id="s15">
<div class="sh"><div class="sn">15</div><div class="st">تشغيل النظام على شبكة LAN</div></div>
<div class="nd">
  <div class="nr">🌐 Router / WiFi للعيادة</div><br/>
  <div class="nds">
    <div class="ndc nds2">
      <div class="ndi">💻</div>
      <div><strong>لابتوب الدكتور</strong></div>
      <div style="color:#94a3b8;font-size:11px">السيرفر الرئيسي</div>
      <div class="ni">192.168.1.10:5000</div>
      <div style="color:#3b82f6;font-size:11px;margin-top:3px">✦ يُشغّل Clinic MS.exe</div>
    </div>
    <div class="na">── WiFi ──</div>
    <div class="ndc">
      <div class="ndi">💻</div>
      <div><strong>الاستقبال</strong></div>
      <div style="color:#94a3b8;font-size:11px">متصفح فقط</div>
      <div class="ni">→ 192.168.1.10:5000</div>
    </div>
    <div class="na">── WiFi ──</div>
    <div class="ndc">
      <div class="ndi">💻</div>
      <div><strong>الدكتور المتدرب</strong></div>
      <div style="color:#94a3b8;font-size:11px">متصفح فقط</div>
      <div class="ni">→ 192.168.1.10:5000</div>
    </div>
  </div>
</div>
<div class="tw"><table>
<thead><tr><th>الخطوة</th><th>الجهاز</th><th>الإجراء</th></tr></thead>
<tbody>
<tr><td>1</td><td>جهاز الدكتور</td><td>شغّل Clinic MS.exe</td></tr>
<tr><td>2</td><td>جهاز الدكتور</td><td>افتح CMD → اكتب <code>ipconfig</code> → IPv4 Address</td></tr>
<tr><td>3</td><td>جهاز الدكتور</td><td>اسمح للمنفذ 5000 في Windows Firewall</td></tr>
<tr><td>4</td><td>الأجهزة الأخرى</td><td>افتح المتصفح → <code>http://192.168.1.10:5000</code></td></tr>
<tr><td>5</td><td>كل الأجهزة</td><td>سجّل الدخول بحسابك الخاص</td></tr>
</tbody>
</table></div>
<div class="al aw"><div class="ali">⚠️</div><div><strong>شرط أساسي:</strong> التطبيق يجب أن يظل مشغّلاً على جهاز الدكتور طوال الدوام. إذا أُغلق → تنقطع كل الأجهزة الأخرى.</div></div>
</section>

<!-- 16 -->
<section class="sc" id="s16">
<div class="sh"><div class="sn">16</div><div class="st">تدفق العمل اليومي</div></div>
<div class="fl">🌅 صباحاً:
  الدكتور يشغّل Clinic MS.exe
  الاستقبال والمتدرب يفتحون المتصفح على IP الدكتور
  لوحة التحكم: مواعيد اليوم + إحصائيات

🦷 أثناء العمل:
  مريض يصل ←
  الاستقبال يفتح الموعد → POST /open-session
  الدكتور يضيف علاجات → POST /treatments/add
  الاستقبال يغلق الجلسة → POST /close-session
  ← تُنشأ فاتورة تلقائياً
  المريض يدفع ← تُوزَّع الدفعة على الفاتورة

🤖 تلقائياً في الخلفية:
  ← إشعارات Telegram/SMS/Email قبل 24 ساعة و 2 ساعة
  ← نسخة احتياطية كل 24 ساعة
  ← استلام تسجيلات مرضى جدد على Telegram Bot</div>
<div class="al as"><div class="ali">🎉</div><div>انتهى التوثيق الكامل! اضغط <strong>Ctrl+P ← Save as PDF</strong> لحفظه كـ PDF.</div></div>
</section>

</main>
</div>
<script>
const secs=document.querySelectorAll('.sc'),links=document.querySelectorAll('.ti');
new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting){links.forEach(l=>{l.style.color='';l.style.borderRightColor='transparent';l.style.background=''});const a=document.querySelector('.ti[href="#'+x.target.id+'"]');if(a){a.style.color='#1e40af';a.style.borderRightColor='#1e40af';a.style.background='#eff6ff'}}})},{threshold:0.2}).observe?secs.forEach(s=>new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting){links.forEach(l=>{l.style.color='';l.style.borderRightColor='transparent';l.style.background=''});const a=document.querySelector('.ti[href="#'+x.target.id+'"]');if(a){a.style.color='#1e40af';a.style.borderRightColor='#1e40af';a.style.background='#eff6ff'}}})},{threshold:0.2}).observe(s)):null;
</script>
</body>
</html>"""

with open("documentation.html", "w", encoding="utf-8") as f:
    f.write(HTML)

print("documentation.html created successfully!")
print(f"File size: {len(HTML)} characters")
