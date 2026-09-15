# Trigger immediate one-time news refresh.
# ============================================================
# Chortkeh News Updater - RSS / DIVERSE SOURCES VERSION
# Fresh Persian economic, financial, industrial and Kerman news
# ============================================================

import html
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser

OUTPUT_FILE = "news-data.json"
MAX_NEWS = 30
MAX_PER_SOURCE = 5
MAX_AGE_DAYS = 30

SOURCES = [
    {"name": "اقتصاد کرمان", "feed": "https://eghtesadkerman.ir/feed/", "local": True},
    {"name": "اتاق بازرگانی کرمان", "feed": "https://otagh-bazargani.com/feed/", "local": True},
    {"name": "خبرگزاری جمهوری اسلامی (ایرنا)", "feed": "https://www.irna.ir/rss", "local": False},
    {"name": "خبرگزاری ایسنا", "feed": "https://www.isna.ir/rss", "local": False},
    {"name": "خبرگزاری مهر", "feed": "https://www.mehrnews.com/rss", "local": False},
    {"name": "خبرگزاری تسنیم", "feed": "https://www.tasnimnews.com/fa/rss/feed/0/8/0/%D8%A7%D9%82%D8%AA%D8%B5%D8%A7%D8%AF", "local": False},
    {"name": "اقتصاد آنلاین", "feed": "https://www.eghtesadonline.com/rss", "local": False},
    {"name": "دنیای اقتصاد", "feed": "https://donya-e-eqtesad.com/rss", "local": False},
    {"name": "سازمان امور مالیاتی کشور", "feed": "https://www.intamedia.ir/rss", "local": False},
]

KEYWORDS = [
    "اقتصاد", "اقتصادی", "تجارت", "بازرگانی", "صنعت", "صنایع", "معدن", "معادن",
    "فولاد", "مس", "آهن", "تولید", "کارخانه", "پیمانکاری", "سرمایه گذاری", "سرمایه‌گذاری",
    "بانک", "بانکی", "بورس", "سهام", "ارز", "دلار", "طلا", "تورم", "بودجه", "وام",
    "تسهیلات", "مالیات", "مالیاتی", "اظهارنامه", "سامانه مؤدیان", "ارزش افزوده", "بیمه",
    "تأمین اجتماعی", "تامین اجتماعی", "حسابداری", "حسابرسی", "حقوق و دستمزد", "کرمان", "سیرجان",
    "رفسنجان", "زرند", "شهربابک", "سرچشمه", "بم", "جیرفت", "کهنوج", "بردسیر", "بافت", "رابر",
    "راور", "کوهبنان", "پابدانا", "گل گهر", "گل‌گهر",
]

BLOCKED = ["facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com"]


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


def is_relevant(title, summary, local=False):
    text = f"{title} {summary}".lower()
    if len(title) < 12:
        return False
    return local or any(k.lower() in text for k in KEYWORDS)


def safe_url(url):
    if not url:
        return ""
    url = str(url).strip()
    if not (url.startswith("https://") or url.startswith("http://")):
        return ""
    if any(domain in url.lower() for domain in BLOCKED):
        return ""
    return url


def fetch_source(source):
    print(f"[SOURCE] {source['name']} -> {source['feed']}")
    parsed = feedparser.parse(source["feed"])
    if getattr(parsed, "bozo", False) and not parsed.entries:
        print("  [FAIL] feed unavailable")
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
        key = re.sub(r"\s+", " ", title.lower())
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "title": title,
            "description": summary[:500],
            "url": url,
            "source": source["name"],
            "date": published.isoformat(),
        })

    items.sort(key=lambda x: x["date"], reverse=True)
    items = items[:MAX_PER_SOURCE]
    print(f"  [OK] fresh relevant items: {len(items)}")
    return items


def main():
    all_news, successful, failed = [], 0, 0
    for source in SOURCES:
        try:
            items = fetch_source(source)
            if items:
                successful += 1
                all_news.extend(items)
            else:
                failed += 1
        except Exception as exc:
            failed += 1
            print(f"  [ERROR] {type(exc).__name__}: {exc}")

    unique, seen_titles = [], set()
    for item in all_news:
        key = re.sub(r"\W+", " ", item["title"].lower()).strip()
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique.append(item)

    def rank(item):
        local_bonus = 2 if item["source"] in {"اقتصاد کرمان", "اتاق بازرگانی کرمان"} else 0
        try:
            dt = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
            age_hours = max(0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600)
        except Exception:
            age_hours = 9999
        return (local_bonus, -age_hours)

    unique.sort(key=rank, reverse=True)
    final_news = unique[:MAX_NEWS]

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "language": "fa",
        "region": "Iran / Kerman",
        "source_count": len(SOURCES),
        "successful_sources": successful,
        "failed_sources": failed,
        "news_count": len(final_news),
        "news": final_news,
    }
    Path(OUTPUT_FILE).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Successful sources: {successful}")
    print(f"Failed sources: {failed}")
    print(f"Final news: {len(final_news)}")


if __name__ == "__main__":
    main()
