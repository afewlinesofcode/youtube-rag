from app.errors import NotFoundError
from app.logger import get_logger
from app.repositories.process_job_repository import (
    create_process_job,
    get_active_process_job,
    get_process_job,
)
from app.repositories.video_repository import get_video, list_videos as list_videos_repo
from app.repositories.messages_repository import list_messages
from app.tasks import process_video_job


logger = get_logger(__name__)


def list_videos() -> list[dict]:
    return list_videos_repo()


def create_video_process_job(youtube_url: str) -> dict:
    active_job = get_active_process_job()
    if active_job is not None:
        raise ValueError(
            "A video processing job is already running. Please wait for it to finish before starting a new one."
        )

    job = create_process_job(youtube_url)
    process_video_job.delay(job["id"])
    logger.info("Queued video processing job_id=%s", job["id"])
    return job


def get_video_process_job(job_id: str) -> dict:
    job = get_process_job(job_id)
    if job is None:
        raise NotFoundError("Process job not found", code="process_job_not_found")
    return job


def get_active_video_process_job() -> dict | None:
    return get_active_process_job()


def list_video_messages(document_id: str) -> list[dict]:
    if get_video(document_id) is None:
        raise NotFoundError("Video not found", code="video_not_found")
    return list_messages(document_id)
