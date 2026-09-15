# Trigger the one-time redesign workflow.
from pathlib import Path
import re

INDEX = Path("index.html")

s = INDEX.read_text(encoding="utf-8")

s = re.sub(
    r'\s*<p class="sirjan-context">.*?</p>\s*',
    '\n\n',
    s,
    flags=re.S,
)

s = s.replace("آخرین اخبار حسابداری، مالیاتی و اقتصادی", "اخبار و رویدادهای اقتصادی", 1)
s = s.replace(
    "جدیدترین اخبار حسابداری، مالیات، بیمه،\nاقتصاد، صنعت، معدن و اخبار اقتصادی کرمان",
    "آخرین اخبار منتخب اقتصادی، صنعتی، معدنی و مالی از منابع معتبر ایران و کرمان",
    1,
)

cities_match = re.search(
    r'<!-- =====================================================\n     CITIES\n===================================================== -->.*?(?=<!-- =====================================================\n     SOFTWARE\n===================================================== -->)',
    s,
    flags=re.S,
)
news_match = re.search(
    r'<!-- =====================================================\n     LATEST NEWS\n===================================================== -->.*?(?=<!-- =====================================================\n     CONTACT\n===================================================== -->)',
    s,
    flags=re.S,
)

if not cities_match or not news_match:
    raise SystemExit("Required homepage blocks were not found")

cities_block = cities_match.group(0).strip() + "\n\n"
news_block = news_match.group(0).strip() + "\n\n"
s = s.replace(cities_match.group(0), "", 1)
s = s.replace(news_match.group(0), "", 1)

services_marker = "<!-- =====================================================\n     SERVICES\n===================================================== -->"
if services_marker not in s:
    raise SystemExit("SERVICES marker not found")
s = s.replace(services_marker, cities_block + news_block + services_marker, 1)

visual_css = r'''

/* =====================================================
   MODERN REFERENCE-STYLE VISUAL LAYER
===================================================== */
body { background:#f7faf9; color:#263b38; }
header { background:linear-gradient(135deg,#073d39,#0b2422); border-bottom:2px solid #d4af37; }
.hero { position:relative; overflow:hidden; padding:58px 0 42px; color:#173f3b; background:radial-gradient(circle at 14% 18%,#d4af3720,transparent 30%),radial-gradient(circle at 88% 20%,#168b8420,transparent 32%),linear-gradient(180deg,#fbfdfc 0%,#eef6f4 100%); border-bottom:0; }
.hero::before { content:""; position:absolute; left:-5%; right:-5%; bottom:-46px; height:170px; background:#dbeae720; clip-path:polygon(0 72%,10% 48%,18% 63%,29% 25%,39% 58%,51% 18%,61% 55%,72% 30%,82% 61%,91% 38%,100% 58%,100% 100%,0 100%); }
.hero::after { content:""; position:absolute; left:-5%; right:-5%; bottom:-62px; height:150px; background:#b8d3ce25; clip-path:polygon(0 72%,13% 56%,24% 70%,36% 42%,47% 67%,58% 34%,70% 66%,81% 48%,91% 67%,100% 51%,100% 100%,0 100%); }
.hero-grid { position:relative; z-index:2; grid-template-columns:1fr; gap:18px; text-align:center; }
.hero > .wrap > div:first-child { display:flex; flex-direction:column; align-items:center; }
.hero .gold { color:#a67d14; font-weight:700; font-size:17px; }
.hero h1 { color:#104f4b; font-size:42px; line-height:1.55; margin:10px 0; }
.hero h1 .gold { color:#104f4b; }
.hero p { color:#60716d; max-width:850px; margin:0 auto; font-size:17px; }
.hero .actions { justify-content:center; }
.hero-card { background:transparent; border:0; box-shadow:none; padding:10px 0 0; }
.hero-card h2 { color:#174f4b; font-size:22px; margin:0 0 12px; }
.hero-card ul { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; max-width:980px; margin:auto; }
.hero-card li { color:#31504b; background:#ffffffdd; border:1px solid #d5e3e0; border-radius:12px; padding:11px 10px; box-shadow:0 5px 18px #174f4b10; }
#cities { background:linear-gradient(180deg,#eef6f4 0%,#f9fbfa 100%); padding-top:58px; padding-bottom:62px; }
#cities .title h2 { color:#174f4b; }
#cities .title p { color:#66736f; }
.cities { grid-template-columns:repeat(4,1fr); gap:14px; }
.city { min-height:72px; display:flex; align-items:center; justify-content:center; gap:8px; padding:14px 10px; border:1px solid #d5e3e0; border-radius:13px; background:#fff; color:#31504b; font-size:16px; font-weight:600; box-shadow:0 5px 18px #174f4b10; }
.city::before { font-size:21px; line-height:1; }
.city:nth-child(1)::before{content:"📍"}.city:nth-child(2)::before{content:"🏙️"}.city:nth-child(3)::before{content:"🏭"}.city:nth-child(4)::before{content:"⛏️"}.city:nth-child(5)::before{content:"⛰️"}.city:nth-child(6)::before{content:"⛏️"}.city:nth-child(7)::before{content:"🏗️"}.city:nth-child(8)::before{content:"🌴"}.city:nth-child(9)::before{content:"🏔️"}.city:nth-child(10)::before{content:"⚙️"}.city:nth-child(11)::before{content:"☀️"}
.city:hover { border-color:#4daea7; background:#fff; color:#0d6d66; transform:translateY(-3px); box-shadow:0 10px 24px #174f4b18; }
#news { background:#eef6f4; padding:42px 0 62px; }
#news > .wrap { background:#f5faf9cc; border:1px solid #dbe8e5; border-radius:24px; padding:30px 28px 34px; box-shadow:0 8px 30px #174f4b0d; }
#news .title { margin-bottom:28px; }
#news .title h2 { color:#174f4b; }
#news .title p { color:#66736f; }
.news-grid { grid-template-columns:repeat(3,1fr); gap:16px; }
.news-card { border-radius:15px; border:1px solid #d6e3e0; padding:20px; box-shadow:0 5px 18px #174f4b10; }
.news-card h3 { color:#174f4b; }
.news-category { background:#e4f2ef; color:#126c66; }
@media(max-width:900px){.hero h1{font-size:35px}.hero-card ul{grid-template-columns:1fr 1fr}.cities{grid-template-columns:1fr 1fr}.news-grid{grid-template-columns:1fr 1fr}#news>.wrap{padding:25px 18px 28px}}
@media(max-width:560px){.hero{padding:48px 0 35px}.hero h1{font-size:29px}.hero p{font-size:16px}.hero-card ul{grid-template-columns:1fr}.cities{grid-template-columns:1fr}.news-grid{grid-template-columns:1fr}#news>.wrap{border-radius:18px;padding:20px 12px 24px}}
'''

if visual_css.strip() not in s:
    s = s.replace("</style>", visual_css + "\n</style>", 1)

INDEX.write_text(s, encoding="utf-8")
print("index.html redesigned successfully")
