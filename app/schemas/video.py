from pydantic import BaseModel, HttpUrl


class ProcessVideoRequest(BaseModel):
    youtube_url: HttpUrl
