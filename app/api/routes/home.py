from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies import SessionDependency
from app.services.projects import list_public_featured_projects
from app.services.seo import build_page_seo
from app.web.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request, session: SessionDependency) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            **build_page_seo(
                request,
                title="AI Blog",
                description=(
                    "Notes on AI systems, software architecture, and product engineering "
                    "from a production FastAPI and AI tooling stack."
                ),
                path="/",
            ),
            "featured_projects": await list_public_featured_projects(session),
        },
    )
