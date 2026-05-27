from __future__ import annotations

from datetime import date

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.repositories.posts import PostRepository
from app.schemas.blog import BlogPost
from app.services.comments import list_approved_comment_counts


async def list_public_posts(
    session: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 10,
) -> list[BlogPost]:
    posts = await PostRepository(session).list_public(offset=offset, limit=limit)
    public_posts = [_to_blog_post(post) for post in posts]
    comment_counts = await list_approved_comment_counts(session, [post.slug for post in public_posts])
    return [
        post.model_copy(update={"comment_count": comment_counts.get(post.slug, 0)})
        for post in public_posts
    ]


async def get_public_post_by_slug(session: AsyncSession, slug: str) -> BlogPost | None:
    post = await PostRepository(session).get_public_by_slug(slug)
    if post is None:
        return None

    view_count = await increment_post_view_count(session, slug)
    public_post = _to_blog_post(post, view_count=view_count or post.view_count)
    comment_counts = await list_approved_comment_counts(session, [post.slug])
    return public_post.model_copy(update={"comment_count": comment_counts.get(post.slug, 0)})


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


async def list_recent_posts(session: AsyncSession, limit: int = 4) -> list[BlogPost]:
    return await list_public_posts(session, limit=limit)


async def list_categories(session: AsyncSession) -> list[str]:
    posts = await PostRepository(session).list_public(offset=0, limit=500)
    return sorted({post.category.name for post in posts if post.category is not None})


async def list_tags(session: AsyncSession) -> list[str]:
    posts = await PostRepository(session).list_public(offset=0, limit=500)
    return sorted({tag.name for post in posts for tag in post.tags})


async def list_posts_for_seo(session: AsyncSession) -> list[BlogPost]:
    return await list_public_posts(session, limit=500)


def _to_blog_post(post: Post, *, view_count: int | None = None) -> BlogPost:
    published_at = post.created_at.date() if post.created_at else date.today()
    description = post.summary or post.seo_description or ""
    return BlogPost(
        slug=post.slug,
        title=post.title,
        description=description,
        author=post.author.username if post.author else "AI Blog",
        category=post.category.name if post.category else "AI",
        tags=[tag.name for tag in post.tags],
        published_at=published_at,
        reading_time_minutes=_estimate_reading_time(post.markdown_content),
        content_markdown=post.markdown_content,
        view_count=post.view_count if view_count is None else view_count,
    )


def _estimate_reading_time(content: str) -> int:
    words = max(len(content), 1) / 500
    return max(1, round(words))
