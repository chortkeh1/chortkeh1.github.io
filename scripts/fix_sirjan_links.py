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
<h2>خدمات تخصصی حسابداری و مالی در سیرجان و صنایع منطقه</h2>
<div class="line"></div>
<p>سیرجان یکی از مراکز مهم فعالیت‌های صنعتی، معدنی، فولادی، پیمانکاری و بازرگانی در استان کرمان است. چرتکه در این صفحه خدمات مالی و حسابداری متناسب با نیاز شرکت‌ها و کسب‌وکارهای سیرجان را معرفی می‌کند.</p>
</div>
<div class="card">
<h3>حسابداری شرکت‌های صنعتی، معدنی و فولادی سیرجان</h3>
<p>شرکت‌های فعال در سیرجان، به‌ویژه مجموعه‌های صنعتی و معدنی و زنجیره تأمین مرتبط با منطقه گل‌گهر، با حجم قابل توجهی از اسناد، قراردادها، خرید و فروش، حقوق و دستمزد و عملیات مالی روبه‌رو هستند. ثبت منظم اسناد، کنترل حساب‌ها، تفکیک مراکز هزینه و تهیه گزارش‌های مالی می‌تواند به مدیریت بهتر اطلاعات مالی کمک کند.</p>
<h3>خدمات مالیاتی، بیمه و حقوق و دستمزد</h3>
<p>خدمات مالیاتی و بیمه‌ای شرکت‌ها شامل رسیدگی به تکالیف قانونی، اظهارنامه‌های مالیاتی، امور سامانه مؤدیان، حقوق و دستمزد و موضوعات مرتبط با بیمه و تأمین اجتماعی است. نوع خدمت مورد نیاز هر مجموعه بر اساس ساختار و فعالیت همان شرکت تعیین می‌شود.</p>
<h3>حسابداری و مشاوره مالی برای شرکت‌های پیمانکاری سیرجان</h3>
<p>در شرکت‌های پیمانکاری، کنترل قراردادها، هزینه‌های پروژه، صورت‌وضعیت‌ها، اسناد خرید و پرداخت و گزارشگری مالی اهمیت ویژه‌ای دارد. برای مطالعه بیشتر، <a href="article-contract-accounting.html">راهنمای حسابداری پیمانکاری و صورت‌وضعیت</a> را نیز ببینید.</p>
<div class="actions"><a class="btn btn-gold" href="tax-return-kerman.html">خدمات اظهارنامه و مالیات</a><a class="btn btn-outline" href="tel:09131989006">تماس با چرتکه</a></div>
</div>
</div>
</section>
'''

# Replace an older local SEO block when it exists.
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

# If no dedicated Sirjan section exists, add it before the related-links block or body end.
if 'id="sirjan-local-seo"' not in text:
    related_pos = re.search(r'<section\b[^>]*\bid=["\']sirjan-related-links["\']', text, flags=re.I)
    if related_pos:
        text = text[:related_pos.start()] + unique_section + text[related_pos.start():]
    else:
        body_match = re.search(r'</body\s*>', text, flags=re.I)
        if body_match:
            text = text[:body_match.start()] + unique_section + text[body_match.start():]

if 'id="sirjan-related-links"' not in text:
    related = '''
<section class="light" id="sirjan-related-links">
<div class="wrap">
<div class="title">
<h2>صفحات مرتبط با خدمات مالی در استان کرمان</h2>
<div class="line"></div>
<p>برای دسترسی سریع‌تر به خدمات حسابداری، حسابرسی و مالیاتی چرتکه در شهرها و مناطق مختلف استان کرمان.</p>
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
    print('Sirjan SEO content and internal links updated.')
else:
    print('Sirjan SEO already up to date.')
