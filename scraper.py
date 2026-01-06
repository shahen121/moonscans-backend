import requests
from bs4 import BeautifulSoup

BASE_URL = "https://moonscans.net"

# هوية المتصفح لتجنب الحظر وضمان الوصول لكل المحتوى
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://moonscans.net/"
}

def get_manga_list():
    url = f"{BASE_URL}/manga/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        mangas = []
        for item in soup.select(".bsx"):
            a_tag = item.select_one("a")
            img_tag = item.select_one("img")
            if not a_tag or not img_tag: continue
            
            mangas.append({
                "title": img_tag.get("alt", "").strip(),
                "slug": a_tag["href"].rstrip("/").split("/")[-1],
                "cover": img_tag.get("src") or img_tag.get("data-src"),
                "url": a_tag["href"]
            })
        return mangas
    except Exception as e:
        print(f"Error in list: {e}")
        return []

def get_manga_details(slug: str):
    url = f"{BASE_URL}/manga/{slug}/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # استخراج البيانات الأساسية (تطابق models.py)
        title = soup.select_one("h1.entry-title").text.strip() if soup.select_one("h1.entry-title") else "Unknown"
        
        # استخراج الملخص بدقة
        summary_tag = soup.select_one(".entry-content p") or soup.select_one(".summary")
        summary = summary_tag.text.strip() if summary_tag else "لا يوجد ملخص متاح."
        
        # استخراج الحالة
        status = "غير معروف"
        for info in soup.select(".tsinfo .imptdt"):
            if "Status" in info.text:
                status = info.select_one("i").text.strip()

        # جلب قائمة الفصول كاملة
        chapters = []
        for link in soup.select("#chapterlist ul li a"):
            chapters.append({
                "name": link.select_one(".chapternum").text.strip() if link.select_one(".chapternum") else link.text.strip(),
                "url": link["href"]
            })

        return {
            "title": title,
            "summary": summary,
            "status": status,
            "chapters": chapters
        }
    except Exception as e:
        print(f"Error in details: {e}")
        return None

def get_chapter_images(chapter_url: str):
    try:
        response = requests.get(chapter_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        images = []
        # البحث عن الصور داخل منطقة القراءة الرئيسية
        for img in soup.select("#readerarea img"):
            # التحقق من كل السمات الممكنة للرابط (لضمان عدم نقص الصور)
            url = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if url and "http" in url:
                images.append(url.strip())
                
        return images
    except Exception as e:
        print(f"Error in images: {e}")
        return []
