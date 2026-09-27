from pathlib import Path
import re
from datetime import date

TODAY = date.today().isoformat()

CITY_SECTIONS = {
    "accounting-auditing-kerman.html": ("کرمان", "خدمات حسابداری، حسابرسی، مالیاتی و مشاوره مالی برای شرکت‌ها، فروشگاه‌ها، پیمانکاران و کسب‌وکارهای شهر کرمان؛ شامل برون‌سپاری حسابداری، حقوق و دستمزد، اظهارنامه و سامانه مؤدیان."),
    "accounting-auditing-kerman-province.html": ("استان کرمان", "خدمات مالی و حسابداری برای کسب‌وکارها و شرکت‌های استان کرمان با پوشش کرمان، سیرجان، رفسنجان، زرند، شهربابک، بم، جیرفت و سایر شهرستان‌ها؛ با تمرکز ویژه بر صنایع، معادن و شرکت‌های پیمانکاری."),
    "accounting-auditing-south-kerman.html": ("جنوب کرمان", "خدمات حسابداری و مالیاتی برای کسب‌وکارهای جنوب کرمان، از جمله جیرفت، کهنوج و شهرستان‌های منطقه؛ شامل حسابداری، اظهارنامه، بیمه، حقوق و دستمزد و مشاوره مالی."),
    "accounting-auditing-rafsanjan.html": ("رفسنجان", "خدمات حسابداری و مالیاتی در رفسنجان برای شرکت‌ها، واحدهای صنعتی، بازرگانی و کسب‌وکارها؛ شامل برون‌سپاری حسابداری، اظهارنامه، بیمه، حقوق و دستمزد و گزارش‌های مدیریتی."),
    "accounting-auditing-zarand.html": ("زرند", "خدمات حسابداری و مالی برای شرکت‌ها و واحدهای صنعتی و معدنی زرند؛ شامل حسابداری صنعتی، بهای تمام‌شده، مالیات، بیمه، حقوق و دستمزد و مشاوره مالی."),
    "accounting-auditing-shahrbabak.html": ("شهربابک و مس سرچشمه", "خدمات تخصصی حسابداری و مالی برای کسب‌وکارها، صنایع و زنجیره تأمین منطقه شهربابک و مس سرچشمه؛ شامل حسابداری، مالیات، بیمه، حسابرسی و گزارش‌های مدیریتی."),
    "accounting-auditing-bam.html": ("بم", "خدمات حسابداری و مالیاتی در بم برای شرکت‌ها و کسب‌وکارهای محلی؛ شامل ثبت اسناد، گزارش‌های مالی، اظهارنامه، بیمه، حقوق و دستمزد و مشاوره مالی."),
    "accounting-auditing-jiroft.html": ("جیرفت", "خدمات حسابداری، مالیاتی و بیمه‌ای در جیرفت برای شرکت‌ها و کسب‌وکارهای جنوب کرمان؛ شامل اظهارنامه، حقوق و دستمزد، گزارش مالی و مشاوره مالی."),
    "accounting-auditing-bardsir-baft-rabar.html": ("بردسیر، بافت و رابر", "خدمات حسابداری و مالیاتی برای شرکت‌ها و کسب‌وکارهای بردسیر، بافت و رابر؛ با پوشش حسابداری، مالیات، بیمه، حقوق و دستمزد و مشاوره مالی."),
    "accounting-auditing-ravar-kuhbanan-pabdana.html": ("راور، کوهبنان و پابدانا", "خدمات حسابداری و مالی برای شرکت‌ها و واحدهای صنعتی و معدنی راور، کوهبنان و پابدانا؛ شامل حسابداری، مالیات، بیمه، حقوق و دستمزد و گزارش‌های مدیریتی."),
}


def inject(path: Path, city: str, description: str):
    text = path.read_text(encoding="utf-8")
    marker = 'id="local-seo-2026"'
    if marker in text:
        return False

    section = f'''\n<section class="light" id="local-seo-2026">\n<div class="wrap">\n<div class="title">\n<h2>خدمات حسابداری و مالی در {city}</h2>\n<div class="line"></div>\n<p>{description}</p>\n</div>\n<div class="card">\n<p><strong>مؤسسه حسابداری و حسابرسی چرتکه</strong> خدمات مالی، حسابداری، حسابرسی، مالیاتی و بیمه‌ای را متناسب با نوع فعالیت مجموعه ارائه می‌کند.</p>\n<p>خدمات قابل ارائه شامل برون‌سپاری حسابداری، تهیه گزارش‌های مالی و مدیریتی، حقوق و دستمزد، اظهارنامه عملکرد، تبصره ماده ۱۰۰، سامانه مؤدیان، کنترل اسناد و مشاوره مالی است.</p>\n<div class="actions"><a class="btn btn-gold" href="tax-return-kerman.html">خدمات اظهارنامه و مالیات</a><a class="btn btn-outline" href="tel:09131989006">تماس با چرتکه</a></div>\n</div>\n</div>\n</section>\n'''

    pos = re.search(r'</main\\s*>', text, flags=re.I)
    if pos:
        text = text[:pos.start()] + section + text[pos.start():]
    else:
        pos = re.search(r'</body\\s*>', text, flags=re.I)
        if not pos:
            return False
        text = text[:pos.start()] + section + text[pos.start():]
    path.write_text(text, encoding="utf-8")
    return True


def refresh_sitemap():
    path = Path("sitemap.xml")
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{TODAY}</lastmod>', text)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    changed = []
    for filename, (city, desc) in CITY_SECTIONS.items():
        path = Path(filename)
        if path.exists() and inject(path, city, desc):
            changed.append(filename)
    refresh_sitemap()
    print("SEO pages updated:", ", ".join(changed) if changed else "no new page blocks")
    print("Sitemap lastmod refreshed:", TODAY)
