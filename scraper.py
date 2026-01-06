import httpx
from bs4 import BeautifulSoup
import json
import re
from typing import List, Optional, Dict, Any
from models import ChapterInfo, MangaInfo, ChapterContent, ChapterPage, SearchResult, MangaCard
import asyncio

BASE_URL = "https://mangawy.app"

async def fetch_page(url: str) -> Optional[str]:
    """جلب صفحة HTML"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"خطأ في جلب الصفحة {url}: {str(e)}")
            return None

async def get_chapters_list(manga_slug: str) -> List[ChapterInfo]:
    """الحصول على قائمة الفصول"""
    url = f"{BASE_URL}/manga/{manga_slug}"
    html = await fetch_page(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    chapters = []
    
    # البحث عن روابط الفصول
    chapter_links = soup.find_all('a', href=lambda x: x and f'/read/{manga_slug}/' in x)
    
    for link in chapter_links:
        href = link.get('href', '')
        # استخراج رقم الفصل من الرابط
        match = re.search(rf'/read/{manga_slug}/(\d+)', href)
        if match:
            chapter_number = int(match.group(1))
            
            # الحصول على عنوان الفصل
            title_elem = link.find('span', class_='chapter-title') or link.find('span') or link
            title = title_elem.get_text(strip=True) if title_elem else f"الفصل {chapter_number}"
            
            chapters.append(ChapterInfo(
                number=chapter_number,
                title=title,
                url=f"{BASE_URL}{href}" if href.startswith('/') else href,
                is_available=True
            ))
    
    # ترتيب الفصول تنازلياً (الأحدث أولاً)
    chapters.sort(key=lambda x: x.number, reverse=True)
    return chapters

async def get_manga_info(manga_slug: str) -> Optional[MangaInfo]:
    """الحصول على معلومات المانجا"""
    url = f"{BASE_URL}/manga/{manga_slug}"
    html = await fetch_page(url)
    
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # العنوان
    title = soup.find('h1', class_='manga-title') or soup.find('h1')
    title_text = title.get_text(strip=True) if title else manga_slug.replace('-', ' ').title()
    
    # الوصف
    description = soup.find('div', class_='description') or soup.find('p', class_='description')
    description_text = description.get_text(strip=True) if description else None
    
    # صورة الغلاف
    cover_img = soup.find('img', class_='cover-image') or soup.find('img', alt=title_text)
    cover_url = cover_img.get('src') if cover_img else None
    
    # المؤلف والفنان
    author = None
    artist = None
    info_table = soup.find('div', class_='manga-info') or soup.find('table', class_='info')
    if info_table:
        for row in info_table.find_all(['tr', 'div']):
            text = row.get_text()
            if 'المؤلف' in text or 'author' in text.lower():
                author = text.split(':')[-1].strip()
            if 'الفنان' in text or 'artist' in text.lower():
                artist = text.split(':')[-1].strip()
    
    # الحالة
    status = soup.find('span', class_='status') or soup.find('span', class_='manga-status')
    status_text = status.get_text(strip=True) if status else None
    
    # النوع
    type_elem = soup.find('span', class_='type') or soup.find('a', class_='type')
    type_text = type_elem.get_text(strip=True) if type_elem else None
    
    # التقييم
    rating = soup.find('span', class_='rating') or soup.find('div', class_='rating')
    if rating:
        rating_match = re.search(r'[\d.]+', rating.get_text())
        rating_value = float(rating_match.group()) if rating_match else None
    else:
        rating_value = None
    
    # عدد المشاهدات
    views = soup.find('span', class_='views') or soup.find('div', class_='views')
    if views:
        views_text = views.get_text()
        views_match = re.search(r'[\d,]+', views_text)
        views_value = int(views_match.group().replace(',', '')) if views_match else None
    else:
        views_value = None
    
    # الأنواع
    genres = []
    genre_links = soup.find_all('a', class_='genre') or soup.find_all('a', href=lambda x: x and '/genre/' in x)
    for genre in genre_links:
        genres.append(genre.get_text(strip=True))
    
    # عدد الفصول
    chapters = await get_chapters_list(manga_slug)
    total_chapters = len(chapters)
    
    return MangaInfo(
        title=title_text,
        slug=manga_slug,
        description=description_text,
        cover_url=cover_url,
        author=author,
        artist=artist,
        status=status_text,
        type=type_text,
        rating=rating_value,
        views=views_value,
        genres=genres,
        total_chapters=total_chapters,
        source_url=url
    )

async def get_chapter_content(manga_slug: str, chapter_number: int) -> Optional[ChapterContent]:
    """الحصول على محتوى الفصل (الصفحات)"""
    url = f"{BASE_URL}/read/{manga_slug}/{chapter_number}"
    html = await fetch_page(url)
    
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # العنوان
    manga_title = soup.find('h1', class_='manga-title') or soup.find('h2', class_='manga-title')
    manga_title_text = manga_title.get_text(strip=True) if manga_title else manga_slug.replace('-', ' ').title()
    
    # عنوان الفصل
    chapter_title_elem = soup.find('h2', class_='chapter-title') or soup.find('span', class_='chapter-title')
    chapter_title = chapter_title_elem.get_text(strip=True) if chapter_title_elem else None
    
    # صفحات الفصل
    pages = []
    page_images = soup.find_all('img', class_='page-image') or soup.find_all('img', {'data-page': True})
    
    if not page_images:
        # محاولة العثور على الصور بطريقة أخرى
        page_images = soup.find_all('img', src=lambda x: x and '.jpg' in x.lower() or '.png' in x.lower())
    
    for idx, img in enumerate(page_images):
        img_url = img.get('src') or img.get('data-src')
        if img_url:
            pages.append(ChapterPage(
                page_number=idx + 1,
                image_url=img_url,
                alt_text=img.get('alt', f"صفحة {idx + 1}")
            ))
    
    # الفصل السابق والتالي
    prev_chapter = chapter_number - 1 if chapter_number > 1 else None
    next_chapter = chapter_number + 1 if len(pages) > 0 else None
    
    # المترجمون
    translators = []
    translator_elems = soup.find_all('span', class_='translator') or soup.find_all('div', class_='translator')
    for elem in translator_elems:
        translators.append(elem.get_text(strip=True))
    
    return ChapterContent(
        manga_slug=manga_slug,
        manga_title=manga_title_text,
        chapter_number=chapter_number,
        chapter_title=chapter_title,
        total_pages=len(pages),
        pages=pages,
        prev_chapter=prev_chapter,
        next_chapter=next_chapter,
        translators=translators
    )

async def search_manga(query: str, limit: int = 10) -> List[SearchResult]:
    """البحث عن مانجا"""
    search_url = f"{BASE_URL}/manga?search={query}"
    html = await fetch_page(search_url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # البحث عن بطاقات المانجا
    manga_cards = soup.find_all('div', class_='manga-card')[:limit]
    
    for card in manga_cards:
        # العنوان والرابط
        title_link = card.find('a', class_='manga-title') or card.find('h3').find('a') if card.find('h3') else None
        if title_link:
            title = title_link.get_text(strip=True)
            href = title_link.get('href', '')
            slug = href.split('/')[-1] if '/' in href else href
        else:
            continue
        
        # صورة الغلاف
        cover_img = card.find('img')
        cover_url = cover_img.get('src') if cover_img else None
        
        # الوصف
        desc = card.find('p', class_='description') or card.find('div', class_='description')
        description = desc.get_text(strip=True)[:200] if desc else None
        
        # الحالة
        status = card.find('span', class_='status') or card.find('div', class_='status')
        status_text = status.get_text(strip=True) if status else None
        
        # النوع
        type_elem = card.find('span', class_='type') or card.find('div', class_='type')
        type_text = type_elem.get_text(strip=True) if type_elem else None
        
        results.append(SearchResult(
            title=title,
            slug=slug,
            cover_url=cover_url,
            description=description,
            status=status_text,
            type=type_text
        ))
    
    return results

async def get_popular_manga(limit: int = 10) -> List[MangaCard]:
    """الحصول على المانجا الشائعة"""
    url = f"{BASE_URL}/rankings"
    html = await fetch_page(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    manga_list = []
    
    # البحث عن المانجا الشائعة
    popular_items = soup.find_all('div', class_='ranking-item')[:limit]
    
    for idx, item in enumerate(popular_items):
        # العنوان والرابط
        title_elem = item.find('h3') or item.find('a', class_='title')
        if title_elem and title_elem.find('a'):
            title = title_elem.find('a').get_text(strip=True)
            href = title_elem.find('a').get('href', '')
            slug = href.split('/')[-1] if '/' in href else str(idx)
        else:
            continue
        
        # صورة الغلاف
        cover_img = item.find('img')
        cover_url = cover_img.get('src') if cover_img else None
        
        # المشاهدات
        views_elem = item.find('span', class_='views') or item.find('div', class_='views')
        views = 0
        if views_elem:
            views_text = views_elem.get_text()
            views_match = re.search(r'[\d,]+', views_text)
            if views_match:
                views = int(views_match.group().replace(',', ''))
        
        # التقييم
        rating_elem = item.find('span', class_='rating') or item.find('div', class_='rating')
        rating = 0.0
        if rating_elem:
            rating_text = rating_elem.get_text()
            rating_match = re.search(r'[\d.]+', rating_text)
            if rating_match:
                rating = float(rating_match.group())
        
        manga_list.append(MangaCard(
            id=idx,
            title=title,
            slug=slug,
            cover_url=cover_url,
            type="manhwa",  # افتراضي
            status="ongoing",  # افتراضي
            rating=rating,
            views=views
        ))
    
    return manga_list
