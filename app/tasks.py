from celery import Celery

from app import db
from app.config import get_settings
from app.logger import configure_logging, get_logger
from app.repositories.process_job_repository import (
    DEFAULT_MAX_ATTEMPTS,
    get_process_job,
    mark_process_job_failed,
    mark_process_job_retryable_failure,
)
from app.services.process_job_service import process_video_job as run_process_video_job


settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)

celery_app = Celery(
    "youtube_rag",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


def _retry_countdown(attempt_count: int) -> int:
    return min(300, 10 * (2 ** max(attempt_count - 1, 0)))


def _error_message(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__


@celery_app.task(name="app.tasks.process_video_job", bind=True, max_retries=DEFAULT_MAX_ATTEMPTS - 1)
def process_video_job(self, job_id: str) -> None:
    logger.info("Starting video process job_id=%s", job_id)
    db.init_pool()

    job = get_process_job(job_id)

    if job is None:
        logger.warning("Process job not found job_id=%s", job_id)
        return

    if job["status"] in {"succeeded", "failed"}:
        logger.info("Skipping terminal process job job_id=%s status=%s", job_id, job["status"])
        return

    try:
        run_process_video_job(job_id)
    except Exception as exc:
        error = _error_message(exc)
        latest_job = get_process_job(job_id)
        attempt_count = int((latest_job or {}).get("attempt_count") or 0)
        max_attempts = int((latest_job or {}).get("max_attempts") or DEFAULT_MAX_ATTEMPTS)

        if attempt_count >= max_attempts or isinstance(exc, ValueError):
            failure_reason = "permanent_error" if isinstance(exc, ValueError) else "transient_error"
            mark_process_job_failed(job_id, error, failure_reason=failure_reason)
            logger.exception("Process job failed job_id=%s", job_id)
            raise

        mark_process_job_retryable_failure(job_id, error)
        countdown = _retry_countdown(attempt_count)

        logger.warning(
            "Retrying process job job_id=%s attempt=%s max_attempts=%s countdown=%s",
            job_id,
            attempt_count,
            max_attempts,
            countdown,
        )
        raise self.retry(exc=exc, countdown=countdown)

    except BaseException as exc:
        logger.exception("Process job failed job_id=%s", job_id)
        raise

    logger.info("Process job succeeded job_id=%s", job_id)
