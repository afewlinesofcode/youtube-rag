"""Compatibility wrappers over db infrastructure and repository modules.

Prefer importing from app.db_infra and app.repositories.* in new code.
"""

from app.db_infra import close_pool, get_conn, init_db, init_pool
from app.repositories.messages_repository import add_message, list_messages
from app.repositories.process_job_repository import (
    create_process_job,
    get_active_process_job,
    get_process_job,
    mark_process_job_failed,
    mark_process_job_running,
    mark_process_job_succeeded,
)
from app.repositories.video_repository import create_video, get_video, list_videos


__all__ = [
    "init_pool",
    "close_pool",
    "get_conn",
    "init_db",
    "list_videos",
    "get_video",
    "create_video",
    "list_messages",
    "add_message",
    "create_process_job",
    "get_active_process_job",
    "get_process_job",
    "mark_process_job_running",
    "mark_process_job_succeeded",
    "mark_process_job_failed",
]
