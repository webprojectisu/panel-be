"""
Global exception handlers registered on the FastAPI application.

All handlers return a uniform JSON envelope:
{
    "error":       "<ERROR_CODE>",
    "message":     "<human readable detail>",
    "status_code": <int>
}
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def _error_response(status_code: int, error_code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_code,
            "message": message,
            "status_code": status_code,
        },
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all AppException subclasses."""
    return _error_response(exc.status_code, exc.error_code, exc.detail)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic v2 request validation errors with field-level detail."""
    field_errors: list[dict] = []
    for error in exc.errors():
        loc = " -> ".join(str(part) for part in error.get("loc", []) if part != "body")
        field_errors.append(
            {
                "field": loc or "root",
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "value_error"),
            }
        )

    message = "; ".join(
        f"{e['field']}: {e['message']}" for e in field_errors
    ) if field_errors else "Request validation failed."

    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": message,
            "status_code": 422,
            "details": field_errors,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler — hides internal details from the client."""
    logger.exception("Unhandled exception for %s %s", request.method, request.url)
    return _error_response(500, "INTERNAL_ERROR", "An unexpected internal error occurred.")


def register_error_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI instance."""
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)
