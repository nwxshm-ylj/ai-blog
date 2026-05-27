"""add project case study fields

Revision ID: 0004_project_case_study
Revises: 0003_add_comments
Create Date: 2026-05-27 00:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_project_case_study"
down_revision: str | None = "0003_add_comments"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column(
        "projects",
        sa.Column("category", sa.String(length=120), server_default="AI 项目", nullable=False),
    )
    op.add_column(
        "projects",
        sa.Column("status", sa.String(length=80), server_default="已发布", nullable=False),
    )
    op.add_column("projects", sa.Column("impact", sa.Text(), nullable=True))
    op.add_column(
        "projects",
        sa.Column(
            "highlights",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.create_index("ix_projects_category", "projects", ["category"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_projects_category", table_name="projects")
    op.drop_column("projects", "highlights")
    op.drop_column("projects", "impact")
    op.drop_column("projects", "status")
    op.drop_column("projects", "category")
    op.drop_column("projects", "summary")
