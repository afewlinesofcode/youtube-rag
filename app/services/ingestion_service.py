import uuid
from app.config import get_settings
from app.repositories.video_repository import create_video
from app.gateways.rag import add_documents, load_documents, summarize_video
from langchain_text_splitters import RecursiveCharacterTextSplitter


def ingest_youtube_video(youtube_url: str) -> dict:
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
            "youtube_url": youtube_url,
            "title": title,
            "topic": topic,
            "chunk_index": index,
            "transcript_source": transcript_source,
        }

    ids = [f"{document_id}:{index}" for index in range(len(chunks))]
    add_documents(chunks, ids=ids)
    return create_video(document_id, youtube_url, title, topic)
