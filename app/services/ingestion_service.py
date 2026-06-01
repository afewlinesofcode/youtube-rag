import uuid

from psycopg.errors import UniqueViolation

from app.config import get_settings
from app.gateways.rag import add_documents, delete_documents, load_documents, summarize_video
from app.logger import get_logger
from app.repositories.video_repository import create_video, get_video_by_youtube_video_id
from langchain_text_splitters import RecursiveCharacterTextSplitter


logger = get_logger(__name__)


def ingest_youtube_video(youtube_url: str, youtube_video_id: str) -> dict:
    existing_video = get_video_by_youtube_video_id(youtube_video_id)
    if existing_video is not None:
        return existing_video

    document_id = str(uuid.uuid4())
    documents, transcript_source = load_documents(youtube_url)

    transcript = "\n\n".join(doc.page_content for doc in documents)
    title, topic = summarize_video(transcript)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=get_settings().chunk_size,
        chunk_overlap=get_settings().chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata = {
            **chunk.metadata,
            "document_id": document_id,
            "youtube_video_id": youtube_video_id,
            "youtube_url": youtube_url,
            "title": title,
            "topic": topic,
            "chunk_index": index,
            "transcript_source": transcript_source,
        }

    ids = [f"{document_id}:{index}" for index in range(len(chunks))]
    add_documents(chunks, ids=ids)

    try:
        return create_video(document_id, youtube_url, youtube_video_id, title, topic)
    except UniqueViolation:
        _delete_written_vectors(ids)
        existing_video = get_video_by_youtube_video_id(youtube_video_id)
        if existing_video is not None:
            return existing_video
        raise
    except Exception:
        _delete_written_vectors(ids)
        raise


def _delete_written_vectors(ids: list[str]) -> None:
    try:
        delete_documents(ids)
        logger.info("Deleted vector documents after failed ingestion ids=%s", ids)
    except Exception:
        logger.exception("Failed to delete vector documents after failed ingestion ids=%s", ids)
