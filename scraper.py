import requests
from bs4 import BeautifulSoup

BASE_URL = "https://moonscans.net"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://moonscans.net/"
}

def get_html(url):
    """دالة مساعدة لتقليل تكرار الكود وتوحيد الطلبات"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_manga_list():
    url = BASE_URL + "/manga/"
    html = get_html(url)
    if not html: return []
    
    soup = BeautifulSoup(html, "html.parser")
    mangas = []
    
    # المحدد .bsx شائع في قوالب ووردبريس للمانجا
    for item in soup.select(".bsx"):
        a_tag = item.select_one("a")
        img_tag = item.select_one("img")
        
        if not a_tag or not img_tag: continue
        
        mangas.append({
            "title": img_tag.get("alt", "").strip(),
            "slug": a_tag["href"].rstrip("/").split("/")[-1],
            "cover": img_tag.get("src", ""),
            "url": a_tag["href"]
        })
    return mangas

def get_manga_details(slug: str):
    url = f"{BASE_URL}/manga/{slug}/"
    html = get_html(url)
    if not html: return None # أو يمكنك إرجاع كائن فارغ حسب رغبتك
    
    soup = BeautifulSoup(html, "html.parser")
    
    # استخراج العنوان
    title = soup.select_one("h1").text.strip() if soup.select_one("h1") else "Unknown"
    
    # محاولة استخراج الملخص (قد يختلف المحدد حسب الموقع)
    summary_tag = soup.select_one(".entry-content p") or soup.select_one(".summary .content")
    summary = summary_tag.text.strip() if summary_tag else "No summary available"
    
    # محاولة استخراج الحالة
    status_tag = soup.select_one(".tsinfo .imptdt i") # نمط شائع
    status = status_tag.text.strip() if status_tag else "Unknown"

    # استخراج قائمة الفصول
    chapters = []
    # المحدد #chapterlist ul li a شائع جداً
    for link in soup.select("#chapterlist ul li a"):
        chap_name = link.select_one(".chapternum")
        name = chap_name.text.strip() if chap_name else link.text.strip()
        
        chapters.append({
            "name": name,
            "url": link["href"]
        })

    return {
        "title": title,
        "summary": summary,
        "status": status,
        "chapters": chapters
    }

def get_chapter_images(chapter_url: str):
    # نستخدم الرابط القادم من الدالة مباشرة
    html = get_html(chapter_url)
    if not html: return []
    
    soup = BeautifulSoup(html, "html.parser")
    
    images = []
    # المحدد #readerarea img هو الأشهر لقراءة المانجا
    for img in soup.select("#readerarea img"):
        src = img.get("src")
        if src:
            images.append(src)
            
    return images
