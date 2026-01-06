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
        soup = BeautifulSoup(response.text, "html.parser")
        
        # جلب العنوان (مرن)
        title_tag = soup.select_one("h1.entry-title") or soup.select_one(".manga-title")
        title = title_tag.text.strip() if title_tag else ""
        
        # جلب القصة
        summary_tag = soup.select_one(".entry-content") or soup.select_one(".synopsis")
        summary = summary_tag.text.strip() if summary_tag else ""
        
        chapters = []
        # البحث عن القائمة (المواقع الجديدة تستخدم كلاسات مثل .eplister أو تضع الفصول في جداول)
        # سنبحث عن الروابط التي تحتوي على كلمة 'read' أو 'chapter'
        chapter_links = soup.select("a[href*='/read/'], a[href*='/chapter/']")
        
        for a_tag in chapter_links:
            name = a_tag.text.strip()
            # استبعاد الروابط المكررة أو الفارغة
            if name and "chapter" in a_tag['href'].lower() or "فصل" in name:
                chapters.append({
                    "name": name,
                    "url": a_tag["href"]
                })
        
        return {
            "title": title,
            "summary": summary,
            "chapters": chapters
        }
    except Exception as e:
        print(f"خطأ في التفاصيل: {e}")
        return {"title": "", "summary": "", "chapters": []}
        

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
