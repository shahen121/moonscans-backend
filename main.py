from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import httpx
from models import MangaInfo, ChapterInfo, ChapterListResponse, ChapterContent
import scraper

app = FastAPI(
    title="Mangawy API",
    description="API للحصول على مانجا من موقع mangawy.app",
    version="1.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mangawy API - اهلاً بك في API مانجاوي", "version": "1.0.0"}

@app.get("/manga/{manga_slug}/chapters", response_model=ChapterListResponse)
async def get_manga_chapters(manga_slug: str):
    """الحصول على قائمة فصول المانجا"""
    try:
        chapters = await scraper.get_chapters_list(manga_slug)
        if not chapters:
            raise HTTPException(status_code=404, detail="المانجا غير موجودة")
        return ChapterListResponse(
            manga_slug=manga_slug,
            chapters=chapters,
            total_chapters=len(chapters)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في جلب الفصول: {str(e)}")

@app.get("/manga/{manga_slug}/info", response_model=MangaInfo)
async def get_manga_info(manga_slug: str):
    """الحصول على معلومات المانجا"""
    try:
        info = await scraper.get_manga_info(manga_slug)
        if not info:
            raise HTTPException(status_code=404, detail="المانجا غير موجودة")
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في جلب المعلومات: {str(e)}")

@app.get("/manga/{manga_slug}/chapters/live")
async def get_manga_chapters_live(manga_slug: str):
    """سحب فصول المانجا مباشرة من mangawy.app"""
    try:
        chapters = await scraper.get_chapters_list(manga_slug)
        if not chapters:
            raise HTTPException(status_code=404, detail="المانجا غير موجودة في mangawy.app")
        return {
            "manga_slug": manga_slug,
            "chapters": chapters,
            "total_chapters": len(chapters),
            "source": "mangawy.app (live)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في جلب الفصول من mangawy.app: {str(e)}")

@app.get("/search")
async def search_manga(q: str = "", limit: int = 10):
    """البحث عن مانجا"""
    try:
        results = await scraper.search_manga(q, limit)
        return {"query": q, "results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في البحث: {str(e)}")

@app.get("/popular")
async def get_popular_manga(limit: int = 10):
    """الحصول على المانجا الشائعة"""
    try:
        manga_list = await scraper.get_popular_manga(limit)
        return {"manga_list": manga_list, "count": len(manga_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في جلب المانجا الشائعة: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
