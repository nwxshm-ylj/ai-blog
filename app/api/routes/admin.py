from __future__ import annotations

from typing import Annotated
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.schemas.admin import AdminPost, AdminProject
from app.services.admin import (
    create_admin_post,
    create_admin_project,
    delete_admin_post,
    delete_admin_project,
    get_admin_post_by_slug,
    get_admin_posts,
    get_admin_project_by_slug,
    get_admin_projects,
    get_dashboard_stats,
    get_empty_admin_post,
    get_empty_admin_project,
    update_admin_post,
    update_admin_project,
    validate_admin_post,
    validate_admin_project,
)
from app.web.templating import templates

router = APIRouter(prefix="/admin", tags=["admin"])
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, session: SessionDependency) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin/index.html",
        context={
            "title": "Admin Dashboard | AI Blog",
            "active_admin_nav": "dashboard",
            "dashboard_stats": await get_dashboard_stats(session),
        },
    )


@router.get("/posts", response_class=HTMLResponse)
async def admin_posts(request: Request, session: SessionDependency) -> HTMLResponse:
    message = request.query_params.get("message")
    return templates.TemplateResponse(
        request=request,
        name="admin/posts.html",
        context={
            "title": "Post Management | AI Blog",
            "active_admin_nav": "posts",
            "posts": await get_admin_posts(session),
            "message": message,
        },
    )


@router.get("/posts/new", response_class=HTMLResponse)
async def admin_new_post(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin/post_form.html",
        context={
            "title": "New Post | AI Blog",
            "active_admin_nav": "posts",
            "form_title": "New post",
            "form_action": "/admin/posts",
            "submit_label": "Create post",
            "post": get_empty_admin_post(),
            "errors": [],
        },
    )


@router.get("/posts/{slug}/edit", response_class=HTMLResponse)
async def admin_edit_post(
    request: Request,
    slug: str,
    session: SessionDependency,
) -> HTMLResponse:
    post = await get_admin_post_by_slug(session, slug)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return templates.TemplateResponse(
        request=request,
        name="admin/post_form.html",
        context={
            "title": f"Edit {post.title or slug} | AI Blog",
            "active_admin_nav": "posts",
            "form_title": "Edit post",
            "form_action": f"/admin/posts/{slug}",
            "submit_label": "Save post",
            "post": post,
            "errors": [],
        },
    )


@router.post("/posts")
async def admin_create_post(
    request: Request,
    session: SessionDependency,
) -> Response:
    post = await _read_admin_post_form(request)
    errors = await validate_admin_post(session, post)
    if errors:
        return templates.TemplateResponse(
            request=request,
            name="admin/post_form.html",
            context={
                "title": "New Post | AI Blog",
                "active_admin_nav": "posts",
                "form_title": "New post",
                "form_action": "/admin/posts",
                "submit_label": "Create post",
                "post": post,
                "errors": errors,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    await create_admin_post(session, post)
    return RedirectResponse(
        url="/admin/posts?message=created",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/posts/{slug}")
async def admin_update_post(
    request: Request,
    slug: str,
    session: SessionDependency,
) -> Response:
    existing = await get_admin_post_by_slug(session, slug)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post = await _read_admin_post_form(request)
    errors = await validate_admin_post(session, post, current_slug=slug)
    if errors:
        return templates.TemplateResponse(
            request=request,
            name="admin/post_form.html",
            context={
                "title": f"Edit {post.title or slug} | AI Blog",
                "active_admin_nav": "posts",
                "form_title": "Edit post",
                "form_action": f"/admin/posts/{slug}",
                "submit_label": "Save post",
                "post": post,
                "errors": errors,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    await update_admin_post(session, slug, post)
    return RedirectResponse(
        url="/admin/posts?message=updated",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/posts/{slug}/delete")
async def admin_delete_post(slug: str, session: SessionDependency) -> RedirectResponse:
    deleted = await delete_admin_post(session, slug)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return RedirectResponse(
        url="/admin/posts?message=deleted",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/projects", response_class=HTMLResponse)
async def admin_projects(request: Request, session: SessionDependency) -> HTMLResponse:
    message = request.query_params.get("message")
    return templates.TemplateResponse(
        request=request,
        name="admin/projects.html",
        context={
            "title": "Project Management | AI Blog",
            "active_admin_nav": "projects",
            "projects": await get_admin_projects(session),
            "message": message,
        },
    )


@router.get("/projects/new", response_class=HTMLResponse)
async def admin_new_project(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin/project_form.html",
        context={
            "title": "New Project | AI Blog",
            "active_admin_nav": "projects",
            "form_title": "New project",
            "form_action": "/admin/projects",
            "submit_label": "Create project",
            "project": get_empty_admin_project(),
            "errors": [],
        },
    )


@router.get("/projects/{slug}/edit", response_class=HTMLResponse)
async def admin_edit_project(
    request: Request,
    slug: str,
    session: SessionDependency,
) -> HTMLResponse:
    project = await get_admin_project_by_slug(session, slug)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return templates.TemplateResponse(
        request=request,
        name="admin/project_form.html",
        context={
            "title": f"Edit {project.title or slug} | AI Blog",
            "active_admin_nav": "projects",
            "form_title": "Edit project",
            "form_action": f"/admin/projects/{slug}",
            "submit_label": "Save project",
            "project": project,
            "errors": [],
        },
    )


@router.post("/projects")
async def admin_create_project(
    request: Request,
    session: SessionDependency,
) -> Response:
    project = await _read_admin_project_form(request)
    errors = await validate_admin_project(session, project)
    if errors:
        return templates.TemplateResponse(
            request=request,
            name="admin/project_form.html",
            context={
                "title": "New Project | AI Blog",
                "active_admin_nav": "projects",
                "form_title": "New project",
                "form_action": "/admin/projects",
                "submit_label": "Create project",
                "project": project,
                "errors": errors,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    await create_admin_project(session, project)
    return RedirectResponse(
        url="/admin/projects?message=created",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/projects/{slug}")
async def admin_update_project(
    request: Request,
    slug: str,
    session: SessionDependency,
) -> Response:
    existing = await get_admin_project_by_slug(session, slug)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    project = await _read_admin_project_form(request)
    errors = await validate_admin_project(session, project, current_slug=slug)
    if errors:
        return templates.TemplateResponse(
            request=request,
            name="admin/project_form.html",
            context={
                "title": f"Edit {project.title or slug} | AI Blog",
                "active_admin_nav": "projects",
                "form_title": "Edit project",
                "form_action": f"/admin/projects/{slug}",
                "submit_label": "Save project",
                "project": project,
                "errors": errors,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    await update_admin_project(session, slug, project)
    return RedirectResponse(
        url="/admin/projects?message=updated",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/projects/{slug}/delete")
async def admin_delete_project(slug: str, session: SessionDependency) -> RedirectResponse:
    deleted = await delete_admin_project(session, slug)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return RedirectResponse(
        url="/admin/projects?message=deleted",
        status_code=status.HTTP_303_SEE_OTHER,
    )


async def _read_admin_post_form(request: Request) -> AdminPost:
    form = await _read_urlencoded_form(request)
    return AdminPost(
        title=form.get("title", "").strip(),
        slug=form.get("slug", "").strip(),
        summary=form.get("summary", "").strip(),
        markdown_content=form.get("markdown_content", "").strip(),
        cover_image=form.get("cover_image", "").strip(),
        is_published=form.get("is_published") == "true",
        seo_title=form.get("seo_title", "").strip(),
        seo_description=form.get("seo_description", "").strip(),
    )


async def _read_admin_project_form(request: Request) -> AdminProject:
    form = await _read_urlencoded_form(request)
    return AdminProject(
        title=form.get("title", "").strip(),
        slug=form.get("slug", "").strip(),
        description=form.get("description", "").strip(),
        tech_stack=form.get("tech_stack", "").strip(),
        github_url=form.get("github_url", "").strip(),
        demo_url=form.get("demo_url", "").strip(),
        cover_image=form.get("cover_image", "").strip(),
        featured=form.get("featured") == "true",
    )


async def _read_urlencoded_form(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[-1] if values else "" for key, values in parsed.items()}
