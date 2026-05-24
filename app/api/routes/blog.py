from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.dependencies import SessionDependency
from app.services.blog import (
    get_public_post_by_slug,
    list_categories,
    list_public_posts,
    list_recent_posts,
    list_tags,
)
from app.services.seo import build_page_seo
from app.web.markdown import render_markdown
from app.web.templating import templates

router = APIRouter(prefix="/blog", tags=["blog"])


@router.get("", response_class=HTMLResponse)
async def blog_index(request: Request, session: SessionDependency) -> HTMLResponse:
    posts = await list_public_posts(session)
    return templates.TemplateResponse(
        request=request,
        name="blog/index.html",
        context={
            **build_page_seo(
                request,
                title="Blog | AI Blog",
                description="Developer notes on AI systems, FastAPI, architecture, and product engineering.",
                path="/blog",
            ),
            "posts": posts,
            "recent_posts": list_recent_posts(),
            "categories": list_categories(),
            "tags": list_tags(),
        },
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def blog_detail(request: Request, slug: str, session: SessionDependency) -> HTMLResponse:
    post = await get_public_post_by_slug(session, slug)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(
        request=request,
        name="blog/detail.html",
        context={
            **build_page_seo(
                request,
                title=f"{post.title} | AI Blog",
                description=post.description,
                path=f"/blog/{post.slug}",
                og_type="article",
            ),
            "post": post,
            "post_html": render_markdown(post.content_markdown),
            "recent_posts": [recent for recent in list_recent_posts() if recent.slug != post.slug],
            "categories": list_categories(),
            "tags": list_tags(),
        },
    )
