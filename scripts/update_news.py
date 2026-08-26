# ============================================================
# Chortkeh News Updater - FAIL SAFE VERSION
# Iran / Kerman Focus
# ============================================================

import json
import re
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser


# ============================================================
# SETTINGS
# ============================================================

OUTPUT_FILE = "news-data.json"

MAX_NEWS = 30

REQUEST_TIMEOUT = 12

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


# ============================================================
# APPROVED SOURCES
# ============================================================

SOURCES = [

    {
        "name": "سازمان امور مالیاتی کشور",
        "url": "https://www.intamedia.ir/setad-news"
    },

    {
        "name": "سازمان تأمین اجتماعی",
        "url": "https://tamin.ir/"
    },

    {
        "name": "بانک مرکزی جمهوری اسلامی ایران",
        "url": "https://www.cbi.ir/"
    },

    {
        "name": "جامعه حسابداران رسمی ایران",
        "url": "https://www.iacpa.ir/"
    },

    {
        "name": "اقتصاد آنلاین",
        "url": "https://www.eghtesadonline.com/"
    },

    {
        "name": "وزارت صنعت، معدن و تجارت",
        "url": "https://www.mimt.gov.ir/"
    },

    {
        "name": "اتاق بازرگانی",
        "url": "https://otagh-bazargani.com/"
    },

    {
        "name": "اقتصاد کرمان",
        "url": "https://eghtesadkerman.ir/"
    },

    {
        "name": "وزارت امور اقتصادی و دارایی",
        "url": "https://www.mefa.ir/"
    },

    {
        "name": "سازمان بورس و اوراق بهادار",
        "url": "https://www.seo.ir/"
    }

]


# ============================================================
# FORBIDDEN / UNWANTED DOMAINS
# ============================================================

BLOCKED_DOMAINS = [

    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "youtube.com",

    "iranintl.com",
    "iran-international.com",

    "google.com",
    "news.google.com",

]


# ============================================================
# KEYWORDS
# ============================================================

IRAN_KEYWORDS = [

    "ایران",
    "ایرانی",
    "کشور",
    "دولت",
    "وزارت",
    "سازمان",
    "بانک مرکزی",
    "اقتصاد",
    "اقتصادی",
    "بازار",
    "تولید",
    "صنعت",
    "معدن",
    "معادن",
    "تجارت",
    "صادرات",
    "واردات",
    "سرمایه گذاری",
    "سرمایه‌گذاری",
    "شرکت",
    "کسب و کار",
    "کسب‌وکار",
    "کارفرما",
    "کارگران",
    "کارکنان",

]


KERMAN_KEYWORDS = [

    "کرمان",
    "سیرجان",
    "رفسنجان",
    "زرند",
    "شهربابک",
    "مس سرچشمه",
    "سرچشمه",
    "بم",
    "جیرفت",
    "کهنوج",
    "بردسیر",
    "بافت",
    "رابر",
    "راور",
    "کوهبنان",
    "پابدانا",
    "جنوب کرمان",
    "گل گهر",
    "گل‌گهر",

]


ACCOUNTING_KEYWORDS = [

    "حسابداری",
    "حسابرس",
    "حسابرسی",
    "حسابداران",
    "مالیات",
    "مالیاتی",
    "اظهارنامه",
    "سامانه مؤدیان",
    "سامانه مودیان",
    "ارزش افزوده",
    "بیمه",
    "تأمین اجتماعی",
    "تامین اجتماعی",
    "حقوق و دستمزد",
    "دستمزد",
    "بخشنامه",
    "قانون مالیات",
    "قانون کار",
    "تکالیف مالیاتی",
    "مالیات بر ارزش افزوده",
    "مالیات بر درآمد",

]


FINANCE_KEYWORDS = [

    "بانک",
    "بانکی",
    "نرخ سود",
    "نرخ بهره",
    "ارز",
    "دلار",
    "طلا",
    "بورس",
    "سهام",
    "فرابورس",
    "اوراق",
    "بازار سرمایه",
    "بودجه",
    "خزانه",
    "منابع مالی",
    "تسهیلات",
    "وام",
    "اعتبار",
    "نقدینگی",
    "تورم",

]


INDUSTRY_KEYWORDS = [

    "صنعت",
    "صنایع",
    "معدن",
    "معادن",
    "فولاد",
    "مس",
    "آهن",
    "تولید",
    "کارخانه",
    "پیمانکاری",
    "انرژی",
    "نیروگاه",
    "بازرگانی",
    "تجارت",
    "سرمایه گذاری",
    "سرمایه‌گذاری",

]


ALL_KEYWORDS = (
    IRAN_KEYWORDS
    + KERMAN_KEYWORDS
    + ACCOUNTING_KEYWORDS
    + FINANCE_KEYWORDS
    + INDUSTRY_KEYWORDS
)


# ============================================================
# HTML PARSER
# ============================================================

class LinkParser(HTMLParser):

    def __init__(self, base_url):
        super().__init__()

        self.base_url = base_url

        self.links = []

        self.current_link = None

        self.current_text = []

        self.title = ""

        self.in_title = False

    def handle_starttag(self, tag, attrs):

        attrs = dict(attrs)

        if tag.lower() == "title":
            self.in_title = True

        if tag.lower() == "a":

            href = attrs.get("href")

            if href:

                self.current_link = urljoin(
                    self.base_url,
                    href
                )

                self.current_text = []

    def handle_data(self, data):

        text = data.strip()

        if not text:
            return

        if self.in_title:

            self.title += " " + text

        if self.current_link:

            self.current_text.append(text)

    def handle_endtag(self, tag):

        if tag.lower() == "title":

            self.in_title = False

        if tag.lower() == "a":

            if self.current_link:

                text = " ".join(self.current_text)

                if text:

                    self.links.append(
                        (
                            self.current_link,
                            text
                        )
                    )

            self.current_link = None

            self.current_text = []


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.strip()

    return text


# ============================================================
# PERSIAN TEXT TEST
# ============================================================

def persian_ratio(text):

    if not text:
        return 0

    persian_chars = len(
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

    return persian_chars / letters


def is_persian(text):

    return persian_ratio(text) >= 0.45


# ============================================================
# DOMAIN TEST
# ============================================================

def is_blocked_url(url):

    lower = url.lower()

    for domain in BLOCKED_DOMAINS:

        if domain in lower:

            return True

    return False


# ============================================================
# KEYWORD SCORE
# ============================================================

def keyword_score(text):

    text = text.lower()

    score = 0

    for keyword in ALL_KEYWORDS:

        if keyword.lower() in text:

            score += 1

    return score


def kerman_score(text):

    text = text.lower()

    score = 0

    for keyword in KERMAN_KEYWORDS:

        if keyword.lower() in text:

            score += 1

    return score


# ============================================================
# RELEVANCE TEST
# ============================================================

def is_relevant(title):

    title = clean_text(title)

    if len(title) < 15:

        return False

    if not is_persian(title):

        return False

    score = keyword_score(title)

    kscore = kerman_score(title)

    # اخبار کرمان همیشه پذیرفته شوند
    if kscore >= 1:

        return True

    # اخبار تخصصی مالی / اقتصادی
    if score >= 2:

        return True

    return False


# ============================================================
# DOWNLOAD PAGE
# ============================================================

def fetch_page(url):

    try:

        request = Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),
            }
        )

        with urlopen(
            request,
            timeout=REQUEST_TIMEOUT
        ) as response:

            data = response.read()

            charset = response.headers.get_content_charset()

            if charset:

                encoding = charset

            else:

                encoding = "utf-8"

            return data.decode(
                encoding,
                errors="ignore"
            )

    except Exception as exc:

        print(
            f"  [ERROR] {url}"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )

        return None


# ============================================================
# EXTRACT LINKS
# ============================================================

def extract_links(source_url, html):

    parser = LinkParser(
        source_url
    )

    try:

        parser.feed(html)

    except Exception as exc:

        print(
            f"  [WARN] HTML parser error: {exc}"
        )

    results = []

    for url, text in parser.links:

        text = clean_text(text)

        if not text:

            continue

        if len(text) < 15:

            continue

        if len(text) > 300:

            continue

        if is_blocked_url(url):

            continue

        results.append(
            {
                "title": text,
                "url": url
            }
        )

    return results


# ============================================================
# REMOVE DUPLICATES
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

    seen = set()

    result = []

    for item in items:

        key = normalize_title(
            item["title"]
        )

        if key in seen:

            continue

        seen.add(key)

        result.append(item)

    return result


# ============================================================
# SOURCE PROCESSING
# ============================================================

def process_source(source):

    name = source["name"]

    url = source["url"]

    print()
    print(
        "------------------------------------------------------------"
    )

    print(
        f"[SOURCE] {name}"
    )

    print(
        f"[URL] {url}"
    )

    html = fetch_page(url)

    if not html:

        print(
            "[SKIP] Source unavailable."
        )

        return []

    links = extract_links(
        url,
        html
    )

    print(
        f"[INFO] Links found: {len(links)}"
    )

    selected = []

    for item in links:

        title = item["title"]

        if not is_relevant(title):

            continue

        selected.append(
            {
                "title": title,
                "url": item["url"],
                "source": name
            }
        )

    print(
        f"[INFO] Relevant Persian news: {len(selected)}"
    )

    return selected


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "============================================================"
    )

    print(
        "Chortkeh News Updater - FAIL SAFE"
    )

    print(
        "Iran / Kerman focused news collector"
    )

    print(
        "============================================================"
    )

    print(
        f"Approved sources: {len(SOURCES)}"
    )

    print(
        f"Maximum news: {MAX_NEWS}"
    )

    print(
        f"Timeout per source: {REQUEST_TIMEOUT} seconds"
    )

    print()

    all_news = []

    successful_sources = 0

    failed_sources = 0

    for source in SOURCES:

        try:

            news = process_source(
                source
            )

            if news:

                successful_sources += 1

                all_news.extend(news)

            else:

                failed_sources += 1

        except Exception as exc:

            failed_sources += 1

            print()

            print(
                f"[FATAL-SOURCE-ERROR] "
                f"{source['name']}"
            )

            print(
                f"{type(exc).__name__}: {exc}"
            )

            print(
                "[CONTINUE] Moving to next source..."
            )

        # جلوگیری از فشار زیاد به سایت‌ها
        time.sleep(1)

    print()
    print(
        "============================================================"
    )

    print(
        "Filtering and sorting..."
    )

    print(
        "============================================================"
    )

    all_news = remove_duplicates(
        all_news
    )

    # اولویت:
    # 1. اخبار کرمان
    # 2. اخبار تخصصی مالی/حسابداری
    # 3. سایر اخبار اقتصادی

    def sort_score(item):

        title = item["title"]

        return (
            kerman_score(title) * 10
            + keyword_score(title)
        )

    all_news.sort(
        key=sort_score,
        reverse=True
    )

    final_news = all_news[
        :MAX_NEWS
    ]

    # ========================================================
    # OUTPUT
    # ========================================================

    output = {

        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "language": "fa",

        "region": "Iran / Kerman",

        "source_count": len(SOURCES),

        "successful_sources":
            successful_sources,

        "failed_sources":
            failed_sources,

        "news_count":
            len(final_news),

        "news":
            final_news

    }

    try:

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

        print()
        print(
            "============================================================"
        )

        print(
            f"Successful sources: "
            f"{successful_sources}"
        )

        print(
            f"Failed sources: "
            f"{failed_sources}"
        )

        print(
            f"Collected news: "
            f"{len(all_news)}"
        )

        print(
            f"Final news: "
            f"{len(final_news)}"
        )

        print(
            f"Output file: "
            f"{OUTPUT_FILE}"
        )

        print(
            "News update completed successfully."
        )

        print(
            "============================================================"
        )

    except Exception as exc:

        print()

        print(
            "[OUTPUT ERROR]"
        )

        print(
            f"{type(exc).__name__}: {exc}"
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
