import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from models import MangaCard, MangaDetails, Chapter

class AzoraScraper:
    def __init__(self, headless=False):
        """إعداد المتصفح المتخفي بأعلى دقة محاكاة"""
        options = uc.ChromeOptions()
        # محاكاة مستخدم حقيقي
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        
        # تشغيل المتصفح (يستخدم المحرك التلقائي لإصدار 3.14)
        self.driver = uc.Chrome(options=options, headless=headless)
        self.wait = WebDriverWait(self.driver, 20)
        print("✅ تم تشغيل محرك الاستخراج المتخفي.")

    def _smart_scroll(self):
        """تمرير ذكي لضمان تحميل جميع الصور بدقة عالية (Lazy Load)"""
        height = self.driver.execute_script("return document.body.scrollHeight")
        for i in range(0, height, 800):
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(0.2)
        self.driver.execute_script("window.scrollTo(0, 0);")

    def get_manga_list(self, url="https://azoramoon.com/") -> List[MangaCard]:
        """سحب قائمة المانجا/المانهوا من الصفحة الرئيسية"""
        print(f"🔄 جاري سحب البيانات من القائمة الرئيسية...")
        self.driver.get(url)
        time.sleep(3)
        self._smart_scroll()
        
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        results = []
        
        # استهداف العناصر بناءً على هيكلية الموقع
        items = soup.select('.bsx')
        for item in items:
            try:
                title_tag = item.select_one('a')
                title = title_tag.get('title')
                link = title_tag.get('href')
                
                # جلب الصورة الأصلية بدقة عالية
                img_tag = item.select_one('img')
                img_url = img_tag.get('data-src') or img_tag.get('src')
                
                # آخر فصل
                latest_chap = item.select_one('.epxs').text.strip() if item.select_one('.epxs') else "N/A"
                
                results.append(MangaCard(
                    title=title,
                    url=link,
                    cover_image=img_url,
                    latest_chapter=latest_chap
                ))
            except Exception:
                continue
        return results

    def get_manga_details(self, url: str) -> MangaDetails:
        """جلب تفاصيل المانجا، الفصول، وحالة القراءة"""
        print(f"🔍 جاري فحص التفاصيل في: {url}")
        self.driver.get(url)
        time.sleep(2)
        
        # محاولة فتح قائمة الفصول كاملة إذا كانت مخفية
        try:
            expand_btn = self.driver.find_element(By.CSS_SELECTOR, ".click-to-load")
            self.driver.execute_script("arguments[0].click();", expand_btn)
            time.sleep(1)
        except:
            pass

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        
        title = soup.select_one('.entry-title').text.strip()
        cover = soup.select_one('.thumb img').get('src')
        
        # استخراج الحالة
        status = "غير معروف"
        info_elements = soup.select('.imptdt')
        for info in info_elements:
            if "الحالة" in info.text or "Status" in info.text:
                status = info.select_one('i').next_sibling.strip()

        # استخراج الفصول
        chapters = []
        chapter_items = soup.select('#chapterlist li')
        for li in chapter_items:
            try:
                num = li.select_one('.chapternum').text.strip()
                date = li.select_one('.chapterdate').text.strip()
                link = li.select_one('a').get('href')
                
                chapters.append(Chapter(
                    number=num,
                    url=link,
                    date=date
                ))
            except:
                continue

        return MangaDetails(
            title=title,
            cover_image=cover,
            total_chapters=len(chapters),
            chapters=chapters,
            status=status
        )

    def close(self):
        self.driver.quit()
