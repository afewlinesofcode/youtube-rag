from fastapi import APIRouter

from app.errors import BadRequestError, InternalServerError
from app.logger import get_logger
from app.schemas.video import ProcessVideoRequest
from app.services.video_service import (
    create_video_process_job,
    get_active_video_process_job,
    get_video_process_job,
    list_video_messages,
    list_videos,
)


router = APIRouter(tags=["videos"])
logger = get_logger(__name__)


@router.get("/api/videos")
def videos() -> list[dict]:
    return list_videos()


@router.post("/api/videos/process", status_code=202)
async def process_video(payload: ProcessVideoRequest) -> dict:
    try:
        return create_video_process_job(str(payload.youtube_url))
    except ValueError as exc:
        raise BadRequestError(str(exc), code="video_process_invalid_request") from exc
    except Exception as exc:
        logger.exception("Could not process video", exc_info=exc)
        raise InternalServerError("Could not process video", code="video_process_failed") from exc


@router.get("/api/videos/process/active")
def active_process_video_job() -> dict | None:
    return get_active_video_process_job()


@router.get("/api/videos/process/{job_id}")
def process_video_status(job_id: str) -> dict:
    return get_video_process_job(job_id)


@router.get("/api/videos/{document_id}/messages")
def messages(document_id: str) -> list[dict]:
    return list_video_messages(document_id)
