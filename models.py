from pydantic import BaseModel
from typing import List


class MangaItem(BaseModel):
    title: str
    slug: str
    cover: str
    url: str


class ChapterItem(BaseModel):
    name: str
    url: str


class MangaDetails(BaseModel):
    title: str
    summary: str
    status: str
    chapters: List[ChapterItem]
