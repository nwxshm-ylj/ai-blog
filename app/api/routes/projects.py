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
from app.web.i18n import translate as t
from app.web.templating import templates

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_class=HTMLResponse)
async def projects_index(request: Request, session: SessionDependency) -> HTMLResponse:
    projects = await list_public_projects(session)
    featured_projects = await list_public_featured_projects(session)
    return templates.TemplateResponse(
        request=request,
        name="projects/index.html",
        context={
            **build_page_seo(
                request,
                title=t(request, "seo.projects.title"),
                description=t(request, "seo.projects.description"),
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
        raise HTTPException(status_code=404, detail="Project not found")

    return templates.TemplateResponse(
        request=request,
        name="projects/detail.html",
        context={
            **build_page_seo(
                request,
                title=f"{project.title} | libaoshuai",
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
