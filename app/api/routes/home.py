from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.services.projects import list_featured_projects
from app.web.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "AI Blog",
            "featured_projects": list_featured_projects(),
        },
    )
