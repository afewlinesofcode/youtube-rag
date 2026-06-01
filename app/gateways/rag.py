from app.gateways.openai import llm
from app.config import get_settings
from app.logger import get_logger
from app.gateways.youtube.transcript import load_docs as _load_transcript_docs
from app.gateways.youtube.audio import load_docs as _load_audio_docs
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector


class VideoMetadata(BaseModel):
    title: str = Field(description="Concise title for the video")
    topic: str = Field(description="Main topic of the video")

COLLECTION_NAME = "youtube_transcripts"

logger = get_logger(__name__)


def summarize_video(transcript: str) -> tuple[str, str]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Create concise metadata for a YouTube transcript. ",
            ),
            ("human", "{transcript}"),
        ]
    )
    clipped = transcript[:12000]

    struct_llm = llm().with_structured_output(
        VideoMetadata, method="json_schema")

    response: VideoMetadata = (prompt | struct_llm).invoke({"transcript": clipped})
    
    title = str(response.title).strip() or "Untitled video"
    topic = str(response.topic).strip() or title

    return title[:180], topic[:240]


def load_documents(youtube_url: str) -> tuple[list, str]:
    settings = get_settings()

    try:
        documents = _load_transcript_docs(youtube_url)
    except Exception:
        logger.exception("Failed to load YouTube transcript for URL: %s", youtube_url)
        documents = []

    if documents:
        return documents, "youtube_transcript"

    if not settings.enable_audio_fallback:
        raise ValueError("No transcript was found for this YouTube URL.")

    try:
        logger.info("Attempting to transcribe audio for YouTube URL: %s", youtube_url)
        documents = _load_audio_docs(youtube_url)
    except Exception:
        logger.exception("Failed to load YouTube audio for URL: %s", youtube_url)
        documents = []

    if not documents:
        raise ValueError("Could not transcribe audio for this YouTube URL.")
    return documents, "audio_transcription"


def add_documents(documents: list, ids: list) -> None:
    _vector_store().add_documents(documents, ids=ids)


def delete_documents(ids: list[str]) -> None:
    if ids:
        _vector_store().delete(ids=ids)


def retriever_for_id(id: str, k: int = 5) -> PGVector:
    return _vector_store().as_retriever(search_kwargs={"k": k, "filter": {"document_id": id}})


def _vector_store() -> PGVector:
    settings = get_settings()
    return PGVector(
        embeddings=_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=settings.pgvector_connection_url,
        use_jsonb=True,
    )


def _embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    return OpenAIEmbeddings(model=settings.openai_embedding_model, api_key=settings.openai_api_key)
