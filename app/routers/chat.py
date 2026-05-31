import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.errors import InternalServerError, NotFoundError
from app.logger import get_logger
from app.schemas.chat import ChatRequest
from app.services.chat_service import generate_chat_answer, stream_chat_answer


router = APIRouter(tags=["chat"])
logger = get_logger(__name__)


@router.post("/api/chat")
async def chat(payload: ChatRequest) -> dict:
    try:
        answer = await generate_chat_answer(payload.document_id, payload.question)
    except NotFoundError:
        raise
    except Exception as exc:
        logger.exception("Could not answer question", exc_info=exc)
        raise InternalServerError("Could not answer question", code="chat_answer_failed") from exc
    return {"answer": answer}


@router.post("/api/chat/stream")
def chat_stream(payload: ChatRequest) -> StreamingResponse:
    try:
        stream = stream_chat_answer(payload.document_id, payload.question)
    except NotFoundError:
        raise
    except Exception as exc:
        logger.exception("Could not start chat stream", exc_info=exc)
        raise InternalServerError("Could not answer question", code="chat_answer_failed") from exc

    def event_stream():
        try:
            for token in stream:
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as exc:
            logger.exception("Chat stream failed", exc_info=exc)
            yield f"data: {json.dumps({'type': 'error', 'detail': 'Could not answer question.'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
