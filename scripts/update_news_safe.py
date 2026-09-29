import html
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

OUTPUT = Path("news-data.json")
MAX_NEWS = 20
MAX_AGE_DAYS = 30
KEYWORDS = (
    "اقتصاد", "اقتصادی", "تجارت", "بازرگانی", "صنعت", "معدن", "معادن", "فولاد", "مس",
    "تولید", "کارخانه", "سرمایه", "بانک", "بورس", "سهام", "مالیات", "مالیاتی", "اظهارنامه",
    "سامانه مؤدیان", "ارزش افزوده", "بیمه", "تأمین اجتماعی", "تامین اجتماعی", "حسابداری",
    "حسابرسی", "حقوق و دستمزد", "بازار", "قیمت", "صادرات", "واردات", "کرمان", "سیرجان",
    "رفسنجان", "زرند", "شهربابک", "سرچشمه", "بم", "جیرفت", "گل گهر", "گل‌گهر"
)
JUNK = ("پادکست", "شماره ", "استخدام مدیر دفتر", "استخدام نماینده")

RSS_SOURCES = [
    ("اقتصاد کرمان", "https://news.google.com/rss/search?q=site%3Aeghtesadkerman.ir&hl=fa&gl=IR&ceid=IR%3Afa"),
    ("اتاق بازرگانی کرمان", "https://news.google.com/rss/search?q=site%3Aotagh-bazargani.com&hl=fa&gl=IR&ceid=IR%3Afa"),
]
DIRECT_SOURCES = [
    ("اقتصاد کرمان", "https://eghtesadkerman.ir/"),
    ("اتاق بازرگانی کرمان", "https://otagh-bazargani.com/"),
]


def clean(value):
    value = html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    return re.sub(r"\s+", " ", value).strip()


def relevant(title, summary=""):
    title = clean(title)
    if len(title) < 12 or any(x in title for x in JUNK):
        return False
    text = f"{title} {clean(summary)}".lower()
    return any(k.lower() in text for k in KEYWORDS)


def parse_date(value):
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    try:
        value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def safe_url(url):
    if not url:
        return ""
    url = str(url).strip()
    return url if url.startswith(("https://", "http://")) else ""


def fetch_rss(name, feed_url):
    print(f"[RSS] {name}")
    parsed = feedparser.parse(feed_url)
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    out, seen = [], set()
    for entry in parsed.entries:
        title = clean(entry.get("title"))
        summary = clean(entry.get("summary") or entry.get("description"))
        url = safe_url(entry.get("link"))
        dt = parse_date(entry.get("published") or entry.get("updated"))
        if not title or not url or not relevant(title, summary):
            continue
        if dt and dt < cutoff:
            continue
        key = re.sub(r"\W+", " ", title.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        out.append({"title": title, "description": summary[:450], "url": url, "source": name, "date": (dt or datetime.now(timezone.utc)).isoformat()})
    print(f"  RSS items: {len(out)}")
    return out[:10]


def fetch_direct(name, homepage):
    print(f"[DIRECT] {name}")
    try:
        response = requests.get(homepage, timeout=20, headers={"User-Agent": "Mozilla/5.0 (compatible; ChortkehNewsBot/1.0)"})
        response.raise_for_status()
    except Exception as exc:
        print(f"  direct error: {type(exc).__name__}: {exc}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    base = urlparse(homepage).netloc.lower().removeprefix("www.")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        title = clean(a.get_text(" ", strip=True))
        href = urljoin(homepage, a.get("href"))
        parsed = urlparse(href)
        if parsed.netloc.lower().removeprefix("www.") != base:
            continue
        if not relevant(title):
            continue
        if len(title) > 180:
            title = title[:180].rsplit(" ", 1)[0]
        key = re.sub(r"\W+", " ", title.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        out.append({"title": title, "description": title, "url": href, "source": name, "date": datetime.now(timezone.utc).isoformat()})
        if len(out) >= 10:
            break
    print(f"  direct items: {len(out)}")
    return out


def load_previous():
    try:
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def main():
    previous = load_previous()
    items = []
    sources = []

    for name, feed in RSS_SOURCES:
        try:
            found = fetch_rss(name, feed)
            if found:
                items.extend(found)
                sources.append(name)
        except Exception as exc:
            print(f"  RSS error: {type(exc).__name__}: {exc}")

    # Direct pages are a fallback, not a replacement for RSS results.
    if len(items) < 5:
        for name, homepage in DIRECT_SOURCES:
            try:
                found = fetch_direct(name, homepage)
                if found:
                    items.extend(found)
                    if name not in sources:
                        sources.append(name)
            except Exception as exc:
                print(f"  direct error: {type(exc).__name__}: {exc}")

    final, seen = [], set()
    for item in sorted(items, key=lambda x: x["date"], reverse=True):
        key = re.sub(r"\W+", " ", item["title"].lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        final.append(item)
        if len(final) >= MAX_NEWS:
            break

    # Never erase a working feed because an external source is temporarily down.
    if not final and previous and previous.get("news"):
        print("No fresh news found; keeping previous news-data.json")
        return

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "language": "fa",
        "region": "Iran / Kerman",
        "source_count": 2,
        "successful_sources": len(sources),
        "failed_sources": max(0, 2 - len(sources)),
        "active_sources": sources,
        "news_count": len(final),
        "news": final,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("FINAL NEWS:", len(final))


if __name__ == "__main__":
    main()
