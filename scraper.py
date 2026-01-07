from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

class AzoraScraper:
    def __init__(self):
        self.base_url = "https://azoramoon.com/"

    async def get_page_content(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent="Mozilla/5.0...")
            page = await context.new_page()
            await stealth_async(page)
            
            await page.goto(url, wait_until="networkidle")
            # وقت انتظار إضافي لتجاوز Cloudflare
            await page.wait_for_timeout(5000) 
            
            content = await page.content()
            
            # استخراج الفصول بناءً على الصورة الرابعة التي أرسلتها (li.wp-manga-chapter)
            chapters = await page.eval_on_selector_all(
                "li.wp-manga-chapter > a", 
                "elements => elements.map(e => ({chapter_title: e.innerText, chapter_url: e.href}))"
            )
            
            # استخراج الصور داخل الفصل بناءً على الصورة الثالثة (div.page-break img)
            images = await page.eval_on_selector_all(
                ".page-break img", 
                "imgs => imgs.map(img => img.src)"
            )
            
            await browser.close()
            return {"chapters": chapters, "images": images}
