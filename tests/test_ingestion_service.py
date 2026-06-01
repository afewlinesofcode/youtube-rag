import unittest
from unittest.mock import patch

from langchain_core.documents import Document
from psycopg.errors import UniqueViolation

from app.services import ingestion_service


class IngestionServiceTest(unittest.TestCase):
    def test_ingestion_cleans_vectors_and_returns_existing_video_after_duplicate_insert(self) -> None:
        existing_video = {"id": "existing-video-id"}
        video_lookup_results = iter([None, existing_video])
        added_ids: list[str] = []
        deleted_ids: list[str] = []

        def raise_duplicate(*args) -> None:
            raise UniqueViolation("duplicate video")

        with (
            patch.object(
                ingestion_service,
                "get_video_by_youtube_video_id",
                side_effect=lambda _: next(video_lookup_results),
            ),
            patch.object(
                ingestion_service,
                "load_documents",
                return_value=([Document(page_content="A transcript about RAG.")], "youtube_transcript"),
            ),
            patch.object(ingestion_service, "summarize_video", return_value=("Title", "Topic")),
            patch.object(ingestion_service, "add_documents", side_effect=lambda _, ids: added_ids.extend(ids)),
            patch.object(ingestion_service, "delete_documents", side_effect=lambda ids: deleted_ids.extend(ids)),
            patch.object(ingestion_service, "create_video", side_effect=raise_duplicate),
        ):
            video = ingestion_service.ingest_youtube_video("https://youtu.be/youtube-id", "youtube-id")

        self.assertEqual(video, existing_video)
        self.assertTrue(added_ids)
        self.assertEqual(deleted_ids, added_ids)


if __name__ == "__main__":
    unittest.main()
