import unittest
from unittest.mock import Mock, patch

from langchain_core.documents import Document

from app.gateways import rag


class RagGatewayTest(unittest.TestCase):
    def test_retriever_for_id_scopes_search_to_document_id(self) -> None:
        vector_store = Mock()
        retriever = Mock()
        vector_store.as_retriever.return_value = retriever

        with patch.object(rag, "_vector_store", return_value=vector_store):
            result = rag.retriever_for_id("video-id")

        self.assertIs(result, retriever)
        vector_store.as_retriever.assert_called_once_with(
            search_kwargs={"k": 5, "filter": {"document_id": "video-id"}}
        )

    def test_load_documents_returns_transcript_docs_when_available(self) -> None:
        docs = [Document(page_content="transcript")]

        with (
            patch.object(rag, "_load_transcript_docs", return_value=docs) as load_transcript,
            patch.object(rag, "_load_audio_docs") as load_audio,
        ):
            result, source = rag.load_documents("https://youtu.be/video-id")

        self.assertEqual(result, docs)
        self.assertEqual(source, "youtube_transcript")
        load_transcript.assert_called_once_with("https://youtu.be/video-id")
        load_audio.assert_not_called()

    def test_load_documents_falls_back_to_audio_when_transcript_fails(self) -> None:
        docs = [Document(page_content="audio transcript")]

        with (
            patch.object(rag, "_load_transcript_docs", side_effect=RuntimeError("no transcript")),
            patch.object(rag, "_load_audio_docs", return_value=docs) as load_audio,
            patch.object(rag, "get_settings", return_value=Mock(enable_audio_fallback=True)),
            patch.object(rag, "logger"),
        ):
            result, source = rag.load_documents("https://youtu.be/video-id")

        self.assertEqual(result, docs)
        self.assertEqual(source, "audio_transcription")
        load_audio.assert_called_once_with("https://youtu.be/video-id")

    def test_load_documents_raises_when_all_sources_fail(self) -> None:
        with (
            patch.object(rag, "_load_transcript_docs", side_effect=RuntimeError("no transcript")),
            patch.object(rag, "_load_audio_docs", side_effect=RuntimeError("no audio")),
            patch.object(rag, "get_settings", return_value=Mock(enable_audio_fallback=True)),
            patch.object(rag, "logger"),
        ):
            with self.assertRaisesRegex(ValueError, "Could not transcribe audio"):
                rag.load_documents("https://youtu.be/video-id")


if __name__ == "__main__":
    unittest.main()
