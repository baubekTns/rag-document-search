"""Structured, redacted application logging with request correlation."""

from contextvars import ContextVar
import json
import logging
from typing import Any


request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


def _payload(event: str, fields: dict[str, Any]) -> str:
    return json.dumps(
        {"event": event, "request_id": request_id_context.get(), **fields},
        sort_keys=True,
        default=str,
    )


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.info(_payload(event, fields))


def log_error_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.error(_payload(event, fields))
