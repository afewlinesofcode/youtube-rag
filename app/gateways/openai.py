from app.config import get_settings
from langchain_openai import ChatOpenAI

def llm() -> ChatOpenAI:
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    
    return ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key
        )
