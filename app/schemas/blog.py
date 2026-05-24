from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class BlogPost(BaseModel):
    slug: str
    title: str
    description: str
    author: str
    category: str
    tags: list[str]
    published_at: date
    reading_time_minutes: int
    content_markdown: str

