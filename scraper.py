from playwright.async_api import async_playwright
from playwright_stealth import stealth # الاستيراد الصحيح
import asyncio

class AzoraScraper:
    async def get_page_content(self, url: str):
        async with async_playwright() as p:
            # تشغيل المتصفح (headless=True للعمل على السيرفر)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # تفعيل التخفي لتجاوز Cloudflare 🤫
            await stealth(page)
            
            await page.goto(url, wait_until="networkidle")
            # وقت إضافي لضمان تحميل الصور وتجاوز الحماية
            await page.wait_for_timeout(7000) 
            
            # استخراج الفصول (بناءً على صورتك: li.wp-manga-chapter > a)
            chapters = await page.eval_on_selector_all(
                "li.wp-manga-chapter > a", 
                "elements => elements.map(e => ({chapter_title: e.innerText.trim(), chapter_url: e.href}))"
            )
            
            # استخراج الصور (بناءً على صورتك: .page-break img)
            images = await page.eval_on_selector_all(
                ".page-break img", 
                "imgs => imgs.map(img => img.src)"
            )
            
            await browser.close()
            return {"chapters": chapters, "images": images}
