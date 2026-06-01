"""process job lifecycle

Revision ID: 20260601_0003
Revises: 20260531_0002
Create Date: 2026-06-01 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260601_0003"
down_revision: Union[str, None] = "20260531_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("process_jobs", sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("process_jobs", sa.Column("max_attempts", sa.Integer(), server_default="3", nullable=False))
    op.add_column("process_jobs", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("process_jobs", sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("process_jobs", sa.Column("last_error", sa.Text(), nullable=True))
    op.add_column("process_jobs", sa.Column("failure_reason", sa.Text(), nullable=True))

    op.create_index("ix_process_jobs_status_started_at", "process_jobs", ["status", "started_at"])


def downgrade() -> None:
    op.drop_index("ix_process_jobs_status_started_at", table_name="process_jobs")
    op.drop_column("process_jobs", "failure_reason")
    op.drop_column("process_jobs", "last_error")
    op.drop_column("process_jobs", "finished_at")
    op.drop_column("process_jobs", "started_at")
    op.drop_column("process_jobs", "max_attempts")
    op.drop_column("process_jobs", "attempt_count")
