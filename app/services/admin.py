from __future__ import annotations

from app.schemas.admin import AdminDashboardStat, AdminPost, AdminProject

_admin_posts: list[AdminPost] = [
    AdminPost(
        title="Designing Reliable RAG Evaluation Pipelines",
        slug="reliable-rag-evaluation-pipelines",
        summary="A practical guide to repeatable retrieval quality checks.",
        markdown_content="# Designing Reliable RAG Evaluation Pipelines\n\nDraft content for the article.",
        cover_image="/static/images/posts/rag-evaluation.jpg",
        is_published=True,
        seo_title="Reliable RAG Evaluation Pipelines",
        seo_description="How to design repeatable evaluation workflows for RAG systems.",
    ),
    AdminPost(
        title="Async FastAPI Patterns for Content Platforms",
        slug="async-fastapi-content-platforms",
        summary="Route, service, and template patterns for maintainable apps.",
        markdown_content="# Async FastAPI Patterns\n\nDraft content for the article.",
        cover_image="/static/images/posts/fastapi-patterns.jpg",
        is_published=False,
        seo_title="Async FastAPI Content Platform Patterns",
        seo_description="Production-minded FastAPI patterns for content applications.",
    ),
]

_admin_projects: list[AdminProject] = [
    AdminProject(
        title="Retrieval Evaluation Studio",
        slug="retrieval-evaluation-studio",
        description="Dashboard for comparing retrieval experiments and quality signals.",
        tech_stack="FastAPI, PostgreSQL, Jinja2, TailwindCSS",
        github_url="https://github.com/example/retrieval-evaluation-studio",
        demo_url="https://example.com/retrieval-evaluation-studio",
        cover_image="/static/images/projects/retrieval-evaluation-studio.jpg",
        featured=True,
    ),
    AdminProject(
        title="Prompt Regression Monitor",
        slug="prompt-regression-monitor",
        description="Internal tool for tracking prompt changes against evaluation suites.",
        tech_stack="Python, SQLAlchemy, Celery, Redis",
        github_url="https://github.com/example/prompt-regression-monitor",
        demo_url="",
        cover_image="/static/images/projects/prompt-regression-monitor.jpg",
        featured=False,
    ),
]


def get_dashboard_stats() -> list[AdminDashboardStat]:
    return [
        AdminDashboardStat(
            label="Total posts",
            value=12,
            description="All posts in the content workspace",
        ),
        AdminDashboardStat(
            label="Total projects",
            value=6,
            description="Portfolio projects tracked for publishing",
        ),
        AdminDashboardStat(
            label="Published posts",
            value=8,
            description="Posts visible on the public blog",
        ),
        AdminDashboardStat(
            label="Draft posts",
            value=4,
            description="Posts waiting for editorial review",
        ),
    ]


def get_admin_posts() -> list[AdminPost]:
    return list(_admin_posts)


def get_admin_post_by_slug(slug: str) -> AdminPost | None:
    return next((post for post in _admin_posts if post.slug == slug), None)


def create_admin_post(post: AdminPost) -> None:
    _admin_posts.append(post)


def update_admin_post(slug: str, post: AdminPost) -> None:
    index = _find_post_index(slug)
    if index is None:
        _admin_posts.append(post)
        return
    _admin_posts[index] = post


def delete_admin_post(slug: str) -> None:
    index = _find_post_index(slug)
    if index is not None:
        del _admin_posts[index]


def validate_admin_post(post: AdminPost) -> list[str]:
    errors: list[str] = []
    if not post.title.strip():
        errors.append("Title is required.")
    if not post.slug.strip():
        errors.append("Slug is required.")
    if not post.summary.strip():
        errors.append("Summary is required.")
    if not post.markdown_content.strip():
        errors.append("Markdown content is required.")
    return errors


def _find_post_index(slug: str) -> int | None:
    for index, post in enumerate(_admin_posts):
        if post.slug == slug:
            return index
    return None


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


def get_admin_projects() -> list[AdminProject]:
    return list(_admin_projects)


def get_admin_project_by_slug(slug: str) -> AdminProject | None:
    return next((project for project in _admin_projects if project.slug == slug), None)


def create_admin_project(project: AdminProject) -> None:
    _admin_projects.append(project)


def update_admin_project(slug: str, project: AdminProject) -> None:
    index = _find_project_index(slug)
    if index is None:
        _admin_projects.append(project)
        return
    _admin_projects[index] = project


def delete_admin_project(slug: str) -> None:
    index = _find_project_index(slug)
    if index is not None:
        del _admin_projects[index]


def validate_admin_project(project: AdminProject) -> list[str]:
    errors: list[str] = []
    if not project.title.strip():
        errors.append("Title is required.")
    if not project.slug.strip():
        errors.append("Slug is required.")
    if not project.description.strip():
        errors.append("Description is required.")
    if not project.tech_stack.strip():
        errors.append("Tech stack is required.")
    return errors


def _find_project_index(slug: str) -> int | None:
    for index, project in enumerate(_admin_projects):
        if project.slug == slug:
            return index
    return None


def get_empty_admin_project() -> AdminProject:
    return AdminProject(
        title="",
        slug="",
        description="",
        tech_stack="",
        github_url="",
        demo_url="",
        cover_image="",
        featured=False,
    )
