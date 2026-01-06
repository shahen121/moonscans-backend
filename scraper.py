import requests
from bs4 import BeautifulSoup

BASE_URL = "https://moonscans.net"

# هوية المتصفح لتجنب الحظر
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://moonscans.net/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}



def get_manga_list():
    try:
        response = requests.get(f"{BASE_URL}/manga/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

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
    except Exception as e:
        print("Error in manga list:", e)
        return []


def get_manga_details(slug: str):
    try:
        response = requests.get(f"{BASE_URL}/manga/{slug}/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.select_one("h1.entry-title")
        title = title.text.strip() if title else "Unknown"

        cover_tag = soup.select_one(".summary_image img")
        cover = cover_tag["src"] if cover_tag else ""

        summary_tag = soup.select_one(".summary__content")
        summary = summary_tag.text.strip() if summary_tag else ""

        chapters = []
        for li in soup.select(".eplister li"):
            a = li.select_one("a")
            chap = li.select_one(".chapternum")
            if not a:
                continue

            chapters.append({
                "name": chap.text.strip() if chap else "Chapter",
                "url": a["href"]
            })

        chapters.reverse()

        return {
            "title": title,
            "cover": cover,
            "summary": summary,
            "status": "Unknown",
            "chapters": chapters
        }
    except Exception as e:
        print("Error in manga details:", e)
        return None


def get_chapter_images(chapter_url: str):
    try:
        response = requests.get(chapter_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        images = []

        # ✅ المكان الصحيح لصور MoonScans
        for img in soup.select("img.ts-main-image"):
            src = img.get("src")
            if src and src.startswith("http"):
                images.append(src.strip())

        return images
    except Exception as e:
        print("Error in chapter images:", e)
        return []
