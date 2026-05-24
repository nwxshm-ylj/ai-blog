from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.services.projects import get_project_by_slug, list_featured_projects, list_projects
from app.services.seo import build_page_seo
from app.web.templating import templates

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_class=HTMLResponse)
async def projects_index(request: Request) -> HTMLResponse:
    projects = list_projects()
    return templates.TemplateResponse(
        request=request,
        name="projects/index.html",
        context={
            **build_page_seo(
                request,
                title="AI Projects | AI Blog",
                description=(
                    "A portfolio of AI engineering projects covering agents, retrieval, "
                    "automation, developer tooling, and production FastAPI systems."
                ),
                path="/projects",
            ),
            "projects": projects,
            "featured_projects": list_featured_projects(),
        },
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def project_detail(request: Request, slug: str) -> HTMLResponse:
    project = get_project_by_slug(slug)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return templates.TemplateResponse(
        request=request,
        name="projects/detail.html",
        context={
            **build_page_seo(
                request,
                title=f"{project.title} | AI Projects",
                description=project.description,
                path=f"/projects/{project.slug}",
                og_type="article",
            ),
            "project": project,
            "related_projects": [
                related
                for related in list_projects()
                if related.slug != project.slug and related.category == project.category
            ][:2],
        },
    )
