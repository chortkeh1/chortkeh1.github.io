import json
import hashlib
import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError


# =========================================================
# تنظیمات اصلی
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = BASE_DIR / "news-data.json"

# حداکثر تعداد خبر در سایت
MAX_ARTICLES = 20

# فقط اخبار این تعداد روز اخیر نگه داشته می‌شوند
MAX_AGE_DAYS = 14

# حداقل امتیاز لازم برای ورود خبر
MIN_SCORE = 4

REQUEST_TIMEOUT = 30


# =========================================================
# منابع خبری
# =========================================================

FEEDS = [

    {
        "name": "اخبار حسابداری و حسابرسی",
        "category": "حسابداری",
        "query":
            "حسابداری OR حسابرسی OR حسابدار OR "
            "حسابداران OR موسسه حسابرسی"
    },

    {
        "name": "اخبار مالیاتی",
        "category": "مالیات",
        "query":
            "مالیات OR مالیاتی OR "
            "سامانه مودیان OR مودیان مالیاتی OR "
            "ارزش افزوده OR مالیات بر ارزش افزوده"
    },

    {
        "name": "اخبار بیمه و تأمین اجتماعی",
        "category": "بیمه",
        "query":
            "تامین اجتماعی OR تأمین اجتماعی OR "
            "بیمه کارگران OR بیمه کارکنان OR "
            "حق بیمه OR لیست بیمه"
    },

    {
        "name": "اخبار کسب‌وکار و شرکت‌ها",
        "category": "کسب‌وکار",
        "query":
            "کسب و کار OR کسب‌وکار OR "
            "شرکت ها OR شرکت‌های ایرانی OR "
            "کارآفرینی OR بنگاه اقتصادی"
    },

    {
        "name": "اخبار اقتصادی ایران",
        "category": "اقتصاد",
        "query":
            "اقتصاد ایران OR بازار ایران OR "
            "فعالیت اقتصادی OR تولید ایران OR "
            "سرمایه گذاری ایران"
    },

    {
        "name": "اخبار اقتصادی کرمان",
        "category": "کرمان",
        "query":
            "کرمان اقتصاد OR کرمان صنعت OR "
            "کرمان معدن OR کرمان سرمایه گذاری OR "
            "معادن کرمان OR شرکت‌های کرمان"
    },

    {
        "name": "اخبار صنایع و معادن",
        "category": "صنعت و معدن",
        "query":
            "معدن ایران OR صنایع معدنی OR "
            "شرکت معدنی OR مس ایران OR "
            "فولاد ایران"
    }
]


# =========================================================
# منابع نامطلوب
# =========================================================

BLOCKED_SOURCES = {

    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "youtube.com",
    "x.com",
    "twitter.com"
}


# =========================================================
# کلمات بسیار نامرتبط
# =========================================================

EXCLUDED_KEYWORDS = [

    "ورزش",
    "فوتبال",
    "والیبال",
    "بسکتبال",
    "تنیس",
    "المپیک",
    "مسابقه",
    "بازیکن",
    "گل",
    "لیگ",

    "سینما",
    "فیلم",
    "بازیگر",
    "موسیقی",
    "خواننده",
    "کنسرت",

    "هواشناسی",
    "زلزله",
    "گردشگری",

    "هولوکاست",
    "نازی",

    "جرم",
    "قتل",
    "سرقت",

    "تصادف",

    "عروسی",
    "ازدواج",

    "مد",
    "لباس",

    "آشپزی",
    "غذا",

    "فناوری موبایل",
    "گوشی موبایل"
]


# =========================================================
# کلیدواژه‌های اصلی
# =========================================================

KEYWORDS = {

    # حسابداری
    "حسابداری": 8,
    "حسابدار": 8,
    "حسابداران": 8,
    "حسابرسی": 8,
    "حسابرس": 8,
    "موسسه حسابرسی": 10,
    "مؤسسه حسابرسی": 10,
    "صورت مالی": 8,
    "گزارش مالی": 7,
    "استاندارد حسابداری": 10,
    "استاندارد حسابرسی": 10,

    # مالیات
    "مالیات": 8,
    "مالیاتی": 8,
    "سامانه مودیان": 12,
    "سامانه مؤدیان": 12,
    "مودیان": 8,
    "مؤدیان": 8,
    "ارزش افزوده": 10,
    "اظهارنامه مالیاتی": 10,
    "اظهارنامه": 6,
    "مالیات بر درآمد": 9,
    "مالیات بر ارزش افزوده": 10,

    # بیمه
    "تامین اجتماعی": 8,
    "تأمین اجتماعی": 8,
    "حق بیمه": 8,
    "بیمه کارگران": 7,
    "بیمه کارکنان": 7,
    "لیست بیمه": 8,

    # حقوق و دستمزد
    "حقوق و دستمزد": 9,
    "حقوق کارگران": 7,
    "حقوق کارکنان": 7,
    "دستمزد": 6,
    "حداقل حقوق": 7,
    "حداقل دستمزد": 8,

    # شرکت و کسب‌وکار
    "شرکت": 4,
    "شرکت‌ها": 4,
    "شرکت های": 4,
    "کسب و کار": 5,
    "کسب‌وکار": 5,
    "کارآفرینی": 4,
    "بنگاه": 4,
    "سرمایه گذاری": 5,
    "سرمایه‌گذاری": 5,

    # اقتصاد
    "اقتصاد ایران": 5,
    "اقتصاد": 3,
    "بازار": 3,
    "تولید": 4,
    "صنعت": 4,
    "صنایع": 4,

    # معدن
    "معدن": 6,
    "معادن": 6,
    "صنایع معدنی": 7,
    "شرکت معدنی": 7,
    "مس": 5,
    "فولاد": 5,

    # کرمان
    "کرمان": 7,
    "سیرجان": 8,
    "رفسنجان": 8,
    "زرند": 8,
    "بم": 6,
    "جیرفت": 6,
    "شهربابک": 8,
    "راور": 7,
    "بافت": 6,
    "بردسیر": 6,
    "رابر": 6,
    "کوهبنان": 7,
    "پابدانا": 7,
    "مس سرچشمه": 10
}


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
# نرمال‌سازی متن فارسی
# =========================================================

def normalize_text(value):

    value = clean_text(value)

    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "ٱ": "ا",
        "\u200c": " ",
        "\u200f": " ",
        "\u200e": " "
    }

    for old, new in replacements.items():

        value = value.replace(
            old,
            new
        )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip().lower()


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
# تبدیل تاریخ به datetime
# =========================================================

def article_datetime(article):

    value = article.get(
        "published",
        ""
    )

    if not value:
        return None

    try:

        dt = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

        if dt.tzinfo is None:

            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(
            timezone.utc
        )

    except Exception:

        return None


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

    print(
        f"  URL: {url}"
    )

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
# امتیازدهی به خبر
# =========================================================

def calculate_score(
    title,
    summary,
    source,
    category
):

    text = normalize_text(
        title + " " +
        summary
    )

    normalized_source = normalize_text(
        source
    )

    score = 0

    matched_keywords = []

    # -----------------------------------------------------
    # امتیاز کلیدواژه‌ها
    # -----------------------------------------------------

    for keyword, points in KEYWORDS.items():

        normalized_keyword = normalize_text(
            keyword
        )

        if normalized_keyword in text:

            score += points

            matched_keywords.append(
                keyword
            )

    # -----------------------------------------------------
    # امتیاز دسته‌بندی
    # -----------------------------------------------------

    category_bonus = {

        "حسابداری": 5,
        "مالیات": 5,
        "بیمه": 4,
        "کسب‌وکار": 3,
        "اقتصاد": 2,
        "کرمان": 5,
        "صنعت و معدن": 4
    }

    score += category_bonus.get(
        category,
        0
    )

    # -----------------------------------------------------
    # امتیاز منبع
    # -----------------------------------------------------

    trusted_source_keywords = [

        "ایرنا",
        "ایسنا",
        "مهر",
        "تسنیم",
        "فارس",
        "اقتصادنیوز",
        "دنیای اقتصاد",
        "ایبنا",
        "اتاق بازرگانی",
        "وزارت اقتصاد",
        "سازمان امور مالیاتی",
        "تامین اجتماعی",
        "تأمین اجتماعی",
        "سازمان حسابرسی",
        "مرکز پژوهش",
        "cnbc",
        "reuters",
        "investopedia",
        "forbes",
        "accountancy"
    ]

    for trusted in trusted_source_keywords:

        if normalize_text(trusted) in normalized_source:

            score += 3

            break

    return score, matched_keywords


# =========================================================
# بررسی منبع مسدود
# =========================================================

def is_blocked_source(source, link):

    source_normalized = normalize_text(
        source
    )

    link_normalized = (
        link.lower()
    )

    for blocked in BLOCKED_SOURCES:

        if (
            blocked in source_normalized
            or blocked in link_normalized
        ):

            return True

    return False


# =========================================================
# بررسی کلمات نامرتبط
# =========================================================

def contains_excluded_keyword(
    title,
    summary
):

    text = normalize_text(
        title + " " + summary
    )

    for keyword in EXCLUDED_KEYWORDS:

        if normalize_text(keyword) in text:

            return True

    return False


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


    now = datetime.now(
        timezone.utc
    )

    cutoff = now - timedelta(
        days=MAX_AGE_DAYS
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

        source = (
            clean_text(source)
            or feed["name"]
        )


        if not title or not link:

            continue


        # -------------------------------------------------
        # حذف شبکه‌های اجتماعی
        # -------------------------------------------------

        if is_blocked_source(
            source,
            link
        ):

            print(
                f"  حذف منبع اجتماعی: {source}"
            )

            continue


        # -------------------------------------------------
        # تاریخ
        # -------------------------------------------------

        published = parse_date(
            pub_date
        )

        article = {

            "id":
                make_id(
                    title,
                    link
                ),

            "title":
                title,

            "summary":
                shorten(
                    description
                ),

            "link":
                link,

            "source":
                source,

            "category":
                feed["category"],

            "published":
                published
        }


        article_dt = article_datetime(
            article
        )


        # -------------------------------------------------
        # خبر بدون تاریخ معتبر
        # -------------------------------------------------

        if article_dt is None:

            print(
                f"  حذف بدون تاریخ معتبر: {title[:80]}"
            )

            continue


        # -------------------------------------------------
        # حذف خبر قدیمی
        # -------------------------------------------------

        if article_dt < cutoff:

            print(
                f"  حذف خبر قدیمی: {title[:80]}"
            )

            continue


        # -------------------------------------------------
        # حذف خبرهای نامرتبط
        # -------------------------------------------------

        if contains_excluded_keyword(
            title,
            description
        ):

            print(
                f"  حذف خبر نامرتبط: {title[:80]}"
            )

            continue


        # -------------------------------------------------
        # امتیازدهی
        # -------------------------------------------------

        score, matched = calculate_score(

            title,
            description,
            source,
            feed["category"]
        )


        article["_score"] = score


        print(
            f"  امتیاز {score}: "
            f"{title[:80]}"
        )


        # -------------------------------------------------
        # حداقل امتیاز
        # -------------------------------------------------

        if score < MIN_SCORE:

            print(
                f"  حذف به دلیل امتیاز پایین: "
                f"{title[:80]}"
            )

            continue


        articles.append(
            article
        )


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
# فیلتر و پاک‌سازی اخبار قبلی
# =========================================================

def clean_existing_articles(
    articles
):

    now = datetime.now(
        timezone.utc
    )

    cutoff = now - timedelta(
        days=MAX_AGE_DAYS
    )

    cleaned = []


    for article in articles:

        if not isinstance(
            article,
            dict
        ):

            continue


        title = clean_text(
            article.get(
                "title",
                ""
            )
        )

        summary = clean_text(
            article.get(
                "summary",
                ""
            )
        )

        source = clean_text(
            article.get(
                "source",
                ""
            )
        )

        link = (
            article.get(
                "link",
                ""
            )
            or ""
        ).strip()


        if not title or not link:

            continue


        # حذف شبکه اجتماعی

        if is_blocked_source(
            source,
            link
        ):

            continue


        # تاریخ

        article_dt = article_datetime(
            article
        )

        if article_dt is None:

            continue


        # حذف قدیمی

        if article_dt < cutoff:

            continue


        # حذف نامرتبط

        if contains_excluded_keyword(
            title,
            summary
        ):

            continue


        score, _ = calculate_score(

            title,
            summary,
            source,
            article.get(
                "category",
                ""
            )
        )


        if score < MIN_SCORE:

            continue


        article["_score"] = score

        cleaned.append(
            article
        )


    return cleaned


# =========================================================
# حذف کلیدهای داخلی قبل از ذخیره
# =========================================================

def prepare_for_output(
    articles
):

    result = []

    for article in articles:

        cleaned = dict(
            article
        )

        cleaned.pop(
            "_score",
            None
        )

        result.append(
            cleaned
        )

    return result


# =========================================================
# اجرای اصلی
# =========================================================

def main():

    print("=" * 60)

    print(
        "شروع بروزرسانی خبرخوان چرتکه..."
    )

    print(
        f"بازه زمانی: {MAX_AGE_DAYS} روز اخیر"
    )

    print(
        f"حداکثر اخبار: {MAX_ARTICLES}"
    )

    print(
        f"حداقل امتیاز: {MIN_SCORE}"
    )

    print("=" * 60)


    all_articles = []

    successful_feeds = 0

    failed_feeds = 0


    # -----------------------------------------------------
    # دریافت منابع
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
                f"  خبرهای معتبر: "
                f"{len(articles)}"
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
    # گزارش
    # -----------------------------------------------------

    print()

    print("=" * 60)

    print(
        f"منابع موفق: "
        f"{successful_feeds}"
    )

    print(
        f"منابع ناموفق: "
        f"{failed_feeds}"
    )

    print(
        f"خبرهای دریافت‌شده: "
        f"{len(all_articles)}"
    )

    print("=" * 60)


    # -----------------------------------------------------
    # اگر هیچ RSS موفق نبود
    # -----------------------------------------------------

    if successful_feeds == 0:

        raise RuntimeError(
            "هیچ‌یک از منابع RSS با موفقیت "
            "دریافت نشدند. "
            "news-data.json تغییر نخواهد کرد."
        )


    # -----------------------------------------------------
    # اخبار قبلی
    # -----------------------------------------------------

    old_articles = load_existing()


    # -----------------------------------------------------
    # پاک‌سازی اخبار قبلی
    # -----------------------------------------------------

    old_articles = clean_existing_articles(
        old_articles
    )


    print(
        f"اخبار قبلی پس از پاک‌سازی: "
        f"{len(old_articles)}"
    )


    # -----------------------------------------------------
    # ترکیب اخبار جدید و قدیمی
    # -----------------------------------------------------

    all_articles.extend(
        old_articles
    )


    # -----------------------------------------------------
    # حذف تکراری‌ها
    # -----------------------------------------------------

    unique = {}


    for article in all_articles:

        article_id = article.get(
            "id"
        )

        if not article_id:

            article_id = make_id(

                article.get(
                    "title",
                    ""
                ),

                article.get(
                    "link",
                    ""
                )
            )

            article["id"] = article_id


        if article_id not in unique:

            unique[
                article_id
            ] = article

        else:

            # اگر نسخه جدید امتیاز بیشتری دارد
            old_score = unique[
                article_id
            ].get(
                "_score",
                0
            )

            new_score = article.get(
                "_score",
                0
            )

            if new_score > old_score:

                unique[
                    article_id
                ] = article


    articles = list(
        unique.values()
    )


    # -----------------------------------------------------
    # مرتب‌سازی بر اساس امتیاز + تاریخ
    # -----------------------------------------------------

    def sort_key(article):

        score = article.get(
            "_score",
            0
        )

        dt = article_datetime(
            article
        )

        timestamp = (
            dt.timestamp()
            if dt
            else 0
        )

        return (
            score,
            timestamp
        )


    articles.sort(
        key=sort_key,
        reverse=True
    )


    # -----------------------------------------------------
    # محدود کردن تعداد
    # -----------------------------------------------------

    articles = articles[
        :MAX_ARTICLES
    ]


    # -----------------------------------------------------
    # حذف فیلد داخلی score
    # -----------------------------------------------------

    articles = prepare_for_output(
        articles
    )


    # -----------------------------------------------------
    # مرتب‌سازی نهایی بر اساس تاریخ
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
    # ذخیره
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
        f"تعداد نهایی اخبار: "
        f"{len(articles)}"
    )

    print(
        f"فایل خروجی: "
        f"{OUTPUT_FILE}"
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
