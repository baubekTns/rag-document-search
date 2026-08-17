import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.schemas.api import ErrorResponse
from app.core.logging import log_error_event


logger = logging.getLogger(__name__)


def app_error_handler(request: Request, error: AppError) -> JSONResponse:
    """Log internal failure detail without exposing it in the API response."""
    log_error_event(logger, "application_error", path=request.url.path, status_code=error.status_code, error_type=type(error).__name__)
    return JSONResponse(
        status_code=error.status_code,
        content=ErrorResponse(detail=error.public_message).model_dump(),
    )
