from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ==================================================
# Chapter Info
# ==================================================
class ChapterInfo(BaseModel):
    number: int
    title: Optional[str] = None
    url: Optional[str] = None
    is_available: bool = True


# ==================================================
# Manga Info
# ==================================================
class MangaInfo(BaseModel):
    title: str
    slug: str

    description: Optional[str] = None
    cover_url: Optional[str] = None

    author: Optional[str] = None
    artist: Optional[str] = None

    status: Optional[str] = None        # ongoing / completed
    type: Optional[str] = None          # manga / manhwa / manhua

    rating: Optional[float] = None
    views: Optional[int] = None

    genres: List[str] = []
    alternative_titles: List[str] = []

    source_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==================================================
# Chapter Page
# ==================================================
class ChapterPage(BaseModel):
    page_number: int
    image_url: str
    alt_text: Optional[str] = None


# ==================================================
# Chapter Content
# ==================================================
class ChapterContent(BaseModel):
    manga_slug: str
    manga_title: str

    chapter_number: int
    chapter_title: Optional[str] = None

    total_pages: int
    pages: List[ChapterPage]

    prev_chapter: Optional[int] = None
    next_chapter: Optional[int] = None

    publish_date: Optional[str] = None
    translators: List[str] = []


# ==================================================
# Search Result
# ==================================================
class SearchResult(BaseModel):
    title: str
    slug: str

    cover_url: Optional[str] = None
    description: Optional[str] = None

    status: Optional[str] = None
    type: Optional[str] = None

    latest_chapter: Optional[str] = None


# ==================================================
# Manga Card (for lists)
# ==================================================
class MangaCard(BaseModel):
    id: int
    title: str
    slug: str

    cover_url: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None

    rating: Optional[float] = None
    views: Optional[int] = None
    chapter_count: Optional[str] = None

    description: Optional[str] = None
    source_url: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    author: Optional[str] = None
    artist: Optional[str] = None
