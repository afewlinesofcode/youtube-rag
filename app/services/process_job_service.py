from app.logger import get_logger
from app.repositories.process_job_repository import (
    get_process_job,
    mark_process_job_failed,
    mark_process_job_running,
    mark_process_job_succeeded,
)
from app.services.ingestion_service import ingest_youtube_video


logger = get_logger(__name__)


def process_video_job(job_id: str) -> None:
    job = get_process_job(job_id)
    if job is None:
        logger.warning("Process job not found job_id=%s", job_id)
        return

    mark_process_job_running(job_id)
    try:
        video = ingest_youtube_video(job["youtube_url"])
    except Exception as exc:
        mark_process_job_failed(job_id, str(exc))
        raise
    else:
        mark_process_job_succeeded(job_id, video["id"])
