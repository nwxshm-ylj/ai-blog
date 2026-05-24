from __future__ import annotations

from typing import Annotated
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.services.auth import SESSION_USER_ID_KEY, authenticate_admin_user
from app.web.templating import templates

router = APIRouter(prefix="/auth", tags=["auth"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "title": "Admin Login | AI Blog",
            "error": None,
            "identifier": "",
            "next_url": _safe_next_url(request.query_params.get("next")),
        },
    )


@router.post("/login")
async def login_action(request: Request, session: SessionDependency) -> Response:
    form = await _read_urlencoded_form(request)
    next_url = _safe_next_url(form.get("next"))
    identifier = form.get("identifier", "").strip()
    result = await authenticate_admin_user(
        session,
        identifier=identifier,
        password=form.get("password", ""),
    )
    if result.user is None:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "title": "Admin Login | AI Blog",
                "error": result.error,
                "identifier": identifier,
                "next_url": next_url,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    request.session[SESSION_USER_ID_KEY] = str(result.user.id)
    return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
async def logout_action(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


async def _read_urlencoded_form(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _safe_next_url(next_url: str | None) -> str:
    if not next_url or not next_url.startswith("/") or next_url.startswith("//"):
        return "/admin"
    return next_url
