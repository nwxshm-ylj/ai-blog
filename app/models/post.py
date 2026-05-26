from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, Table, Text, false
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


post_tags = Table(
    "post_tags",
    Base.metadata,
    Column(
        "post_id",
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Post(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "posts"
    __table_args__ = (
        Index("ix_posts_author_id", "author_id"),
        Index("ix_posts_category_id", "category_id"),
        Index("ix_posts_is_published", "is_published"),
        Index("ix_posts_created_at", "created_at"),
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    seo_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seo_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
        nullable=False,
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    author: Mapped["User"] = relationship(back_populates="posts")
    category: Mapped[Optional["Category"]] = relationship(back_populates="posts")
    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts",
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )
