from pathlib import Path
import html
import json
import re
from datetime import date

TODAY = date.today().isoformat()
BASE = "https://chortkeh1.github.io/"

CITY_SECTIONS = {
    "accounting-auditing-kerman-province.html": ("استان کرمان", "خدمات حسابداری و مالی در سراسر استان کرمان با تمرکز بر شرکت‌های صنعتی و معدنی، پیمانکاران، بازرگانان و کسب‌وکارهای محلی؛ پوشش کرمان، سیرجان، رفسنجان، زرند، شهربابک، بم، جیرفت و سایر شهرستان‌ها."),
    "accounting-auditing-south-kerman.html": ("جنوب کرمان", "خدمات حسابداری، مالیاتی و بیمه‌ای برای کسب‌وکارهای جنوب کرمان، به‌ویژه جیرفت، کهنوج، قلعه‌گنج، منوجان، فاریاب و مناطق پیرامونی؛ متناسب با فعالیت‌های بازرگانی، کشاورزی، پیمانکاری و خدماتی."),
    "accounting-auditing-rafsanjan.html": ("رفسنجان", "خدمات حسابداری و مالیاتی در رفسنجان برای شرکت‌ها، واحدهای صنعتی، بازرگانی و کسب‌وکارها؛ با توجه به نیازهای گزارشگری، حقوق و دستمزد، اظهارنامه، بیمه و کنترل اسناد مالی."),
    "accounting-auditing-zarand.html": ("زرند", "خدمات حسابداری و مالی برای شرکت‌ها و واحدهای صنعتی و معدنی زرند؛ با تمرکز بر حسابداری صنعتی، بهای تمام‌شده، کنترل هزینه‌های تولید، مالیات، بیمه و گزارش‌های مدیریتی."),
    "accounting-auditing-shahrbabak.html": ("شهربابک و مس سرچشمه", "خدمات تخصصی حسابداری و مالی برای کسب‌وکارها، صنایع و زنجیره تأمین منطقه شهربابک و مس سرچشمه؛ شامل حسابداری، حسابرسی، مالیات، بیمه و گزارش‌های مدیریتی متناسب با فعالیت صنعتی و معدنی."),
    "accounting-auditing-bam.html": ("بم", "خدمات حسابداری و مالیاتی در بم برای شرکت‌ها و کسب‌وکارهای محلی؛ شامل ثبت و کنترل اسناد، گزارش‌های مالی، اظهارنامه، بیمه، حقوق و دستمزد و مشاوره مالی."),
    "accounting-auditing-jiroft.html": ("جیرفت", "خدمات حسابداری، مالیاتی و بیمه‌ای در جیرفت برای شرکت‌ها و کسب‌وکارهای جنوب کرمان؛ شامل گزارشگری مالی، اظهارنامه، حقوق و دستمزد، کنترل اسناد و مشاوره مالی."),
    "accounting-auditing-bardsir-baft-rabar.html": ("بردسیر، بافت و رابر", "خدمات حسابداری و مالیاتی برای شرکت‌ها و کسب‌وکارهای بردسیر، بافت و رابر؛ با پوشش حسابداری، مالیات، بیمه، حقوق و دستمزد، حسابرسی و مشاوره مالی."),
    "accounting-auditing-ravar-kuhbanan-pabdana.html": ("راور، کوهبنان و پابدانا", "خدمات حسابداری و مالی برای شرکت‌ها و واحدهای صنعتی و معدنی راور، کوهبنان و پابدانا؛ شامل حسابداری صنعتی، مالیات، بیمه، حقوق و دستمزد و گزارش‌های مدیریتی."),
    "accounting-auditing-kerman.html": ("شهر کرمان", "خدمات تخصصی حسابداری، حسابرسی، مالیاتی، بیمه و مشاوره مالی برای شرکت‌ها و کسب‌وکارهای شهر کرمان؛ شامل برون‌سپاری حسابداری، تهیه گزارش‌های مالی، حقوق و دستمزد، کنترل اسناد و استقرار سیستم‌های مالی."),
}

PAGE_LINKS = [
    ("accounting-auditing-kerman.html", "خدمات حسابداری و حسابرسی در شهر کرمان"),

    ("accounting-auditing-kerman-province.html", "خدمات حسابداری و حسابرسی در استان کرمان"),
    ("accounting-auditing-sirjan.html", "خدمات حسابداری و مالی در سیرجان"),
    ("accounting-auditing-rafsanjan.html", "خدمات حسابداری و مالی در رفسنجان"),
    ("accounting-auditing-zarand.html", "خدمات حسابداری و مالی در زرند"),
    ("accounting-auditing-shahrbabak.html", "خدمات حسابداری در شهربابک و مس سرچشمه"),
    ("accounting-auditing-bam.html", "خدمات حسابداری و مالیاتی در بم"),
    ("accounting-auditing-jiroft.html", "خدمات حسابداری و مالیاتی در جیرفت"),
    ("accounting-auditing-bardsir-baft-rabar.html", "خدمات حسابداری در بردسیر، بافت و رابر"),
    ("accounting-auditing-ravar-kuhbanan-pabdana.html", "خدمات حسابداری در راور، کوهبنان و پابدانا"),
    ("accounting-auditing-south-kerman.html", "خدمات حسابداری و مالیاتی در جنوب کرمان"),
    ("tax-return-kerman.html", "خدمات اظهارنامه و مالیات در کرمان"),
    ("article-mining-cost-accounting.html", "راهنمای بهای تمام‌شده در شرکت‌های معدنی"),
    ("article-contract-accounting.html", "راهنمای حسابداری پیمانکاری و صورت‌وضعیت"),
]

SITEMAP_PAGES = [
    "index.html", "accounting-auditing-kerman.html", "accounting-auditing-kerman-province.html", "accounting-auditing-sirjan.html",
    "accounting-auditing-rafsanjan.html", "accounting-auditing-zarand.html", "accounting-auditing-shahrbabak.html",
    "accounting-auditing-bardsir-baft-rabar.html", "accounting-auditing-ravar-kuhbanan-pabdana.html",
    "accounting-auditing-bam.html", "accounting-auditing-jiroft.html", "accounting-auditing-south-kerman.html",
    "news.html", "tax-return-kerman.html", "article-mining-cost-accounting.html", "article-contract-accounting.html",
]


def local_section(city, description):
    return f'''\n<section class="light" id="local-seo-services">\n<div class="wrap">\n<div class="title">\n<h2>خدمات حسابداری و مالی در {html.escape(city)}</h2>\n<div class="line"></div>\n<p>{html.escape(description)}</p>\n</div>\n<div class="card">\n<p><strong>خدمات متناسب با فعالیت مجموعه</strong></p>\n<p>چرتکه خدمات برون‌سپاری حسابداری، تهیه گزارش‌های مالی و مدیریتی، حقوق و دستمزد، اظهارنامه عملکرد، تبصره ماده ۱۰۰، سامانه مؤدیان، کنترل اسناد، امور بیمه‌ای و مشاوره مالی را متناسب با نوع فعالیت ارائه می‌کند.</p>\n<p>برای شرکت‌های صنعتی، معدنی و پیمانکاری، کنترل هزینه، بهای تمام‌شده، ساماندهی فرآیندهای مالی و استقرار نرم‌افزارهای حسابداری نیز در نظر گرفته می‌شود.</p>\n<div class="actions"><a class="btn btn-gold" href="tax-return-kerman.html">خدمات اظهارنامه و مالیات</a><a class="btn btn-outline" href="tel:09131989006">تماس با چرتکه</a></div>\n</div>\n</div>\n</section>\n'''


def replace_local_blocks(text, city, description):
    block = local_section(city, description)
    patterns = [
        r'<section\b[^>]*\bid=["\']local-seo-services["\'][\s\S]*?</section>\s*<section\b[^>]*\bid=["\']local-seo-2026["\'][\s\S]*?</section>',
        r'<section\b[^>]*\bid=["\']local-seo-services["\'][\s\S]*?</section>',
        r'<section\b[^>]*\bid=["\']local-seo-2026["\'][\s\S]*?</section>',
    ]
    for pattern in patterns:
        text2, n = re.subn(pattern, block, text, count=1, flags=re.I)
        if n:
            return text2, True
    return text, False


def related_links(current):
    links = [(p, label) for p, label in PAGE_LINKS if p != current and Path(p).exists()]
    items = ''.join(f'<li><a href="{html.escape(p)}">{html.escape(label)}</a></li>' for p, label in links[:9])
    return f'''\n<section class="light" id="seo-related-links">\n<div class="wrap">\n<div class="title">\n<h2>صفحات مرتبط</h2>\n<div class="line"></div>\n<p>برای دسترسی مستقیم به خدمات و مطالب مرتبط، صفحات زیر را ببینید.</p>\n</div>\n<ul style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px;list-style:none;margin:0;padding:0">\n{items}\n</ul>\n</div>\n</section>\n'''


def add_related_links(text, current):
    if 'id="seo-related-links"' in text:
        return text, False
    match = re.search(r'</body\s*>', text, flags=re.I)
    if not match:
        return text, False
    return text[:match.start()] + related_links(current) + text[match.start():], True


def fix_kerman_alias(text):
    original = text
    text = re.sub(r'<meta\s+name=["\']robots["\'][^>]*>', '<meta name="robots" content="index, follow, max-image-preview:large">', text, count=1, flags=re.I)
    text = re.sub(r'<link\s+rel=["\']canonical["\'][^>]*>', '<link rel="canonical" href="https://chortkeh1.github.io/accounting-auditing-kerman.html">', text, count=1, flags=re.I)
    return text, text != original

def add_home_articles(text):
    if 'id="seo-articles"' in text:
        return text, False
    block = '''\n<section class="light" id="seo-articles">\n<div class="wrap">\n<div class="title">\n<h2>مقالات کاربردی حسابداری و مالی</h2>\n<div class="line"></div>\n<p>مطالب آموزشی و کاربردی برای مدیران، حسابداران و شرکت‌های صنعتی، معدنی و پیمانکاری کرمان.</p>\n</div>\n<div class="grid3">\n<div class="card"><h3><a href="article-mining-cost-accounting.html">بهای تمام‌شده در شرکت‌های معدنی</a></h3><p>راهنمای کاربردی شناسایی هزینه‌های استخراج و تولید، هزینه‌یابی و گزارش‌های مدیریتی در شرکت‌های معدنی.</p></div>\n<div class="card"><h3><a href="article-contract-accounting.html">حسابداری پیمانکاری و صورت‌وضعیت</a></h3><p>اصول ثبت و کنترل عملیات مالی پیمانکاری، صورت‌وضعیت، هزینه‌های پروژه و گزارشگری برای مدیران.</p></div>\n</div>\n</div>\n</section>\n'''
    match = re.search(r'</body\s*>', text, flags=re.I)
    if not match:
        return text, False
    return text[:match.start()] + block + text[match.start():], True


def render_news_static(text):
    data_path = Path('news-data.json')
    if not data_path.exists() or 'id="newsStaticFallback"' in text:
        return text, False
    try:
        data = json.loads(data_path.read_text(encoding='utf-8'))
    except Exception:
        return text, False
    items = data.get('news') if isinstance(data, dict) else []
    if not isinstance(items, list) or not items:
        return text, False
    cards = []
    for item in items[:10]:
        title = html.escape(str(item.get('title') or 'خبر اقتصادی'))
        desc = html.escape(str(item.get('description') or item.get('summary') or ''))
        source = html.escape(str(item.get('source') or 'منبع خبری'))
        url = html.escape(str(item.get('url') or '#'), quote=True)
        cards.append(f'<article class="news-card"><span class="news-category">{source}</span><h2>{title}</h2><p>{desc}</p><a class="news-link" href="{url}" target="_blank" rel="noopener noreferrer">مشاهده خبر ←</a></article>')
    block = '<div id="newsStaticFallback" class="news-grid" aria-label="اخبار فعلی">' + ''.join(cards) + '</div>\n'
    marker = '<div id="newsGrid" class="news-grid" hidden></div>'
    if marker not in text:
        return text, False
    text = text.replace(marker, marker + block, 1)
    text = text.replace("status.hidden=true;grid.hidden=false;", "status.hidden=true;grid.hidden=false;document.getElementById('newsStaticFallback')?.remove();", 1)
    return text, True


def update_page(filename, city=None, description=None):
    path = Path(filename)
    if not path.exists():
        return False
    text = path.read_text(encoding='utf-8')
    original = text
    if city and description:
        text, _ = replace_local_blocks(text, city, description)
        text, _ = add_related_links(text, filename)
    if filename == 'accounting-auditing-kerman.html':
        text, _ = fix_kerman_alias(text)
    if filename == 'index.html':
        text, _ = add_home_articles(text)
    if filename == 'news.html':
        text, _ = render_news_static(text)
    if text != original:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def normalize_kerman_links():
    return []

def update_sitemap(changed_files):
    path = Path('sitemap.xml')
    existing = {}
    if path.exists():
        old = path.read_text(encoding='utf-8')
        for loc, lastmod in re.findall(r'<url>\s*<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>\s*</url>', old):
            existing[loc] = lastmod
    for filename in SITEMAP_PAGES:
        if not Path(filename).exists():
            continue
        loc = BASE + ('' if filename == 'index.html' else filename)
        if filename in changed_files or loc not in existing:
            existing[loc] = TODAY
    allowed = {BASE + ('' if p == 'index.html' else p) for p in SITEMAP_PAGES if Path(p).exists()}
    existing = {k: v for k, v in existing.items() if k in allowed}
    ordered = [BASE + ('' if p == 'index.html' else p) for p in SITEMAP_PAGES if Path(p).exists()]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', '']
    for loc in ordered:
        xml.append(f'  <url><loc>{loc}</loc><lastmod>{existing.get(loc, TODAY)}</lastmod></url>')
    xml += ['', '</urlset>', '']
    new = '\n'.join(xml)
    old = path.read_text(encoding='utf-8') if path.exists() else ''
    if new != old:
        path.write_text(new, encoding='utf-8')
        return True
    return False


if __name__ == '__main__':
    changed = []
    if update_page('index.html'):
        changed.append('index.html')
    if update_page('news.html'):
        changed.append('news.html')
    for filename, (city, desc) in CITY_SECTIONS.items():
        if update_page(filename, city, desc):
            changed.append(filename)
    changed.extend(normalize_kerman_links())
    if update_sitemap(changed):
        changed.append('sitemap.xml')
    print('SEO maintenance changed:', ', '.join(dict.fromkeys(changed)) if changed else 'no changes')
