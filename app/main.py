import uuid

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app import db
from app.errors import register_exception_handlers
from app.logger import bind_request_id, configure_logging, get_logger, reset_request_id
from app.routers import chat_router, videos_router


logger = get_logger(__name__)
app = FastAPI(title="YouTube RAG")
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(videos_router)
app.include_router(chat_router)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    token = bind_request_id(request_id)
    try:
        response = await call_next(request)
    finally:
        reset_request_id(token)
    response.headers["x-request-id"] = request_id
    return response


@app.on_event("startup")
def startup() -> None:
    configure_logging(get_settings().log_level)
    logger.info("Initializing application")
    db.init_pool()


@app.on_event("shutdown")
def shutdown() -> None:
    logger.info("Shutting down application")
    db.close_pool()


@app.get("/")
def index() -> FileResponse:
    return FileResponse("static/index.html")
