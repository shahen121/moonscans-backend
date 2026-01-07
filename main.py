import sys
from scraper import AzoraScraper

def main():
    print(f"🚀 نظام Scraper المتقدم - إصدار بايثون: {sys.version}")
    
    # تشغيل المتصفح (اجعل headless=True للتشغيل الصامت)
    scraper = AzoraScraper(headless=False)
    
    try:
        # 1. جلب القائمة
        list_items = scraper.get_manga_list()
        print(f"✅ تم العثور على {len(list_items)} عمل في القائمة.")
        
        # 2. عرض عينة من النتائج
        for idx, item in enumerate(list_items[:5]):
            print(f"   [{idx+1}] {item.title} - {item.latest_chapter}")
            
        # 3. جلب تفاصيل أول عمل كمثال
        if list_items:
            example_url = list_items[0].url
            details = scraper.get_manga_details(example_url)
            
            print("\n" + "="*40)
            print(f"📖 العنوان: {details.title}")
            print(f"📊 الحالة: {details.status}")
            print(f"🔢 عدد الفصول: {details.total_chapters}")
            print(f"🖼️ رابط الصورة: {details.cover_image}")
            print("="*40)
            
            if details.chapters:
                print(f"🆕 أحدث فصل متاح: {details.chapters[0].number}")
                print(f"📅 تاريخ النشر: {details.chapters[0].date}")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
    finally:
        scraper.close()
        print("👋 تم إغلاق النظام بنجاح.")

if __name__ == "__main__":
    main()
