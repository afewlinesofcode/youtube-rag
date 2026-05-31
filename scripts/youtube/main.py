from urllib.parse import urlparse, parse_qs
from langchain_core.documents import Document
from youtube_transcript_api import YouTubeTranscriptApi

youtube_url = "https://www.youtube.com/watch?v=g6H_mdz4fOg"


def extract_youtube_video_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.hostname in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")

    if parsed.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query)["v"][0]

        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]

        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2]

    raise ValueError(f"Unsupported YouTube URL: {url}")


def load_youtube_transcript(youtube_url: str, languages: list[str] = ["en"]) -> list[Document]:
    video_id = extract_youtube_video_id(youtube_url)

    transcript = YouTubeTranscriptApi().fetch(
        video_id,
        languages=languages,
    )

    text = " ".join(item.text for item in transcript)

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


docs = load_youtube_transcript(youtube_url)
print(docs[0].page_content)