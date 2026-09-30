from pathlib import Path
import re

PATH = Path('accounting-auditing-sirjan.html')
if not PATH.exists():
    raise SystemExit('Sirjan page not found')

text = PATH.read_text(encoding='utf-8')
original = text

unique_section = '''
<section class="light" id="sirjan-local-seo">
<div class="wrap">
<div class="title">
<h2>خدمات حسابداری و مالی در سیرجان و صنایع منطقه</h2>
<div class="line"></div>
<p>چرتکه در سیرجان به شرکت‌های صنعتی، معدنی، فولادی، پیمانکاری، بازرگانی و کسب‌وکارهای محلی در زمینه حسابداری، حسابرسی، مالیات، بیمه، حقوق و دستمزد و گزارش‌های مدیریتی خدمات ارائه می‌کند.</p>
</div>
<div class="card">
<p>برای مجموعه‌هایی که با صنایع و معادن سیرجان و گل‌گهر، پیمانکاران و زنجیره تأمین منطقه همکاری دارند، تفکیک مراکز هزینه، کنترل اسناد، گزارشگری مالی و ساماندهی فرآیندهای مالی اهمیت ویژه‌ای دارد.</p>
<p>خدمات اظهارنامه عملکرد، تبصره ماده ۱۰۰، سامانه مؤدیان، کنترل حقوق و دستمزد و مشاوره مالی نیز متناسب با نوع فعالیت قابل ارائه است.</p>
<div class="actions"><a class="btn btn-gold" href="tax-return-kerman.html">خدمات اظهارنامه و مالیات</a><a class="btn btn-outline" href="tel:09131989006">تماس با چرتکه</a></div>
</div>
</div>
</section>
'''

# Replace the old duplicated/local block if present; otherwise add the unique block.
patterns = [
    r'<section\b[^>]*\bid=["\']local-seo-services["\'][\s\S]*?</section>\s*<section\b[^>]*\bid=["\']local-seo-2026["\'][\s\S]*?</section>',
    r'<section\b[^>]*\bid=["\']local-seo-services["\'][\s\S]*?</section>',
    r'<section\b[^>]*\bid=["\']local-seo-2026["\'][\s\S]*?</section>',
]
for pattern in patterns:
    text2, count = re.subn(pattern, unique_section, text, count=1, flags=re.I)
    if count:
        text = text2
        break

if 'id="sirjan-related-links"' not in text:
    related = '''
<section class="light" id="sirjan-related-links">
<div class="wrap">
<div class="title">
<h2>صفحات مرتبط</h2>
<div class="line"></div>
<p>صفحات مرتبط با خدمات مالی، حسابداری و مالیاتی چرتکه در استان کرمان.</p>
</div>
<ul style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px;list-style:none;margin:0;padding:0">
<li><a href="accounting-auditing-kerman-province.html">خدمات حسابداری در استان کرمان</a></li>
<li><a href="accounting-auditing-rafsanjan.html">خدمات حسابداری در رفسنجان</a></li>
<li><a href="accounting-auditing-zarand.html">خدمات حسابداری در زرند</a></li>
<li><a href="accounting-auditing-shahrbabak.html">خدمات حسابداری در شهربابک و مس سرچشمه</a></li>
<li><a href="accounting-auditing-bam.html">خدمات حسابداری در بم</a></li>
<li><a href="accounting-auditing-jiroft.html">خدمات حسابداری در جیرفت</a></li>
<li><a href="accounting-auditing-south-kerman.html">خدمات حسابداری در جنوب کرمان</a></li>
<li><a href="article-mining-cost-accounting.html">راهنمای بهای تمام‌شده در شرکت‌های معدنی</a></li>
<li><a href="article-contract-accounting.html">راهنمای حسابداری پیمانکاری و صورت‌وضعیت</a></li>
</ul>
</div>
</section>
'''
    match = re.search(r'</body\s*>', text, flags=re.I)
    if match:
        text = text[:match.start()] + related + text[match.start():]

if text != original:
    PATH.write_text(text, encoding='utf-8')
    print('Sirjan SEO links/content updated.')
else:
    print('Sirjan SEO already up to date.')
