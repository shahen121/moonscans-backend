import requests
from bs4 import BeautifulSoup

BASE_URL = "https://moonscans.net"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://moonscans.net/"
}


def get_manga_list():
    html = requests.get(f"{BASE_URL}/manga/", headers=HEADERS, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    mangas = []

    for item in soup.select(".bsx"):
        a = item.select_one("a")
        img = item.select_one("img")

        if not a or not img:
            continue

        mangas.append({
            "title": img.get("alt", "").strip(),
            "slug": a["href"].rstrip("/").split("/")[-1],
            "cover": img.get("src"),
            "url": a["href"]
        })

    return mangas


def get_manga_details(slug: str):
    url = f"{BASE_URL}/manga/{slug}/"
    html = requests.get(url, headers=HEADERS, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    # 🟢 العنوان
    title_tag = soup.select_one("h1")
    title = title_tag.text.strip() if title_tag else ""

    # 🟢 صورة الغلاف
    cover_tag = soup.select_one(".summary_image img")
    cover = cover_tag["src"] if cover_tag else ""

    # 🟢 الملخص
    summary_tag = soup.select_one(".summary__content")
    summary = summary_tag.text.strip() if summary_tag else ""

    # 🟢 الفصول
    chapters = []
    for li in soup.select(".eplister li"):
        a = li.select_one("a")
        chap_num = li.select_one(".chapternum")

        if not a:
            continue

        chapters.append({
            "name": chap_num.text.strip() if chap_num else "Chapter",
            "url": a["href"]
        })

    chapters.reverse()  # من الأقدم للأحدث

    return {
        "title": title,
        "cover": cover,
        "summary": summary,
        "status": "Unknown",
        "chapters": chapters
    }


def get_chapter_images(chapter_url: str):
    html = requests.get(chapter_url, headers=HEADERS, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    images = []
    for img in soup.select(".reading-content img"):
        src = img.get("data-src") or img.get("src")
        if src:
            images.append(src)

    return images
