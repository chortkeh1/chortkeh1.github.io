# -*- coding: utf-8 -*-

"""
خبرخوان مؤسسه حسابداری و حسابرسی چرتکه
نسخه اختصاصی ایران / کرمان

ویژگی‌ها:
- بدون Google News
- منابع مشخص و قابل کنترل
- اولویت RSS
- استخراج HTML در صورت نبود RSS
- فقط اخبار فارسی
- فیلتر موضوعی
- حذف منابع نامطلوب
- امتیازدهی هوشمند
- حذف اخبار تکراری
- محدودیت سنی اخبار
- خروجی news-data.json
"""

import json
import re
import html
import hashlib
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime


# ============================================================
# تنظیمات اصلی
# ============================================================

OUTPUT_FILE = "news-data.json"

MAX_NEWS = 30

MAX_AGE_DAYS = 14

MIN_SCORE = 5

REQUEST_TIMEOUT = 25

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0 Safari/537.36"
)


# ============================================================
# منابع خبری
# ============================================================

SOURCES = [

    {
        "name": "سازمان امور مالیاتی",
        "category": "مالیات",
        "url": "https://www.intamedia.ir/setad-news",
        "rss": [
            "https://www.intamedia.ir/rss",
            "https://www.intamedia.ir/rss.xml"
        ],
        "keywords": [
            "مالیات",
            "مالیاتی",
            "سامانه مودیان",
            "سامانه مؤدیان",
            "مودیان",
            "مودیان مالیاتی",
            "ارزش افزوده",
            "اظهارنامه",
            "مالیات بر ارزش افزوده",
            "مالیات بر درآمد",
            "مالیات شرکت",
            "مالیات اشخاص حقوقی",
            "صورتحساب الکترونیکی"
        ],
        "priority": 10
    },


    {
        "name": "سازمان تأمین اجتماعی",
        "category": "بیمه",
        "url": "https://tamin.ir/",
        "rss": [
            "https://news.tamin.ir/rss",
            "https://news.tamin.ir/rss.xml",
            "https://news.tamin.ir/feed",
            "https://tamin.ir/rss",
            "https://tamin.ir/rss.xml"
        ],
        "keywords": [
            "تامین اجتماعی",
            "تأمین اجتماعی",
            "حق بیمه",
            "بیمه",
            "بیمه کارگران",
            "بیمه کارکنان",
            "کارفرما",
            "لیست بیمه",
            "بازنشستگی",
            "مستمری",
            "مفاصا حساب",
            "بیمه اجباری",
            "بیمه کارفرمایان"
        ],
        "priority": 10
    },


    {
        "name": "بانک مرکزی جمهوری اسلامی ایران",
        "category": "اقتصاد",
        "url": "https://www.cbi.ir/",
        "rss": [
            "https://www.cbi.ir/rss.aspx",
            "https://www.cbi.ir/rss.aspx?type=1"
        ],
        "keywords": [
            "بانک مرکزی",
            "بانکی",
            "بانک",
            "نرخ سود",
            "نرخ بهره",
            "ارز",
            "دلار",
            "تسهیلات",
            "اعتبار",
            "تورم",
            "پول",
            "نقدینگی",
            "سیاست پولی",
            "شبکه بانکی"
        ],
        "priority": 8
    },


    {
        "name": "جامعه حسابداران رسمی ایران",
        "category": "حسابداری و حسابرسی",
        "url": "https://www.iacpa.ir/",
        "rss": [
            "https://www.iacpa.ir/rss",
            "https://www.iacpa.ir/rss.xml",
            "https://www.iacpa.ir/feed"
        ],
        "keywords": [
            "حسابداری",
            "حسابرس",
            "حسابرسی",
            "حسابداران رسمی",
            "جامعه حسابداران رسمی",
            "استاندارد حسابداری",
            "استاندارد حسابرسی",
            "صورت های مالی",
            "صورت‌های مالی",
            "گزارش حسابرس",
            "موسسه حسابرسی",
            "مؤسسه حسابرسی"
        ],
        "priority": 10
    },


    {
        "name": "اقتصاد آنلاین",
        "category": "اقتصاد و کسب‌وکار",
        "url": "https://www.eghtesadonline.com/",
        "rss": [
            "https://www.eghtesadonline.com/rss",
            "https://www.eghtesadonline.com/rss.xml",
            "https://www.eghtesadonline.com/feed"
        ],
        "keywords": [
            "اقتصاد",
            "اقتصادی",
            "کسب و کار",
            "کسب‌وکار",
            "شرکت",
            "تولید",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "بازار",
            "بانک",
            "مالیات",
            "بورس",
            "صنعت",
            "تجارت"
        ],
        "priority": 6
    },


    {
        "name": "وزارت صنعت، معدن و تجارت",
        "category": "صنعت و معدن",
        "url": "https://www.mimt.gov.ir/",
        "rss": [
            "https://www.mimt.gov.ir/rss",
            "https://www.mimt.gov.ir/rss.xml",
            "https://www.mimt.gov.ir/feed"
        ],
        "keywords": [
            "صمت",
            "صنعت",
            "معدن",
            "معادن",
            "معدنی",
            "تولید",
            "تولیدکننده",
            "فولاد",
            "مس",
            "صنایع معدنی",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "تجارت",
            "بازرگانی"
        ],
        "priority": 9
    },


    {
        "name": "اتاق بازرگانی",
        "category": "تجارت و کسب‌وکار",
        "url": "https://otagh-bazargani.com/",
        "rss": [
            "https://otagh-bazargani.com/rss",
            "https://otagh-bazargani.com/rss.xml",
            "https://otagh-bazargani.com/feed"
        ],
        "keywords": [
            "اتاق بازرگانی",
            "بازرگانی",
            "تجارت",
            "کسب و کار",
            "کسب‌وکار",
            "صادرات",
            "واردات",
            "شرکت",
            "تولید",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "فعال اقتصادی"
        ],
        "priority": 7
    },


    {
        "name": "اقتصاد کرمان",
        "category": "کرمان",
        "url": "https://eghtesadkerman.ir/",
        "rss": [
            "https://eghtesadkerman.ir/rss",
            "https://eghtesadkerman.ir/rss.xml",
            "https://eghtesadkerman.ir/feed"
        ],
        "keywords": [
            "کرمان",
            "سیرجان",
            "رفسنجان",
            "زرند",
            "شهربابک",
            "سرچشمه",
            "گل گهر",
            "گل‌گهر",
            "بم",
            "جیرفت",
            "بافت",
            "بردسیر",
            "کوهبنان",
            "راور",
            "معدن کرمان",
            "صنعت کرمان",
            "اقتصاد کرمان",
            "سرمایه گذاری کرمان",
            "سرمایه‌گذاری کرمان"
        ],
        "priority": 12
    },


    {
        "name": "وزارت امور اقتصادی و دارایی",
        "category": "اقتصاد و امور مالی",
        "url": "https://www.mefa.ir/",
        "rss": [
            "https://www.mefa.ir/rss",
            "https://www.mefa.ir/rss.xml",
            "https://www.mefa.ir/feed"
        ],
        "keywords": [
            "اقتصاد",
            "امور اقتصادی",
            "دارایی",
            "مالیات",
            "گمرک",
            "سرمایه گذاری",
            "سرمایه‌گذاری",
            "تولید",
            "تامین مالی",
            "تأمین مالی",
            "خصوصی سازی",
            "خصوصی‌سازی",
            "بدهی",
            "بودجه",
            "بانک"
        ],
        "priority": 8
    },


    {
        "name": "سازمان بورس و اوراق بهادار",
        "category": "بورس و بازار سرمایه",
        "url": "https://www.seo.ir/",
        "rss": [
            "https://www.seo.ir/rss",
            "https://www.seo.ir/rss.xml",
            "https://www.seo.ir/feed"
        ],
        "keywords": [
            "بورس",
            "بازار سرمایه",
            "اوراق بهادار",
            "سازمان بورس",
            "شرکت بورسی",
            "صورت های مالی",
            "صورت‌های مالی",
            "گزارش مالی",
            "مجمع",
            "سهام",
            "سرمایه گذاری",
            "سرمایه‌گذاری"
        ],
        "priority": 7
    }

]


# ============================================================
# کلمات حذف
# ============================================================

EXCLUDE_KEYWORDS = [

    "فوتبال",
    "ورزش",
    "لیگ",
    "استقلال",
    "پرسپولیس",
    "والیبال",
    "بسکتبال",

    "سینما",
    "بازیگر",
    "فیلم",
    "تلویزیون",
    "موسیقی",
    "خواننده",

    "فال",
    "سرگرمی",
    "عکس روز",

    "تصادف",
    "قتل",
    "حوادث",

    "اینستاگرام",
    "فیسبوک",
    "فیس بوک",
    "تلگرام",

    "ترامپ",
    "جنگ اسرائیل",
    "جنگ غزه"
]


# ============================================================
# منابع غیرمجاز
# ============================================================

BLOCKED_DOMAINS = [

    "facebook.com",
    "www.facebook.com",

    "instagram.com",
    "www.instagram.com",

    "twitter.com",
    "x.com",

    "t.me",
    "telegram.me",

    "iranintl.com",
    "www.iranintl.com",

    "youtube.com",
    "www.youtube.com"
]


# ============================================================
# Session
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": USER_AGENT,
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.5"
})


# ============================================================
# ابزارهای عمومی
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = html.unescape(str(text))

    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "‌": " ",
        "\u200c": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def is_persian(text):

    if not text:
        return False

    persian_chars = len(
        re.findall(
            r"[آ-ی]",
            text
        )
    )

    latin_chars = len(
        re.findall(
            r"[A-Za-z]",
            text
        )
    )

    if persian_chars < 8:
        return False

    if latin_chars > persian_chars * 2:
        return False

    return True


def clean_html(text):

    if not text:
        return ""

    soup = BeautifulSoup(
        text,
        "html.parser"
    )

    text = soup.get_text(
        " ",
        strip=True
    )

    return normalize_text(text)


def parse_date(value):

    if not value:
        return None

    value = str(value).strip()

    # RSS استاندارد
    try:
        return parsedate_to_datetime(value)
    except Exception:
        pass

    # ISO
    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except Exception:
        pass

    # تاریخ فارسی/عددی ساده
    patterns = [
        r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})",
        r"(\d{4})\.(\d{1,2})\.(\d{1,2})"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            value
        )

        if match:

            try:

                return datetime(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                    tzinfo=timezone.utc
                )

            except Exception:
                pass

    return None


def make_id(title, url):

    raw = (
        normalize_text(title)
        + "|"
        + normalize_text(url)
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:16]


def domain_of(url):

    try:

        domain = urlparse(
            url
        ).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:

        return ""


def is_blocked_url(url):

    domain = domain_of(url)

    for blocked in BLOCKED_DOMAINS:

        if domain == blocked:
            return True

        if domain.endswith("." + blocked):
            return True

    return False


# ============================================================
# دریافت URL
# ============================================================

def fetch(url):

    try:

        response = session.get(
            url,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        response.encoding = (
            response.apparent_encoding
            or response.encoding
            or "utf-8"
        )

        return response

    except Exception as exc:

        print(
            f"  خطا در دریافت: {exc}"
        )

        return None


# ============================================================
# استخراج RSS
# ============================================================

def parse_rss(
    content,
    source
):

    soup = BeautifulSoup(
        content,
        "xml"
    )

    items = soup.find_all(
        ["item", "entry"]
    )

    results = []

    for item in items:

        title_tag = item.find(
            ["title"]
        )

        link_tag = item.find(
            ["link"]
        )

        description_tag = item.find(
            ["description", "summary", "content"]
        )

        date_tag = item.find(
            [
                "pubDate",
                "published",
                "updated",
                "dc:date"
            ]
        )

        title = (
            title_tag.get_text(
                " ",
                strip=True
            )
            if title_tag
            else ""
        )

        url = ""

        if link_tag:

            if link_tag.get("href"):

                url = link_tag.get(
                    "href"
                )

            else:

                url = link_tag.get_text(
                    " ",
                    strip=True
                )

        description = (
            description_tag.get_text(
                " ",
                strip=True
            )
            if description_tag
            else ""
        )

        date = (
            date_tag.get_text(
                " ",
                strip=True
            )
            if date_tag
            else ""
        )

        if not url:
            continue

        url = urljoin(
            source["url"],
            url
        )

        results.append({
            "title": normalize_text(title),
            "url": url,
            "summary": clean_html(description),
            "date": parse_date(date),
            "source": source["name"],
            "category": source["category"],
            "priority": source["priority"]
        })

    return results


# ============================================================
# استخراج لینک‌های صفحه HTML
# ============================================================

def parse_html_page(
    content,
    source
):

    soup = BeautifulSoup(
        content,
        "html.parser"
    )

    results = []

    # لینک‌هایی که احتمالاً خبر هستند
    links = soup.find_all(
        "a",
        href=True
    )

    seen = set()

    for link in links:

        title = normalize_text(
            link.get_text(
                " ",
                strip=True
            )
        )

        href = link.get(
            "href"
        )

        if not title or not href:
            continue

        if len(title) < 20:
            continue

        if len(title) > 300:
            continue

        url = urljoin(
            source["url"],
            href
        )

        if url in seen:
            continue

        seen.add(url)

        # فقط لینک‌های همان دامنه
        source_domain = domain_of(
            source["url"]
        )

        link_domain = domain_of(
            url
        )

        if link_domain and link_domain != source_domain:
            continue

        # حذف لینک‌های عمومی
        lower_url = url.lower()

        bad_parts = [
            "/contact",
            "/about",
            "/login",
            "/search",
            "/archive",
            "/gallery",
            "/video",
            "/photo"
        ]

        if any(
            part in lower_url
            for part in bad_parts
        ):
            continue

        # پیدا کردن والد برای خلاصه
        summary = ""

        parent = link.parent

        if parent:

            parent_text = normalize_text(
                parent.get_text(
                    " ",
                    strip=True
                )
            )

            if len(parent_text) > len(title):

                summary = parent_text

                summary = summary.replace(
                    title,
                    ""
                ).strip()

        results.append({
            "title": title,
            "url": url,
            "summary": summary[:500],
            "date": None,
            "source": source["name"],
            "category": source["category"],
            "priority": source["priority"]
        })

    return results


# ============================================================
# پیدا کردن RSS
# ============================================================

def discover_rss(
    source
):

    response = fetch(
        source["url"]
    )

    if not response:
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    discovered = []

    for tag in soup.find_all(
        "link",
        href=True
    ):

        rel = tag.get(
            "rel",
            []
        )

        rel_text = " ".join(
            rel
        ).lower()

        typ = tag.get(
            "type",
            ""
        ).lower()

        if (
            "alternate" in rel_text
            and (
                "rss" in typ
                or "atom" in typ
                or "xml" in typ
            )
        ):

            discovered.append(
                urljoin(
                    source["url"],
                    tag["href"]
                )
            )

    return discovered


# ============================================================
# دریافت اخبار یک منبع
# ============================================================

def fetch_source(
    source
):

    print()
    print(
        f"دریافت: {source['name']}"
    )

    # --------------------------------------------------------
    # اول RSS های مشخص
    # --------------------------------------------------------

    rss_urls = list(
        source.get(
            "rss",
            []
        )
    )

    # --------------------------------------------------------
    # سپس RSS کشف‌شده
    # --------------------------------------------------------

    discovered = discover_rss(
        source
    )

    for url in discovered:

        if url not in rss_urls:
            rss_urls.append(url)

    # --------------------------------------------------------
    # امتحان RSS
    # --------------------------------------------------------

    for rss_url in rss_urls:

        print(
            f"  RSS: {rss_url}"
        )

        response = fetch(
            rss_url
        )

        if not response:
            continue

        content_type = (
            response.headers.get(
                "content-type",
                ""
            ).lower()
        )

        text_start = response.text[
            :500
        ].lower()

        if (
            "xml" not in content_type
            and "<rss" not in text_start
            and "<feed" not in text_start
        ):
            continue

        items = parse_rss(
            response.text,
            source
        )

        if items:

            print(
                f"  تعداد RSS: {len(items)}"
            )

            return items

    # --------------------------------------------------------
    # اگر RSS نبود، HTML
    # --------------------------------------------------------

    print(
        "  RSS قابل استفاده پیدا نشد؛ بررسی HTML..."
    )

    response = fetch(
        source["url"]
    )

    if not response:
        return []

    items = parse_html_page(
        response.text,
        source
    )

    print(
        f"  تعداد لینک‌های استخراج‌شده: {len(items)}"
    )

    return items


# ============================================================
# امتیازدهی خبر
# ============================================================

def score_news(
    item
):

    title = normalize_text(
        item.get(
            "title",
            ""
        )
    )

    summary = normalize_text(
        item.get(
            "summary",
            ""
        )
    )

    text = (
        title
        + " "
        + summary
    )

    score = int(
        item.get(
            "priority",
            0
        )
    )

    source = item.get(
        "source",
        ""
    )

    category = item.get(
        "category",
        ""
    )

    # --------------------------------------------------------
    # امتیاز موضوع
    # --------------------------------------------------------

    for keyword in [
        "مالیات",
        "سامانه مودیان",
        "سامانه مؤدیان",
        "ارزش افزوده",
        "اظهارنامه",
        "صورتحساب الکترونیکی"
    ]:

        if keyword in text:
            score += 5

    for keyword in [
        "حسابداری",
        "حسابرس",
        "حسابرسی",
        "حسابداران رسمی",
        "صورت های مالی",
        "صورت‌های مالی"
    ]:

        if keyword in text:
            score += 5

    for keyword in [
        "تامین اجتماعی",
        "تأمین اجتماعی",
        "حق بیمه",
        "لیست بیمه",
        "کارفرما",
        "بازنشستگی"
    ]:

        if keyword in text:
            score += 5

    for keyword in [
        "معدن",
        "معادن",
        "صنعت",
        "مس",
        "فولاد",
        "تولید"
    ]:

        if keyword in text:
            score += 3

    # --------------------------------------------------------
    # کرمان امتیاز ویژه دارد
    # --------------------------------------------------------

    kerman_keywords = [
        "کرمان",
        "سیرجان",
        "رفسنجان",
        "زرند",
        "شهربابک",
        "سرچشمه",
        "گل گهر",
        "گل‌گهر",
        "بم",
        "جیرفت",
        "بافت",
        "بردسیر",
        "کوهبنان",
        "راور"
    ]

    for keyword in kerman_keywords:

        if keyword in text:

            score += 8

            break

    # --------------------------------------------------------
    # منبع اختصاصی کرمان
    # --------------------------------------------------------

    if source == "اقتصاد کرمان":

        score += 8

    # --------------------------------------------------------
    # خبرهای خیلی کوتاه
    # --------------------------------------------------------

    if len(title) < 30:

        score -= 2

    # --------------------------------------------------------
    # کلمات نامرتبط
    # --------------------------------------------------------

    for keyword in EXCLUDE_KEYWORDS:

        if keyword in text:

            score -= 20

    # --------------------------------------------------------
    # انگلیسی بودن
    # --------------------------------------------------------

    if not is_persian(
        title
    ):

        score -= 30

    # --------------------------------------------------------
    # دسته‌های بسیار مرتبط
    # --------------------------------------------------------

    if category in [
        "مالیات",
        "بیمه",
        "حسابداری و حسابرسی",
        "صنعت و معدن",
        "کرمان"
    ]:

        score += 3

    return score


# ============================================================
# اعتبارسنجی خبر
# ============================================================

def validate_news(
    item
):

    title = normalize_text(
        item.get(
            "title",
            ""
        )
    )

    url = item.get(
        "url",
        ""
    )

    if not title:
        return False

    if not url:
        return False

    if is_blocked_url(
        url
    ):
        return False

    if not is_persian(
        title
    ):
        return False

    # حذف عنوان‌های نامرتبط
    lower_title = title.lower()

    for keyword in EXCLUDE_KEYWORDS:

        if keyword in lower_title:
            return False

    # باید حداقل یک کلیدواژه مرتبط وجود داشته باشد
    combined = normalize_text(
        title
        + " "
        + item.get(
            "summary",
            ""
        )
    )

    relevant_keywords = [

        "حسابداری",
        "حسابرس",
        "حسابرسی",
        "مالیات",
        "مالیاتی",
        "مودیان",
        "ارزش افزوده",
        "اظهارنامه",

        "تامین اجتماعی",
        "تأمین اجتماعی",
        "بیمه",
        "حق بیمه",
        "کارفرما",

        "اقتصاد",
        "اقتصادی",
        "بانک",
        "بانکی",
        "سرمایه گذاری",
        "سرمایه‌گذاری",
        "تولید",
        "تجارت",

        "صنعت",
        "معدن",
        "مس",
        "فولاد",

        "کرمان",
        "سیرجان",
        "رفسنجان",
        "زرند",
        "شهربابک",
        "سرچشمه",
        "گل گهر",
        "گل‌گهر",
        "بم",
        "جیرفت"
    ]

    if not any(
        keyword in combined
        for keyword in relevant_keywords
    ):

        return False

    return True


# ============================================================
# تاریخ و پاکسازی
# ============================================================

def process_date(
    item
):

    date = item.get(
        "date"
    )

    if date is None:

        # برای HTML که تاریخ ندارد،
        # فعلاً تاریخ امروز را ثبت می‌کنیم.
        return datetime.now(
            timezone.utc
        )

    if date.tzinfo is None:

        date = date.replace(
            tzinfo=timezone.utc
        )

    return date


def remove_old_news(
    items
):

    now = datetime.now(
        timezone.utc
    )

    cutoff = (
        now
        - timedelta(
            days=MAX_AGE_DAYS
        )
    )

    result = []

    for item in items:

        date = process_date(
            item
        )

        if date >= cutoff:

            item["date"] = date

            result.append(
                item
            )

    return result


# ============================================================
# حذف تکراری
# ============================================================

def remove_duplicates(
    items
):

    seen_ids = set()

    result = []

    for item in items:

        news_id = make_id(
            item["title"],
            item["url"]
        )

        if news_id in seen_ids:
            continue

        seen_ids.add(
            news_id
        )

        item["id"] = news_id

        result.append(
            item
        )

    return result


# ============================================================
# خروجی JSON
# ============================================================

def prepare_output(
    items
):

    output = []

    for item in items:

        date = item.get(
            "date"
        )

        if isinstance(
            date,
            datetime
        ):

            date_string = date.astimezone(
                timezone.utc
            ).isoformat()

        else:

            date_string = str(
                date or ""
            )

        output.append({

            "id": item.get(
                "id",
                ""
            ),

            "title": normalize_text(
                item.get(
                    "title",
                    ""
                )
            ),

            "summary": normalize_text(
                item.get(
                    "summary",
                    ""
                )
            )[:500],

            "url": item.get(
                "url",
                ""
            ),

            "source": item.get(
                "source",
                ""
            ),

            "category": item.get(
                "category",
                ""
            ),

            "date": date_string,

            "score": int(
                item.get(
                    "score",
                    0
                )
            )
        })

    return output


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "شروع بروزرسانی خبرخوان چرتکه"
    )

    print(
        "نسخه: ایران / کرمان / منابع اختصاصی"
    )

    print(
        f"حداکثر اخبار: {MAX_NEWS}"
    )

    print(
        f"بازه زمانی: {MAX_AGE_DAYS} روز"
    )

    print(
        f"حداقل امتیاز: {MIN_SCORE}"
    )

    print("=" * 60)


    all_news = []

    successful_sources = 0

    failed_sources = 0


    # ========================================================
    # دریافت منابع
    # ========================================================

    for source in SOURCES:

        try:

            items = fetch_source(
                source
            )

            if items:

                successful_sources += 1

                print(
                    f"  منبع موفق: {source['name']}"
                )

                all_news.extend(
                    items
                )

            else:

                failed_sources += 1

                print(
                    f"  منبع بدون خبر: {source['name']}"
                )

        except Exception as exc:

            failed_sources += 1

            print(
                f"  خطای منبع {source['name']}: {exc}"
            )

        time.sleep(1)


    print()
    print("=" * 60)

    print(
        f"منابع موفق: {successful_sources}"
    )

    print(
        f"منابع ناموفق: {failed_sources}"
    )

    print(
        f"خبرهای اولیه: {len(all_news)}"
    )

    print("=" * 60)


    # ========================================================
    # حذف اخبار قدیمی
    # ========================================================

    all_news = remove_old_news(
        all_news
    )

    print(
        f"پس از حذف اخبار قدیمی: {len(all_news)}"
    )


    # ========================================================
    # اعتبارسنجی
    # ========================================================

    valid_news = []

    for item in all_news:

        if validate_news(
            item
        ):

            valid_news.append(
                item
            )

    print(
        f"پس از فیلتر موضوعی: {len(valid_news)}"
    )


    # ========================================================
    # امتیازدهی
    # ========================================================

    for item in valid_news:

        item["score"] = score_news(
            item
        )


    # ========================================================
    # حذف امتیاز پایین
    # ========================================================

    valid_news = [
        item
        for item in valid_news
        if item["score"] >= MIN_SCORE
    ]

    print(
        f"پس از حداقل امتیاز: {len(valid_news)}"
    )


    # ========================================================
    # حذف تکراری
    # ========================================================

    valid_news = remove_duplicates(
        valid_news
    )

    print(
        f"پس از حذف تکراری‌ها: {len(valid_news)}"
    )


    # ========================================================
    # مرتب‌سازی
    # ========================================================

    valid_news.sort(
        key=lambda item: (
            item.get(
                "score",
                0
            ),
            process_date(
                item
            )
        ),
        reverse=True
    )


    # ========================================================
    # انتخاب نهایی
    # ========================================================

    final_news = valid_news[
        :MAX_NEWS
    ]


    # ========================================================
    # خروجی
    # ========================================================

    output = prepare_output(
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


    # ========================================================
    # گزارش
    # ========================================================

    print()
    print("=" * 60)

    print(
        f"تعداد نهایی اخبار: {len(output)}"
    )

    print(
        f"فایل خروجی: {OUTPUT_FILE}"
    )

    print(
        "خبرخوان با موفقیت بروزرسانی شد."
    )

    print("=" * 60)


    # ========================================================
    # نمایش اخبار نهایی برای بررسی
    # ========================================================

    print()

    print(
        "اخبار انتخاب‌شده:"
    )

    print("-" * 60)

    for index, item in enumerate(
        output,
        start=1
    ):

        print(
            f"{index}. "
            f"[{item['category']}] "
            f"{item['title']} "
            f"(امتیاز: {item['score']})"
        )

    print("-" * 60)


if __name__ == "__main__":

    main()
