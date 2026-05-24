from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.services.blog import (
    get_post_by_slug,
    list_categories,
    list_posts,
    list_recent_posts,
    list_tags,
)
from app.web.markdown import render_markdown
from app.web.templating import templates

router = APIRouter(prefix="/blog", tags=["blog"])


@router.get("", response_class=HTMLResponse)
async def blog_index(request: Request) -> HTMLResponse:
    posts = list_posts()
    return templates.TemplateResponse(
        request=request,
        name="blog/index.html",
        context={
            "title": "Blog | AI Blog",
            "meta_description": "Developer notes on AI systems, FastAPI, architecture, and product engineering.",
            "posts": posts,
            "recent_posts": list_recent_posts(),
            "categories": list_categories(),
            "tags": list_tags(),
        },
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def blog_detail(request: Request, slug: str) -> HTMLResponse:
    post = get_post_by_slug(slug)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(
        request=request,
        name="blog/detail.html",
        context={
            "title": f"{post.title} | AI Blog",
            "meta_description": post.description,
            "post": post,
            "post_html": render_markdown(post.content_markdown),
            "recent_posts": [recent for recent in list_recent_posts() if recent.slug != post.slug],
            "categories": list_categories(),
            "tags": list_tags(),
        },
    )

