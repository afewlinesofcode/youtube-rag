"""video ingestion idempotency

Revision ID: 20260531_0002
Revises: 20260531_0001
Create Date: 2026-05-31 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260531_0002"
down_revision: Union[str, None] = "20260531_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("videos", sa.Column("youtube_video_id", sa.Text(), nullable=True))
    op.add_column("process_jobs", sa.Column("youtube_video_id", sa.Text(), nullable=True))

    op.create_index("ix_videos_youtube_video_id", "videos", ["youtube_video_id"])
    op.create_index(
        "uq_videos_youtube_video_id",
        "videos",
        ["youtube_video_id"],
        unique=True,
        postgresql_where=sa.text("youtube_video_id IS NOT NULL"),
    )
    op.create_index(
        "ix_process_jobs_youtube_video_id_updated_at",
        "process_jobs",
        ["youtube_video_id", sa.text("updated_at DESC")],
    )
    op.create_index(
        "uq_process_jobs_active_youtube_video_id",
        "process_jobs",
        ["youtube_video_id"],
        unique=True,
        postgresql_where=sa.text("youtube_video_id IS NOT NULL AND status IN ('queued', 'running')"),
    )


def downgrade() -> None:
    op.drop_index("uq_process_jobs_active_youtube_video_id", table_name="process_jobs")
    op.drop_index("ix_process_jobs_youtube_video_id_updated_at", table_name="process_jobs")
    op.drop_index("uq_videos_youtube_video_id", table_name="videos")
    op.drop_index("ix_videos_youtube_video_id", table_name="videos")
    op.drop_column("process_jobs", "youtube_video_id")
    op.drop_column("videos", "youtube_video_id")
