"""
Middleware that logs every request with method, path, status, and latency.
Pure ASGI implementation (no BaseHTTPMiddleware — avoids asyncpg conflicts).
"""

import time

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

logger = structlog.get_logger(__name__)


class AccessLogMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = 500
        path = scope.get("path", "")

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        await self.app(scope, receive, send_wrapper)

        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        # Skip health check noise
        if path not in ("/health", "/api/v1/health"):
            logger.info(
                "request",
                method=scope.get("method", ""),
                path=path,
                status=status_code,
                latency_ms=latency_ms,
            )
