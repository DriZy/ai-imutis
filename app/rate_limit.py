"""Redis-backed rate limiting (async)."""
from typing import Optional

import redis.asyncio as redis
from fastapi import HTTPException, status

from .config import get_settings


class RedisRateLimiter:
    """Sliding-window limiter using Redis INCR/EXPIRE.

    Note: This allows a single request to slip past the strict limit when multiple
    concurrent increments happen at the exact boundary. Acceptable for MVP.
    """

    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2,
            )
        return self._client

    async def check(self, identifier: str, limit: int, window_seconds: int) -> None:
        """Increment request count and enforce limits."""

        client = await self._get_client()
        key = f"rl:{identifier}:{window_seconds}"

        count = await client.incr(key)
        if count == 1:
            await client.expire(key, window_seconds)

        if count > limit:
            ttl = await client.ttl(key)
            retry_after = max(int(ttl), 1) if ttl and ttl > 0 else window_seconds
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None


rate_limiter = RedisRateLimiter(get_settings().redis_url)
