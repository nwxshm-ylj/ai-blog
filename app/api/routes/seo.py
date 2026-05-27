from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.dependencies import SessionDependency
from app.services.blog import list_posts_for_seo
from app.services.projects import list_projects_for_seo
from app.services.seo import build_robots_txt, build_rss_feed, build_sitemap

router = APIRouter(tags=["seo"])


@router.get("/rss.xml", response_class=Response)
async def rss_feed(request: Request, session: SessionDependency) -> Response:
    content = build_rss_feed(str(request.base_url), await list_posts_for_seo(session))
    return Response(content=content, media_type="application/rss+xml; charset=utf-8")


@router.get("/sitemap.xml", response_class=Response)
async def sitemap(request: Request, session: SessionDependency) -> Response:
    content = build_sitemap(
        str(request.base_url),
        await list_posts_for_seo(session),
        await list_projects_for_seo(session),
    )
    return Response(content=content, media_type="application/xml; charset=utf-8")


@router.get("/robots.txt", response_class=Response)
async def robots_txt(request: Request) -> Response:
    content = build_robots_txt(str(request.base_url))
    return Response(content=content, media_type="text/plain; charset=utf-8")
