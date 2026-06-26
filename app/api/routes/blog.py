from __future__ import annotations

import uuid
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.dependencies import SessionDependency
from app.schemas.blog import BlogPost
from app.services.auth import SESSION_USER_ID_KEY
from app.services.blog import (
    get_public_post_by_slug,
    list_categories,
    list_public_posts,
    list_recent_posts,
    list_tags,
)
from app.services.comments import list_approved_comments_for_post, submit_blog_comment
from app.services.seo import build_page_seo
from app.web.flash import flash
from app.web.i18n import translate as t
from app.web.markdown import render_markdown
from app.web.security import verify_csrf_token
from app.web.templating import templates

router = APIRouter(prefix="/blog", tags=["blog"])
BLOG_PAGE_SIZE = 6


@router.get("", response_class=HTMLResponse)
async def blog_index(request: Request, session: SessionDependency) -> HTMLResponse:
    all_posts = await list_public_posts(session, limit=500)
    search_query = request.query_params.get("q", "").strip()
    selected_category = request.query_params.get("category", "").strip()

    filtered_posts = all_posts
    if selected_category:
        filtered_posts = [post for post in filtered_posts if post.category == selected_category]
    if search_query:
        needle = search_query.casefold()
        filtered_posts = [
            post
            for post in filtered_posts
            if needle
            in " ".join(
                [post.title, post.description, post.category, *post.tags]
            ).casefold()
        ]

    page = _positive_int(request.query_params.get("page"), default=1)
    total_pages = max(1, (len(filtered_posts) + BLOG_PAGE_SIZE - 1) // BLOG_PAGE_SIZE)
    page = min(page, total_pages)
    offset = (page - 1) * BLOG_PAGE_SIZE
    posts = filtered_posts[offset : offset + BLOG_PAGE_SIZE]

    return templates.TemplateResponse(
        request=request,
        name="blog/index.html",
        context={
            **build_page_seo(
                request,
                title=t(request, "seo.blog.title"),
                description=t(request, "seo.blog.description"),
                path="/blog",
            ),
            "posts": posts,
            "recent_posts": all_posts[:4],
            "categories": await list_categories(session),
            "tags": await list_tags(session),
            "search_query": search_query,
            "selected_category": selected_category,
            "page": page,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages,
        },
    )


def _positive_int(raw_value: str | None, *, default: int) -> int:
    try:
        value = int(raw_value or "")
    except ValueError:
        return default
    return max(value, 1)


@router.get("/{slug}", response_class=HTMLResponse)
async def blog_detail(request: Request, slug: str, session: SessionDependency) -> HTMLResponse:
    post = await get_public_post_by_slug(session, slug)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse(
        request=request,
        name="blog/detail.html",
        context=await _build_blog_detail_context(request, session, post),
    )


@router.post("/{slug}/comments")
async def submit_comment(
    request: Request,
    slug: str,
    session: SessionDependency,
) -> Response:
    post = await get_public_post_by_slug(session, slug)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    form = await request.form()
    csrf_value = form.get("csrf_token")
    verify_csrf_token(request, csrf_value if isinstance(csrf_value, str) else None)

    user_id = _current_user_id(request)
    if user_id is None:
        next_url = quote(str(request.url.path), safe="/")
        return RedirectResponse(
            url=f"/auth/login?next={next_url}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    content = form.get("content")
    submitted_content = content if isinstance(content, str) else ""
    result = await submit_blog_comment(session, post, user_id, submitted_content)
    if result.created:
        flash(request, "Comment submitted and pending review.", "success")
        return RedirectResponse(
            url=f"/blog/{post.slug}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return templates.TemplateResponse(
        request=request,
        name="blog/detail.html",
        context=await _build_blog_detail_context(
            request,
            session,
            post,
            comment_errors=result.errors,
            comment_content=submitted_content,
        ),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def _build_blog_detail_context(
    request: Request,
    session: SessionDependency,
    post: BlogPost,
    *,
    comment_errors: list[str] | None = None,
    comment_content: str = "",
) -> dict[str, Any]:
    return {
        **build_page_seo(
            request,
            title=f"{post.title} | libaoshuai",
            description=post.description,
            path=f"/blog/{post.slug}",
            og_type="article",
        ),
        "post": post,
        "post_html": render_markdown(post.content_markdown),
        "recent_posts": [recent for recent in await list_recent_posts(session) if recent.slug != post.slug],
        "categories": await list_categories(session),
        "tags": await list_tags(session),
        "comments": await list_approved_comments_for_post(session, post.slug),
        "comment_errors": comment_errors or [],
        "comment_content": comment_content,
    }


def _current_user_id(request: Request) -> uuid.UUID | None:
    raw_user_id = request.session.get(SESSION_USER_ID_KEY)
    if not isinstance(raw_user_id, str):
        return None
    try:
        return uuid.UUID(raw_user_id)
    except ValueError:
        return None
