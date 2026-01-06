import cloudscraper
from bs4 import BeautifulSoup
import json
import urllib.parse
from typing import List, Dict, Any

# --- الإعدادات الأساسية ---
BASE_URL = "https://mangawy.app"

# إعداد الـ Scraper لتجاوز حماية Cloudflare
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
    "Referer": BASE_URL + "/"
}

# --- الدوال المساعدة ---

def clean_url(url: str) -> str:
    """تنظيف وتنسيق الروابط"""
    if not url: return ""
    url = url.strip()
    if url.startswith("//"):
        return "https:" + url
    return url

# --- الدوال الرئيسية ---

def get_manga_list() -> List[Dict[str, str]]:
    """جلب قائمة المانجا من الصفحة الرئيسية"""
    url = f"{BASE_URL}/manga/"
    try:
        response = scraper.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        mangas = []
        # البحث عن العناصر التي تحتوي على المانجا (بناءً على الكلاس الشائع)
        for item in soup.select(".bsx, .listupd .bs"):
            a_tag = item.select_one("a")
            img_tag = item.select_one("img")
            
            if a_tag and img_tag:
                cover_url = img_tag.get("src") or img_tag.get("data-src") or ""
                mangas.append({
                    "title": img_tag.get("alt", "").strip(),
                    "slug": a_tag["href"].rstrip("/").split("/")[-1],
                    "cover": clean_url(cover_url),
                    "url": a_tag["href"]
                })
        return mangas
    except Exception as e:
        print(f"Error in get_manga_list: {e}")
        return []

def get_manga_details(slug: str) -> Dict[str, Any]:
    """جلب تفاصيل المانجا باستخدام JSON-LD والـ HTML كخيار احتياطي"""
    url = f"{BASE_URL}/manga/{slug}/"
    try:
        response = scraper.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        result = {
            "title": "",
            "summary": "",
            "chapters": []
        }

        # 1. محاولة استخراج البيانات من سكريبت JSON-LD (الأكثر استقراراً)
        json_script = soup.find("script", type="application/ld+json")
        if json_script:
            try:
                data = json.loads(json_script.string)
                graphs = data.get("@graph", [data]) if isinstance(data, dict) else []
                for entry in graphs:
                    if entry.get("@type") in ["Manga", "Article", "Product"]:
                        result["title"] = entry.get("name") or entry.get("headline")
                        result["summary"] = entry.get("description")
                        break
            except: pass

        # 2. خيار احتياطي (Fallback) إذا كان JSON ناقصاً
        if not result["title"]:
            title_tag = soup.select_one("h1.entry-title, .manga-title")
            result["title"] = title_tag.text.strip() if title_tag else ""
        
        if not result["summary"]:
            sum_tag = soup.select_one(".entry-content, .synopsis")
            result["summary"] = sum_tag.text.strip() if sum_tag else ""

        # 3. جلب الفصول (بشكل مرن)
        # نبحث عن الروابط التي تحتوي على 'read' أو 'chapter' داخل حاوية الفصول
        chapter_elements = soup.select("a[href*='/read/'], .eplister li a, #chapterlist li a")
        seen_urls = set()
        
        for a in chapter_elements:
            link = a["href"]
            name = a.text.strip()
            # تجنب تكرار الفصول وتصفية الروابط غير الضرورية
            if link not in seen_urls and (any(char.isdigit() for char in name) or "فصل" in name):
                result["chapters"].append({
                    "name": name,
                    "url": link
                })
                seen_urls.add(link)

        return result
    except Exception as e:
        print(f"Error in get_manga_details: {e}")
        return {"title": "", "summary": "", "chapters": []}

def get_chapter_images(chapter_url: str) -> List[str]:
    """جلب صور الفصل مع دعم Lazy Loading وفلترة النطاق الموثوق"""
    try:
        # فك تشفير الرابط في حال كان يحتوي على رموز عربية
        decoded_url = urllib.parse.unquote(chapter_url)
        response = scraper.get(decoded_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        images = []
        # تحديد منطقة القارئ بناءً على الصورة التي أرفقتها (reader-mode أو حاوية الصور)
        reader = soup.select_one(".reader-mode, #readerarea, .flex-col.items-center")
        
        if reader:
            img_tags = reader.find_all("img")
            for img in img_tags:
                # التحقق من السمات المختلفة التي قد تخزن الرابط الحقيقي (Lazy Loading)
                img_url = (
                    img.get("data-src") or 
                    img.get("data-lazy-src") or 
                    img.get("src")
                )
                
                if img_url:
                    full_url = clean_url(img_url)
                    # التأكد من أن الصورة تابعة لسيرفر الصور وليس أيقونة أو إعلانات
                    if "appswat" in full_url or "uploads" in full_url:
                        # إزالة أي معايير إضافية مثل ?resize
                        final_url = full_url.split('?')[0]
                        images.append(final_url)
        
        # إزالة التكرار مع الحفاظ على الترتيب
        return list(dict.fromkeys(images))
    except Exception as e:
        print(f"Error in get_chapter_images: {e}")
        return []

# --- مثال على الاستخدام ---
if __name__ == "__main__":
    # تجربة جلب تفاصيل مانجا
    manga_slug = "absolute-regression" # مثال
    details = get_manga_details(manga_slug)
    print(f"Manga Title: {details['title']}")
    
    if details['chapters']:
        first_chapter_url = details['chapters'][0]['url']
        imgs = get_chapter_images(first_chapter_url)
        print(f"Found {len(imgs)} images in the first chapter.")
