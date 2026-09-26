from pathlib import Path
import re

TAX_SECTION = '''<section class="light" id="urgent-tax-campaign">
<div class="wrap">
<div class="card" style="border-right:6px solid #d4af37;">
<h2>آخرین فرصت ثبت اظهارنامه عملکرد اشخاص حقیقی و تبصره ماده ۱۰۰</h2>
<p><strong>مهلت مهم:</strong> مهلت تسلیم اظهارنامه عملکرد اشخاص حقیقی و تکمیل فرم مالیات مقطوع تبصره ماده ۱۰۰ برای عملکرد سال ۱۴۰۴ تا پایان روز <strong>۳۰ آبان ۱۴۰۵</strong> تمدید شده است.</p>
<p><strong>خدمات چرتکه:</strong> ثبت و آماده‌سازی اظهارنامه عملکرد اشخاص حقیقی، بررسی و تکمیل فرم تبصره ماده ۱۰۰، کنترل اطلاعات مالی، مشاوره مالیاتی و بررسی اسناد و مدارک.</p>
<div class="actions"><a class="btn btn-gold" href="tax-return-kerman.html">ثبت اظهارنامه عملکرد و تبصره ماده ۱۰۰</a><a class="btn btn-outline" href="tel:09131989006">تماس فوری 09131989006</a></div>
</div>
</div>
</section>'''

PANORAMA_CSS = '''
<style id="chortkeh-clean-panorama-header">
header {
    min-height: 0 !important;
    height: auto !important;
    background-image: url('kerman_panorama_clean.png') !important;
    background-position: center center !important;
    background-size: cover !important;
    background-repeat: no-repeat !important;
    border-bottom: 2px solid #d4af37 !important;
}
.nav {
    min-height: 78px !important;
    height: auto !important;
    padding: 4px 0 !important;
    background: transparent !important;
    border-bottom: 0 !important;
    border-radius: 0 !important;
    backdrop-filter: none !important;
}
.nav nav a {
    color: #173d39 !important;
    text-shadow: 0 1px 2px rgba(255,255,255,.9), 0 0 4px rgba(255,255,255,.65) !important;
}
.nav nav a:hover {
    color: #0f5f5a !important;
}
.brand small {
    color: #173d39 !important;
    text-shadow: 0 1px 2px rgba(255,255,255,.9), 0 0 4px rgba(255,255,255,.65) !important;
}
.logo {
    mix-blend-mode: lighten !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
</style>
'''

SIRJAN_SECTION = '''<section class="light" id="sirjan-industrial-accounting">
<div class="wrap">
<div class="title">
<h2>خدمات حسابداری و مالی شرکت‌های صنعتی و معدنی سیرجان</h2>
<div class="line"></div>
<p>خدمات تخصصی برای شرکت‌های فعال در سیرجان، گل‌گهر، صنایع فولادی، معدنی، پیمانکاری و زنجیره تأمین.</p>
</div>
<div class="card">
<p><strong>چرتکه در سیرجان</strong> خدمات حسابداری، حسابرسی، مالیاتی، بیمه و مشاوره مالی را برای شرکت‌ها و کسب‌وکارهای فعال در حوزه‌های صنعتی و معدنی ارائه می‌کند.</p>
<p>از جمله خدمات قابل ارائه می‌توان به برون‌سپاری حسابداری، تهیه گزارش‌های مالی و مدیریتی، حقوق و دستمزد، کنترل اسناد، رسیدگی حسابرسی، اظهارنامه‌های مالیاتی، سامانه مؤدیان و مشاوره مالی اشاره کرد.</p>
<div class="actions">
<a class="btn btn-gold" href="tax-return-kerman.html">خدمات مالیاتی و اظهارنامه</a>
<a class="btn btn-outline" href="tel:09131989006">تماس با چرتکه در سیرجان</a>
</div>
</div>
</div>
</section>'''


def update_homepage():
    path = Path("index.html")
    text = path.read_text(encoding="utf-8")

    pattern = r'<section\s+class="light"\s+id="urgent-tax-campaign">.*?</section>'
    if re.search(pattern, text, flags=re.S):
        text = re.sub(pattern, TAX_SECTION, text, count=1, flags=re.S)
    else:
        match = re.search(r'<main\b[^>]*>', text, flags=re.I)
        if match:
            pos = match.end()
            text = text[:pos] + "\n" + TAX_SECTION + "\n" + text[pos:]
        else:
            body_match = re.search(r'<body\b[^>]*>', text, flags=re.I)
            if not body_match:
                raise RuntimeError("Homepage body element not found")
            pos = body_match.end()
            text = text[:pos] + "\n" + TAX_SECTION + "\n" + text[pos:]

    text = re.sub(r'<style\s+id="chortkeh-clean-panorama-header">.*?</style>\s*', '', text, flags=re.S)
    if '</head>' in text.lower():
        text = re.sub(r'</head>', PANORAMA_CSS + '\n</head>', text, count=1, flags=re.I)
    else:
        text = PANORAMA_CSS + text
    path.write_text(text, encoding="utf-8")


def update_sirjan():
    path = Path("accounting-auditing-sirjan.html")
    text = path.read_text(encoding="utf-8")

    # Update existing SEO descriptions when present; do not fail if wording changed.
    text = re.sub(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])[^"\']*(["\'])',
        r'\1مؤسسه حسابداری و حسابرسی چرتکه در سیرجان؛ ارائه خدمات حسابداری، حسابرسی، مالیاتی، بیمه و مشاوره مالی برای شرکت‌های صنعتی، معدنی، فولادی، پیمانکاری و بازرگانی در سیرجان و گل‌گهر.\2',
        text, count=1, flags=re.I
    )

    if 'id="sirjan-industrial-accounting"' not in text:
        main_end = re.search(r'</main\s*>', text, flags=re.I)
        if main_end:
            text = text[:main_end.start()] + SIRJAN_SECTION + "\n" + text[main_end.start():]
        else:
            body_end = re.search(r'</body\s*>', text, flags=re.I)
            if body_end:
                text = text[:body_end.start()] + SIRJAN_SECTION + "\n" + text[body_end.start():]
            else:
                raise RuntimeError("Sirjan body end not found")

    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    update_homepage()
    update_sirjan()
    print("Site fixes applied successfully.")
