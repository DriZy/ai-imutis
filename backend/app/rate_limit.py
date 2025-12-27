"""Simple in-memory rate limiting (suitable for local development)."""
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, Dict
import asyncio

from fastapi import HTTPException, status


class RateLimiter:
    """Lightweight sliding-window rate limiter.

    For production, replace with a Redis-backed implementation to ensure accuracy
    across multiple processes/replicas.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._requests: Dict[str, Deque[datetime]] = defaultdict(deque)

    async def check(self, identifier: str, limit: int, window_seconds: int) -> None:
        """Validate whether the identifier is within the allowed rate."""

        async with self._lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)
            records = self._requests[identifier]

            # Drop records outside of the window
            while records and records[0] < window_start:
                records.popleft()

            if len(records) >= limit:
                retry_after = (records[0] + timedelta(seconds=window_seconds) - now).total_seconds()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Try again later.",
                    headers={"Retry-After": str(int(max(retry_after, 1)))},
                )

            records.append(now)


rate_limiter = RateLimiter()
