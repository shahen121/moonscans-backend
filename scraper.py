import httpx
from bs4 import BeautifulSoup
import re
from typing import List, Optional
from models import (
    ChapterInfo,
    MangaInfo,
    ChapterContent,
    ChapterPage,
    SearchResult,
    MangaCard
)

BASE_URL = "https://mangawy.app"


# --------------------------------------------------
# Fetch HTML
# --------------------------------------------------
async def fetch_page(url: str) -> Optional[str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"[FETCH ERROR] {url} -> {e}")
            return None


# --------------------------------------------------
# Chapters List
# --------------------------------------------------
async def get_chapters_list(manga_slug: str) -> List[ChapterInfo]:
    url = f"{BASE_URL}/manga/{manga_slug}"
    html = await fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    chapters: List[ChapterInfo] = []

    links = soup.select(f'a[href^="/read/{manga_slug}/"]')

    for link in links:
        href = link.get("href", "")
        match = re.search(r"/read/.+?/(\d+)", href)
        if not match:
            continue

        number = int(match.group(1))
        title = link.get_text(strip=True) or f"الفصل {number}"

        chapters.append(
            ChapterInfo(
                number=number,
                title=title,
                url=BASE_URL + href,
                is_available=True
            )
        )

    chapters.sort(key=lambda x: x.number, reverse=True)
    return chapters


# --------------------------------------------------
# Manga Info
# --------------------------------------------------
async def get_manga_info(manga_slug: str) -> Optional[MangaInfo]:
    url = f"{BASE_URL}/manga/{manga_slug}"
    html = await fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1")
    title_text = title.get_text(strip=True) if title else manga_slug.replace("-", " ")

    description = soup.select_one("p.text-zinc-500")
    desc_text = description.get_text(strip=True) if description else None

    cover = soup.find("img")
    cover_url = cover.get("src") if cover else None

    chapters = await get_chapters_list(manga_slug)

    return MangaInfo(
        title=title_text,
        slug=manga_slug,
        description=desc_text,
        cover_url=cover_url,
        total_chapters=len(chapters),
        source_url=url
    )


# --------------------------------------------------
# Chapter Content (FIXED)
# --------------------------------------------------
async def get_chapter_content(
    manga_slug: str,
    chapter_number: int
) -> Optional[ChapterContent]:

    url = f"{BASE_URL}/read/{manga_slug}/{chapter_number}"
    html = await fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Manga title
    manga_title = soup.find("h1") or soup.find("h2")
    manga_title_text = (
        manga_title.get_text(strip=True)
        if manga_title else manga_slug.replace("-", " ")
    )

    # Pages (THE IMPORTANT PART)
    pages: List[ChapterPage] = []

    image_nodes = soup.select("div[data-page] img")

    for idx, img in enumerate(image_nodes, start=1):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue

        pages.append(
            ChapterPage(
                page_number=idx,
                image_url=src,
                alt_text=img.get("alt", f"صفحة {idx}")
            )
        )

    if not pages:
        print("[WARNING] No pages found")

    return ChapterContent(
        manga_slug=manga_slug,
        manga_title=manga_title_text,
        chapter_number=chapter_number,
        total_pages=len(pages),
        pages=pages,
        prev_chapter=chapter_number - 1 if chapter_number > 1 else None,
        next_chapter=chapter_number + 1 if pages else None
    )


# --------------------------------------------------
# Search
# --------------------------------------------------
async def search_manga(query: str, limit: int = 10) -> List[SearchResult]:
    url = f"{BASE_URL}/manga?search={query}"
    html = await fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    results: List[SearchResult] = []

    cards = soup.select("a[href^='/manga/']")[:limit]

    for card in cards:
        title = card.get_text(strip=True)
        href = card.get("href", "")
        slug = href.split("/")[-1]

        results.append(
            SearchResult(
                title=title,
                slug=slug
            )
        )

    return results


# --------------------------------------------------
# Popular Manga
# --------------------------------------------------
async def get_popular_manga(limit: int = 10) -> List[MangaCard]:
    url = f"{BASE_URL}/rankings"
    html = await fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    manga_list: List[MangaCard] = []

    items = soup.select("a[href^='/manga/']")[:limit]

    for idx, item in enumerate(items):
        title = item.get_text(strip=True)
        slug = item.get("href", "").split("/")[-1]

        manga_list.append(
            MangaCard(
                id=idx,
                title=title,
                slug=slug,
                cover_url="",
                type="manhwa",
                status="ongoing",
                rating=0.0,
                views=0
            )
        )

    return manga_list
