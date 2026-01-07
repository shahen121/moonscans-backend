from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class MessageResponse(BaseModel):
    """
    نموذج استجابة الرسائل البسيطة (مثل رسالة الترحيب في الـ Root)
    """
    message: str = Field(..., example="Azora Moon API is Running!")

class Chapter(BaseModel):
    """
    تمثيل بيانات الفصل الواحد - Chapter Data Representation
    """
    number: str = Field(..., description="رقم أو اسم الفصل", example="الفصل 150")
    url: HttpUrl = Field(..., description="رابط الوصول للفصل")
    date: str = Field(..., description="تاريخ نشر الفصل", example="منذ يومين")
    is_read: bool = Field(default=False, description="حالة القراءة: افتراضياً غير مقروء")
    last_read_at: Optional[datetime] = Field(None, description="توقيت آخر قراءة")

class MangaCard(BaseModel):
    """
    تمثيل البطاقة المختصرة في القوائم الرئيسية - Manga Card Representation
    """
    title: str = Field(..., description="عنوان المانجا")
    url: HttpUrl = Field(..., description="رابط صفحة المانجا")
    cover_image: HttpUrl = Field(..., description="رابط صورة الغلاف بدقة عالية")
    latest_chapter: str = Field(..., description="رقم أحدث فصل متوفر")

class MangaDetails(BaseModel):
    """
    التفاصيل الكاملة للعمل ومعلومات الفصول - Full Manga Details and Chapters
    """
    title: str = Field(..., example="Solo Leveling")
    description: Optional[str] = Field("لا يوجد وصف متاح", description="نبذة عن قصة العمل")
    cover_image: HttpUrl = Field(..., description="رابط الصورة الأصلية")
    total_chapters: int = Field(..., description="إجمالي عدد الفصول المكتشفة")
    chapters: List[Chapter] = Field(..., description="قائمة الفصول المتاحة")
    status: str = Field(..., description="حالة العمل: مستمر، منتهي، متوقف", example="مستمر")
    rating: Optional[float] = Field(None, description="التقييم الرقمي للعمل", ge=0, le=5)

class APIError(BaseModel):
    """
    نموذج الأخطاء المتوافق مع FastAPI ValidationError
    """
    loc: List[str]
    msg: str
    type: str
