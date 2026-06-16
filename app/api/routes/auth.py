from __future__ import annotations

from typing import Annotated
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.models.user import User
from app.services.auth import (
    SESSION_IS_ADMIN_KEY,
    SESSION_USER_ID_KEY,
    SESSION_USERNAME_KEY,
    RegistrationData,
    authenticate_user,
    register_public_user,
)
from app.web.flash import flash
from app.web.security import verify_csrf_token
from app.web.templating import templates

router = APIRouter(prefix="/auth", tags=["auth"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "title": "登录 | 李宝帅作品集",
            "error": None,
            "identifier": "",
            "next_url": _safe_next_url(request.query_params.get("next"), default="/"),
        },
    )


@router.post("/login")
async def login_action(request: Request, session: SessionDependency) -> Response:
    form = await _read_urlencoded_form(request)
    verify_csrf_token(request, form.get("csrf_token"))
    next_url = _safe_next_url(form.get("next"), default="/")
    identifier = form.get("identifier", "").strip()
    result = await authenticate_user(
        session,
        identifier=identifier,
        password=form.get("password", ""),
    )
    if result.user is None:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "title": "登录 | 李宝帅作品集",
                "error": result.error,
                "identifier": identifier,
                "next_url": next_url,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    _login_session(request, result.user)
    flash(request, "已登录。", "success")
    return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={
            "title": "创建账号 | 李宝帅作品集",
            "errors": [],
            "email": "",
            "username": "",
            "next_url": _safe_next_url(request.query_params.get("next"), default="/"),
        },
    )


@router.post("/register")
async def register_action(request: Request, session: SessionDependency) -> Response:
    form = await _read_urlencoded_form(request)
    verify_csrf_token(request, form.get("csrf_token"))
    next_url = _safe_next_url(form.get("next"), default="/")
    email = form.get("email", "").strip()
    username = form.get("username", "").strip()
    result = await register_public_user(
        session,
        RegistrationData(
            email=email,
            username=username,
            password=form.get("password", ""),
            password_confirm=form.get("password_confirm", ""),
        ),
    )
    if result.user is None:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "title": "创建账号 | 李宝帅作品集",
                "errors": result.errors,
                "email": email,
                "username": username,
                "next_url": next_url,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    _login_session(request, result.user)
    flash(request, "账号已创建。", "success")
    return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
async def logout_action(request: Request) -> RedirectResponse:
    form = await _read_urlencoded_form(request)
    verify_csrf_token(request, form.get("csrf_token"))
    request.session.clear()
    flash(request, "已退出登录。", "success")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


def _login_session(request: Request, user: User) -> None:
    csrf_token = request.session.get("csrf_token")
    request.session.clear()
    if isinstance(csrf_token, str):
        request.session["csrf_token"] = csrf_token
    request.session[SESSION_USER_ID_KEY] = str(user.id)
    request.session[SESSION_USERNAME_KEY] = user.username
    request.session[SESSION_IS_ADMIN_KEY] = user.is_admin


async def _read_urlencoded_form(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}


def _safe_next_url(next_url: str | None, *, default: str) -> str:
    if not next_url or not next_url.startswith("/") or next_url.startswith("//"):
        return default
    return next_url
