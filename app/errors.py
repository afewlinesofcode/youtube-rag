from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base exception for application-level errors exposed via API."""

    def __init__(self, message: str, *, status_code: int = 500, code: str = "internal_error") -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


class BadRequestError(AppError):
    def __init__(self, message: str, *, code: str = "bad_request") -> None:
        super().__init__(message, status_code=400, code=code)


class NotFoundError(AppError):
    def __init__(self, message: str, *, code: str = "not_found") -> None:
        super().__init__(message, status_code=404, code=code)


class InternalServerError(AppError):
    def __init__(self, message: str = "Internal server error", *, code: str = "internal_error") -> None:
        super().__init__(message, status_code=500, code=code)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("Application error: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error_code": exc.code},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error_code": "internal_error"},
        )
