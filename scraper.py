import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth # تم تعديل الاستيراد هنا

class AzoraScraper:
    def __init__(self):
        self.base_url = "https://azoramoon.com/"

    async def get_page_content(self, url):
        async with async_playwright() as p:
            # تشغيل المتصفح بوضع headless=True للعمل على Render
            browser = await p.chromium.launch(headless=True)
            
            # إعداد سياق المتصفح مع User-Agent حقيقي لتبدو كمتصفح بشري
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # تفعيل ميزة التخفي لتجاوز حماية Cloudflare 🤫
            await stealth(page) # تم تعديل الاستدعاء هنا ليناسب النسخة الحديثة
            
            print(f"جاري الانتقال إلى: {url}")
            # ننتظر حتى تهدأ الشبكة لضمان تحميل العناصر
            await page.goto(url, wait_until="networkidle")
            
            # وقت انتظار إضافي (5 ثوانٍ) لضمان انتهاء تحدي Cloudflare
            await page.wait_for_timeout(5000) 
            
            # استخراج الفصول بناءً على الكلاسات التي وجدناها في الصور 📚
            # Selector: li.wp-manga-chapter > a
            chapters = await page.eval_on_selector_all(
                "li.wp-manga-chapter > a", 
                "elements => elements.map(e => ({chapter_title: e.innerText.trim(), chapter_url: e.href}))"
            )
            
            # استخراج روابط الصور داخل الفصل 🖼️
            # Selector: .page-break img
            images = await page.eval_on_selector_all(
                ".page-break img", 
                "imgs => imgs.map(img => img.src)"
            )
            
            await browser.close()
            
            # إعادة البيانات المنظمة
            return {
                "chapters_count": len(chapters),
                "chapters": chapters, 
                "images_count": len(images),
                "images": images
            }

# كود تجريبي للتأكد من العمل (يمكنك حذفه عند ربطه بـ FastAPI)
if __name__ == "__main__":
    scraper = AzoraScraper()
    # جرب وضع رابط مانجا حقيقي هنا للاختبار
    test_url = "https://azoramoon.com/series/omniscient-readers-viewpoint-11/"
    asyncio.run(scraper.get_page_content(test_url))
