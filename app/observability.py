"""Observability helpers (logging, Sentry)."""
import logging
from typing import Optional

import sentry_sdk

logger = logging.getLogger("ai-imutis")


def init_sentry(dsn: Optional[str], environment: str, release: str) -> None:
    """Initialize Sentry if DSN is provided."""

    if not dsn:
        logger.info("Sentry DSN not set; skipping Sentry init")
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        traces_sample_rate=0.1,
    )
    logger.info("Sentry initialized")
