import cloudscraper
from bs4 import BeautifulSoup

BASE_URL = "https://moonscans.net"

# استخدام cloudscraper بدل requests لمشكلة Cloudflare
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://moonscans.net/"
}

def get_manga_list():
    url = BASE_URL + "/manga/"
    try:
        response = scraper.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        mangas = []
        for item in soup.select(".bsx"):
            a_tag = item.select_one("a")
            img_tag = item.select_one("img")
            if not a_tag or not img_tag: 
                continue
            
            mangas.append({
                "title": img_tag.get("alt", "").strip(),
                "slug": a_tag["href"].rstrip("/").split("/")[-1],
                "cover": img_tag["src"],
                "url": a_tag["href"]
            })
        return mangas
    except Exception as e:
        print(f"خطأ في جلب قائمة المانجا: {e}")
        return []

def get_manga_details(slug: str):
    url = f"{BASE_URL}/manga/{slug}/"
    try:
        response = scraper.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        # استخراج العنوان
        title = ""
        title_tag = soup.select_one("h1.entry-title")
        if title_tag:
            title = title_tag.text.strip()
        
        # استخراج الوصف
        summary = ""
        summary_tag = soup.select_one(".entry-content")
        if summary_tag:
            summary = summary_tag.text.strip()
        
        # استخراج الحالة
        status = ""
        status_tag = soup.select_one(".imptdt")
        if status_tag:
            status = status_tag.text.strip()
        
        # استخراج قائمة الفصول (من الأحدث للأقدم)
        chapters = []
        chapter_list = soup.select("div#chapterlist ul li")
        for chapter_item in chapter_list:
            a_tag = chapter_item.select_one("a")
            if a_tag:
                chapter_name = a_tag.text.strip()
                chapter_url = a_tag["href"]
                chapters.append({
                    "name": chapter_name,
                    "url": chapter_url
                })
        
        return {
            "title": title,
            "summary": summary,
            "status": status,
            "chapters": chapters
        }
    except Exception as e:
        print(f"خطأ في جلب تفاصيل المانجا {slug}: {e}")
        return {
            "title": "",
            "summary": "",
            "status": "",
            "chapters": []
        }

def get_chapter_images(chapter_url: str):
    """هذه هي الدالة التي كانت تحتاج التعديل"""
    try:
        # ✅ الآن نستخدم scraper مع الـheaders الصحيحة
        response = scraper.get(chapter_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        images = []
        # البحث عن صور داخل قارئ المانجا (اضبط الـselector حسب الموقع)
        image_containers = soup.select("div#reader img, .reading-content img, .entry-content img, .page-break img")
        
        for img in image_containers:
            img_url = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if img_url:
                # التأكد من أن الرابط كامل
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif not img_url.startswith("http"):
                    img_url = BASE_URL + img_url
                
                images.append(img_url.strip())
        
        return images
    except Exception as e:
        print(f"خطأ في جلب صور الفصل من {chapter_url}: {e}")
        return []
