"""add project view count

Revision ID: 0002_add_project_view_count
Revises: 0001_initial_database
Create Date: 2026-05-24 23:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_project_view_count"
down_revision: str | None = "0001_initial_database"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("view_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("projects", "view_count")
