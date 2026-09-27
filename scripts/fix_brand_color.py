from pathlib import Path
import re

CSS = '''<style id="chortkeh-brand-color-fix">
/* Make the Chortkeh wordmark clearly visible over the panorama. */
.brand {
    color: #0f5f5a !important;
    font-weight: 900 !important;
    text-shadow:
        0 1px 0 rgba(255,255,255,.98),
        0 0 3px rgba(255,255,255,.95),
        0 0 7px rgba(255,255,255,.75) !important;
}

.brand small {
    color: #173d39 !important;
    font-weight: 800 !important;
    text-shadow:
        0 1px 0 rgba(255,255,255,.98),
        0 0 4px rgba(255,255,255,.9) !important;
}
</style>'''

path = Path("index.html")
text = path.read_text(encoding="utf-8")

text = re.sub(
    r'<style\s+id="chortkeh-brand-color-fix">.*?</style>\s*',
    '',
    text,
    flags=re.S,
)

text = re.sub(r'</head>', CSS + '\n</head>', text, count=1, flags=re.I)
path.write_text(text, encoding="utf-8")
print("Brand color fixed successfully.")
