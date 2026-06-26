from __future__ import annotations

from datetime import date

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.repositories.posts import PostRepository
from app.schemas.blog import BlogPost
from app.services.comments import list_approved_comment_counts
from app.services.db_guard import run_optional_db_operation


DEFAULT_PORTFOLIO_POSTS: tuple[BlogPost, ...] = (
    BlogPost(
        slug="vehicle-vision-inspection-from-design-to-production",
        title="整车视觉检测系统：从方案设计到三条产线落地",
        description="复盘工业相机部署、YOLO 模型训练、边缘推理、MES 比对和现场大屏的完整落地链路。",
        author="libaoshuai",
        category="工业视觉",
        tags=["PyTorch", "YOLO", "海康 MVS", "MES"],
        published_at=date(2026, 6, 20),
        reading_time_minutes=5,
        content_markdown=(
            "## 项目目标\n\n"
            "产线需要对运动车辆的轮毂、尾标等 20 余项零件配置进行实时检测，并将检测结果与 MES 订单配置自动比对。"
            "系统的目标不是单独验证模型精度，而是形成可连续运行、结果可追溯的自动检测流程。\n\n"
            "## 方案规划\n\n"
            "规划阶段先根据车辆节拍、检测区域和现场空间确定相机部署位置与拍摄角度，再设计触发逻辑、图像传输、边缘推理、MES 比对和结果展示链路。"
            "相机使用海康 MVS 配置固定触发方式、曝光和进光量，减少班次、环境光和车辆位置变化对图像质量的影响。\n\n"
            "## 模型与部署\n\n"
            "图像通过 X-AnyLabel 批量标注，算法选择 YOLO，使用 PyTorch 完成训练。"
            "训练完成后将模型转换为 ONNX，并部署到边缘端执行推理。Python 服务负责触发拍摄、接收图像、调用模型和整理检测结果。\n\n"
            "## 系统集成\n\n"
            "推理结果通过 API 与 MES 中的车辆配置进行自动比对，并同步输出到边缘端和 MES。"
            "现场大屏使用 Flask 开发，用于展示车辆、检测项、识别结果和异常状态，便于检验人员复核。\n\n"
            "## 落地结果\n\n"
            "系统已应用于 3 条产线，覆盖 20 余项零件配置检测，替代 3 名检验员的重复目视检查工作，整车识别合格率达到 95% 以上。"
        ),
    ),
    BlogPost(
        slug="bolt-torque-quality-prediction-pipeline",
        title="螺栓扭矩质量预测：从曲线特征到风险预警",
        description="介绍扭矩数据采集、特征工程、TensorFlow 模型训练、四类风险识别和邮件预警闭环。",
        author="libaoshuai",
        category="制造质量预测",
        tags=["TensorFlow", "Pandas", "MySQL", "质量预测"],
        published_at=date(2026, 6, 23),
        reading_time_minutes=5,
        content_markdown=(
            "## 业务目标\n\n"
            "系统根据螺栓拧紧记录和扭矩曲线，使用机器学习实时判断扭矩质量状态，识别四类质量风险，并将异常记录推送给现场工程师。\n\n"
            "## 数据采集\n\n"
            "后端使用 Python 开发。定时任务每小时从生产 MySQL 数据库抽取螺栓拧紧记录和扭矩曲线明细，写入中间表，形成稳定的训练与推理数据入口。\n\n"
            "## 特征工程\n\n"
            "使用 NumPy、Pandas 完成清洗和特征处理。结合业务规则提取扭矩曲线波动次数、掉底异常、拧紧状态和扭矩类别等特征，"
            "再完成特征编码、归一化和统一训练数据集构建。\n\n"
            "## 模型训练与推理\n\n"
            "训练阶段对比多种机器学习方法，并使用 TensorFlow 构建多层感知机进行风险分级预测。"
            "模型部署后按小时处理新增扭矩数据，复用训练阶段的数据处理流程并输出四类质量风险。\n\n"
            "## 预警闭环\n\n"
            "后台筛选预测为 Risk 的记录，自动发送邮件给工程师。预警信息保留对应的螺栓记录和特征数据，支持异常追溯、人工确认和质量闭环管理。"
        ),
    ),
)


async def list_public_posts(
    session: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 10,
) -> list[BlogPost]:
    posts = await run_optional_db_operation(
        lambda: PostRepository(session).list_public(offset=offset, limit=limit),
        [],
    )
    public_posts = [_to_blog_post(post) for post in posts]
    if not public_posts:
        return _fallback_posts(offset=offset, limit=limit)
    comment_counts = await list_approved_comment_counts(session, [post.slug for post in public_posts])
    return [
        post.model_copy(update={"comment_count": comment_counts.get(post.slug, 0)})
        for post in public_posts
    ]


async def get_public_post_by_slug(session: AsyncSession, slug: str) -> BlogPost | None:
    post = await run_optional_db_operation(
        lambda: PostRepository(session).get_public_by_slug(slug),
        None,
    )
    if post is None:
        return next((item.model_copy(deep=True) for item in DEFAULT_PORTFOLIO_POSTS if item.slug == slug), None)

    view_count = await run_optional_db_operation(
        lambda: increment_post_view_count(session, slug),
        post.view_count,
    )
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
    posts = await run_optional_db_operation(
        lambda: PostRepository(session).list_public(offset=0, limit=500),
        [],
    )
    categories = sorted({post.category.name for post in posts if post.category is not None})
    return categories or sorted({post.category for post in DEFAULT_PORTFOLIO_POSTS})


async def list_tags(session: AsyncSession) -> list[str]:
    posts = await run_optional_db_operation(
        lambda: PostRepository(session).list_public(offset=0, limit=500),
        [],
    )
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
