from __future__ import annotations

import logging
from contextvars import ContextVar, Token


request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def bind_request_id(request_id: str) -> Token:
    return request_id_var.set(request_id)


def reset_request_id(token: Token) -> None:
    request_id_var.reset(token)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    if getattr(root, "_youtube_rag_logging_configured", False):
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] [request_id=%(request_id)s] %(message)s"
        )
    )
    handler.addFilter(RequestContextFilter())

    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    root._youtube_rag_logging_configured = True
