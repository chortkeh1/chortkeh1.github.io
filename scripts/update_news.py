# ============================================================
# Chortkeh News Updater - balanced multi-source RSS
# ============================================================
import html
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser

OUTPUT_FILE = "news-data.json"
MAX_NEWS = 30
MAX_PER_SOURCE_FETCH = 8
MAX_AGE_DAYS = 14

SOURCES = [
    {"name": "اقتصاد کرمان", "feed": "https://news.google.com/rss/search?q=site%3Aeghtesadkerman.ir&hl=fa&gl=IR&ceid=IR%3Afa", "local": True},
    {"name": "اتاق بازرگانی کرمان", "feed": "https://news.google.com/rss/search?q=site%3Aotagh-bazargani.com&hl=fa&gl=IR&ceid=IR%3Afa", "local": True},
    {"name": "خبرگزاری تسنیم", "feed": "https://www.tasnimnews.com/fa/rss/feed/0/8/0/%D8%A7%D9%82%D8%AA%D8%B5%D8%A7%D8%AF", "local": False},
    {"name": "خبرگزاری ایسنا", "feed": "https://www.isna.ir/rss", "local": False},
    {"name": "خبرگزاری مهر", "feed": "https://www.mehrnews.com/rss", "local": False},
    {"name": "باشگاه خبرنگاران جوان", "feed": "https://www.yjc.ir/fa/rss/allnews", "local": False},
    {"name": "تابناک", "feed": "https://www.tabnak.ir/fa/rss/allnews", "local": False},
    {"name": "خبرآنلاین", "feed": "https://www.khabaronline.ir/rss", "local": False},
    {"name": "عصر ایران", "feed": "https://www.asriran.com/fa/rss/allnews", "local": False},
    {"name": "دنیای اقتصاد", "feed": "https://donya-e-eqtesad.com/rss", "local": False},
]

KEYWORDS = [
    "اقتصاد", "اقتصادی", "تجارت", "بازرگانی", "صنعت", "صنایع", "معدن", "معادن",
    "فولاد", "مس", "آهن", "تولید", "کارخانه", "پیمانکاری", "سرمایه گذاری", "سرمایه‌گذاری",
    "بانک", "بانکی", "بورس", "سهام", "ارز", "دلار", "طلا", "تورم", "بودجه", "وام",
    "تسهیلات", "مالیات", "مالیاتی", "اظهارنامه", "سامانه مؤدیان", "ارزش افزوده", "بیمه",
    "تأمین اجتماعی", "تامین اجتماعی", "حسابداری", "حسابرسی", "حقوق و دستمزد", "کرمان", "سیرجان",
    "رفسنجان", "زرند", "شهربابک", "سرچشمه", "بم", "جیرفت", "کهنوج", "بردسیر", "بافت", "رابر",
    "راور", "کوهبنان", "پابدانا", "گل گهر", "گل‌گهر"
]

BLOCKED = ["facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com"]
JUNK = ["پادکست", "شماره ", "شمارهٔ", "استخدام مدیر دفتر", "استخدام نماینده"]

def clean_text(value):
    if not value:
        return ""
    value = html.unescape(re.sub(r"<[^>]+>", " ", str(value)))
    return re.sub(r"\s+", " ", value).strip()

def parse_date(entry):
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            try:
                dt = parsedate_to_datetime(value)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        value = entry.get(key)
        if value:
            try:
                from calendar import timegm
                return datetime.fromtimestamp(timegm(value), tz=timezone.utc)
            except Exception:
                pass
    return None

def safe_url(url):
    if not url:
        return ""
    url = str(url).strip()
    if not (url.startswith("https://") or url.startswith("http://")):
        return ""
    if any(domain in url.lower() for domain in BLOCKED):
        return ""
    return url

def is_relevant(title, summary, local):
    title_l = title.lower()
    text_l = f"{title} {summary}".lower()
    economic = [
        "اقتصاد", "اقتصادی", "تجارت", "بازرگانی", "صنعت", "صنایع", "معدن", "معادن",
        "فولاد", "مس", "آهن", "تولید", "کارخانه", "پیمانکاری", "سرمایه", "بانک", "بانکی",
        "بورس", "سهام", "ارز", "دلار", "طلا", "تورم", "بودجه", "وام", "تسهیلات", "مالیات",
        "مالیاتی", "اظهارنامه", "سامانه مؤدیان", "ارزش افزوده", "بیمه", "تأمین اجتماعی",
        "تامین اجتماعی", "حسابداری", "حسابرسی", "حقوق و دستمزد", "بازار", "قیمت", "صادرات", "واردات",
        "سرمایه‌گذاری", "سرمایه گذاری", "هزینه", "درآمد"
    ]
    local_terms = ["کرمان", "سیرجان", "رفسنجان", "زرند", "شهربابک", "سرچشمه", "بم", "جیرفت", "کهنوج", "بردسیر", "بافت", "رابر", "راور", "کوهبنان", "پابدانا", "گل گهر", "گل‌گهر"]
    junk = ["پادکست", "شماره ", "شمارهٔ", "استخدام مدیر دفتر", "استخدام نماینده", "فوتبال", "استقلال", "پرسپولیس", "سینما", "فیلم", "بازیگر", "موسیقی", "ورزش", "سلامت", "پزشکی", "حوادث", "جنایی"]
    if len(title) < 12 or any(x in title for x in junk):
        return False
    has_economic_title = any(k in title_l for k in economic)
    has_economic_text = any(k in text_l for k in economic)
    has_local = any(k in text_l for k in local_terms)
    return has_economic_title

def fetch_source(source):
    print(f"[SOURCE] {source['name']} -> {source['feed']}")
    parsed = feedparser.parse(source["feed"])
    if not parsed.entries:
        print("  [FAIL] no entries")
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    items, seen = [], set()
    for entry in parsed.entries:
        title = clean_text(entry.get("title"))
        summary = clean_text(entry.get("summary") or entry.get("description"))
        url = safe_url(entry.get("link"))
        published = parse_date(entry)
        if not title or not url or not published or published < cutoff:
            continue
        if not is_relevant(title, summary, source.get("local", False)):
            continue
        key = re.sub(r"\W+", " ", title.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "title": title,
            "description": summary[:450],
            "url": url,
            "source": source["name"],
            "date": published.isoformat(),
        })
    items.sort(key=lambda x: x["date"], reverse=True)
    print(f"  [OK] {len(items[:MAX_PER_SOURCE_FETCH])} relevant fresh items")
    return items[:MAX_PER_SOURCE_FETCH]

def main():
    by_source = defaultdict(list)
    successful = 0
    failed = 0
    for source in SOURCES:
        try:
            items = fetch_source(source)
            if items:
                successful += 1
                by_source[source["name"]].extend(items)
            else:
                failed += 1
        except Exception as exc:
            failed += 1
            print(f"  [ERROR] {source['name']}: {type(exc).__name__}: {exc}")

    seen_titles = set()
    for source_name in list(by_source):
        clean = []
        for item in by_source[source_name]:
            key = re.sub(r"\W+", " ", item["title"].lower()).strip()
            if key not in seen_titles:
                seen_titles.add(key)
                clean.append(item)
        by_source[source_name] = clean

    ordered_sources = [s["name"] for s in SOURCES if by_source.get(s["name"])]
    final_news = []
    cursor = 0
    while len(final_news) < MAX_NEWS and ordered_sources:
        added = False
        for source_name in ordered_sources:
            items = by_source[source_name]
            if cursor < len(items) and len(final_news) < MAX_NEWS:
                final_news.append(items[cursor])
                added = True
        if not added:
            break
        cursor += 1

    final_news.sort(key=lambda x: x["date"], reverse=True)

    # FINAL HEADLINE SANITY FILTER v3
    economic_title_terms = [
        "اقتصاد", "اقتصادی", "تجارت", "بازرگانی", "صنعت", "صنایع", "معدن", "معادن",
        "فولاد", "تولید", "کارخانه", "پیمانکاری", "سرمایه", "سرمایه‌گذاری", "سرمایه گذاری",
        "بانک", "بانکی", "بورس", "سهام", "ارز", "دلار", "طلا", "تورم", "بودجه", "وام",
        "تسهیلات", "مالیات", "مالیاتی", "اظهارنامه", "سامانه مؤدیان", "ارزش افزوده", "بیمه",
        "تأمین اجتماعی", "تامین اجتماعی", "حسابداری", "حسابرسی", "حقوق و دستمزد", "بازار",
        "قیمت", "صادرات", "واردات"
    ]
    non_economic_title_terms = [
        "آتش", "حریق", "انفجار", "فوتبال", "استقلال", "پرسپولیس", "ورزش", "سینما", "فیلم",
        "بازیگر", "موسیقی", "هنر", "فرهنگ", "رونمایی", "مستند", "سردار", "جنگ", "حمله",
        "حوادث", "پزشکی", "بیمار", "دارو", "گردشگری", "تئاتر"
    ]

    def whole_term(title, term):
        pattern = r"(?<![\wآ-ی])" + re.escape(term.lower()) + r"(?![\wآ-ی])"
        return re.search(pattern, title.lower()) is not None

    final_news = []
    for item in final_news:
        title = item.get("title", "")
        if any(whole_term(title, bad) for bad in non_economic_title_terms):
            continue
        if any(whole_term(title, good) for good in economic_title_terms):
            final_news.append(item)
        if len(final_news) >= MAX_NEWS:
            break

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "language": "fa",
        "region": "Iran / Kerman",
        "source_count": len(SOURCES),
        "successful_sources": successful,
        "failed_sources": failed,
        "active_sources": ordered_sources,
        "news_count": len(final_news),
        "news": final_news,
    }
    Path(OUTPUT_FILE).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ACTIVE SOURCES:", ", ".join(ordered_sources))
    print("FINAL NEWS:", len(final_news))

if __name__ == "__main__":
    main()
