from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]

# Fix known broken internal links on the province page.
province = root / "accounting-auditing-kerman-province.html"
text = province.read_text(encoding="utf-8")
replacements = {
    'href="accounting-auditing-rafanjan.html"': 'href="accounting-auditing-rafsanjan.html"',
    'href="accounting-auditing-ravar-kohbanan-pabdana.html"': 'href="accounting-auditing-ravar-kuhbanan-pabdana.html"',
}
for old, new in replacements.items():
    text = text.replace(old, new)
province.write_text(text, encoding="utf-8")

# Improve the Kerman city page's links to pages that already exist.
kerman = root / "accounting-auditing-kerman.html"
text = kerman.read_text(encoding="utf-8")
city_links = {
    '<a class="city" href="#contact">کهنوج</a>': '<a class="city" href="accounting-auditing-south-kerman.html">کهنوج</a>',
    '<a class="city" href="#contact">فهرج</a>': '<a class="city" href="accounting-auditing-bam.html">فهرج</a>',
    '<a class="city" href="#contact">عنبرآباد</a>': '<a class="city" href="accounting-auditing-jiroft.html">عنبرآباد</a>',
    '<a class="city" href="#contact">منوجان</a>': '<a class="city" href="accounting-auditing-south-kerman.html">منوجان</a>',
    '<a class="city" href="#contact">قلعه‌گنج</a>': '<a class="city" href="accounting-auditing-south-kerman.html">قلعه‌گنج</a>',
    '<a class="city" href="#contact">رودبار جنوب</a>': '<a class="city" href="accounting-auditing-south-kerman.html">رودبار جنوب</a>',
}
for old, new in city_links.items():
    text = text.replace(old, new)
# The pages already exist, so remove the outdated statement saying they will be created later.
text = text.replace(
    'در مراحل بعد، برای شهرهای مهم استان\nصفحات اختصاصی و محتوای تخصصی ایجاد خواهد شد.',
    'برای شهرهای مهم استان، صفحات اختصاصی و محتوای تخصصی در دسترس است.'
)
kerman.write_text(text, encoding="utf-8")

subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
subprocess.run(["git", "add", "accounting-auditing-kerman-province.html", "accounting-auditing-kerman.html"], cwd=root, check=True)
subprocess.run(["git", "commit", "-m", "Fix internal links and city references"], cwd=root, check=True)
subprocess.run(["git", "rm", ".github/workflows/internal-links-once.yml", "scripts/internal_links_once.py"], cwd=root, check=True)
subprocess.run(["git", "commit", "-m", "Remove one-time internal link workflow"], cwd=root, check=True)
subprocess.run(["git", "push"], cwd=root, check=True)
