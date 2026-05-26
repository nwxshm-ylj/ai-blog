from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project as ProjectModel
from app.schemas.projects import Project
from app.services.db_guard import run_optional_db_operation


_PROJECTS: list[Project] = [
    Project(
        slug="retrieval-evaluation-studio",
        title="Retrieval Evaluation Studio",
        description=(
            "A dashboard for testing RAG pipelines against curated prompts, source coverage, "
            "latency budgets, and answer quality checks."
        ),
        summary="Measure retrieval quality before shipping AI search experiences.",
        category="AI Infrastructure",
        tech_stack=["FastAPI", "PostgreSQL", "pgvector", "OpenAI", "TailwindCSS"],
        github_url="https://github.com/example/retrieval-evaluation-studio",
        demo_url="https://example.com/retrieval-evaluation-studio",
        featured=True,
        status="Prototype",
        impact="Cuts manual QA time for retrieval changes by turning regressions into reviewable runs.",
        highlights=[
            "Prompt set versioning for repeatable evaluations.",
            "Side-by-side answer, source, and latency comparisons.",
            "Exportable reports for product and engineering reviews.",
        ],
    ),
    Project(
        slug="agent-ops-console",
        title="Agent Ops Console",
        description=(
            "An operations surface for monitoring tool calls, trace timelines, escalation events, "
            "and completion quality across AI agents."
        ),
        summary="Observe agent behavior with production-focused trace workflows.",
        category="Agent Tooling",
        tech_stack=["Python", "FastAPI", "SQLAlchemy", "Jinja2", "Redis"],
        github_url="https://github.com/example/agent-ops-console",
        demo_url="https://example.com/agent-ops-console",
        featured=True,
        status="Case study",
        impact="Gives teams a practical control plane for debugging agent workflows after launch.",
        highlights=[
            "Trace timeline with tool, model, and human-review events.",
            "Operational filters for failed tasks and slow steps.",
            "Environment-aware project views for staging and production.",
        ],
    ),
    Project(
        slug="content-intelligence-pipeline",
        title="Content Intelligence Pipeline",
        description=(
            "A batch pipeline that classifies research notes, extracts structured metadata, "
            "and drafts editorial briefs for technical writing."
        ),
        summary="Turn raw research notes into structured editorial inputs.",
        category="Automation",
        tech_stack=["Python", "OpenAI", "PostgreSQL", "Celery", "Markdown"],
        github_url="https://github.com/example/content-intelligence-pipeline",
        demo_url=None,
        featured=False,
        status="Internal tool",
        impact="Keeps technical content planning searchable, reusable, and easier to maintain.",
        highlights=[
            "Schema-first extraction for topics, links, and evidence.",
            "Queue-based processing for long-running research folders.",
            "Markdown output that can move directly into editorial review.",
        ],
    ),
    Project(
        slug="model-release-notes",
        title="Model Release Notes",
        description=(
            "A lightweight publishing workflow for tracking model changes, benchmark deltas, "
            "migration notes, and customer-facing release copy."
        ),
        summary="Coordinate AI model updates with clear engineering and product context.",
        category="Developer Experience",
        tech_stack=["FastAPI", "Jinja2", "TailwindCSS", "SQLAlchemy"],
        github_url="https://github.com/example/model-release-notes",
        demo_url="https://example.com/model-release-notes",
        featured=False,
        status="Design build",
        impact="Reduces release confusion by pairing technical deltas with migration guidance.",
        highlights=[
            "Structured release entries for engineering and product teams.",
            "Comparison views for benchmark and behavior changes.",
            "SEO-ready public notes with canonical project URLs.",
        ],
    ),
]


def list_projects() -> list[Project]:
    return _PROJECTS


async def list_public_projects(session: AsyncSession) -> list[Project]:
    counts = await run_optional_db_operation(lambda: _get_view_counts(session), {})
    return [_with_view_count(project, counts.get(project.slug, project.view_count)) for project in list_projects()]


def list_featured_projects() -> list[Project]:
    return [project for project in _PROJECTS if project.featured]


async def list_public_featured_projects(session: AsyncSession) -> list[Project]:
    return [project for project in await list_public_projects(session) if project.featured]


def get_project_by_slug(slug: str) -> Project | None:
    return next((project for project in _PROJECTS if project.slug == slug), None)


async def get_public_project_by_slug(session: AsyncSession, slug: str) -> Project | None:
    project = get_project_by_slug(slug)
    if project is None:
        return None

    view_count = await run_optional_db_operation(
        lambda: increment_project_view_count(session, slug),
        None,
    )
    if view_count is None:
        view_count = project.view_count + 1
        project.view_count = view_count

    return _with_view_count(project, view_count)


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


async def _get_view_counts(session: AsyncSession) -> dict[str, int]:
    slugs = [project.slug for project in _PROJECTS]
    statement = select(ProjectModel.slug, ProjectModel.view_count).where(ProjectModel.slug.in_(slugs))
    result = await session.execute(statement)
    return dict(result.all())


def _with_view_count(project: Project, view_count: int) -> Project:
    return project.model_copy(update={"view_count": view_count})
