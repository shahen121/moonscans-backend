import cloudscraper
from bs4 import BeautifulSoup
import time

BASE_URL = "https://mangawy.app"

# استخدام cloudscraper للتغلب على Cloudflare
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    },
    delay=10  # تأخير 10 ثواني لإعادة المحاولة إذا تم حجبنا
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
            
            cover_url = img_tag.get("src", "")
            # تحويل روابط wp.com إلى روابط مباشرة
            if "wp.com" in cover_url:
                cover_url = cover_url.replace("i3.wp.com/", "").replace("i1.wp.com/", "")
            
            mangas.append({
                "title": img_tag.get("alt", "").strip(),
                "slug": a_tag["href"].rstrip("/").split("/")[-1],
                "cover": cover_url,
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
        
        title = soup.select_one("h1.entry-title").text.strip() if soup.select_one("h1.entry-title") else ""
        summary = soup.select_one(".entry-content").text.strip() if soup.select_one(".entry-content") else ""
        status = soup.select_one(".imptdt").text.strip() if soup.select_one(".imptdt") else ""
        
        chapters = []
        chapter_list = soup.select("div#chapterlist ul li")
        for chapter_item in chapter_list:
            a_tag = chapter_item.select_one("a")
            if a_tag:
                chapters.append({
                    "name": a_tag.text.strip(),
                    "url": a_tag["href"]
                })
        
        return {
            "title": title,
            "summary": summary,
            "status": status,
            "chapters": chapters
        }
    except Exception as e:
        print(f"خطأ في جلب تفاصيل المانجا {slug}: {e}")
        return {"title": "", "summary": "", "status": "", "chapters": []}

def get_chapter_images(chapter_url: str):
    """دالة محسّنة للحصول على صور الفصل الأصلية"""
    try:
        print(f"جلب صور الفصل من: {chapter_url}")
        
        response = scraper.get(chapter_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        images = []
        
        # ✅ البحث داخل div#readerarea (مكان صور الفصل)
        reader_area = soup.select_one("div#readerarea")
        if reader_area:
            # البحث عن كل صور ts-main-image
            img_tags = reader_area.select("img.ts-main-image")
            
            for img in img_tags:
                # الحصول على src مباشرة
                img_url = img.get("src") or img.get("data-src")
                
                # تجاهل صورة الـ placeholder والصور المصغرة
                if not img_url or "readerarea.svg" in img_url or "?resize=" in img_url:
                    continue
                
                # تنظيف الروابط
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif not img_url.startswith("http"):
                    img_url = BASE_URL + img_url
                
                images.append(img_url.strip())
        
        # إذا لم نجد صور، نحاول طريقة بديلة
        if not images:
            print("لم يتم العثور على صور، جارٍ المحاولة بطريقة بديلة...")
            all_imgs = soup.select("img")
            for img in all_imgs:
                img_url = img.get("src") or img.get("data-src")
                if img_url and "uploads" in img_url and "?resize=" not in img_url:
                    images.append(img_url)
        
        print(f"✅ تم العثور على {len(images)} صورة")
        return images
        
    except Exception as e:
        print(f"خطأ: {e}")
        return []
