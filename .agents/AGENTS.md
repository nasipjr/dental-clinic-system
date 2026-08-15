# Project Rules

- Always write technical terms in Arabic transliteration (e.g., لارافيل for Laravel, فلاسك for Flask, كومبوزر for Composer, مايجريشن for Migration, موديل for Model, بي اتش بي for PHP) within Arabic sentences to preserve RTL formatting.
- Keep exact English code and commands inside fenced code blocks.
- Admin login credentials for system testing/login: Username `admin`, Password `admin123`.
- **UI Design System Standard**:
  - Use the native application Arabic typography (`Cairo` / inherit font).
  - Use dark glassmorphism: 1px subtle tinted translucent border (`rgba(...)`), 8-15% translucent background fill, bright clear text/neon icon color matching the semantic role (sky blue, purple, amber, emerald, ruby red).
  - Header & Action buttons should be sleek pills (`border-radius: 50rem; padding: 4px 13px;`) or squircle action icons (`border-radius: 10px-12px;`) with smooth hover glow and slight lift (`transform: translateY(-1px)`).
  - **Standard Procedure Dropdown Selection**:
    - All procedure dropdown selectors must use categorized `<optgroup>` labels (e.g. `── فحص وتشخيص ──`, `── حشوات ومعالجات تجميلية ──`, `── علاج عصب وجذور ──`, `── جراحة وقلع ──`, `── تعويضات وتيجان ──`, `── تقويم أسنان ──`, `── أسنان أطفال ──`, `── إجراءات عامة وأخرى ──`).
    - Option labels must display the procedure name with formatted price and currency symbol: `اسم الإجراء (السعر ل.س)`.

