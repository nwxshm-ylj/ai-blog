from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project as ProjectModel
from app.repositories.projects import ProjectRepository
from app.schemas.projects import Project

DEFAULT_PORTFOLIO_PROJECTS: tuple[Project, ...] = (
    Project(
        slug="vehicle-configuration-vision-inspection",
        title="AI 整车配置视觉检测系统",
        description=(
            "面向汽车制造下线检查场景，使用工业相机、视觉识别和配置规则校验，辅助识别车辆外观件与配置项是否匹配生产订单。"
        ),
        summary="工业视觉检测系统，覆盖 20+ 配置项检测，并在 3 条产线落地使用。",
        category="工业视觉检测",
        tech_stack=["Python", "OpenCV", "YOLO", "FastAPI", "PostgreSQL", "MES 集成"],
        featured=True,
        status="产线实践",
        impact=(
            "系统将人工配置核对转为视觉识别加规则校验的流程，覆盖 20+ 配置项检测，并支持 3 条产线的现场使用。"
        ),
        highlights=[
            "项目背景：整车配置项多、人工核对容易受节拍和经验影响，需要在不干扰产线的前提下提升检查一致性。",
            "解决的问题：识别外观配置与订单配置不一致、漏检和复核成本高的问题。",
            "我的职责：参与检测流程设计、视觉识别结果对接、配置规则梳理、后端接口与现场问题闭环。",
            "工程难点：现场光照、角度、遮挡和车型差异会影响识别稳定性，需要结合规则校验和异常复核机制。",
            "结果/影响：覆盖 20+ 配置项检测，并在 3 条产线落地，减少重复人工核对工作。",
        ],
        view_count=0,
    ),
    Project(
        slug="certificate-ocr-validation",
        title="证书 OCR 信息提取与自动校验系统",
        description=(
            "针对制造业务中的证书、合格证和随车文件录入场景，构建 OCR 信息提取、字段结构化和业务规则自动校验流程。"
        ),
        summary="将证书信息人工核对流程自动化，典型操作时间从约 30s 缩短到约 5s。",
        category="OCR 自动化",
        tech_stack=["Python", "OCR", "FastAPI", "SQL", "Jinja2", "规则校验"],
        featured=True,
        status="业务实践",
        impact="通过 OCR 提取和规则校验减少重复录入，典型操作时间从约 30s 缩短到约 5s。",
        highlights=[
            "项目背景：证书信息字段多、人工录入和复核重复度高，且容易出现格式或字段不一致。",
            "解决的问题：自动提取关键字段，并根据业务规则校验证书信息与系统数据是否一致。",
            "我的职责：梳理字段映射规则、实现 OCR 结果解析、后端校验接口和异常提示逻辑。",
            "工程难点：OCR 结果存在错字、漏字和版式差异，需要设计容错解析和人工复核入口。",
            "结果/影响：将典型人工操作时间从约 30s 降至约 5s，提升了证书核对效率。",
        ],
        view_count=0,
    ),
    Project(
        slug="manufacturing-quality-analytics-platform",
        title="制造质量数据分析平台",
        description=(
            "围绕制造质量、缺陷、返修和过程数据，构建 SQL 数据模型、Power BI 看板和分析指标体系，用于质量问题定位和趋势跟踪。"
        ),
        summary="制造质量指标体系与数据看板，支持缺陷趋势、返修分布和质量问题追踪。",
        category="制造数据分析",
        tech_stack=["SQL", "Power BI", "Python", "PostgreSQL", "DAX", "ETL"],
        featured=True,
        status="分析实践",
        impact="将分散质量数据整理为可追踪指标，帮助识别缺陷分布、返修趋势和重点质量问题。",
        highlights=[
            "项目背景：制造质量数据分散在多个业务系统中，现场分析依赖人工导出和临时表格。",
            "解决的问题：建立质量指标口径，跟踪缺陷类型、责任区域、返修趋势和工艺关联因素。",
            "我的职责：设计 SQL 查询与数据模型、搭建 Power BI 看板、维护指标口径和分析视图。",
            "工程难点：不同系统字段口径不一致，需要在清洗、关联和聚合阶段保持可解释性。",
            "结果/影响：形成可复用的质量分析视图，支持日常质量例会和问题追踪。",
        ],
        view_count=0,
    ),
    Project(
        slug="bolt-torque-status-monitoring",
        title="螺栓扭矩状态自动监控系统",
        description=(
            "针对装配过程中的关键扭矩数据，构建状态采集、异常识别和可视化监控流程，辅助现场及时发现漏拧、错拧和参数异常。"
        ),
        summary="自动监控关键螺栓扭矩状态，支持异常发现、追溯和现场质量闭环。",
        category="制造系统集成",
        tech_stack=["Python", "SQL", "FastAPI", "PostgreSQL", "工业数据采集", "可视化"],
        featured=False,
        status="工程实践",
        impact="将关键扭矩状态从事后抽查推进到过程监控，提升异常发现和追溯效率。",
        highlights=[
            "项目背景：关键装配扭矩影响质量安全，人工抽查难以及时覆盖所有异常状态。",
            "解决的问题：自动采集和分析扭矩状态，识别漏拧、错拧、超限和数据缺失等问题。",
            "我的职责：设计数据状态规则、实现后端查询与异常聚合、对接现场追溯需求。",
            "工程难点：设备数据、工位节拍和质量规则需要统一到可维护的数据模型中。",
            "结果/影响：提升关键工序异常发现速度，为现场质量闭环提供数据依据。",
        ],
        view_count=0,
    ),
    Project(
        slug="secom-semiconductor-defect-yield-analysis",
        title="SECOM 半导体缺陷检测 / 良率分析项目",
        description=(
            "基于公开 SECOM 半导体制造数据集，进行高维传感器数据清洗、特征筛选、缺陷预测和良率分析方法验证。"
        ),
        summary="半导体数据分析学习项目，聚焦高维传感器数据、缺陷预测和良率分析。",
        category="半导体数据分析",
        tech_stack=["Python", "pandas", "scikit-learn", "XGBoost", "特征工程", "数据可视化"],
        featured=True,
        status="学习项目",
        impact="形成面向半导体智能制造岗位的缺陷检测和良率分析项目复盘材料。",
        highlights=[
            "项目背景：半导体制造数据维度高、缺失值多、类别不平衡，适合作为良率分析和缺陷预测练习场景。",
            "解决的问题：探索如何从高维传感器数据中筛选有效特征，并建立缺陷预测基线模型。",
            "我的职责：完成数据清洗、缺失值处理、特征选择、模型训练和结果复盘。",
            "工程难点：特征数量远高于样本量，需要控制过拟合并解释特征对预测结果的影响。",
            "结果/影响：沉淀半导体数据分析实践方法，为转向 AOI、良率和工艺数据分析岗位做准备。",
        ],
        view_count=0,
    ),
    Project(
        slug="rag-industrial-knowledge-base-qa",
        title="RAG 工业知识库问答应用",
        description=(
            "面向设备手册、工艺规范、质量问题记录等工业文档，探索基于向量检索和 LLM 的知识库问答应用。"
        ),
        summary="RAG / Agent 应用探索项目，用于工业文档检索、问答和知识复用。",
        category="RAG / Agent 应用",
        tech_stack=["Python", "FastAPI", "LLM", "RAG", "Vector Search", "PostgreSQL"],
        featured=False,
        status="探索项目",
        impact="验证工业文档问答的基本链路，为后续设备知识库和质量经验库应用积累方案。",
        highlights=[
            "项目背景：工业现场知识分散在手册、规范、邮件和问题记录中，检索和复用成本较高。",
            "解决的问题：将文档切分、向量化并建立问答入口，辅助快速定位设备、工艺和质量相关知识。",
            "我的职责：设计 RAG 流程、实现文档解析与检索接口、评估回答引用和可追溯性。",
            "工程难点：工业文档术语密集，答案需要可追溯来源，不能只依赖模型生成。",
            "结果/影响：完成工业知识库问答链路探索，为 RAG 与制造系统结合提供原型基础。",
        ],
        view_count=0,
    ),
)


async def list_public_projects(
    session: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 12,
) -> list[Project]:
    projects = await ProjectRepository(session).list_public(offset=offset, limit=limit)
    public_projects = [_to_public_project(project) for project in projects]
    if public_projects:
        return public_projects
    return _fallback_projects(offset=offset, limit=limit)


async def list_public_featured_projects(session: AsyncSession, *, limit: int = 4) -> list[Project]:
    projects = await ProjectRepository(session).list_featured(limit=limit)
    public_projects = [_to_public_project(project) for project in projects]
    if public_projects:
        return public_projects
    return [project for project in _fallback_projects(offset=0, limit=len(DEFAULT_PORTFOLIO_PROJECTS)) if project.featured][:limit]


async def get_public_project_by_slug(session: AsyncSession, slug: str) -> Project | None:
    project = await ProjectRepository(session).get_by_slug(slug)
    if project is None:
        return next((fallback for fallback in _fallback_projects(offset=0, limit=len(DEFAULT_PORTFOLIO_PROJECTS)) if fallback.slug == slug), None)

    view_count = await increment_project_view_count(session, slug)
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
    projects = await ProjectRepository(session).list_public(offset=0, limit=500)
    public_projects = [_to_public_project(project) for project in projects]
    return public_projects or _fallback_projects(offset=0, limit=len(DEFAULT_PORTFOLIO_PROJECTS))


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
        featured=project.featured,
        status=project.status,
        impact=project.impact or description,
        highlights=project.highlights or [],
        view_count=project.view_count if view_count is None else view_count,
    )


def _fallback_projects(*, offset: int, limit: int) -> list[Project]:
    return [project.model_copy(deep=True) for project in DEFAULT_PORTFOLIO_PROJECTS[offset : offset + limit]]
