from pathlib import Path
import re

p = Path('accounting-auditing-kerman.html')
s = p.read_text(encoding='utf-8')

replacements = [
    (r'<title>\s*.*?\s*</title>', '<title>\nحسابداری و حسابرسی در شهر کرمان | خدمات مالی و مالیاتی چرتکه\n</title>'),
    (r'(<meta name="description"\s*\ncontent=").*?(">)', r'\1خدمات حسابداری، حسابرسی، مالیاتی، بیمه و مشاوره مالی برای شرکت‌ها، اصناف و کسب‌وکارهای شهر کرمان؛ همراه با خدمات نرم‌افزارهای مالی و مشاوره تخصصی چرتکه.\2'),
    (r'(<meta property="og:title"\s*\n\s*content=").*?(">)', r'\1حسابداری و حسابرسی در شهر کرمان | چرتکه\2'),
    (r'(<meta property="og:description"\s*\n\s*content=").*?(">)', r'\1خدمات تخصصی حسابداری، حسابرسی، مالیاتی، بیمه و مشاوره مالی برای شرکت‌ها و کسب‌وکارهای شهر کرمان.\2'),
    (r'(<meta name="twitter:title"\s*\n\s*content=").*?(">)', r'\1حسابداری و حسابرسی در شهر کرمان | چرتکه\2'),
    (r'(<meta name="twitter:description"\s*\n\s*content=").*?(">)', r'\1خدمات حسابداری، حسابرسی، مالیاتی، بیمه و مشاوره مالی در شهر کرمان.\2'),
]
for pattern, repl in replacements:
    s2, n = re.subn(pattern, repl, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'Expected exactly one match, got {n}: {pattern}')
    s = s2

p.write_text(s, encoding='utf-8')
print('SEO metadata finalized for accounting-auditing-kerman.html')
