import unittest
from unittest.mock import patch

from app.errors import NotFoundError
from app.services import chat_service


class ChatServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_generate_chat_answer_rejects_unknown_video(self) -> None:
        with patch.object(chat_service, "get_video", return_value=None):
            with self.assertRaises(NotFoundError):
                await chat_service.generate_chat_answer("missing-video", "question")

    async def test_generate_chat_answer_delegates_for_existing_video(self) -> None:
        with (
            patch.object(chat_service, "get_video", return_value={"id": "video-id"}),
            patch.object(chat_service, "answer_question", return_value="answer") as answer_question,
        ):
            answer = await chat_service.generate_chat_answer("video-id", "  question  ")

        self.assertEqual(answer, "answer")
        answer_question.assert_called_once_with("video-id", "question")

    def test_stream_chat_answer_rejects_unknown_video(self) -> None:
        with patch.object(chat_service, "get_video", return_value=None):
            with self.assertRaises(NotFoundError):
                chat_service.stream_chat_answer("missing-video", "question")

    def test_stream_chat_answer_delegates_for_existing_video(self) -> None:
        stream = iter(["answer"])
        with (
            patch.object(chat_service, "get_video", return_value={"id": "video-id"}),
            patch.object(chat_service, "stream_answer_question", return_value=stream) as stream_answer_question,
        ):
            result = chat_service.stream_chat_answer("video-id", "  question  ")

        self.assertIs(result, stream)
        stream_answer_question.assert_called_once_with("video-id", "question")


if __name__ == "__main__":
    unittest.main()
