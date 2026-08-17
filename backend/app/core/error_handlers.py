import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.schemas.api import ErrorResponse


logger = logging.getLogger(__name__)


def app_error_handler(request: Request, error: AppError) -> JSONResponse:
    """Log internal failure detail without exposing it in the API response."""
    logger.error("Application error on %s: %s", request.url.path, error.message)
    return JSONResponse(
        status_code=error.status_code,
        content=ErrorResponse(detail=error.public_message).model_dump(),
    )
