from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project as ProjectModel
from app.repositories.projects import ProjectRepository
from app.schemas.projects import Project
from app.services.db_guard import run_optional_db_operation


DEFAULT_PORTFOLIO_PROJECTS: tuple[Project, ...] = (
    Project(
        slug="vehicle-configuration-vision-inspection",
        title="基于AI的整车视觉检测系统",
        description=(
            "使用 AI 算法与海康工业相机，对产线上运动车辆的轮毂、尾标等 20 余项零件配置进行实时检测，"
            "并将识别结果与 MES 订单配置自动比对。"
        ),
        summary="覆盖 20+ 配置项的整车视觉检测系统，已在 3 条产线落地，整车识别合格率达到 95% 以上。",
        category="工业视觉检测",
        tech_stack=["Python", "PyTorch", "YOLO", "海康 MVS SDK", "ONNX", "Flask", "MES API"],
        cover_image="/static/images/project-vision-inspection.png",
        featured=True,
        status="已落地 · 3 条产线",
        impact="替代 3 名检验员的重复目视检查工作，整车识别合格率达到 95% 以上。",
        highlights=[
            "规划设计：依据实时检测需求，规划工业相机部署位置、拍摄角度、触发逻辑和系统整体架构，形成实施方案。",
            "图像采集：使用海康 MVS 配置相机参数，固定触发方式与进光量，保证不同班次和车辆通过时的图像质量一致性。",
            "系统链路：使用 Python 完成相机触发、图像传输和边缘端推理，并将推理结果与 MES 配置自动比对。",
            "模型训练：使用 X-AnyLabel 批量标注图像，基于 PyTorch 训练 YOLO 模型，转换为 ONNX 后部署到边缘端。",
            "现场交互：使用 Flask 开发检测大屏，通过 API 与 MES 交互，在边缘端和 MES 同步展示检测结果。",
            "落地成果：系统应用于 3 条产线，覆盖轮毂、尾标等 20 余项配置，替代 3 名检验员重复检查工作。",
        ],
        view_count=0,
    ),
    Project(
        slug="bolt-torque-status-monitoring",
        title="螺栓扭矩质量预测系统",
        description=(
            "基于螺栓拧紧记录与扭矩曲线，使用机器学习和多层感知机进行质量风险预测，"
            "实时识别四类质量风险并将异常推送给现场工程师。"
        ),
        summary="从生产数据库自动抽取扭矩数据，完成特征处理、风险分级预测和异常预警，支撑质量追溯闭环。",
        category="制造质量预测",
        tech_stack=["Python", "TensorFlow", "NumPy", "Pandas", "MySQL", "MLP", "定时任务", "邮件预警"],
        cover_image="/static/images/project-quality-analytics.png",
        featured=True,
        status="已落地 · 实时监控",
        impact="实现小时级自动推理与四类质量风险识别，将 Risk 记录实时推送给工程师进行追溯和闭环处理。",
        highlights=[
            "数据采集：使用 Python 定时任务，每小时从生产 MySQL 数据库抽取螺栓拧紧记录和扭矩曲线明细，写入中间表。",
            "特征工程：使用 NumPy、Pandas 清洗数据，提取曲线波动次数、掉底异常、拧紧状态和扭矩类别等业务特征。",
            "训练数据：完成特征编码、归一化和统一训练数据集构建，保证训练与线上推理使用一致的数据处理流程。",
            "模型训练：对比多种机器学习方法，并使用 TensorFlow 构建多层感知机，完成四类质量风险分级预测。",
            "在线推理：模型部署后对小时级扭矩数据自动推理，输出质量风险类别和对应的异常记录。",
            "预警闭环：筛选预测为 Risk 的记录，自动发送邮件给工程师，支撑异常追溯和质量闭环管理。",
        ],
        view_count=0,
    ),
)
CORE_PROJECT_SLUGS = tuple(project.slug for project in DEFAULT_PORTFOLIO_PROJECTS)


async def list_public_projects(
    session: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 12,
) -> list[Project]:
    projects = await run_optional_db_operation(
        lambda: ProjectRepository(session).list_public(offset=0, limit=500),
        [],
    )
    public_projects = _merge_core_projects(projects)
    return public_projects[offset : offset + limit]


async def list_public_featured_projects(session: AsyncSession, *, limit: int = 4) -> list[Project]:
    projects = await run_optional_db_operation(
        lambda: ProjectRepository(session).list_public(offset=0, limit=500),
        [],
    )
    return _merge_core_projects(projects)[:limit]


async def get_public_project_by_slug(session: AsyncSession, slug: str) -> Project | None:
    if slug not in CORE_PROJECT_SLUGS:
        return None
    project = await run_optional_db_operation(
        lambda: ProjectRepository(session).get_by_slug(slug),
        None,
    )
    if project is None:
        return next((item.model_copy(deep=True) for item in DEFAULT_PORTFOLIO_PROJECTS if item.slug == slug), None)

    view_count = await run_optional_db_operation(
        lambda: increment_project_view_count(session, slug),
        project.view_count,
    )
    return _to_public_project(project, view_count=view_count or project.view_count)


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


async def list_projects_for_seo(session: AsyncSession) -> list[Project]:
    projects = await run_optional_db_operation(
        lambda: ProjectRepository(session).list_public(offset=0, limit=500),
        [],
    )
    return _merge_core_projects(projects)


def _to_public_project(project: ProjectModel, *, view_count: int | None = None) -> Project:
    description = project.description or ""
    summary = project.summary or description
    return Project(
        slug=project.slug,
        title=project.title,
        description=description,
        summary=summary,
        category=project.category,
        tech_stack=project.tech_stack,
        github_url=project.github_url,
        demo_url=project.demo_url,
        cover_image=project.cover_image,
        featured=project.featured,
        status=project.status,
        impact=project.impact or description,
        highlights=project.highlights or [],
        view_count=project.view_count if view_count is None else view_count,
    )


def _fallback_projects(*, offset: int, limit: int) -> list[Project]:
    return [project.model_copy(deep=True) for project in DEFAULT_PORTFOLIO_PROJECTS[offset : offset + limit]]


def _merge_core_projects(projects: list[ProjectModel]) -> list[Project]:
    database_projects = {
        project.slug: _to_public_project(project)
        for project in projects
        if project.slug in CORE_PROJECT_SLUGS
    }
    return [
        database_projects.get(project.slug, project.model_copy(deep=True))
        for project in DEFAULT_PORTFOLIO_PROJECTS
    ]
