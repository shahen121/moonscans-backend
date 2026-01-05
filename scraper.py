import requests
from bs4 import BeautifulSoup

BASE_URL = "https://moonscans.net"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
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
            "cover": img["src"],
            "url": a["href"]
        })

    return mangas


def get_manga_details(slug: str):
    url = f"{BASE_URL}/manga/{slug}/"
    html = requests.get(url, headers=HEADERS, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("h1")
    title = title.text.strip() if title else ""

    summary_tag = soup.select_one(".entry-content p")
    summary = summary_tag.text.strip() if summary_tag else ""

    chapters = []

    # ✅ MoonScans chapters selector
    for li in soup.select(".eplister li"):
        a = li.select_one("a")
        if not a:
            continue

        chapter_name = li.select_one(".chapternum")
        chapter_name = chapter_name.text.strip() if chapter_name else "Chapter"

        chapters.append({
            "name": chapter_name,
            "url": a["href"]
        })

    # 🔁 ترتيب من الأقدم للأحدث
    chapters.reverse()

    return {
        "title": title,
        "summary": summary,
        "status": "Unknown",
        "chapters": chapters
    }


def get_chapter_images(chapter_url: str):
    html = requests.get(
        chapter_url,          # ✅ الرابط الصحيح
        headers=HEADERS,      # ✅ نفس الهوية
        timeout=15
    ).text

    soup = BeautifulSoup(html, "html.parser")

    images = []
    for img in soup.select(".reading-content img"):
        src = img.get("data-src") or img.get("src")
        if src:
            images.append(src)

    return images
