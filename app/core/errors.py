from __future__ import annotations

from typing import Any, Optional
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def error_envelope(
    status_code: int,
    error_type: str,
    message: str,
    details: Optional[Any] = None,
) -> dict:
    """Builds a standardized error response envelope."""
    body: dict = {
        "error": {
            "status_code": status_code,
            "type": error_type,
            "message": message,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return body


def error_response(
    status_code: int,
    error_type: str,
    message: str,
    details: Optional[Any] = None,
) -> JSONResponse:
    """Returns a JSONResponse with the standard error structure."""
    return JSONResponse(
        status_code=status_code,
        content=error_envelope(status_code, error_type, message, details),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handles standard HTTP exceptions."""
    type_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        500: "internal_server_error",
    }
    error_type = type_map.get(exc.status_code, "http_error")
    logger.warning(f"HTTP {exc.status_code} - {error_type}: {exc.detail}")
    return error_response(
        status_code=exc.status_code,
        error_type=error_type,
        message=str(exc.detail),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles Pydantic validation errors."""
    details = [
        {
            "field": " -> ".join(str(loc) for loc in err["loc"]),
            "issue": err["msg"],
            "input": err.get("input"),
        }
        for err in exc.errors()
    ]
    logger.warning(f"Validation failure on {request.url}: {details}")
    return error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error_type="validation_error",
        message="Request validation failed.",
        details=details,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallthrough handler for unexpected server errors."""
    logger.exception(f"Unhandled exception on {request.url}")
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="internal_server_error",
        message="An internal server error occurred.",
    )
