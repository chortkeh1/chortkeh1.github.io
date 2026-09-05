from pathlib import Path
import re

for path in sorted(Path('.').glob('*.html')):
    text = path.read_text(encoding='utf-8')
    h1s = re.findall(r'<h1\b[^>]*>(.*?)</h1>', text, flags=re.I | re.S)
    cleaned = []
    for h in h1s:
        h = re.sub(r'<[^>]+>', ' ', h)
        h = re.sub(r'\s+', ' ', h).strip()
        cleaned.append(h)
    print(f'FILE: {path.name}')
    print(f'H1_COUNT: {len(cleaned)}')
    for i, h in enumerate(cleaned, 1):
        print(f'H1_{i}: {h}')
    print('---')
