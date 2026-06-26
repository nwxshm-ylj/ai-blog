from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.services.seo import build_page_seo
from app.web.i18n import translate as t
from app.web.templating import templates

router = APIRouter()


@router.get("/ai-lab", response_class=HTMLResponse)
async def ai_lab_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="ai_lab.html",
        context={
            **build_page_seo(
                request,
                title=t(request, "seo.ai_lab.title"),
                description=t(request, "seo.ai_lab.description"),
                path="/ai-lab",
            ),
        },
    )


@router.get("/resume", response_class=HTMLResponse)
async def resume_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="resume.html",
        context={
            **build_page_seo(
                request,
                title=t(request, "seo.resume.title"),
                description=t(request, "seo.resume.description"),
                path="/resume",
            ),
        },
    )
