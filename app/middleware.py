"""Custom middleware for request context handling."""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request id and timing metadata to each request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore[override]
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        request.state.request_id = request_id

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = f"{duration_ms:.2f}"
        return response


class DeviceIPMiddleware(BaseHTTPMiddleware):
    """Extract device IP and fingerprint from headers and attach to request state."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore[override]
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
        device_fingerprint = request.headers.get("X-Device-Fingerprint")
        device_ip_header = request.headers.get("X-Device-IP")

        request.state.device_ip = device_ip_header or client_ip
        request.state.device_fingerprint = device_fingerprint

        response = await call_next(request)
        if device_ip_header:
            response.headers["X-Device-IP"] = device_ip_header
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add basic security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore[override]
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-XSS-Protection", "0")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; frame-ancestors 'none'; object-src 'none'",
        )
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        return response
