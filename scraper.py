import re
from typing import List, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

BASE_URL = "https://mangawy.app"


# ------------------------------
# Data Classes
# ------------------------------
@dataclass
class ChapterPage:
    page_number: int
    image_url: str
    alt_text: str

@dataclass
class ChapterContent:
    manga_slug: str
    manga_title: str
    chapter_number: int
    total_pages: int
    pages: List[ChapterPage]
    prev_chapter: Optional[int]
    next_chapter: Optional[int]

@dataclass
class ChapterInfo:
    number: int
    title: str
    url: str
    is_available: bool

@dataclass
class MangaInfo:
    title: str
    slug: str
    description: Optional[str]
    cover_url: Optional[str]
    total_chapters: int
    source_url: str

@dataclass
class SearchResult:
    title: str
    slug: str

@dataclass
class MangaCard:
    id: int
    title: str
    slug: str
    cover_url: str
    type: str
    status: str
    rating: float
    views: int


# ------------------------------
# Playwright helper
# ------------------------------
async def fetch_page_content(url: str, wait: int = 3000) -> Optional[str]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(wait)
            html = await page.content()
        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            html = None
        await browser.close()
        return html


# ------------------------------
# Chapters List
# ------------------------------
async def get_chapters_list(manga_slug: str) -> List[ChapterInfo]:
    url = f"{BASE_URL}/manga/{manga_slug}"
    html = await fetch_page_content(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    chapters: List[ChapterInfo] = []

    links = soup.select(f'a[href^="/read/{manga_slug}/"]')
    for link in links:
        href = link.get("href", "")
        match = re.search(r"/read/.+?/(\d+)(?:/|$)", href)
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


# ------------------------------
# Manga Info
# ------------------------------
async def get_manga_info(manga_slug: str) -> Optional[MangaInfo]:
    url = f"{BASE_URL}/manga/{manga_slug}"
    html = await fetch_page_content(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1")
    title_text = title_tag.get_text(strip=True) if title_tag else manga_slug.replace("-", " ")

    description_tag = soup.select_one("p.text-zinc-500")
    description_text = description_tag.get_text(strip=True) if description_tag else None

    cover_tag = soup.find("img")
    cover_url = cover_tag.get("src") if cover_tag else None

    chapters = await get_chapters_list(manga_slug)

    return MangaInfo(
        title=title_text,
        slug=manga_slug,
        description=description_text,
        cover_url=cover_url,
        total_chapters=len(chapters),
        source_url=url
    )


# ------------------------------
# Chapter Content
# ------------------------------
async def get_chapter_content(manga_slug: str, chapter_number: int) -> Optional[ChapterContent]:
    url = f"{BASE_URL}/read/{manga_slug}/{chapter_number}"
    html = await fetch_page_content(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Manga title
    manga_title_tag = soup.find("h1") or soup.find("h2")
    manga_title = manga_title_tag.get_text(strip=True) if manga_title_tag else manga_slug.replace("-", " ")

    # Pages
    pages: List[ChapterPage] = []
    image_nodes = soup.select("div[data-page] img")
    for idx, img in enumerate(image_nodes, start=1):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy")
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
        print(f"[WARNING] No pages found for {manga_slug} Chapter {chapter_number}")

    return ChapterContent(
        manga_slug=manga_slug,
        manga_title=manga_title,
        chapter_number=chapter_number,
        total_pages=len(pages),
        pages=pages,
        prev_chapter=chapter_number - 1 if chapter_number > 1 else None,
        next_chapter=chapter_number + 1 if pages else None
    )


# ------------------------------
# Search
# ------------------------------
async def search_manga(query: str, limit: int = 10) -> List[SearchResult]:
    url = f"{BASE_URL}/manga?search={query}"
    html = await fetch_page_content(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    results: List[SearchResult] = []

    cards = soup.select("a[href^='/manga/']")[:limit]
    for card in cards:
        title = card.get_text(strip=True)
        href = card.get("href", "")
        slug = href.split("/")[-1]
        results.append(SearchResult(title=title, slug=slug))

    return results


# ------------------------------
# Popular Manga
# ------------------------------
async def get_popular_manga(limit: int = 10) -> List[MangaCard]:
    url = f"{BASE_URL}/rankings"
    html = await fetch_page_content(url)
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
