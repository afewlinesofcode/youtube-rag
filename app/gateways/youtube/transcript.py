from langchain_core.documents import Document
from youtube_transcript_api import YouTubeTranscriptApi

from app.gateways.youtube.url import extract_youtube_video_id


def load_docs(youtube_url: str) -> list[Document]:
    video_id = extract_youtube_video_id(youtube_url)

    transcript_list = YouTubeTranscriptApi().list(video_id)
    transcripts = next(iter(transcript_list))
    transcript = transcripts.fetch()

    text = "\n".join(item.text for item in transcript)

    return [
        Document(
            page_content=text,
            metadata={
                "source": youtube_url,
                "video_id": video_id,
                "language": transcript.language_code,
            },
        )
    ]
