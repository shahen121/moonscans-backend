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
    html = requests.get(
        f"{BASE_URL}/manga/{slug}/",
        headers=HEADERS,
        timeout=15
    ).text

    soup = BeautifulSoup(html, "html.parser")

    chapters = []
    for ch in soup.select(".wp-manga-chapter a"):
        chapters.append({
            "name": ch.text.strip(),
            "url": ch["href"]
        })

    return {
        "title": soup.select_one("h1").text.strip() if soup.select_one("h1") else "",
        "summary": soup.select_one(".summary__content").text.strip() if soup.select_one(".summary__content") else "",
        "status": soup.select_one(".post-status").text.strip() if soup.select_one(".post-status") else "Unknown",
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
