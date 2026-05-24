from __future__ import annotations

from app.schemas.admin import AdminDashboardStat, AdminPost, AdminProject


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
    return [
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


def get_admin_post_by_slug(slug: str) -> AdminPost | None:
    return next((post for post in get_admin_posts() if post.slug == slug), None)


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
    return [
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


def get_admin_project_by_slug(slug: str) -> AdminProject | None:
    return next((project for project in get_admin_projects() if project.slug == slug), None)


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
