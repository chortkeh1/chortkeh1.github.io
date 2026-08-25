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
from urllib.error import HTTPError, URLError


# =========================================================
# تنظیمات
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = BASE_DIR / "news-data.json"

MAX_ARTICLES = 80

REQUEST_TIMEOUT = 30


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

    print(f"  URL: {url}")

    request = urllib.request.Request(

        url,

        headers={
            "User-Agent":
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120 Safari/537.36",

            "Accept":
                "application/rss+xml, "
                "application/xml, "
                "text/xml, "
                "*/*"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT
        ) as response:

            status = response.status

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            data = response.read()

            print(
                f"  HTTP Status: {status}"
            )

            print(
                f"  Content-Type: {content_type}"
            )

            print(
                f"  حجم پاسخ: {len(data)} bytes"
            )

            if not data:

                raise RuntimeError(
                    "پاسخ RSS خالی است."
                )

            return data

    except HTTPError as error:

        raise RuntimeError(
            f"HTTP Error {error.code}: "
            f"{error.reason}"
        )

    except URLError as error:

        raise RuntimeError(
            f"URL Error: {error.reason}"
        )

    except TimeoutError:

        raise RuntimeError(
            "Timeout در دریافت RSS"
        )


# =========================================================
# پردازش RSS
# =========================================================

def parse_feed(xml_data, feed):

    articles = []

    try:

        root = ET.fromstring(
            xml_data
        )

    except ET.ParseError as error:

        raise RuntimeError(
            f"خطا در پردازش XML/RSS: {error}"
        )


    channel = root.find(
        "channel"
    )

    if channel is None:

        raise RuntimeError(
            "عنصر channel در RSS پیدا نشد."
        )


    items = channel.findall(
        "item"
    )

    print(
        f"  تعداد item در RSS: {len(items)}"
    )


    for item in items:

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

            "id":
                article_id,

            "title":
                title,

            "summary":
                shorten(description),

            "link":
                link,

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

        print(
            "فایل news-data.json وجود ندارد."
        )

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


        articles = data.get(
            "articles",
            []
        )


        if not isinstance(
            articles,
            list
        ):

            return []


        print(
            f"اخبار قبلی: {len(articles)}"
        )


        return articles


    except Exception as error:

        print(
            f"خطا در خواندن اخبار قبلی: {error}"
        )

        return []


# =========================================================
# اجرای اصلی
# =========================================================

def main():

    print("=" * 60)

    print(
        "شروع بروزرسانی خبرخوان چرتکه..."
    )

    print("=" * 60)


    all_articles = []

    successful_feeds = 0

    failed_feeds = 0


    # -----------------------------------------------------
    # دریافت منابع خبری
    # -----------------------------------------------------

    for feed in FEEDS:

        print()

        print(
            f"دریافت: {feed['name']}"
        )

        print(
            f"دسته‌بندی: {feed['category']}"
        )

        print(
            f"Query: {feed['query']}"
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
                f"  خبرهای معتبر: {len(articles)}"
            )


            all_articles.extend(
                articles
            )


            successful_feeds += 1


        except Exception as error:

            failed_feeds += 1

            print(
                f"  ERROR: {error}"
            )


    # -----------------------------------------------------
    # گزارش دریافت
    # -----------------------------------------------------

    print()

    print("=" * 60)

    print(
        f"منابع موفق: {successful_feeds}"
    )

    print(
        f"منابع ناموفق: {failed_feeds}"
    )

    print(
        f"خبرهای دریافت‌شده: {len(all_articles)}"
    )

    print("=" * 60)


    # -----------------------------------------------------
    # اگر هیچ منبعی موفق نبوده است
    # -----------------------------------------------------

    if successful_feeds == 0:

        raise RuntimeError(
            "هیچ‌یک از منابع RSS با موفقیت دریافت نشدند. "
            "news-data.json تغییر نخواهد کرد."
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


    # -----------------------------------------------------
    # گزارش نهایی
    # -----------------------------------------------------

    print()

    print("=" * 60)

    print(
        f"تعداد نهایی اخبار: {len(articles)}"
    )

    print(
        f"فایل خروجی: {OUTPUT_FILE}"
    )

    print(
        "خبرخوان با موفقیت بروزرسانی شد."
    )

    print("=" * 60)


# =========================================================
# شروع برنامه
# =========================================================

if __name__ == "__main__":

    main()
