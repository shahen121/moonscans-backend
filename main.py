from fastapi import FastAPI, Query
import urllib.parse
from typing import List
from scraper import (
    get_manga_list,
    get_manga_details,
    get_chapter_images
)

app = FastAPI(
    title="Moonscans API",
    description="Unofficial API for Moonscans (Personal Use)",
    version="1.0.0"
)

# 1. جلب قائمة المانجا
@app.get("/manga")
def manga_list():
    return get_manga_list()

# 2. جلب تفاصيل مانجا معينة (Dynamic Route)
@app.get("/manga/{slug}")
def manga_details(slug: str):
    return get_manga_details(slug)

# 3. جلب صور الفصل (مع فك التشفير للروابط العربية)
@app.get("/chapter/images")
def chapter_images(url: str = Query(..., description="Chapter URL")):
    # فك تشفير الروابط للتعامل مع الحروف العربية والرموز الخاصة
    decoded_url = urllib.parse.unquote(url)
    
    # ملاحظة: يفضل دائماً طباعة الروابط للتأكد أثناء التطوير
    print(f"Requesting URL: {decoded_url}")
    
    return {
        "images": get_chapter_images(decoded_url)
    }
