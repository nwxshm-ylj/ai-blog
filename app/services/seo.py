from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timezone
from email.utils import format_datetime
from urllib.parse import urljoin
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from fastapi import Request

from app.schemas.blog import BlogPost
from app.schemas.projects import Project

DEFAULT_OG_IMAGE = "/static/images/industrial-ai-hero.png"
DEFAULT_DESCRIPTION = "libaoshuai 的 AI 作品集，聚焦整车视觉检测与螺栓扭矩质量预测两个生产级项目。"


@dataclass(frozen=True)
class PageSeo:
    title: str
    description: str
    url: str
    image: str = DEFAULT_OG_IMAGE
    og_type: str = "website"


def absolute_url(base_url: str, path: str) -> str:
    return urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))


def build_page_seo(
    request: Request,
    *,
    title: str,
    description: str,
    path: str | None = None,
    og_type: str = "website",
    image: str = DEFAULT_OG_IMAGE,
) -> dict[str, str]:
    page_url = absolute_url(str(request.base_url), path or request.url.path)
    image_url = absolute_url(str(request.base_url), image) if image.startswith("/") else image
    seo = PageSeo(
        title=title,
        description=description,
        url=page_url,
        image=image_url,
        og_type=og_type,
    )
    return {
        "title": seo.title,
        "meta_description": seo.description,
        "canonical_url": seo.url,
        "og_title": seo.title,
        "og_description": seo.description,
        "og_type": seo.og_type,
        "og_url": seo.url,
        "og_image": seo.image,
        "twitter_card": "summary_large_image",
        "twitter_title": seo.title,
        "twitter_description": seo.description,
        "twitter_image": seo.image,
    }


def build_rss_feed(base_url: str, posts: list[BlogPost]) -> str:
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "libaoshuai | AI 与制造数字化"
    SubElement(channel, "link").text = absolute_url(base_url, "/blog")
    SubElement(channel, "description").text = DEFAULT_DESCRIPTION
    SubElement(channel, "language").text = "zh-cn"
    SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))

    for post in posts:
        post_url = absolute_url(base_url, f"/blog/{post.slug}")
        pub_date = datetime.combine(post.published_at, time.min, tzinfo=timezone.utc)
        item = SubElement(channel, "item")
        SubElement(item, "title").text = post.title
        SubElement(item, "link").text = post_url
        SubElement(item, "guid", isPermaLink="true").text = post_url
        SubElement(item, "description").text = post.description
        SubElement(item, "pubDate").text = format_datetime(pub_date)
        SubElement(item, "author").text = post.author
        SubElement(item, "category").text = post.category

    return _xml_document(rss)


def build_sitemap(base_url: str, posts: list[BlogPost], projects: list[Project]) -> str:
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    _add_sitemap_url(urlset, absolute_url(base_url, "/"), priority="1.0")
    _add_sitemap_url(urlset, absolute_url(base_url, "/blog"), priority="0.9")
    _add_sitemap_url(urlset, absolute_url(base_url, "/projects"), priority="0.8")
    _add_sitemap_url(urlset, absolute_url(base_url, "/about"), priority="0.7")
    _add_sitemap_url(urlset, absolute_url(base_url, "/contact"), priority="0.6")

    for post in posts:
        _add_sitemap_url(
            urlset,
            absolute_url(base_url, f"/blog/{post.slug}"),
            lastmod=post.published_at.isoformat(),
            priority="0.7",
        )

    for project in projects:
        _add_sitemap_url(
            urlset,
            absolute_url(base_url, f"/projects/{project.slug}"),
            priority="0.6",
        )

    return _xml_document(urlset)


def build_robots_txt(base_url: str) -> str:
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {absolute_url(base_url, '/sitemap.xml')}",
            "",
        ]
    )


def _add_sitemap_url(
    urlset: Element,
    loc: str,
    *,
    lastmod: str | None = None,
    priority: str,
) -> None:
    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = loc
    if lastmod is not None:
        SubElement(url, "lastmod").text = lastmod
    SubElement(url, "priority").text = priority


def _xml_document(root: Element) -> str:
    rough_xml = ElementTree.tostring(root, encoding="utf-8")
    return minidom.parseString(rough_xml).toprettyxml(indent="  ")
