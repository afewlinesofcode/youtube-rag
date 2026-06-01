import unittest
from unittest.mock import Mock, patch

from langchain_core.documents import Document

from app.services import qa_service
from app.services.qa_service import _chunk_to_text


class FakePrompt:
    def __init__(self, chain):
        self.chain = chain

    def __or__(self, _model):
        return self.chain


class FakeContextualizeChain:
    def __init__(self):
        self.invocation = None

    def invoke(self, invocation):
        self.invocation = invocation
        return Mock(content="standalone question")


class QaServiceTest(unittest.TestCase):
    def test_chunk_to_text_returns_string_content(self) -> None:
        self.assertEqual(_chunk_to_text("plain text"), "plain text")

    def test_chunk_to_text_joins_list_content(self) -> None:
        content = [
            {"type": "text", "text": "hello "},
            "there",
            {"type": "image_url", "image_url": "ignored"},
            {"type": "text", "text": "!"},
        ]

        self.assertEqual(_chunk_to_text(content), "hello there!")

    def test_chunk_to_text_ignores_unknown_content(self) -> None:
        self.assertEqual(_chunk_to_text({"text": "not a supported chunk"}), "")

    def test_prepare_qa_context_rewrites_question_and_retrieves_matching_docs(self) -> None:
        chain = FakeContextualizeChain()
        model = Mock(name="chat_model")
        retriever = Mock()
        retriever.invoke.return_value = [
            Document(page_content="first chunk"),
            Document(page_content="second chunk"),
        ]

        with (
            patch.object(qa_service, "llm", return_value=model),
            patch.object(qa_service, "retriever_for_id", return_value=retriever) as retriever_for_id,
            patch.object(qa_service, "list_messages", return_value=[{"role": "user", "content": "previous question"}]),
            patch.object(qa_service.ChatPromptTemplate, "from_messages", return_value=FakePrompt(chain)),
        ):
            chat_model, context = qa_service._prepare_qa_context("video-id", "follow up?")

        self.assertIs(chat_model, model)
        self.assertEqual(context, "first chunk\n\nsecond chunk")
        retriever_for_id.assert_called_once_with("video-id", k=5)
        retriever.invoke.assert_called_once_with("standalone question")
        self.assertEqual(chain.invocation["input"], "follow up?")
        self.assertEqual(len(chain.invocation["chat_history"]), 1)


if __name__ == "__main__":
    unittest.main()
