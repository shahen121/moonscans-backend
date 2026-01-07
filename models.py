from pydantic import BaseModel
from typing import List, Optional

class Chapter(BaseModel):
    """تمثيل بيانات الفصل الواحد"""
    number: str
    url: str
    date: str
    is_read: bool = False

class MangaCard(BaseModel):
    """تمثيل البطاقة المختصرة في القوائم"""
    title: str
    url: str
    cover_image: str
    latest_chapter: str

class MangaDetails(BaseModel):
    """التفاصيل الكاملة للعمل"""
    title: str
    description: Optional[str] = ""
    cover_image: str
    total_chapters: int
    chapters: List[Chapter]
    status: str
