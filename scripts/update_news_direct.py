import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCES = [
    ("اقتصاد کرمان", "https://eghtesadkerman.ir/", re.compile(r"/News/\d+", re.I)),
    ("اتاق بازرگانی کرمان", "https://otagh-bazargani.com/", re.compile(r"/\d+(?:-\d+)?/?$", re.I)),
]
MAX_PER_SOURCE = 10
MAX_NEWS = 20
JUNK = ("پادکست", "شماره ", "استخدام مدیر دفتر", "استخدام نماینده")
KEYWORDS = ("اقتصاد", "اقتصادی", "تجارت", "بازرگانی", "صنعت", "معدن", "فولاد", "مس", "تولید", "سرمایه", "بانک", "بورس", "سهام", "مالیات", "مالیاتی", "اظهارنامه", "بیمه", "تأمین اجتماعی", "تامین اجتماعی", "حسابداری", "حسابرسی", "حقوق", "بازار", "قیمت", "صادرات", "واردات", "سرمایه‌گذاری", "کرمان", "سیرجان", "رفسنجان", "زرند", "شهربابک", "سرچشمه", "بم", "جیرفت", "گل گهر", "گل‌گهر")


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def relevant(title, text):
    title = clean(title)
    if len(title) < 12 or any(x in title for x in JUNK):
        return False
    return any(k in f"{title} {clean(text)}" for k in KEYWORDS)


def article_date(url):
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup.select('meta[property="article:published_time"], meta[itemprop="datePublished"], time[datetime]'):
            value = tag.get("content") or tag.get("datetime")
            if value:
                return value
    except Exception:
        pass
    return datetime.now(timezone.utc).isoformat()


def fetch_source(name, homepage, pattern):
    r = requests.get(homepage, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = urljoin(homepage, a["href"])
        title = clean(a.get_text(" ", strip=True))
        if not pattern.search(href) or href.rstrip("/") == homepage.rstrip("/"):
            continue
        if href in seen or not relevant(title, title):
            continue
        seen.add(href)
        items.append({"title": title, "description": title, "url": href, "source": name, "date": article_date(href)})
        if len(items) >= MAX_PER_SOURCE:
            break
    return items


def main():
    news = []
    active = []
    for name, homepage, pattern in SOURCES:
        try:
            items = fetch_source(name, homepage, pattern)
            if items:
                active.append(name)
                news.extend(items)
            print(f"{name}: {len(items)}")
        except Exception as exc:
            print(f"{name}: ERROR {type(exc).__name__}: {exc}")
    seen = set()
    final = []
    for item in sorted(news, key=lambda x: x["date"], reverse=True):
        key = item["title"].lower()
        if key and key not in seen:
            seen.add(key)
            final.append(item)
        if len(final) >= MAX_NEWS:
            break
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "language": "fa",
        "region": "Iran / Kerman",
        "source_count": 2,
        "successful_sources": len(active),
        "failed_sources": 2 - len(active),
        "active_sources": active,
        "news_count": len(final),
        "news": final,
    }
    Path("news-data.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("FINAL NEWS:", len(final))


if __name__ == "__main__":
    main()
