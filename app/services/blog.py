from __future__ import annotations

from datetime import date

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.repositories.posts import PostRepository
from app.schemas.blog import BlogPost
from app.services.comments import list_approved_comment_counts

DEFAULT_PORTFOLIO_POSTS: tuple[BlogPost, ...] = (
    BlogPost(
        slug="industrial-vision-from-model-to-production-line",
        title="工业视觉检测系统如何从模型走向产线",
        description="从检测目标、数据采集、模型推理、规则校验到现场反馈闭环，梳理工业视觉系统落地时需要补齐的工程环节。",
        author="IndusAI Lab",
        category="工业视觉",
        tags=["工业视觉", "质量检测", "产线落地"],
        published_at=date(2026, 1, 5),
        reading_time_minutes=3,
        content_markdown=(
            "这是一篇计划中的项目复盘，后续会补充工业视觉检测系统从模型验证到产线使用的完整过程。"
        ),
    ),
    BlogPost(
        slug="manufacturing-quality-metrics-design",
        title="制造质量数据分析中的指标体系设计",
        description="围绕缺陷、返修、工位、车型、批次和工艺参数，说明制造质量分析中如何建立可解释、可追踪的指标体系。",
        author="IndusAI Lab",
        category="制造数据分析",
        tags=["Power BI", "SQL", "质量分析"],
        published_at=date(2026, 1, 12),
        reading_time_minutes=3,
        content_markdown="这是一篇计划中的分析笔记，后续会补充质量指标口径、数据建模和看板设计方法。",
    ),
    BlogPost(
        slug="secom-semiconductor-defect-detection-review",
        title="SECOM 半导体缺陷检测项目复盘",
        description="基于公开 SECOM 数据集，复盘高维传感器数据清洗、特征筛选、类别不平衡处理和缺陷预测建模过程。",
        author="IndusAI Lab",
        category="半导体数据分析",
        tags=["SECOM", "良率分析", "机器学习"],
        published_at=date(2026, 1, 19),
        reading_time_minutes=3,
        content_markdown="这是一篇计划中的项目复盘，后续会补充 SECOM 数据分析流程、模型基线和结果解释。",
    ),
    BlogPost(
        slug="rag-industrial-document-qa",
        title="RAG 知识库在工业文档问答中的应用",
        description="探索如何将设备手册、工艺规范和质量问题记录转为可检索、可追溯的工业知识库问答应用。",
        author="IndusAI Lab",
        category="RAG 应用",
        tags=["RAG", "LLM", "工业知识库"],
        published_at=date(2026, 1, 26),
        reading_time_minutes=3,
        content_markdown="这是一篇计划中的工程笔记，后续会补充文档切分、向量检索、引用追踪和回答评估方案。",
    ),
    BlogPost(
        slug="fastapi-ai-portfolio-site",
        title="FastAPI 如何支撑个人 AI 作品集网站",
        description="说明本站如何使用 FastAPI、Jinja2、SQLAlchemy、PostgreSQL、Alembic、TailwindCSS 和 Docker Compose 构建作品集能力。",
        author="IndusAI Lab",
        category="后端工程",
        tags=["FastAPI", "Jinja2", "SEO"],
        published_at=date(2026, 2, 2),
        reading_time_minutes=3,
        content_markdown="这是一篇计划中的建站笔记，后续会补充本站架构、后台管理、SEO、i18n 和部署设计。",
    ),
)


async def list_public_posts(
    session: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 10,
) -> list[BlogPost]:
    posts = await PostRepository(session).list_public(offset=offset, limit=limit)
    public_posts = [_to_blog_post(post) for post in posts]
    if not public_posts:
        return _fallback_posts(offset=offset, limit=limit)
    comment_counts = await list_approved_comment_counts(session, [post.slug for post in public_posts])
    return [
        post.model_copy(update={"comment_count": comment_counts.get(post.slug, 0)})
        for post in public_posts
    ]


async def get_public_post_by_slug(session: AsyncSession, slug: str) -> BlogPost | None:
    post = await PostRepository(session).get_public_by_slug(slug)
    if post is None:
        return next((fallback for fallback in _fallback_posts(offset=0, limit=len(DEFAULT_PORTFOLIO_POSTS)) if fallback.slug == slug), None)

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
    categories = sorted({post.category.name for post in posts if post.category is not None})
    return categories or sorted({post.category for post in DEFAULT_PORTFOLIO_POSTS})


async def list_tags(session: AsyncSession) -> list[str]:
    posts = await PostRepository(session).list_public(offset=0, limit=500)
    tags = sorted({tag.name for post in posts for tag in post.tags})
    return tags or sorted({tag for post in DEFAULT_PORTFOLIO_POSTS for tag in post.tags})


async def list_posts_for_seo(session: AsyncSession) -> list[BlogPost]:
    return await list_public_posts(session, limit=500)


def _to_blog_post(post: Post, *, view_count: int | None = None) -> BlogPost:
    published_at = post.created_at.date() if post.created_at else date.today()
    description = post.summary or post.seo_description or ""
    return BlogPost(
        slug=post.slug,
        title=post.title,
        description=description,
        author=post.author.username if post.author else "IndusAI Lab",
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


def _fallback_posts(*, offset: int, limit: int) -> list[BlogPost]:
    return [post.model_copy(deep=True) for post in DEFAULT_PORTFOLIO_POSTS[offset : offset + limit]]
