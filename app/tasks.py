from celery import Celery

from app import db
from app.config import get_settings
from app.logger import configure_logging, get_logger
from app.services.process_job_service import process_video_job as run_process_video_job


settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)

celery_app = Celery(
    "youtube_rag",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


@celery_app.task(name="app.tasks.process_video_job")
def process_video_job(job_id: str) -> None:
    logger.info("Starting video process job_id=%s", job_id)
    db.init_pool()

    try:
        run_process_video_job(job_id)
    except Exception as exc:
        logger.exception("Process job failed job_id=%s", job_id, exc_info=exc)
        raise

    logger.info("Process job succeeded job_id=%s", job_id)
