from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies import SessionDependency
from app.services.projects import list_public_featured_projects
from app.services.seo import build_page_seo
from app.web.i18n import get_lang
from app.web.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request, session: SessionDependency) -> HTMLResponse:
    is_en = get_lang(request) == "en"
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            **build_page_seo(
                request,
                title=(
                    "IndusAI Lab | Industrial AI & Manufacturing Intelligence Tech Site"
                    if is_en
                    else "IndusAI Lab | 工业 AI 与制造数字化技术站"
                ),
                description=(
                    "IndusAI Lab is a technical site covering industrial AI vision, manufacturing "
                    "quality analytics, Python backend systems, semiconductor analytics, "
                    "and RAG / Agent application exploration."
                    if is_en
                    else "IndusAI Lab 是一个聚焦工业 AI 与制造数字化实践的技术站，覆盖工业视觉检测、制造质量数据分析、Python 后端系统、半导体数据分析实践和 RAG / Agent 应用探索。"
                ),
                path="/",
            ),
            "featured_projects": await list_public_featured_projects(session),
        },
    )


@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request) -> HTMLResponse:
    is_en = get_lang(request) == "en"
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            **build_page_seo(
                request,
                title=(
                    "About | IndusAI Lab"
                    if is_en
                    else "关于我 | IndusAI Lab"
                ),
                description=(
                    "A professional technical profile for IndusAI Lab, covering industrial "
                    "AI positioning, technical directions, project methodology, focus areas, "
                    "and current exploration topics."
                    if is_en
                    else "IndusAI Lab 的职业技术 Profile，介绍工业 AI 定位、技术方向、项目方法论、关注领域与正在探索的方向。"
                ),
                path="/about",
            ),
        },
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request) -> HTMLResponse:
    is_en = get_lang(request) == "en"
    return templates.TemplateResponse(
        request=request,
        name="contact.html",
        context={
            **build_page_seo(
                request,
                title=(
                    "Contact | IndusAI Lab"
                    if is_en
                    else "联系方式 | IndusAI Lab"
                ),
                description=(
                    "Contact information for technical discussions about industrial AI, "
                    "manufacturing analytics, Python backend systems, RAG, and Agent applications."
                    if is_en
                    else "用于工业 AI、制造数据分析、Python 后端系统、RAG 与 Agent 应用技术交流的联系方式。"
                ),
                path="/contact",
            ),
        },
    )
