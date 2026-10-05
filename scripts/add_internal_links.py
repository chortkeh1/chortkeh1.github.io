from pathlib import Path
import html
import re

LINKS = [
    ("accounting-auditing-kerman.html", "خدمات حسابداری و حسابرسی در شهر کرمان"),
    ("accounting-auditing-kerman-province.html", "خدمات حسابداری و حسابرسی در استان کرمان"),
    ("accounting-auditing-sirjan.html", "خدمات حسابداری و مالی در سیرجان"),
    ("accounting-auditing-rafsanjan.html", "خدمات حسابداری و مالی در رفسنجان"),
    ("accounting-auditing-zarand.html", "خدمات حسابداری و مالی در زرند"),
    ("accounting-auditing-shahrbabak.html", "خدمات حسابداری در شهربابک و مس سرچشمه"),
    ("accounting-auditing-bardsir-baft-rabar.html", "خدمات حسابداری در بردسیر، بافت و رابر"),
    ("accounting-auditing-ravar-kuhbanan-pabdana.html", "خدمات حسابداری در راور، کوهبنان و پابدانا"),
    ("accounting-auditing-bam.html", "خدمات حسابداری و مالیاتی در بم"),
    ("accounting-auditing-jiroft.html", "خدمات حسابداری و مالیاتی در جیرفت"),
    ("accounting-auditing-south-kerman.html", "خدمات حسابداری و مالیاتی در جنوب کرمان"),
    ("tax-return-kerman.html", "خدمات اظهارنامه و مالیات در کرمان"),
    ("article-mining-cost-accounting.html", "بهای تمام‌شده در شرکت‌های معدنی"),
    ("article-contract-accounting.html", "حسابداری پیمانکاری و صورت‌وضعیت"),
]

STYLE = '''<style id="internal-links-style">
.internal-seo-links{margin:38px auto 0;padding:22px;background:#edf5f3;border:1px solid #d7e3e0;border-radius:12px}
.internal-seo-links h2{color:#174f4b;font-size:22px;margin:0 0 12px}
.internal-seo-links ul{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:9px;list-style:none;margin:0;padding:0}
.internal-seo-links a{display:block;padding:9px 12px;background:#fff;border-radius:8px;color:#126c66;font-weight:bold}
</style>'''

def section(current):
    items=[]
    for path,label in LINKS:
        if path==current or not Path(path).exists():
            continue
        items.append(f'<li><a href="{html.escape(path)}">{html.escape(label)}</a></li>')
    return ('<section class="internal-seo-links" id="internal-seo-links">'
            '<h2>خدمات و مطالب مرتبط</h2>'
            '<p>برای مطالعه خدمات و مطالب تخصصی مرتبط با حسابداری، مالیات، حسابرسی و فعالیت‌های صنعتی و پیمانکاری:</p>'
            '<ul>' + ''.join(items) + '</ul></section>')

for path in sorted(Path('.').glob('*.html')):
    text=path.read_text(encoding='utf-8')
    if 'id="internal-seo-links"' in text:
        continue
    match=re.search(r'</body\s*>', text, flags=re.I)
    if not match:
        continue
    if 'id="internal-links-style"' not in text:
        text=text.replace('</head>', STYLE+'\n</head>', 1)
    block=section(path.name)
    text=text[:match.start()]+block+'\n'+text[match.start():]
    path.write_text(text, encoding='utf-8')
    print('INTERNAL LINKS:', path.name)
