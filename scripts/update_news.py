import json
import hashlib
import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


# =========================================================
# تنظیمات
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = BASE_DIR / "news-data.json"

MAX_ARTICLES = 80


# =========================================================
# منابع خبری
# =========================================================

FEEDS = [

    {
        "name": "اخبار مالی و حسابداری",
        "category": "حسابداری",
        "query": "حسابداری OR حسابرسی OR حسابداران"
    },

    {
        "name": "اخبار مالیاتی",
        "category": "مالیات",
        "query": "مالیات OR مالیاتی OR سامانه مودیان"
    },

    {
        "name": "اخبار بیمه و تأمین اجتماعی",
        "category": "بیمه",
        "query": "تامین اجتماعی OR بیمه کارگران OR بیمه تامین اجتماعی"
    },

    {
        "name": "اخبار اقتصادی کرمان",
        "category": "کرمان",
        "query": "کرمان اقتصاد OR کرمان صنعت OR کرمان معدن"
    },

    {
        "name": "اخبار اقتصادی ایران",
        "category": "اقتصاد",
        "query": "اقتصاد ایران OR بازار ایران OR شرکت های ایرانی"
    },

    {
        "name": "اخبار کسب‌وکار",
        "category": "کسب‌وکار",
        "query": "کسب و کار OR شرکت ها OR کارآفرینی"
    }
]


# =========================================================
# تمیز کردن متن
# =========================================================

def clean_text(value):

    if not value:
        return ""

    value = html.unescape(value)

    value = re.sub(
        r"<[^>]+>",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# =========================================================
# کوتاه کردن خلاصه
# =========================================================

def shorten(text, length=240):

    text = clean_text(text)

    if len(text) <= length:
        return text

    return text[:length].rsplit(
        " ",
        1
    )[0] + "…"


# =========================================================
# تبدیل تاریخ
# =========================================================

def parse_date(value):

    if not value:
        return ""

    value = value.strip()

    try:

        dt = parsedate_to_datetime(
            value
        )

        if dt.tzinfo is None:

            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(
            timezone.utc
        ).isoformat()

    except Exception:

        return value


# =========================================================
# ساخت شناسه یکتا
# =========================================================

def make_id(title, link):

    raw = (
        title.strip()
        + "|"
        + link.strip()
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:20]


# =========================================================
# ساخت آدرس RSS
# =========================================================

def build_feed_url(query):

    encoded = urllib.parse.quote_plus(
        query
    )

    return (
        "https://news.google.com/rss/search?"
        "q="
        + encoded
        + "&hl=fa&gl=IR&ceid=IR:fa"
    )


# =========================================================
# دریافت RSS
# =========================================================

def fetch_feed(feed):

    url = build_feed_url(
        feed["query"]
    )

    request = urllib.request.Request(

        url,

        headers={
            "User-Agent":
                "Mozilla/5.0 "
                "(compatible; ChortkehNewsBot/1.0)"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        return response.read()


# =========================================================
# پردازش RSS
# =========================================================

def parse_feed(xml_data, feed):

    articles = []

    root = ET.fromstring(
        xml_data
    )

    channel = root.find(
        "channel"
    )

    if channel is None:

        return articles


    for item in channel.findall(
        "item"
    ):

        title = item.findtext(
            "title",
            ""
        )

        link = item.findtext(
            "link",
            ""
        )

        description = item.findtext(
            "description",
            ""
        )

        pub_date = item.findtext(
            "pubDate",
            ""
        )

        source_element = item.find(
            "source"
        )

        source = ""

        if source_element is not None:

            source = (
                source_element.text
                or ""
            )


        title = clean_text(
            title
        )

        description = clean_text(
            description
        )

        link = (
            link.strip()
            if link
            else ""
        )


        if not title or not link:

            continue


        article_id = make_id(
            title,
            link
        )


        articles.append({

            "id": article_id,

            "title": title,

            "summary": shorten(
                description
            ),

            "link": link,

            "source":
                clean_text(source)
                or feed["name"],

            "category":
                feed["category"],

            "published":
                parse_date(pub_date)

        })


    return articles


# =========================================================
# خواندن اخبار قبلی
# =========================================================

def load_existing():

    if not OUTPUT_FILE.exists():

        return []


    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

        return data.get(
            "articles",
            []
        )

    except Exception:

        return []


# =========================================================
# اجرای اصلی
# =========================================================

def main():

    print(
        "شروع بروزرسانی خبرخوان چرتکه..."
    )


    all_articles = []


    for feed in FEEDS:

        print(
            f"دریافت: {feed['name']}"
        )


        try:

            xml_data = fetch_feed(
                feed
            )

            articles = parse_feed(
                xml_data,
                feed
            )


            print(
                f"  {len(articles)} خبر دریافت شد."
            )


            all_articles.extend(
                articles
            )


        except Exception as error:

            print(
                f"خطا در منبع "
                f"{feed['name']}: "
                f"{error}"
            )


    # -----------------------------------------------------
    # اضافه کردن اخبار قبلی
    # -----------------------------------------------------

    old_articles = load_existing()

    all_articles.extend(
        old_articles
    )


    # -----------------------------------------------------
    # حذف اخبار تکراری
    # -----------------------------------------------------

    unique = {}


    for article in all_articles:

        article_id = article.get(
            "id"
        )


        if not article_id:

            continue


        if article_id not in unique:

            unique[
                article_id
            ] = article


    articles = list(
        unique.values()
    )


    # -----------------------------------------------------
    # مرتب‌سازی بر اساس تاریخ
    # -----------------------------------------------------

    articles.sort(

        key=lambda item:
            item.get(
                "published",
                ""
            ),

        reverse=True
    )


    # -----------------------------------------------------
    # محدود کردن تعداد اخبار
    # -----------------------------------------------------

    articles = articles[
        :MAX_ARTICLES
    ]


    # -----------------------------------------------------
    # ساخت خروجی
    # -----------------------------------------------------

    output = {

        "updated":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "articles":
            articles
    }


    # -----------------------------------------------------
    # ذخیره فایل
    # -----------------------------------------------------

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


    print(
        f"تعداد نهایی اخبار: "
        f"{len(articles)}"
    )


    print(
        "خبرخوان با موفقیت بروزرسانی شد."
    )


# =========================================================
# شروع برنامه
# =========================================================

if __name__ == "__main__":

    main()
