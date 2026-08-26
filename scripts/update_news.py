#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
Chortkeh News Updater
============================================================

هدف:
- دریافت اخبار فقط از منابع منتخب ایران و کرمان
- حذف Google News
- حذف منابع نامرتبط و انگلیسی
- حذف منابع نامطلوب
- تولید news-data.json
- بدون نیاز به requests
- مناسب برای GitHub Actions
============================================================
"""

import json
import re
import ssl
import time
from datetime import datetime, timezone, timedelta
from html import unescape
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET


# ============================================================
# تنظیمات اصلی
# ============================================================

OUTPUT_FILE = "news-data.json"

MAX_NEWS = 30

# فقط خبرهای چند روز اخیر
MAX_AGE_DAYS = 14

# حداکثر خبر از هر منبع
MAX_PER_SOURCE = 8

TIMEOUT = 20

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/139.0 Safari/537.36"
)


# ============================================================
# منابع خبری رسمی و منتخب
# ============================================================

SOURCES = [
    {
        "name": "سازمان امور مالیاتی کشور",
        "url": "https://www.intamedia.ir/setad-news",
        "priority": 10,
        "keywords": [
            "مالیات",
            "مالیاتی",
            "مودیان",
            "سامانه مودیان",
            "اظهارنامه",
            "ارزش افزوده",
            "حسابداری",
        ],
    },

    {
        "name": "سازمان تأمین اجتماعی",
        "url": "https://tamin.ir/",
        "priority": 10,
        "keywords": [
            "تامین اجتماعی",
            "تأمین اجتماعی",
            "بیمه",
            "کارفرما",
            "کارگر",
            "بازنشستگی",
            "حقوق",
            "دستمزد",
        ],
    },

    {
        "name": "بانک مرکزی جمهوری اسلامی ایران",
        "url": "https://www.cbi.ir/",
        "priority": 10,
        "keywords": [
            "بانک مرکزی",
            "بانک",
            "ارز",
            "نرخ ارز",
            "پول",
            "تسهیلات",
            "بانکی",
            "اقتصاد",
            "تورم",
        ],
    },

    {
        "name": "جامعه حسابداران رسمی ایران",
        "url": "https://www.iacpa.ir/",
        "priority": 10,
        "keywords": [
            "حسابداری",
            "حسابرسی",
            "حسابدار",
            "حسابرس",
            "استاندارد حسابداری",
            "استاندارد حسابرسی",
            "گزارش مالی",
        ],
    },

    {
        "name": "اقتصاد آنلاین",
        "url": "https://www.eghtesadonline.com/",
        "priority": 8,
        "keywords": [
            "اقتصاد",
            "مالیات",
            "بانک",
            "بورس",
            "بازار",
            "صنعت",
            "معدن",
            "تولید",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "کسب و کار",
        ],
    },

    {
        "name": "وزارت صنعت، معدن و تجارت",
        "url": "https://www.mimt.gov.ir/",
        "priority": 10,
        "keywords": [
            "صنعت",
            "معدن",
            "تجارت",
            "تولید",
            "صنایع",
            "معدنی",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "صادرات",
            "واردات",
        ],
    },

    {
        "name": "اتاق بازرگانی",
        "url": "https://otagh-bazargani.com/",
        "priority": 8,
        "keywords": [
            "بازرگانی",
            "تجارت",
            "اقتصاد",
            "کسب و کار",
            "تولید",
            "صادرات",
            "واردات",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
        ],
    },

    {
        "name": "اقتصاد کرمان",
        "url": "https://eghtesadkerman.ir/",
        "priority": 12,
        "keywords": [
            "کرمان",
            "سیرجان",
            "رفسنجان",
            "زرند",
            "شهربابک",
            "مس سرچشمه",
            "بم",
            "جیرفت",
            "معدن",
            "معدنی",
            "صنعت",
            "اقتصاد",
            "تولید",
            "بازرگانی",
        ],
    },

    {
        "name": "وزارت امور اقتصادی و دارایی",
        "url": "https://www.mefa.ir/",
        "priority": 10,
        "keywords": [
            "اقتصاد",
            "مالیات",
            "دارایی",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "بانک",
            "تولید",
            "خصوصی سازی",
            "خصوصی‌سازی",
        ],
    },

    {
        "name": "سازمان بورس و اوراق بهادار",
        "url": "https://www.seo.ir/",
        "priority": 9,
        "keywords": [
            "بورس",
            "اوراق بهادار",
            "بازار سرمایه",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "شرکت",
            "صورت مالی",
            "گزارش مالی",
        ],
    },
]


# ============================================================
# کلمات کلیدی بسیار مرتبط با سایت چرتکه
# ============================================================

HIGH_VALUE_KEYWORDS = [
    "حسابداری",
    "حسابرس",
    "حسابرسی",
    "مالیات",
    "مالیاتی",
    "مودیان",
    "سامانه مودیان",
    "اظهارنامه",
    "ارزش افزوده",
    "بیمه",
    "تامین اجتماعی",
    "تأمین اجتماعی",
    "حقوق و دستمزد",
    "بانک مرکزی",
    "اقتصاد",
    "معدن",
    "معدنی",
    "صنعت",
    "تولید",
    "کرمان",
    "سیرجان",
    "رفسنجان",
    "زرند",
    "شهربابک",
    "مس سرچشمه",
    "بم",
    "جیرفت",
    "بورس",
    "بازار سرمایه",
    "شرکت",
    "کسب و کار",
]


# ============================================================
# کلمات نامطلوب
# ============================================================

BAD_KEYWORDS = [
    "فیسبوک",
    "facebook",
    "اینستاگرام",
    "instagram",
    "ایران اینترنشنال",
    "iran international",
    "instagram",
    "twitter",
    "x.com",
    "تلگرام",
    "telegram",
    "ورزش",
    "فوتبال",
    "والیبال",
    "سینما",
    "بازیگر",
    "خواننده",
    "موسیقی",
    "فال",
    "سرگرمی",
    "حوادث",
    "قتل",
    "تصادف",
    "جنگ",
    "سلبریتی",
]


# ============================================================
# SSL
# ============================================================

SSL_CONTEXT = ssl.create_default_context()

try:
    SSL_CONTEXT.set_ciphers("DEFAULT:@SECLEVEL=1")
except Exception:
    pass


# ============================================================
# ابزار دریافت صفحه
# ============================================================

def fetch_url(url):
    """
    دریافت محتویات URL بدون requests
    """

    try:
        req = Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "fa,en;q=0.7",
            },
        )

        with urlopen(
            req,
            timeout=TIMEOUT,
            context=SSL_CONTEXT
        ) as response:

            content = response.read()

            content_type = response.headers.get(
                "Content-Type",
                ""
            ).lower()

            charset = "utf-8"

            match = re.search(
                r"charset=([a-zA-Z0-9_-]+)",
                content_type
            )

            if match:
                charset = match.group(1)

            try:
                return content.decode(
                    charset,
                    errors="ignore"
                )

            except Exception:
                return content.decode(
                    "utf-8",
                    errors="ignore"
                )

    except HTTPError as e:
        print(
            f"HTTP ERROR {e.code}: {url}"
        )

    except URLError as e:
        print(
            f"URL ERROR: {url} -> {e.reason}"
        )

    except Exception as e:
        print(
            f"ERROR: {url} -> {e}"
        )

    return ""


# ============================================================
# پاکسازی HTML
# ============================================================

def clean_html(text):
    if not text:
        return ""

    text = unescape(text)

    text = re.sub(
        r"<script.*?</script>",
        " ",
        text,
        flags=re.I | re.S
    )

    text = re.sub(
        r"<style.*?</style>",
        " ",
        text,
        flags=re.I | re.S
    )

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# تشخیص فارسی
# ============================================================

def persian_ratio(text):

    if not text:
        return 0

    persian = len(
        re.findall(
            r"[\u0600-\u06FF]",
            text
        )
    )

    letters = len(
        re.findall(
            r"[A-Za-z\u0600-\u06FF]",
            text
        )
    )

    if letters == 0:
        return 0

    return persian / letters


# ============================================================
# حذف URLهای نامطلوب
# ============================================================

def is_bad_url(url):

    value = url.lower()

    blocked_domains = [
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "x.com",
        "t.me",
        "telegram.me",
        "iranintl.com",
        "iran-international.com",
    ]

    for domain in blocked_domains:
        if domain in value:
            return True

    return False


# ============================================================
# حذف خبر نامطلوب
# ============================================================

def is_bad_news(title, description=""):

    text = (
        title + " " + description
    ).lower()

    for word in BAD_KEYWORDS:

        if word.lower() in text:
            return True

    return False


# ============================================================
# امتیازدهی خبر
# ============================================================

def calculate_score(
    title,
    description,
    source
):

    text = (
        title + " " + description
    ).lower()

    score = source["priority"]

    # خبر فارسی
    ratio = persian_ratio(text)

    if ratio >= 0.70:
        score += 8

    elif ratio >= 0.50:
        score += 4

    else:
        score -= 10

    # کلمات بسیار مهم
    for keyword in HIGH_VALUE_KEYWORDS:

        if keyword.lower() in text:
            score += 4

    # کلمات اختصاصی منبع
    for keyword in source["keywords"]:

        if keyword.lower() in text:
            score += 3

    # تمرکز ویژه روی کرمان
    kerman_keywords = [
        "کرمان",
        "سیرجان",
        "رفسنجان",
        "زرند",
        "شهربابک",
        "مس سرچشمه",
        "بم",
        "جیرفت",
    ]

    for keyword in kerman_keywords:

        if keyword in text:
            score += 5

    return score


# ============================================================
# استخراج RSS
# ============================================================

def parse_rss(content, source):

    items = []

    if not content:
        return items

    try:
        root = ET.fromstring(content)

    except Exception:
        return items

    for item in root.iter():

        if item.tag.lower().endswith("item"):

            title = ""
            link = ""
            description = ""
            pub_date = ""

            for child in item:

                tag = child.tag.lower()

                if tag.endswith("title"):
                    title = clean_html(
                        child.text or ""
                    )

                elif tag.endswith("link"):
                    link = (
                        child.text or ""
                    ).strip()

                elif tag.endswith(
                    "description"
                ):
                    description = clean_html(
                        child.text or ""
                    )

                elif (
                    tag.endswith("pubdate")
                    or tag.endswith("published")
                    or tag.endswith("updated")
                ):
                    pub_date = (
                        child.text or ""
                    ).strip()

            if title and link:

                items.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "pub_date": pub_date,
                    "source": source["name"],
                    "priority": source["priority"],
                })

    return items


# ============================================================
# جستجوی RSS احتمالی
# ============================================================

def discover_feeds(source_url):

    parsed = urlparse(source_url)

    base = (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
    )

    candidates = [
        source_url.rstrip("/") + "/rss",
        source_url.rstrip("/") + "/feed",
        source_url.rstrip("/") + "/rss.xml",
        source_url.rstrip("/") + "/feed.xml",
        source_url.rstrip("/") + "/news/rss",
        base + "/rss",
        base + "/feed",
        base + "/rss.xml",
        base + "/feed.xml",
    ]

    return list(dict.fromkeys(candidates))


# ============================================================
# استخراج خبر از HTML
# ============================================================

def parse_html_links(
    content,
    source
):

    items = []

    if not content:
        return items

    # استخراج لینک و عنوان تقریبی
    pattern = re.compile(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>'
        r'(.*?)</a>',
        re.I | re.S
    )

    for match in pattern.finditer(content):

        href = match.group(1)

        text = clean_html(
            match.group(2)
        )

        if not text:
            continue

        if len(text) < 20:
            continue

        if len(text) > 250:
            continue

        link = urljoin(
            source["url"],
            href
        )

        if is_bad_url(link):
            continue

        if is_bad_news(
            text,
            ""
        ):
            continue

        items.append({
            "title": text,
            "link": link,
            "description": "",
            "pub_date": "",
            "source": source["name"],
            "priority": source["priority"],
        })

    return items


# ============================================================
# دریافت اخبار هر منبع
# ============================================================

def collect_source(source):

    print(
        f"\nدر حال بررسی: "
        f"{source['name']}"
    )

    all_items = []

    # --------------------------------------------------------
    # مرحله اول: RSS
    # --------------------------------------------------------

    feeds = discover_feeds(
        source["url"]
    )

    for feed in feeds:

        content = fetch_url(feed)

        if not content:
            continue

        items = parse_rss(
            content,
            source
        )

        if items:

            all_items.extend(items)

            print(
                f"RSS موفق: {feed}"
            )

            break

        time.sleep(0.3)

    # --------------------------------------------------------
    # مرحله دوم: HTML
    # --------------------------------------------------------

    if not all_items:

        content = fetch_url(
            source["url"]
        )

        if content:

            items = parse_html_links(
                content,
                source
            )

            all_items.extend(items)

            if items:
                print(
                    f"HTML موفق: "
                    f"{len(items)} خبر"
                )

    # --------------------------------------------------------
    # حذف موارد نامطلوب
    # --------------------------------------------------------

    clean_items = []

    seen = set()

    for item in all_items:

        title = item["title"].strip()

        link = item["link"].strip()

        if not title or not link:
            continue

        if link in seen:
            continue

        seen.add(link)

        if is_bad_url(link):
            continue

        if is_bad_news(
            title,
            item.get(
                "description",
                ""
            )
        ):
            continue

        item["score"] = calculate_score(
            title,
            item.get(
                "description",
                ""
            ),
            source
        )

        clean_items.append(item)

    clean_items.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    clean_items = clean_items[
        :MAX_PER_SOURCE
    ]

    print(
        f"خبرهای قابل استفاده: "
        f"{len(clean_items)}"
    )

    return clean_items


# ============================================================
# حذف خبرهای تکراری
# ============================================================

def normalize_title(title):

    title = title.lower()

    title = re.sub(
        r"[^\w\u0600-\u06FF\s]",
        " ",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


def remove_duplicates(items):

    result = []

    seen_titles = set()
    seen_links = set()

    for item in items:

        title_key = normalize_title(
            item["title"]
        )

        link = item["link"]

        if (
            title_key in seen_titles
            or link in seen_links
        ):
            continue

        seen_titles.add(
            title_key
        )

        seen_links.add(
            link
        )

        result.append(item)

    return result


# ============================================================
# ساخت خروجی
# ============================================================

def build_output(items):

    now = datetime.now(
        timezone.utc
    ).astimezone(
        timezone(
            timedelta(hours=3, minutes=30)
        )
    )

    output = {
        "updated_at": now.isoformat(),
        "count": len(items),
        "news": []
    }

    for item in items:

        output["news"].append({
            "title": item["title"],
            "description": item.get(
                "description",
                ""
            ),
            "url": item["link"],
            "source": item["source"],
            "published": item.get(
                "pub_date",
                ""
            ),
            "score": item.get(
                "score",
                0
            ),
        })

    return output


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "خبرخوان جدید مؤسسه چرتکه"
    )

    print("=" * 60)

    all_news = []

    successful = 0
    failed = 0

    # --------------------------------------------------------
    # منابع
    # --------------------------------------------------------

    for source in SOURCES:

        news = collect_source(
            source
        )

        if news:

            successful += 1

            all_news.extend(
                news
            )

        else:

            failed += 1

        time.sleep(0.5)

    # --------------------------------------------------------
    # حذف تکراری‌ها
    # --------------------------------------------------------

    all_news = remove_duplicates(
        all_news
    )

    # --------------------------------------------------------
    # مرتب‌سازی
    # --------------------------------------------------------

    all_news.sort(
        key=lambda x: x.get(
            "score",
            0
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # تعداد نهایی
    # --------------------------------------------------------

    final_news = all_news[
        :MAX_NEWS
    ]

    # --------------------------------------------------------
    # خروجی
    # --------------------------------------------------------

    output = build_output(
        final_news
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------------
    # گزارش
    # --------------------------------------------------------

    print("\n")
    print("=" * 60)

    print(
        f"منابع موفق: {successful}"
    )

    print(
        f"منابع ناموفق: {failed}"
    )

    print(
        f"خبرهای دریافت‌شده: "
        f"{len(all_news)}"
    )

    print(
        f"تعداد نهایی اخبار: "
        f"{len(final_news)}"
    )

    print(
        f"فایل خروجی: "
        f"{OUTPUT_FILE}"
    )

    print(
        "خبرخوان با موفقیت بروزرسانی شد."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
