from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project as ProjectModel
from app.repositories.projects import ProjectRepository
from app.schemas.projects import Project


async def list_public_projects(
    session: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 12,
) -> list[Project]:
    projects = await ProjectRepository(session).list_public(offset=offset, limit=limit)
    return [_to_public_project(project) for project in projects]


async def list_public_featured_projects(session: AsyncSession, *, limit: int = 4) -> list[Project]:
    projects = await ProjectRepository(session).list_featured(limit=limit)
    return [_to_public_project(project) for project in projects]


async def get_public_project_by_slug(session: AsyncSession, slug: str) -> Project | None:
    project = await ProjectRepository(session).get_by_slug(slug)
    if project is None:
        return None

    view_count = await increment_project_view_count(session, slug)
    return _to_public_project(project, view_count=view_count or project.view_count)


async def increment_project_view_count(session: AsyncSession, slug: str) -> int | None:
    statement = (
        update(ProjectModel)
        .where(ProjectModel.slug == slug)
        .values(view_count=ProjectModel.view_count + 1)
        .returning(ProjectModel.view_count)
    )
    result = await session.execute(statement)
    view_count = result.scalar_one_or_none()
    if view_count is not None:
        await session.commit()
    return view_count


async def list_projects_for_seo(session: AsyncSession) -> list[Project]:
    projects = await ProjectRepository(session).list_public(offset=0, limit=500)
    return [_to_public_project(project) for project in projects]


def _to_public_project(project: ProjectModel, *, view_count: int | None = None) -> Project:
    description = project.description or ""
    summary = project.summary or description
    return Project(
        slug=project.slug,
        title=project.title,
        description=description,
        summary=summary,
        category=project.category,
        tech_stack=project.tech_stack,
        github_url=project.github_url,
        demo_url=project.demo_url,
        featured=project.featured,
        status=project.status,
        impact=project.impact or description,
        highlights=project.highlights or [],
        view_count=project.view_count if view_count is None else view_count,
    )
