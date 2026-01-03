from fastapi import FastAPI, Query
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


@app.get("/manga")
def manga_list():
    return get_manga_list()


@app.get("/manga/{slug}")
def manga_details(slug: str):
    return get_manga_details(slug)


@app.get("/chapter/images")
def chapter_images(url: str = Query(..., description="Chapter URL")):
    return {
        "images": get_chapter_images(url)
    }
