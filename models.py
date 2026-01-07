from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Chapter(BaseModel):
    """
    تمثيل بيانات الفصل الواحد - Chapter Data Representation
    """
    number: str = Field(..., description="رقم أو اسم الفصل")
    url: str = Field(..., description="رابط الوصول للفصل")
    date: str = Field(..., description="تاريخ نشر الفصل")
    is_read: bool = False  # حالة القراءة: افتراضياً غير مقروء
    last_read_at: Optional[datetime] = None  # توقيت آخر قراءة

class MangaCard(BaseModel):
    """
    تمثيل البطاقة المختصرة في القوائم الرئيسية - Manga Card Representation
    """
    title: str = Field(..., description="عنوان المانجا")
    url: str = Field(..., description="رابط صفحة المانجا")
    cover_image: str = Field(..., description="رابط صورة الغلاف بدقة عالية")
    latest_chapter: str = Field(..., description="رقم أحدث فصل متوفر")

class MangaDetails(BaseModel):
    """
    التفاصيل الكاملة للعمل ومعلومات الفصول - Full Manga Details and Chapters
    """
    title: str
    description: Optional[str] = "لا يوجد وصف متاح"
    cover_image: str
    total_chapters: int
    chapters: List[Chapter]
    status: str  # حالة العمل: مستمر، منتهي، متوقف
    rating: Optional[float] = None  # التقييم إن وجد
