from typing import Iterator

from app.repositories.messages_repository import add_message, list_messages
from app.gateways.openai import llm
from app.gateways.rag import retriever_for_id
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def answer_question(video_id: str, question: str) -> str:
    chat_model, context = _prepare_qa_context(video_id, question)
    qa_chain = _qa_prompt() | chat_model
    result = qa_chain.invoke({"input": question, "context": context})
    answer = str(result.content).strip()

    _persist_chat_messages(video_id, question, answer)

    return answer


def stream_answer_question(video_id: str, question: str) -> Iterator[str]:
    chat_model, context = _prepare_qa_context(video_id, question)
    qa_chain = _qa_prompt() | chat_model

    answer_parts: list[str] = []
    for chunk in qa_chain.stream({"input": question, "context": context}):
        text = _chunk_to_text(chunk.content)
        if not text:
            continue
        answer_parts.append(text)
        yield text

    answer = "".join(answer_parts).strip()
    if not answer:
        raise RuntimeError("Received empty answer from model.")

    _persist_chat_messages(video_id, question, answer)


def _prepare_qa_context(video_id: str, question: str) -> tuple:
    retriever = retriever_for_id(video_id, k=5)
    chat_model = llm()
    chat_history = _history_for_chain(video_id)

    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Rewrite the latest user question as a standalone question using the chat history. "
                "Do not answer it.",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    contextualize_chain = contextualize_prompt | chat_model
    contextualized_result = contextualize_chain.invoke({"input": question, "chat_history": chat_history})

    standalone_question = str(contextualized_result.content).strip()
    docs = retriever.invoke(standalone_question)
    return chat_model, _format_docs(docs)


def _qa_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer using only the retrieved transcript context. "
                "If the answer is not in the transcript, say that the video does not cover it.\n\n"
                "Context:\n{context}",
            ),
            ("human", "{input}"),
        ]
    )


def _persist_chat_messages(video_id: str, question: str, answer: str) -> None:
    add_message(video_id, "user", question)
    add_message(video_id, "assistant", answer)


def _chunk_to_text(content: object) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)

    return ""


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def _history_for_chain(video_id: str) -> list[HumanMessage | AIMessage]:
    history: list[HumanMessage | AIMessage] = []
    for message in list_messages(video_id):
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            history.append(AIMessage(content=message["content"]))
    return history