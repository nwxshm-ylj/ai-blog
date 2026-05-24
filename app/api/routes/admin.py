from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.services.admin import (
    get_admin_post_by_slug,
    get_admin_posts,
    get_admin_project_by_slug,
    get_admin_projects,
    get_dashboard_stats,
    get_empty_admin_post,
    get_empty_admin_project,
)
from app.web.templating import templates

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin/index.html",
        context={
            "title": "Admin Dashboard | AI Blog",
            "active_admin_nav": "dashboard",
            "dashboard_stats": get_dashboard_stats(),
        },
    )


@router.get("/posts", response_class=HTMLResponse)
async def admin_posts(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin/posts.html",
        context={
            "title": "Post Management | AI Blog",
            "active_admin_nav": "posts",
            "posts": get_admin_posts(),
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
        },
    )


@router.get("/posts/{slug}/edit", response_class=HTMLResponse)
async def admin_edit_post(request: Request, slug: str) -> HTMLResponse:
    post = get_admin_post_by_slug(slug) or get_empty_admin_post()
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
        },
    )


@router.get("/projects", response_class=HTMLResponse)
async def admin_projects(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin/projects.html",
        context={
            "title": "Project Management | AI Blog",
            "active_admin_nav": "projects",
            "projects": get_admin_projects(),
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
        },
    )


@router.get("/projects/{slug}/edit", response_class=HTMLResponse)
async def admin_edit_project(request: Request, slug: str) -> HTMLResponse:
    project = get_admin_project_by_slug(slug) or get_empty_admin_project()
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
        },
    )
