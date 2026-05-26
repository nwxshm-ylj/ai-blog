from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from time import monotonic
from typing import TypeVar

from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

T = TypeVar("T")

_OPTIONAL_DB_TIMEOUT_SECONDS = 0.35
_OPTIONAL_DB_RETRY_INTERVAL_SECONDS = 30.0
_optional_db_retry_at = 0.0


async def run_optional_db_operation(operation: Callable[[], Awaitable[T]], fallback: T) -> T:
    global _optional_db_retry_at

    now = monotonic()
    if now < _optional_db_retry_at:
        return fallback

    try:
        return await asyncio.wait_for(operation(), timeout=_OPTIONAL_DB_TIMEOUT_SECONDS)
    except (asyncio.TimeoutError, TimeoutError, OSError, SQLAlchemyError) as exc:
        _optional_db_retry_at = monotonic() + _OPTIONAL_DB_RETRY_INTERVAL_SECONDS
        logger.warning(
            "Optional public database operation failed; skipping optional DB reads for %.0f seconds: %s",
            _OPTIONAL_DB_RETRY_INTERVAL_SECONDS,
            exc,
        )
        return fallback
