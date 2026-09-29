from pathlib import Path
import re
from datetime import date

TODAY = date.today().isoformat()

CITY_SECTIONS = {
    "accounting-auditing-kerman.html": (
        "کرمان",
        "خدمات حسابداری و مالی در شهر کرمان برای شرکت‌ها، فروشگاه‌ها، پیمانکاران و کسب‌وکارهای محلی؛ شامل برون‌سپاری حسابداری، حقوق و دستمزد، اظهارنامه، تبصره ماده ۱۰۰، سامانه مؤدیان و مشاوره مالی."
    ),
    "accounting-auditing-kerman-province.html": (
        "استان کرمان",
        "خدمات مالی و حسابداری برای شرکت‌ها و کسب‌وکارهای استان کرمان با پوشش کرمان، سیرجان، رفسنجان، زرند، شهربابک، بم، جیرفت و سایر شهرستان‌ها؛ با تمرکز ویژه بر صنایع، معادن و شرکت‌های پیمانکاری."
    ),
    "accounting-auditing-south-kerman.html": (
        "جنوب کرمان",
        "خدمات حسابداری و مالیاتی برای کسب‌وکارهای جنوب کرمان، از جمله جیرفت، کهنوج، قلعه‌گنج، منوجان، فاریاب و اسفندقه؛ شامل حسابداری، اظهارنامه، بیمه، حقوق و دستمزد و مشاوره مالی."
    ),
    "accounting-auditing-rafsanjan.html": (
        "رفسنجان",
        "خدمات حسابداری و مالیاتی در رفسنجان برای شرکت‌ها، واحدهای صنعتی، بازرگانی و کسب‌وکارها؛ شامل برون‌سپاری حسابداری، اظهارنامه، بیمه، حقوق و دستمزد و گزارش‌های مدیریتی."
    ),
    "accounting-auditing-zarand.html": (
        "زرند",
        "خدمات حسابداری و مالی برای شرکت‌ها و واحدهای صنعتی و معدنی زرند؛ شامل حسابداری صنعتی، بهای تمام‌شده، مالیات، بیمه، حقوق و دستمزد و مشاوره مالی."
    ),
    "accounting-auditing-shahrbabak.html": (
        "شهربابک و مس سرچشمه",
        "خدمات تخصصی حسابداری و مالی برای کسب‌وکارها، صنایع و زنجیره تأمین منطقه شهربابک و مس سرچشمه؛ شامل حسابداری، مالیات، بیمه، حسابرسی و گزارش‌های مدیریتی."
    ),
    "accounting-auditing-bam.html": (
        "بم",
        "خدمات حسابداری و مالیاتی در بم برای شرکت‌ها و کسب‌وکارهای محلی؛ شامل ثبت اسناد، گزارش‌های مالی، اظهارنامه، بیمه، حقوق و دستمزد و مشاوره مالی."
    ),
    "accounting-auditing-jiroft.html": (
        "جیرفت",
        "خدمات حسابداری، مالیاتی و بیمه‌ای در جیرفت برای شرکت‌ها و کسب‌وکارهای جنوب کرمان؛ شامل اظهارنامه، حقوق و دستمزد، گزارش مالی و مشاوره مالی."
    ),
    "accounting-auditing-bardsir-baft-rabar.html": (
        "بردسیر، بافت و رابر",
        "خدمات حسابداری و مالیاتی برای شرکت‌ها و کسب‌وکارهای بردسیر، بافت و رابر؛ با پوشش حسابداری، مالیات، بیمه، حقوق و دستمزد و مشاوره مالی."
    ),
    "accounting-auditing-ravar-kuhbanan-pabdana.html": (
        "راور، کوهبنان و پابدانا",
        "خدمات حسابداری و مالی برای شرکت‌ها و واحدهای صنعتی و معدنی راور، کوهبنان و پابدانا؛ شامل حسابداری، مالیات، بیمه، حقوق و دستمزد و گزارش‌های مدیریتی."
    ),
}

PANORAMA_CSS = '''
<style id="chortkeh-clean-panorama-header">
header {
    background-image: url('kerman_panorama_clean.png') !important;
    background-position: center center !important;
    background-size: cover !important;
    background-repeat: no-repeat !important;
    background-color: transparent !important;
    border-bottom: 2px solid #d4af37 !important;
}
.nav {
    background: transparent !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
}
.nav nav a, header nav a {
    color: #102f2c !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    text-shadow: 0 1px 0 rgba(255,255,255,.98), 0 0 4px rgba(255,255,255,.92) !important;
}
.brand {
    color: #0f5f5a !important;
    font-weight: 900 !important;
    text-shadow: 0 1px 0 rgba(255,255,255,.98), 0 0 5px rgba(255,255,255,.9) !important;
}
.brand small {
    color: #102f2c !important;
    font-weight: 800 !important;
    text-shadow: 0 1px 0 rgba(255,255,255,.98), 0 0 4px rgba(255,255,255,.95) !important;
}
header .btn, header .btn-gold, .nav .btn, .nav .btn-gold {
    background: #0f5f5a !important;
    color: #fff !important;
    border: 2px solid #d4af37 !important;
    font-weight: 900 !important;
}
.logo {
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    mix-blend-mode: screen !important;
}
header::before, header::after, .nav::before, .nav::after {
    content: none !important;
    display: none !important;
}
</style>
'''


def local_section(city, description):
    return f'''\n<section class="light" id="local-seo-2026">\n<div class="wrap">\n<div class="title">\n<h2>خدمات حسابداری و مالی در {city}</h2>\n<div class="line"></div>\n<p>{description}</p>\n</div>\n<div class="card">\n<p><strong>مؤسسه حسابداری و حسابرسی چرتکه</strong> خدمات مالی، حسابداری، حسابرسی، مالیاتی و بیمه‌ای را متناسب با نوع فعالیت مجموعه ارائه می‌کند.</p>\n<p>خدمات قابل ارائه شامل برون‌سپاری حسابداری، تهیه گزارش‌های مالی و مدیریتی، حقوق و دستمزد، اظهارنامه عملکرد، تبصره ماده ۱۰۰، سامانه مؤدیان، کنترل اسناد و مشاوره مالی است.</p>\n<div class="actions"><a class="btn btn-gold" href="tax-return-kerman.html">خدمات اظهارنامه و مالیات</a><a class="btn btn-outline" href="tel:09131989006">تماس با چرتکه</a></div>\n</div>\n</div>\n</section>\n'''


def insert_before_body(text, block):
    if 'id="local-seo-2026"' in text:
        return text, False
    match = re.search(r'</body\s*>', text, flags=re.I)
    if match:
        return text[:match.start()] + block + text[match.start():], True
    match = re.search(r'</html\s*>', text, flags=re.I)
    if match:
        return text[:match.start()] + block + text[match.start():], True
    return text + block, True


def update_city_page(filename, city, description):
    path = Path(filename)
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    text, changed = insert_before_body(text, local_section(city, description))
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def update_homepage():
    path = Path("index.html")
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<style\s+id="chortkeh-clean-panorama-header">.*?</style>\s*', '', text, flags=re.S)
    head = re.search(r'</head\s*>', text, flags=re.I)
    if head:
        text = text[:head.start()] + PANORAMA_CSS + '\n' + text[head.start():]
    path.write_text(text, encoding="utf-8")
    return True


def refresh_sitemap():
    path = Path("sitemap.xml")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{TODAY}</lastmod>', text)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    changed = []
    if update_homepage():
        changed.append("index.html")
    for filename, (city, desc) in CITY_SECTIONS.items():
        if update_city_page(filename, city, desc):
            changed.append(filename)
    refresh_sitemap()
    print("SEO maintenance changed:", ", ".join(changed) if changed else "no page changes")
    print("Sitemap lastmod refreshed:", TODAY)
