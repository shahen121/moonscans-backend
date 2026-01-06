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


import requests
from bs4 import BeautifulSoup

# الرؤوس الضرورية لتجنب الحظر من الموقع 🛡️
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://moonscans.net/"
}

def get_chapter_images(chapter_url: str):
    try:
        # إرسال طلب للموقع جلب محتوى الصفحة 🌐
        response = requests.get(chapter_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        images = []

        # تحديد منطقة القراءة الرئيسية في الموقع 📖
        # ملاحظة: الموقع غالباً يستخدم id="readerarea" لصور الفصل
        reader_area = soup.select_one("#readerarea")
        
        if reader_area:
            # البحث عن كل وسوم الصور داخل منطقة القراءة
            for img in reader_area.find_all("img"):
                # محاولة جلب الرابط من عدة مصادر لضمان النجاح 🖼️
                url = (
                    img.get("data-src") or 
                    img.get("src") or 
                    img.get("data-lazy-src")
                )

                if url:
                    clean_url = url.strip()
                    # إصلاح الروابط التي تبدأ بـ //
                    if clean_url.startswith("//"):
                        clean_url = "https:" + clean_url
                    
                    # التأكد من إضافة الصور الحقيقية فقط
                    if any(ext in clean_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        images.append(clean_url)

        return images

    except Exception as e:
        print(f"حدث خطأ أثناء جلب الصور: {e}")
        return []

# --- تجربة الكود بالرابط الذي أرسلته ---
test_url = "https://moonscans.net/%d8%a7%d9%84%d9%81%d8%b5%d9%84-%d8%b1%d9%82%d9%85-1-solo-leveling/"
chapter_images = get_chapter_images(test_url)

print(f"تم العثور على {len(chapter_images)} صورة.")
for i, img_url in enumerate(chapter_images[:5]): # عرض أول 5 روابط للتأكد
    print(f"صورة {i+1}: {img_url}")
