from pathlib import Path
import re

BLOCK_RE = re.compile(r'\s*<section class="internal-seo-links" id="internal-seo-links">.*?</section>\s*', re.I | re.S)

for path in sorted(Path('.').glob('*.html')):
    text = path.read_text(encoding='utf-8')
    if 'id="internal-seo-links"' not in text:
        continue
    block_match = BLOCK_RE.search(text)
    if not block_match:
        continue
    block = block_match.group(0).strip()
    text = BLOCK_RE.sub('\n', text, count=1)
    footer = re.search(r'<footer\b', text, flags=re.I)
    if footer:
        text = text[:footer.start()] + '\n' + block + '\n' + text[footer.start():]
    else:
        end = re.search(r'</body\s*>', text, flags=re.I)
        if end:
            text = text[:end.start()] + '\n' + block + '\n' + text[end.start():]
        else:
            continue
    path.write_text(text, encoding='utf-8')
    print('REPAIRED:', path.name)
