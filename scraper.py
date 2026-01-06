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
    "Referer": "https://mangawy.app/"
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
    try:
        response = scraper.get(chapter_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        images = []
        
        # البحث عن الحاويات التي تبدأ بـ data-page (كما في الصورة)
        page_containers = soup.find_all("div", attrs={"data-page": True})
        
        for container in page_containers:
            img_tag = container.find("img")
            if img_tag:
                # محاولة جلب الرابط من src أو data-src (للتغلب على الـ Lazy Load)
                img_url = img_tag.get("src") or img_tag.get("data-src")
                
                if img_url:
                    # تنظيف الرابط
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url
                    images.append(img_url.strip())
        
        # إذا فشلت الطريقة الأولى، نبحث عن كل الصور داخل class="reader-mode"
        if not images:
            reader_div = soup.select_one(".reader-mode")
            if reader_div:
                for img in reader_div.find_all("img"):
                    url = img.get("src") or img.get("data-src")
                    if url and "appswat.com" in url: # النطاق الظاهر في الصورة
                        images.append(url)

        return images
    except Exception as e:
        print(f"Error: {e}")
        return []
