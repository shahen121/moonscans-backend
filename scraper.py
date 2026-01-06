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
        url = f"{BASE_URL}/manga/{slug}/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # جلب قائمة الفصول من المكان الصحيح في Moonscans
        chapters = []
        # الموقع يستخدم كلاس eplister أو وسم مشابه للفصول
        chapter_elements = soup.select(".eplister li")
        
        for li in chapter_elements:
            a_tag = li.select_one("a")
            if a_tag:
                name = li.select_one(".chapternum").text.strip() if li.select_one(".chapternum") else "Chapter"
                link = a_tag['href']
                chapters.append({
                    "name": name,
                    "url": link
                })

        # ترتيب الفصول من الأقدم للأحدث (اختياري)
        chapters.reverse() 

        return {
            "title": soup.select_one("h1.entry-title").text.strip() if soup.select_one("h1.entry-title") else "Unknown",
            "cover": soup.select_one(".thumb img")["src"] if soup.select_one(".thumb img") else "",
            "summary": soup.select_one(".entry-content p").text.strip() if soup.select_one(".entry-content p") else "",
            "chapters": chapters
        }
    except Exception as e:
        print(f"Error in details: {e}")
        return None

def get_chapter_images(chapter_url: str):
    try:
        # التأكد من أننا نستخدم الرابط الحقيقي الممرر
        response = requests.get(chapter_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        images = []

        # في Moonscans، الصور موجودة داخل div بـ id="readerarea"
        reader_area = soup.select_one("#readerarea")
        if reader_area:
            for img in reader_area.find_all("img"):
                # جلب الرابط مع مراعاة التحميل المتأخر
                url = img.get("data-src") or img.get("src") or img.get("data-lazy-src")
                if url:
                    url = url.strip()
                    if url.startswith("//"): url = "https:" + url
                    if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        images.append(url)
        return images
    except Exception as e:
        print(f"Error in images: {e}")
        return []
