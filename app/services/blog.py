from __future__ import annotations

from datetime import date

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas.blog import BlogPost
from app.services.db_guard import run_optional_db_operation


_POSTS: list[BlogPost] = [
    BlogPost(
        slug="building-a-layered-fastapi-blog",
        title="Building a Layered FastAPI Blog",
        description=(
            "A practical walkthrough of keeping routes, services, schemas, and templates "
            "separate while shipping a small developer blog."
        ),
        author="AI Blog Team",
        category="Architecture",
        tags=["FastAPI", "Jinja2", "Architecture"],
        published_at=date(2026, 5, 24),
        reading_time_minutes=6,
        content_markdown="""# Building a Layered FastAPI Blog

Small FastAPI applications stay easier to change when the public web layer is kept thin. Routes should coordinate request and response behavior, while service modules own retrieval and business rules.

## Route responsibilities

The blog route only needs to collect posts, render markdown, and pass SEO-friendly context into the template.

```python
@router.get("/blog/{slug}")
async def post_detail(request: Request, slug: str) -> HTMLResponse:
    post = get_post_by_slug(slug)
    return templates.TemplateResponse(request, "blog/detail.html", {"post": post})
```

That keeps template composition independent from persistence decisions. When PostgreSQL-backed posts arrive later, the templates and route shape can stay stable.

## Template structure

Reusable components keep cards, sidebars, and tag pills consistent. The page templates remain focused on document structure and metadata.
""",
    ),
    BlogPost(
        slug="markdown-for-developer-notes",
        title="Markdown for Developer Notes",
        description=(
            "Markdown gives engineering posts a compact authoring format while still "
            "supporting code blocks, headings, lists, and links."
        ),
        author="AI Blog Team",
        category="Writing",
        tags=["Markdown", "Developer Experience", "Syntax Highlighting"],
        published_at=date(2026, 5, 18),
        reading_time_minutes=4,
        content_markdown="""# Markdown for Developer Notes

Developer blogs need prose and code to sit comfortably together. Markdown is a good fit because it keeps source content readable and portable.

## Code blocks

Fenced code blocks make examples scannable and easy to highlight:

```sql
select slug, title, published_at
from posts
where status = 'published'
order by published_at desc;
```

## Editorial workflow

Start with plain files and mock data. Move to database-backed content only when publishing workflows need it.
""",
    ),
    BlogPost(
        slug="designing-dark-mode-reading-pages",
        title="Designing Dark Mode Reading Pages",
        description=(
            "Minimal dark interfaces work best when typography, spacing, and contrast "
            "do the heavy lifting."
        ),
        author="AI Blog Team",
        category="Design",
        tags=["TailwindCSS", "Dark Mode", "UX"],
        published_at=date(2026, 5, 10),
        reading_time_minutes=5,
        content_markdown="""# Designing Dark Mode Reading Pages

Dark developer blogs should feel quiet and focused. The page needs strong hierarchy, restrained borders, and enough contrast for long reading sessions.

## Practical rules

- Keep the content column narrow.
- Let metadata support the title instead of competing with it.
- Use code surfaces that are visually distinct from article prose.
- Keep tags and categories visible but secondary.

```css
.article {
  max-width: 72ch;
  line-height: 1.75;
}
```

These small choices make the reading experience feel intentional without adding visual noise.
""",
    ),
]


def list_posts() -> list[BlogPost]:
    return sorted(_POSTS, key=lambda post: post.published_at, reverse=True)


async def list_public_posts(session: AsyncSession) -> list[BlogPost]:
    counts = await run_optional_db_operation(lambda: _get_view_counts(session), {})
    return [_with_view_count(post, counts.get(post.slug, post.view_count)) for post in list_posts()]


def get_post_by_slug(slug: str) -> BlogPost | None:
    return next((post for post in _POSTS if post.slug == slug), None)


async def get_public_post_by_slug(session: AsyncSession, slug: str) -> BlogPost | None:
    post = get_post_by_slug(slug)
    if post is None:
        return None

    view_count = await run_optional_db_operation(
        lambda: increment_post_view_count(session, slug),
        None,
    )
    if view_count is None:
        view_count = post.view_count + 1
        post.view_count = view_count

    return _with_view_count(post, view_count)


async def increment_post_view_count(session: AsyncSession, slug: str) -> int | None:
    statement = (
        update(Post)
        .where(Post.slug == slug, Post.is_published.is_(True))
        .values(view_count=Post.view_count + 1)
        .returning(Post.view_count)
    )
    result = await session.execute(statement)
    view_count = result.scalar_one_or_none()
    if view_count is not None:
        await session.commit()
    return view_count


def list_recent_posts(limit: int = 4) -> list[BlogPost]:
    return list_posts()[:limit]


def list_categories() -> list[str]:
    return sorted({post.category for post in _POSTS})


def list_tags() -> list[str]:
    return sorted({tag for post in _POSTS for tag in post.tags})


async def _get_view_counts(session: AsyncSession) -> dict[str, int]:
    slugs = [post.slug for post in _POSTS]
    statement = select(Post.slug, Post.view_count).where(Post.slug.in_(slugs))
    result = await session.execute(statement)
    return dict(result.all())


def _with_view_count(post: BlogPost, view_count: int) -> BlogPost:
    return post.model_copy(update={"view_count": view_count})
