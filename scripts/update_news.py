# ============================================================
# Chortkeh News Updater - Kerman-only official/local sources
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
MAX_NEWS = 20
MAX_PER_SOURCE_FETCH = 10
MAX_AGE_DAYS = 14

# IMPORTANT: only these two sources are allowed on the Chortkeh site.
# Google News RSS is used only as a feed reader, with an explicit site: filter.
SOURCES = [
    {
        "name": "اقتصاد کرمان",
        "feed": "https://news.google.com/rss/search?q=site%3Aeghtesadkerman.ir&hl=fa&gl=IR&ceid=IR%3Afa",
        "domain": "eghtesadkerman.ir",
    },
    {
        "name": "اتاق بازرگانی کرمان",
        "feed": "https://news.google.com/rss/search?q=site%3Aotagh-bazargani.com&hl=fa&gl=IR&ceid=IR%3Afa",
        "domain": "otagh-bazargani.com",
    },
]

BLOCKED = ["facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com"]
JUNK = [
    "پادکست", "شماره ", "شمارهٔ", "استخدام مدیر دفتر", "استخدام نماینده",
]


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


def is_relevant(title, summary):
    if len(title) < 12 or any(x in title for x in JUNK):
        return False
    economic = [
        "اقتصاد", "اقتصادی", "تجارت", "بازرگانی", "صنعت", "صنایع", "معدن", "معادن",
        "فولاد", "مس", "آهن", "تولید", "کارخانه", "پیمانکاری", "سرمایه", "بانک", "بانکی",
        "بورس", "سهام", "ارز", "دلار", "طلا", "تورم", "بودجه", "تسهیلات", "مالیات",
        "مالیاتی", "اظهارنامه", "سامانه مؤدیان", "ارزش افزوده", "بیمه", "تأمین اجتماعی",
        "تامین اجتماعی", "حسابداری", "حسابرسی", "حقوق و دستمزد", "بازار", "قیمت", "صادرات", "واردات",
        "سرمایه‌گذاری", "سرمایه گذاری", "هزینه", "درآمد", "کرمان", "سیرجان", "رفسنجان", "زرند",
        "شهربابک", "سرچشمه", "بم", "جیرفت", "گل گهر", "گل‌گهر",
    ]
    text = f"{title} {summary}".lower()
    return any(k.lower() in text for k in economic)


def belongs_to_source(entry, source):
    # Google News entries normally expose source metadata. Require the expected
    # source/domain so that no unrelated publisher can enter the site feed.
    source_meta = entry.get("source") or {}
    source_text = clean_text(source_meta.get("title") or source_meta.get("url"))
    raw = f"{source_text} {entry.get('link', '')}".lower()
    domain = source["domain"].lower()
    return domain in raw or source["name"].lower() in source_text.lower()


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
        if not belongs_to_source(entry, source):
            continue
        if not is_relevant(title, summary):
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

    # Interleave the two approved sources so one publisher does not dominate.
    final_news = []
    seen_titles = set()
    cursor = 0
    while len(final_news) < MAX_NEWS:
        added = False
        for source in SOURCES:
            items = by_source[source["name"]]
            if cursor < len(items):
                item = items[cursor]
                key = re.sub(r"\W+", " ", item["title"].lower()).strip()
                if key not in seen_titles:
                    seen_titles.add(key)
                    final_news.append(item)
                    added = True
                if len(final_news) >= MAX_NEWS:
                    break
        if not added:
            break
        cursor += 1

    final_news.sort(key=lambda x: x["date"], reverse=True)
    final_news = final_news[:MAX_NEWS]

    active_sources = [s["name"] for s in SOURCES if by_source[s["name"]]]
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "language": "fa",
        "region": "Iran / Kerman",
        "source_count": 2,
        "successful_sources": successful,
        "failed_sources": failed,
        "active_sources": active_sources,
        "news_count": len(final_news),
        "news": final_news,
    }
    Path(OUTPUT_FILE).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("ACTIVE SOURCES:", ", ".join(active_sources) or "none")
    print("FINAL NEWS:", len(final_news))


if __name__ == "__main__":
    main()
