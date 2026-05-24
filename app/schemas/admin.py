from __future__ import annotations

from pydantic import BaseModel


class AdminDashboardStat(BaseModel):
    label: str
    value: int
    description: str


class AdminPost(BaseModel):
    title: str
    slug: str
    summary: str
    markdown_content: str
    cover_image: str
    is_published: bool
    seo_title: str
    seo_description: str


class AdminProject(BaseModel):
    title: str
    slug: str
    description: str
    tech_stack: str
    github_url: str
    demo_url: str
    cover_image: str
    featured: bool
