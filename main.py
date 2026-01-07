from pydantic import BaseModel
from typing import List

class MangaResult(BaseModel):
    title: str
    url: str

class Chapter(BaseModel):
    chapter_title: str
    chapter_url: str

class ChapterContent(BaseModel):
    images: List[str]
