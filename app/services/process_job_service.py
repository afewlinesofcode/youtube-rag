from app.logger import get_logger
from app.repositories.process_job_repository import (
    get_process_job,
    mark_process_job_running,
    mark_process_job_succeeded,
)
from app.gateways.youtube.url import extract_youtube_video_id
from app.services.ingestion_service import ingest_youtube_video


logger = get_logger(__name__)


def process_video_job(job_id: str) -> dict | None:
    job = get_process_job(job_id)
    if job is None:
        logger.warning("Process job not found job_id=%s", job_id)
        return None

    if job["status"] in {"succeeded", "failed"}:
        logger.info("Skipping terminal process job job_id=%s status=%s", job_id, job["status"])
        return job

    running_job = mark_process_job_running(job_id)
    if running_job is None:
        logger.info("Process job was not runnable job_id=%s", job_id)
        return get_process_job(job_id)

    youtube_video_id = running_job.get("youtube_video_id") or extract_youtube_video_id(running_job["youtube_url"])
    video = ingest_youtube_video(running_job["youtube_url"], youtube_video_id)
    mark_process_job_succeeded(job_id, video["id"])
    return get_process_job(job_id)
