from __future__ import annotations

import uuid
from dataclasses import dataclass
from time import monotonic

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.repositories.comments import CommentRepository
from app.repositories.posts import PostRepository
from app.repositories.users import UserRepository
from app.schemas.blog import BlogPost
from app.schemas.comments import AdminComment, PublicComment
from app.services.db_guard import run_optional_db_operation

COMMENT_MAX_LENGTH = 2000
COMMENT_RATE_LIMIT_COUNT = 5
COMMENT_RATE_LIMIT_WINDOW_SECONDS = 60.0
_comment_submission_times: dict[uuid.UUID, list[float]] = {}


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
    rate_limit_error = _check_comment_rate_limit(user_id)
    if rate_limit_error:
        return CommentSubmissionResult(created=False, errors=[rate_limit_error])

    try:
        user = await UserRepository(session).get(user_id)
        if user is None:
            return CommentSubmissionResult(
                created=False,
                errors=["请重新登录后再发表评论。"],
            )

        post_model = await PostRepository(session).get_public_by_slug(post.slug)
        if post_model is None:
            return CommentSubmissionResult(
                created=False,
                errors=["文章不存在或尚未发布。"],
            )
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
            errors=["评论功能暂时不可用，请稍后再试。"],
        )

    return CommentSubmissionResult(created=True, errors=[])


async def list_admin_comments(session: AsyncSession) -> list[AdminComment]:
    comments = await CommentRepository(session).list_admin()
    return [_to_admin_comment(comment) for comment in comments]


async def list_approved_comment_counts(
    session: AsyncSession,
    slugs: list[str],
) -> dict[str, int]:
    return await run_optional_db_operation(
        lambda: CommentRepository(session).count_approved_by_post_slugs(slugs),
        {},
    )


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
        errors.append("请输入评论内容。")
    elif len(content) > COMMENT_MAX_LENGTH:
        errors.append(f"评论不能超过 {COMMENT_MAX_LENGTH} 个字符。")
    return errors


async def _list_approved_comments_for_post(
    session: AsyncSession,
    slug: str,
) -> list[PublicComment]:
    comments = await CommentRepository(session).list_approved_by_post_slug(slug)
    return [_to_public_comment(comment) for comment in comments]


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


def _check_comment_rate_limit(user_id: uuid.UUID) -> str | None:
    now = monotonic()
    recent_times = [
        submitted_at
        for submitted_at in _comment_submission_times.get(user_id, [])
        if now - submitted_at < COMMENT_RATE_LIMIT_WINDOW_SECONDS
    ]
    if len(recent_times) >= COMMENT_RATE_LIMIT_COUNT:
        _comment_submission_times[user_id] = recent_times
        return "评论提交过于频繁，请稍后再试。"

    recent_times.append(now)
    _comment_submission_times[user_id] = recent_times
    return None


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
