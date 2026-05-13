#!/usr/bin/env python3

"""In-memory sliding-window rate limiter middleware."""

from __future__ import annotations

import logging
import os
import time
from collections import defaultdict
from threading import Lock

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

_DEFAULT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
_DEFAULT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


class RateLimitMiddleware:
    """Per-client IP sliding-window rate limiter."""

    def __init__(  # noqa: D107
        self,
        app: ASGIApp,
        max_requests: int = _DEFAULT_MAX_REQUESTS,
        window_seconds: int = _DEFAULT_WINDOW_SECONDS,
    ) -> None:
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _is_limited(self, client_ip: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            timestamps = self._timestamps[client_ip]
            self._timestamps[client_ip] = [t for t in timestamps if t > cutoff]
            timestamps = self._timestamps[client_ip]
            if not timestamps:
                del self._timestamps[client_ip]
                self._timestamps[client_ip] = [now]
                return False
            if len(timestamps) >= self.max_requests:
                return True
            timestamps.append(now)
            return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # noqa: D102
        if scope["type"] not in ("http",):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        client_ip = self._client_ip(request)

        if self._is_limited(client_ip):
            logger.warning("Rate limit exceeded for %s", client_ip)
            response = JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


__all__ = ["RateLimitMiddleware"]
