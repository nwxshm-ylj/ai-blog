from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, HttpUrl


class Project(BaseModel):
    slug: str
    title: str
    description: str
    summary: str
    category: str
    tech_stack: list[str]
    github_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    featured: bool = False
    status: str
    impact: str
    highlights: list[str]
