import json
import urllib.parse
from bs4 import BeautifulSoup
from curl_cffi import requests  # المكتبة الأقوى لتخطي Cloudflare

# --- الإعدادات ---
# ملاحظة: تأكد من تثبيت المكتبة عبر: pip install curl_cffi
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
}

def safe_get(url):
    """محاكاة متصفح حقيقي لتجنب الحجب [cloudflare]"""
    try:
        # محاكاة بصمة متصفح Chrome 120 بالكامل
        response = requests.get(url, impersonate="chrome120", headers=HEADERS, timeout=30)
        return response
    except Exception as e:
        print(f"Request Error: {e}")
        return None

def get_manga_list(base_url):
    """جلب قائمة المانجا - متوافق مع بنية الصور المرفقة"""
    response = safe_get(f"{base_url}/manga/")
    if not response or response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    mangas = []
    
    # البحث عن المانجا في كلا القالبين (Madara و Custom)
    items = soup.select(".bsx, .page-item-detail, .manga-item")
    
    for item in items:
        a_tag = item.select_one("a")
        img_tag = item.select_one("img")
        if a_tag and img_tag:
            cover = img_tag.get("data-src") or img_tag.get("src") or ""
            mangas.append({
                "title": img_tag.get("alt", "").strip(),
                "slug": a_tag["href"].rstrip("/").split("/")[-1],
                "cover": cover.split('?')[0], # تنظيف رابط الصورة
                "url": a_tag["href"]
            })
    return mangas

def get_manga_details(url):
    """استخراج التفاصيل والفصول باستخدام JSON-LD والـ HTML"""
    response = safe_get(url)
    if not response: return {}

    soup = BeautifulSoup(response.text, "html.parser")
    
    # محاولة جلب البيانات من JSON-LD لضمان الاستقرار
    title, summary = "", ""
    json_script = soup.find("script", type="application/ld+json")
    if json_script:
        try:
            data = json.loads(json_script.string)
            graph = data.get("@graph", [data])
            for item in graph:
                if item.get("@type") in ["Manga", "Article", "Product"]:
                    title = item.get("name") or item.get("headline")
                    summary = item.get("description")
                    break
        except: pass

    # إذا لم نجد JSON، نستخدم الـ Selectors التقليدية
    if not title:
        title_tag = soup.select_one("h1.entry-title, .post-title h1")
        title = title_tag.text.strip() if title_tag else ""
    
    # استخراج الفصول - متوافق مع قالب Madara
    chapters = []
    chapter_links = soup.select(".wp-manga-chapter a, #chapterlist a, a[href*='/read/']")
    for a in chapter_links:
        name = a.text.strip()
        if name and (any(c.isdigit() for c in name) or "فصل" in name):
            chapters.append({
                "name": name,
                "url": a["href"]
            })
    
    return {"title": title, "summary": summary, "chapters": chapters}

def get_chapter_images(chapter_url):
    """جلب الصور بناءً على بنية DOM في الصورة"""
    decoded_url = urllib.parse.unquote(chapter_url)
    response = safe_get(decoded_url)
    if not response: return []

    soup = BeautifulSoup(response.text, "html.parser")
    images = []

    # استهداف حاويات data-page كما يظهر في Inspect Element
    reader_area = soup.select_one(".reader-mode, .reading-content, #readerarea")
    if reader_area:
        img_tags = reader_area.find_all("img")
        for img in img_tags:
            # ترتيب جلب الرابط لضمان تخطي Lazy Load
            url = img.get("data-src") or img.get("src") or img.get("data-lazy-src")
            if url and ("appswat" in url or "uploads" in url or "azoramoon" in url):
                # تنظيف الرابط من التشفير أو التلاعب بالمقاسات
                clean_url = url.split('?')[0].strip()
                if clean_url.startswith("//"): clean_url = "https:" + clean_url
                images.append(clean_url)

    return list(dict.fromkeys(images)) # حذف التكرار مع الحفاظ على الترتيب
