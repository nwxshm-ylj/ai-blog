from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies import SessionDependency
from app.services.projects import list_public_featured_projects
from app.services.seo import build_page_seo
from app.web.i18n import get_lang
from app.web.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request, session: SessionDependency) -> HTMLResponse:
    is_en = get_lang(request) == "en"
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            **build_page_seo(
                request,
                title=(
                    "Li Baoshuai | Industrial AI & Manufacturing Analytics Portfolio"
                    if is_en
                    else "李宝帅 | 工业AI与制造数字化作品集"
                ),
                description=(
                    "Li Baoshuai's portfolio covering industrial AI vision, manufacturing "
                    "quality analytics, Python backend systems, semiconductor analytics, "
                    "and RAG / Agent application exploration."
                    if is_en
                    else "李宝帅的工业 AI 与制造数字化作品集，覆盖工业视觉检测、制造质量数据分析、Python 后端系统、半导体数据分析实践和 RAG / Agent 应用探索。"
                ),
                path="/",
            ),
            "featured_projects": await list_public_featured_projects(session),
        },
    )
