from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.post import Post
from app.repositories.comments import CommentRepository
from app.repositories.posts import PostRepository
from app.repositories.users import UserRepository
from app.schemas.blog import BlogPost
from app.schemas.comments import AdminComment, PublicComment
from app.services.admin import DEFAULT_AUTHOR_EMAIL
from app.services.db_guard import run_optional_db_operation

COMMENT_MAX_LENGTH = 2000


@dataclass(frozen=True)
class CommentSubmissionResult:
    created: bool
    errors: list[str]


async def list_approved_comments_for_post(
    session: AsyncSession,
    slug: str,
) -> list[PublicComment]:
    return await run_optional_db_operation(
        lambda: _list_approved_comments_for_post(session, slug),
        [],
    )


async def submit_blog_comment(
    session: AsyncSession,
    post: BlogPost,
    user_id: uuid.UUID,
    content: str,
) -> CommentSubmissionResult:
    normalized_content = _normalize_content(content)
    errors = validate_comment_content(normalized_content)
    if errors:
        return CommentSubmissionResult(created=False, errors=errors)

    try:
        user = await UserRepository(session).get(user_id)
        if user is None:
            return CommentSubmissionResult(
                created=False,
                errors=["Sign in again before commenting."],
            )

        post_model = await _get_or_create_comment_post(session, post)
        await CommentRepository(session).add(
            Comment(
                post_id=post_model.id,
                user_id=user.id,
                content=normalized_content,
                is_approved=False,
            )
        )
        await session.commit()
    except (OSError, SQLAlchemyError):
        await session.rollback()
        return CommentSubmissionResult(
            created=False,
            errors=["Comments are temporarily unavailable. Try again later."],
        )

    return CommentSubmissionResult(created=True, errors=[])


async def list_admin_comments(session: AsyncSession) -> list[AdminComment]:
    comments = await CommentRepository(session).list_admin()
    return [_to_admin_comment(comment) for comment in comments]


async def approve_comment(session: AsyncSession, comment_id: uuid.UUID) -> bool:
    return await _set_comment_approval(session, comment_id, is_approved=True)


async def hide_comment(session: AsyncSession, comment_id: uuid.UUID) -> bool:
    return await _set_comment_approval(session, comment_id, is_approved=False)


async def delete_comment(session: AsyncSession, comment_id: uuid.UUID) -> bool:
    repository = CommentRepository(session)
    comment = await repository.get(comment_id)
    if comment is None:
        return False

    await repository.delete(comment)
    await session.commit()
    return True


def validate_comment_content(content: str) -> list[str]:
    errors: list[str] = []
    if not content:
        errors.append("Comment content is required.")
    elif len(content) > COMMENT_MAX_LENGTH:
        errors.append(f"Comment must be {COMMENT_MAX_LENGTH} characters or fewer.")
    return errors


async def _list_approved_comments_for_post(
    session: AsyncSession,
    slug: str,
) -> list[PublicComment]:
    comments = await CommentRepository(session).list_approved_by_post_slug(slug)
    return [_to_public_comment(comment) for comment in comments]


async def _get_or_create_comment_post(session: AsyncSession, post: BlogPost) -> Post:
    repository = PostRepository(session)
    existing = await repository.get_by_slug(post.slug)
    if existing is not None:
        return existing

    author = await UserRepository(session).get_by(email=DEFAULT_AUTHOR_EMAIL)
    if author is None:
        raise SQLAlchemyError(
            "Default admin author is required before comments can mirror static posts."
        )

    return await repository.add(
        Post(
            author_id=author.id,
            title=post.title,
            slug=post.slug,
            summary=post.description,
            markdown_content=post.content_markdown,
            is_published=True,
            seo_title=post.title,
            seo_description=post.description,
        )
    )


async def _set_comment_approval(
    session: AsyncSession,
    comment_id: uuid.UUID,
    *,
    is_approved: bool,
) -> bool:
    comment = await CommentRepository(session).get(comment_id)
    if comment is None:
        return False

    comment.is_approved = is_approved
    await session.commit()
    return True


def _normalize_content(content: str) -> str:
    return " ".join(content.strip().split())


def _to_public_comment(comment: Comment) -> PublicComment:
    return PublicComment(
        id=comment.id,
        author_name=comment.user.username,
        content=comment.content,
        created_at=comment.created_at,
    )


def _to_admin_comment(comment: Comment) -> AdminComment:
    return AdminComment(
        id=comment.id,
        post_slug=comment.post.slug,
        post_title=comment.post.title,
        author_name=comment.user.username,
        content=comment.content,
        is_approved=comment.is_approved,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )
