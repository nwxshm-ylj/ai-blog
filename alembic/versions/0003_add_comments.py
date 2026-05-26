"""add comments

Revision ID: 0003_add_comments
Revises: 0002_add_project_view_count
Create Date: 2026-05-26 22:45:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003_add_comments"
down_revision: str | None = "0002_add_project_view_count"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_approved", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_created_at", "comments", ["created_at"], unique=False)
    op.create_index("ix_comments_is_approved", "comments", ["is_approved"], unique=False)
    op.create_index("ix_comments_post_id", "comments", ["post_id"], unique=False)
    op.create_index("ix_comments_user_id", "comments", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_comments_user_id", table_name="comments")
    op.drop_index("ix_comments_post_id", table_name="comments")
    op.drop_index("ix_comments_is_approved", table_name="comments")
    op.drop_index("ix_comments_created_at", table_name="comments")
    op.drop_table("comments")
