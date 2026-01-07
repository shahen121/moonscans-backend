from pydantic import BaseModel
from typing import List, Optional

class Chapter(BaseModel):
    chapter_title: str
    chapter_url: str

class MangaData(BaseModel):
    chapters: List[Chapter]
    images: List[str]
