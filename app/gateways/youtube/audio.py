from pathlib import Path
from app.logger import get_logger
from app.config import get_settings
import yt_dlp
from langchain_core.documents import Document
from faster_whisper import WhisperModel

logger = get_logger(__name__)

def load_docs(youtube_url: str) -> list[Document]:
    settings = get_settings()
    audio_path, video_id = _download_audio(youtube_url)

    model = WhisperModel(
        settings.whisper_model,
        device="cpu",
        compute_type="int8",
    )

    try:
        segments, info = model.transcribe(
            str(audio_path),
            beam_size=5,
        )
    except Exception as e:
        logger.error(f"Failed to transcribe audio for {youtube_url}: {e}")
        raise
    finally:
        if audio_path.exists():
            audio_path.unlink()

    text = "\n".join(segment.text for segment in segments)

    return [
        Document(
            page_content=text,
            metadata={
                "source": youtube_url,
                "video_id": video_id,
                "language": info.language,
            },
        )
    ]

def _download_audio(youtube_url: str) -> tuple[Path, str]:
    try:
      settings = get_settings()
      base_dir = Path(settings.audio_download_dir)
      base_dir.mkdir(parents=True, exist_ok=True)
      
      ydl_opts = {
          "format": "m4a/bestaudio/best",
          "outtmpl": str(base_dir / "%(id)s.%(ext)s"),
          "postprocessors": [
              {
                  "key": "FFmpegExtractAudio",
                  "preferredcodec": "m4a",
              }
          ],
          "quiet": True,
          "no_warnings": True,
      }

      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
          info = ydl.extract_info(youtube_url, download=True)
      
      video_id = info["id"]
      return base_dir / f"{video_id}.m4a", video_id
    except Exception as e:
        logger.error(f"Failed to download audio for {youtube_url}: {e}")
        raise