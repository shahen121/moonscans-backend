async def get_popular_manga(limit: int = 10) -> List[MangaCard]:
    """الحصول على المانجا الشائعة"""
    url = f"{BASE_URL}/rankings"
    html = await fetch_page(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    manga_list: List[MangaCard] = []
    
    # افتراض: عناصر القائمة تحتوي كل واحدة على بطاقة مع عناصر مثل:
    # - عنوان وربط: <a class="title" href="/manga/slug">عنوان</a>
    # - صورة الغلاف: <img src="..." />
    # - وصف/الوضع/النوع غالباً ضمن نفس البطاقة
    ranking_items = soup.find_all('div', class_='ranking-item')
    
    for item in ranking_items[:limit]:
        # العنوان والرابط
        title_tag = item.find(['a', 'h3'], class_='title')
        title = None
        slug = None
        cover_url = None
        description = None
        status_text = None
        type_text = None

        if title_tag:
            title = title_tag.get_text(strip=True)
            href = title_tag.get('href', '')
            slug = href.split('/')[-1] if href else None
        else:
            # محاولة احتياطية من بنية أخرى
            h3 = item.find('h3')
            if h3:
                a = h3.find('a')
                if a:
                    title = a.get_text(strip=True)
                    href = a.get('href', '')
                    slug = href.split('/')[-1] if href else None

        # الغلاف
        cover_img = item.find('img')
        if cover_img:
            cover_url = cover_img.get('src') or cover_img.get('data-src')

        # الوصف/الحالة/النوع (إن وجدت)
        desc_tag = item.find('p', class_='description') or item.find('div', class_='description')
        if desc_tag:
            description = desc_tag.get_text(strip=True)

        status_tag = item.find('span', class_='status') or item.find('div', class_='status')
        if status_tag:
            status_text = status_tag.get_text(strip=True)

        type_tag = item.find('span', class_='type') or item.find('div', class_='type')
        if type_tag:
            type_text = type_tag.get_text(strip=True)

        if title and slug:
            manga_list.append(MangaCard(
                title=title,
                slug=slug,
                cover_url=cover_url,
                description=description,
                status=status_text,
                type=type_text
            ))
        else:
            # تخطى البطاقة إذا لم نستطع استخراج العنوان/الـ slug
            continue
    
    return manga_list
