from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies import SessionDependency
from app.services.projects import list_public_featured_projects
from app.services.seo import build_page_seo
from app.web.i18n import translate as t
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
                title=t(request, "seo.home.title"),
                description=t(request, "seo.home.description"),
                path="/",
            ),
            "featured_projects": await list_public_featured_projects(session),
        },
    )


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            **build_page_seo(
                request,
                title=t(request, "seo.about.title"),
                description=t(request, "seo.about.description"),
                path="/about",
            ),
        },
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={
            **build_page_seo(
                request,
                title=t(request, "seo.contact.title"),
                description=t(request, "seo.contact.description"),
                path="/contact",
            ),
        },
    )
