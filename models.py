from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ChapterInfo(BaseModel):
    """معلومات الفصل"""
    number: int
    title: Optional[str] = None
    url: Optional[str] = None
    publish_date: Optional[str] = None
    is_available: bool = True

class MangaInfo(BaseModel):
    """معلومات المانجا"""
    title: str
    slug: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    author: Optional[str] = None
    artist: Optional[str] = None
    status: Optional[str] = None  # ongoing, completed, etc.
    type: Optional[str] = None  # manga, manhwa, manhua
    rating: Optional[float] = None
    views: Optional[int] = None
    genres: List[str] = []
    total_chapters: Optional[int] = None
    alternative_titles: List[str] = []
    source_url: Optional[str] = None

class ChapterListResponse(BaseModel):
    """استجابة قائمة الفصول"""
    manga_slug: str
    chapters: List[ChapterInfo]
    total_chapters: int

class ChapterPage(BaseModel):
    """صفحة الفصل"""
    page_number: int
    image_url: str
    alt_text: Optional[str] = None

class ChapterContent(BaseModel):
    """محتوى الفصل الكامل"""
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

class SearchResult(BaseModel):
    """نتيجة البحث"""
    title: str
    slug: str
    cover_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    latest_chapter: Optional[str] = None

class MangaCard(BaseModel):
    """بطاقة مانجا للقوائم"""
    id: int
    title: str
    slug: str
    cover_url: str
    type: str
    status: str
    rating: float
    views: int
    chapter_count: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    author: Optional[str] = None
    artist: Optional[str] = None
