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


@router.get("", response_class=HTMLResponse)
async def blog_index(request: Request, session: SessionDependency) -> HTMLResponse:
    posts = await list_public_posts(session)
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
            "recent_posts": await list_recent_posts(session),
            "categories": await list_categories(session),
            "tags": await list_tags(session),
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
