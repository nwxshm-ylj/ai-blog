from __future__ import annotations

from re import fullmatch

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.models.project import Project
from app.models.user import User
from app.repositories.posts import PostRepository
from app.repositories.projects import ProjectRepository
from app.repositories.users import UserRepository
from app.schemas.admin import AdminDashboardStat, AdminPost, AdminProject
from app.services.auth import LOCAL_DEV_ADMIN_EMAIL

DEFAULT_AUTHOR_EMAIL = LOCAL_DEV_ADMIN_EMAIL
SLUG_PATTERN = r"[A-Za-z0-9][A-Za-z0-9_-]*"


async def get_dashboard_stats(session: AsyncSession) -> list[AdminDashboardStat]:
    total_posts = await _count(session, Post)
    total_projects = await _count(session, Project)
    published_posts = await _count(session, Post, Post.is_published.is_(True))
    draft_posts = total_posts - published_posts

    return [
        AdminDashboardStat(
            label="文章总数",
            value=total_posts,
            description="内容工作区中的全部文章",
        ),
        AdminDashboardStat(
            label="项目总数",
            value=total_projects,
            description="当前管理的作品集项目",
        ),
        AdminDashboardStat(
            label="已发布文章",
            value=published_posts,
            description="前台博客中可见的文章",
        ),
        AdminDashboardStat(
            label="草稿文章",
            value=draft_posts,
            description="等待编辑和审核的文章",
        ),
    ]


async def get_admin_posts(session: AsyncSession) -> list[AdminPost]:
    repository = PostRepository(session)
    posts = await repository.list_admin()
    return [_post_to_admin(post) for post in posts]


async def get_admin_post_by_slug(session: AsyncSession, slug: str) -> AdminPost | None:
    repository = PostRepository(session)
    post = await repository.get_by_slug(slug)
    return _post_to_admin(post) if post else None


async def create_admin_post(session: AsyncSession, post: AdminPost) -> None:
    repository = PostRepository(session)
    author = await _get_or_create_default_admin_user(session)
    await repository.add(
        Post(
            author_id=author.id,
            title=post.title,
            slug=post.slug,
            summary=_optional(post.summary),
            markdown_content=post.markdown_content,
            cover_image=_optional(post.cover_image),
            is_published=post.is_published,
            seo_title=_optional(post.seo_title),
            seo_description=_optional(post.seo_description),
        )
    )
    await session.commit()


async def update_admin_post(session: AsyncSession, slug: str, post: AdminPost) -> bool:
    repository = PostRepository(session)
    existing = await repository.get_by_slug(slug)
    if existing is None:
        return False

    existing.title = post.title
    existing.slug = post.slug
    existing.summary = _optional(post.summary)
    existing.markdown_content = post.markdown_content
    existing.cover_image = _optional(post.cover_image)
    existing.is_published = post.is_published
    existing.seo_title = _optional(post.seo_title)
    existing.seo_description = _optional(post.seo_description)
    await session.commit()
    return True


async def delete_admin_post(session: AsyncSession, slug: str) -> bool:
    repository = PostRepository(session)
    existing = await repository.get_by_slug(slug)
    if existing is None:
        return False

    await repository.delete(existing)
    await session.commit()
    return True


async def validate_admin_post(
    session: AsyncSession,
    post: AdminPost,
    *,
    current_slug: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if not post.title.strip():
        errors.append("请输入标题。")
    if not post.slug.strip():
        errors.append("请输入链接标识。")
    elif fullmatch(SLUG_PATTERN, post.slug.strip()) is None:
        errors.append("链接标识只能包含字母、数字、下划线和连字符。")
    if not post.summary.strip():
        errors.append("请输入摘要。")
    if not post.markdown_content.strip():
        errors.append("请输入 Markdown 内容。")

    if post.slug.strip() and post.slug != current_slug:
        existing = await PostRepository(session).get_by_slug(post.slug)
        if existing is not None:
            errors.append("链接标识已被使用。")

    return errors


def get_empty_admin_post() -> AdminPost:
    return AdminPost(
        title="",
        slug="",
        summary="",
        markdown_content="",
        cover_image="",
        is_published=False,
        seo_title="",
        seo_description="",
    )


async def get_admin_projects(session: AsyncSession) -> list[AdminProject]:
    repository = ProjectRepository(session)
    projects = await repository.list_admin()
    return [_project_to_admin(project) for project in projects]


async def get_admin_project_by_slug(
    session: AsyncSession,
    slug: str,
) -> AdminProject | None:
    repository = ProjectRepository(session)
    project = await repository.get_by_slug(slug)
    return _project_to_admin(project) if project else None


async def create_admin_project(session: AsyncSession, project: AdminProject) -> None:
    repository = ProjectRepository(session)
    await repository.add(
        Project(
            title=project.title,
            slug=project.slug,
            description=_optional(project.description),
            summary=_optional(project.summary),
            category=project.category or "AI 项目",
            status=project.status or "已发布",
            impact=_optional(project.impact),
            highlights=_split_lines(project.highlights),
            tech_stack=_split_tech_stack(project.tech_stack),
            github_url=_optional(project.github_url),
            demo_url=_optional(project.demo_url),
            cover_image=_optional(project.cover_image),
            featured=project.featured,
        )
    )
    await session.commit()


async def update_admin_project(
    session: AsyncSession,
    slug: str,
    project: AdminProject,
) -> bool:
    repository = ProjectRepository(session)
    existing = await repository.get_by_slug(slug)
    if existing is None:
        return False

    existing.title = project.title
    existing.slug = project.slug
    existing.description = _optional(project.description)
    existing.summary = _optional(project.summary)
    existing.category = project.category or "AI 项目"
    existing.status = project.status or "已发布"
    existing.impact = _optional(project.impact)
    existing.highlights = _split_lines(project.highlights)
    existing.tech_stack = _split_tech_stack(project.tech_stack)
    existing.github_url = _optional(project.github_url)
    existing.demo_url = _optional(project.demo_url)
    existing.cover_image = _optional(project.cover_image)
    existing.featured = project.featured
    await session.commit()
    return True


async def delete_admin_project(session: AsyncSession, slug: str) -> bool:
    repository = ProjectRepository(session)
    existing = await repository.get_by_slug(slug)
    if existing is None:
        return False

    await repository.delete(existing)
    await session.commit()
    return True


async def validate_admin_project(
    session: AsyncSession,
    project: AdminProject,
    *,
    current_slug: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if not project.title.strip():
        errors.append("请输入标题。")
    if not project.slug.strip():
        errors.append("请输入链接标识。")
    elif fullmatch(SLUG_PATTERN, project.slug.strip()) is None:
        errors.append("链接标识只能包含字母、数字、下划线和连字符。")
    if not project.description.strip():
        errors.append("请输入描述。")
    if not project.category.strip():
        errors.append("请输入分类。")
    if not project.status.strip():
        errors.append("请输入状态。")
    if not project.tech_stack.strip():
        errors.append("请输入技术栈。")

    if project.slug.strip() and project.slug != current_slug:
        existing = await ProjectRepository(session).get_by_slug(project.slug)
        if existing is not None:
            errors.append("链接标识已被使用。")

    return errors


def get_empty_admin_project() -> AdminProject:
    return AdminProject(
        title="",
        slug="",
        description="",
        summary="",
        category="AI 项目",
        status="已发布",
        impact="",
        highlights="",
        tech_stack="",
        github_url="",
        demo_url="",
        cover_image="",
        featured=False,
    )


async def _count(session: AsyncSession, model: type[Post] | type[Project], *filters: object) -> int:
    statement = select(func.count()).select_from(model)
    if filters:
        statement = statement.where(*filters)
    result = await session.execute(statement)
    return result.scalar_one()


async def _get_or_create_default_admin_user(session: AsyncSession) -> User:
    repository = UserRepository(session)
    user = await repository.get_by(email=DEFAULT_AUTHOR_EMAIL)
    if user is not None:
        return user

    raise RuntimeError(
        "缺少默认管理员作者。请先运行本地开发管理员初始化命令。"
    )


def _post_to_admin(post: Post) -> AdminPost:
    return AdminPost(
        title=post.title,
        slug=post.slug,
        summary=post.summary or "",
        markdown_content=post.markdown_content,
        cover_image=post.cover_image or "",
        is_published=post.is_published,
        seo_title=post.seo_title or "",
        seo_description=post.seo_description or "",
    )


def _project_to_admin(project: Project) -> AdminProject:
    return AdminProject(
        title=project.title,
        slug=project.slug,
        description=project.description or "",
        summary=project.summary or "",
        category=project.category,
        status=project.status,
        impact=project.impact or "",
        highlights="\n".join(project.highlights or []),
        tech_stack=", ".join(project.tech_stack),
        github_url=project.github_url or "",
        demo_url=project.demo_url or "",
        cover_image=project.cover_image or "",
        featured=project.featured,
    )


def _split_tech_stack(tech_stack: str) -> list[str]:
    return [item.strip() for item in tech_stack.split(",") if item.strip()]


def _split_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _optional(value: str) -> str | None:
    return value.strip() or None
