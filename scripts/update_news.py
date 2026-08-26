import json
import re
import html
import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


# ============================================================
# خبرخوان چرتکه - نسخه ایران / کرمان
# ============================================================

OUTPUT_FILE = "news-data.json"

MAX_NEWS = 30
DAYS_BACK = 14
MIN_SCORE = 3

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
)

NOW = datetime.now(timezone.utc)
CUTOFF_DATE = NOW - timedelta(days=DAYS_BACK)


# ============================================================
# منابع و جستجوها
# ============================================================

NEWS_SOURCES = [

    {
        "name": "حسابداری و حسابرسی",
        "category": "حسابداری",
        "queries": [
            "حسابداری",
            "حسابرسی",
            "حسابدار",
            "موسسه حسابرسی",
            "حسابداری شرکت ها",
            "صورت های مالی"
        ]
    },

    {
        "name": "مالیات",
        "category": "مالیات",
        "queries": [
            "مالیات",
            "مالیاتی",
            "سامانه مودیان",
            "مودیان مالیاتی",
            "ارزش افزوده",
            "مالیات بر ارزش افزوده",
            "اظهارنامه مالیاتی"
        ]
    },

    {
        "name": "بیمه و تامین اجتماعی",
        "category": "بیمه",
        "queries": [
            "تامین اجتماعی",
            "تأمین اجتماعی",
            "بیمه کارگران",
            "بیمه کارکنان",
            "حق بیمه",
            "لیست بیمه",
            "بازنشستگی"
        ]
    },

    {
        "name": "اقتصاد ایران",
        "category": "اقتصاد",
        "queries": [
            "اقتصاد ایران",
            "اقتصاد کشور",
            "بازار ایران",
            "تولید ایران",
            "سرمایه گذاری",
            "فعالیت اقتصادی"
        ]
    },

    {
        "name": "کسب و کار و شرکت ها",
        "category": "کسب‌وکار",
        "queries": [
            "کسب و کار",
            "کسب‌وکار",
            "شرکت های ایرانی",
            "شرکت‌های ایرانی",
            "کارآفرینی",
            "بنگاه اقتصادی",
            "تولیدکنندگان"
        ]
    },

    {
        "name": "صنعت و معدن",
        "category": "صنعت و معدن",
        "queries": [
            "معدن ایران",
            "صنایع معدنی",
            "شرکت معدنی",
            "مس ایران",
            "فولاد ایران",
            "صنعت ایران",
            "معادن ایران"
        ]
    },

    {
        "name": "اقتصاد و صنعت کرمان",
        "category": "کرمان",
        "queries": [
            "کرمان اقتصاد",
            "کرمان صنعت",
            "کرمان معدن",
            "کرمان سرمایه گذاری",
            "معادن کرمان",
            "شرکت های کرمان",
            "سیرجان معدن",
            "سیرجان اقتصاد",
            "رفسنجان اقتصاد",
            "رفسنجان معدن",
            "زرند معدن",
            "شهربابک معدن",
            "سرچشمه مس",
            "بم اقتصاد",
            "جیرفت اقتصاد"
        ]
    }
]


# ============================================================
# کلمات مهم برای امتیازدهی
# ============================================================

HIGH_VALUE_KEYWORDS = {
    "مالیات": 5,
    "سامانه مودیان": 6,
    "مودیان مالیاتی": 6,
    "ارزش افزوده": 5,
    "حسابرسی": 5,
    "حسابداری": 5,
    "صورت های مالی": 4,
    "صورت‌های مالی": 4,
    "تامین اجتماعی": 4,
    "تأمین اجتماعی": 4,
    "حق بیمه": 4,
    "معدن": 4,
    "معادن": 4,
    "مس": 4,
    "فولاد": 3,
    "شرکت": 2,
    "سرمایه گذاری": 2,
    "سرمایه‌گذاری": 2,
    "تولید": 2
}


KERMAN_KEYWORDS = {
    "کرمان": 7,
    "سیرجان": 7,
    "رفسنجان": 6,
    "زرند": 6,
    "شهربابک": 6,
    "سرچشمه": 7,
    "بم": 5,
    "جیرفت": 5,
    "انار": 4,
    "بردسیر": 4,
    "راور": 4,
    "کوهبنان": 4
}


# ============================================================
# منابع نامعتبر / تبلیغاتی
# ============================================================

BLOCKED_DOMAINS = [
    "shopify.com",
    "nordvpn.com",
    "investopedia.com",
    "coingape.com"
]


# ============================================================
# ابزارها
# ============================================================

def clean_text(value):
    if not value:
        return ""

    value = html.unescape(value)

    value = re.sub(r"<[^>]+>", " ", value)

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_text(value):
    value = clean_text(value)

    replacements = {
        "ي": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return value.lower()


def make_id(title, link):
    raw = f"{title}|{link}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def parse_date(value):

    if not value:
        return NOW

    value = value.strip()

    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            return dt.astimezone(timezone.utc)

        except Exception:
            continue

    return NOW


def fetch_rss(query):

    encoded_query = quote(query)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}"
        "&hl=fa"
        "&gl=IR"
        "&ceid=IR:fa"
    )

    print(f"  Query: {query}")
    print(f"  URL: {url}")

    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT
        }
    )

    try:

        with urlopen(request, timeout=20) as response:

            data = response.read()

            print(f"  HTTP Status: {response.status}")
            print(f"  Content-Type: {response.headers.get('Content-Type')}")
            print(f"  حجم پاسخ: {len(data)} bytes")

            return data

    except Exception as e:

        print(f"  خطا در دریافت RSS: {e}")

        return None


def extract_source(link):

    if not link:
        return ""

    match = re.search(
        r"https?://(?:www\.)?([^/]+)",
        link
    )

    if match:
        return match.group(1).lower()

    return ""


def is_blocked(link):

    domain = extract_source(link)

    for blocked in BLOCKED_DOMAINS:

        if blocked in domain:
            return True

    return False


def score_article(title, description, category, source):

    text = normalize_text(
        f"{title} {description}"
    )

    score = 0

    # -----------------------------------------
    # امتیاز موضوعی
    # -----------------------------------------

    for keyword, points in HIGH_VALUE_KEYWORDS.items():

        if normalize_text(keyword) in text:
            score += points

    # -----------------------------------------
    # امتیاز کرمان
    # -----------------------------------------

    for keyword, points in KERMAN_KEYWORDS.items():

        if normalize_text(keyword) in text:
            score += points

    # -----------------------------------------
    # امتیاز دسته کرمان
    # -----------------------------------------

    if category == "کرمان":
        score += 3

    # -----------------------------------------
    # خبر فارسی
    # -----------------------------------------

    persian_chars = len(
        re.findall(r"[\u0600-\u06FF]", text)
    )

    latin_chars = len(
        re.findall(r"[A-Za-z]", text)
    )

    if persian_chars > latin_chars:
        score += 3

    # -----------------------------------------
    # کاهش امتیاز خبرهای عمومی انگلیسی
    # -----------------------------------------

    if latin_chars > persian_chars * 2:
        score -= 4

    # -----------------------------------------
    # منبع
    # -----------------------------------------

    if source.endswith(".ir"):
        score += 3

    return score


def parse_rss(data, category):

    if not data:
        return []

    articles = []

    try:

        root = ET.fromstring(data)

    except Exception as e:

        print(f"  خطا در پردازش XML: {e}")

        return []

    items = root.findall(".//item")

    print(f"  تعداد item در RSS: {len(items)}")

    for item in items:

        title = clean_text(
            item.findtext("title", "")
        )

        link = clean_text(
            item.findtext("link", "")
        )

        description = clean_text(
            item.findtext("description", "")
        )

        pub_date = clean_text(
            item.findtext("pubDate", "")
        )

        source_node = item.find("source")

        source_name = ""

        if source_node is not None:

            source_name = clean_text(
                source_node.text or ""
            )

        if not title or not link:
            continue

        if is_blocked(link):
            continue

        published = parse_date(pub_date)

        # خبر خیلی قدیمی نباشد
        if published < CUTOFF_DATE:
            continue

        score = score_article(
            title,
            description,
            category,
            source_name
        )

        if score < MIN_SCORE:
            continue

        articles.append({
            "id": make_id(title, link),
            "title": title,
            "description": description[:500],
            "link": link,
            "source": source_name,
            "category": category,
            "published": published.isoformat(),
            "score": score
        })

    return articles


# ============================================================
# اجرای خبرخوان
# ============================================================

def main():

    print("=" * 60)
    print("شروع بروزرسانی خبرخوان چرتکه...")
    print(f"بازه زمانی: {DAYS_BACK} روز اخیر")
    print(f"حداکثر اخبار: {MAX_NEWS}")
    print(f"حداقل امتیاز: {MIN_SCORE}")
    print("=" * 60)

    all_articles = []

    successful_sources = 0
    failed_sources = 0

    for source in NEWS_SOURCES:

        print()
        print(
            f"دریافت: {source['name']}"
        )

        print(
            f"دسته‌بندی: {source['category']}"
        )

        source_articles = []

        # هر دسته چند Query دارد
        for query in source["queries"]:

            data = fetch_rss(query)

            if data is None:

                failed_sources += 1

                continue

            successful_sources += 1

            articles = parse_rss(
                data,
                source["category"]
            )

            source_articles.extend(articles)

        # حذف تکراری‌های همان دسته

        unique = {}

        for article in source_articles:

            unique[article["id"]] = article

        source_articles = list(
            unique.values()
        )

        print(
            f"  خبرهای معتبر: {len(source_articles)}"
        )

        all_articles.extend(
            source_articles
        )

    # ========================================================
    # حذف اخبار تکراری
    # ========================================================

    unique_articles = {}

    for article in all_articles:

        article_id = article["id"]

        if article_id not in unique_articles:

            unique_articles[article_id] = article

        else:

            # اگر همان خبر در چند Query دیده شد
            # بالاترین امتیاز را نگه می‌داریم

            if (
                article["score"]
                > unique_articles[article_id]["score"]
            ):

                unique_articles[article_id] = article

    all_articles = list(
        unique_articles.values()
    )

    # ========================================================
    # مرتب‌سازی
    # ========================================================

    all_articles.sort(
        key=lambda x: (
            x["score"],
            x["published"]
        ),
        reverse=True
    )

    # ========================================================
    # محدود کردن تعداد اخبار
    # ========================================================

    final_articles = all_articles[:MAX_NEWS]

    # ========================================================
    # خروجی
    # ========================================================

    output = {
        "updated": datetime.now(
            timezone.utc
        ).isoformat(),

        "count": len(final_articles),

        "articles": final_articles
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 60)

    print(
        f"منابع موفق: {successful_sources}"
    )

    print(
        f"منابع ناموفق: {failed_sources}"
    )

    print(
        f"خبرهای دریافت‌شده: {len(all_articles)}"
    )

    print(
        f"تعداد نهایی اخبار: {len(final_articles)}"
    )

    print(
        f"فایل خروجی: {OUTPUT_FILE}"
    )

    print(
        "خبرخوان با موفقیت بروزرسانی شد."
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
