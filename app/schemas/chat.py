from typing import Annotated

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    document_id: str
    question: Annotated[str, Field(min_length=1, max_length=4000)]
