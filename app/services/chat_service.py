from fastapi.concurrency import run_in_threadpool

from app.errors import NotFoundError
from app.repositories.video_repository import get_video
from app.services.qa_service import answer_question, stream_answer_question


async def generate_chat_answer(document_id: str, question: str) -> str:
    if get_video(document_id) is None:
        raise NotFoundError("Video not found", code="video_not_found")

    return await run_in_threadpool(
        answer_question,
        document_id,
        question.strip(),
    )


def stream_chat_answer(document_id: str, question: str):
    if get_video(document_id) is None:
        raise NotFoundError("Video not found", code="video_not_found")

    return stream_answer_question(document_id, question.strip())
