from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.dependencies import SessionDependency
from app.services.projects import (
    get_public_project_by_slug,
    list_public_featured_projects,
    list_public_projects,
)
from app.services.seo import build_page_seo
from app.web.i18n import get_lang
from app.web.templating import templates

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_class=HTMLResponse)
async def projects_index(request: Request, session: SessionDependency) -> HTMLResponse:
    projects = await list_public_projects(session)
    featured_projects = await list_public_featured_projects(session)
    is_en = get_lang(request) == "en"
    return templates.TemplateResponse(
        request=request,
        name="projects/index.html",
        context={
            **build_page_seo(
                request,
                title=(
                    "Projects | Li Baoshuai Industrial AI Portfolio"
                    if is_en
                    else "项目案例 | 李宝帅工业AI与制造数字化作品集"
                ),
                description=(
                    "Case studies across industrial vision inspection, certificate OCR "
                    "validation, manufacturing quality analytics, torque monitoring, "
                    "SECOM semiconductor analytics, and RAG industrial knowledge bases."
                    if is_en
                    else "工业 AI 与制造数字化项目案例，覆盖整车配置视觉检测、证书 OCR 自动校验、制造质量数据分析、扭矩状态监控、SECOM 半导体分析和 RAG 工业知识库应用。"
                ),
                path="/projects",
            ),
            "projects": projects,
            "featured_projects": featured_projects,
        },
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def project_detail(request: Request, slug: str, session: SessionDependency) -> HTMLResponse:
    project = await get_public_project_by_slug(session, slug)
    if project is None:
        raise HTTPException(status_code=404, detail="项目不存在")

    is_en = get_lang(request) == "en"
    return templates.TemplateResponse(
        request=request,
        name="projects/detail.html",
        context={
            **build_page_seo(
                request,
                title=(
                    f"{project.title} | Li Baoshuai Industrial AI Portfolio"
                    if is_en
                    else f"{project.title} | 工业AI项目案例"
                ),
                description=project.description,
                path=f"/projects/{project.slug}",
                og_type="article",
            ),
            "project": project,
            "related_projects": [
                related
                for related in await list_public_projects(session)
                if related.slug != project.slug and related.category == project.category
            ][:2],
        },
    )
