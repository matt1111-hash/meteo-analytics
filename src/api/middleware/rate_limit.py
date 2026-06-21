#!/usr/bin/env python3

"""In-memory sliding-window rate limiter middleware."""

from __future__ import annotations

import logging
import os
import time
from threading import Lock

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

_DEFAULT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
_DEFAULT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
_DEFAULT_MAX_CLIENTS = int(os.getenv("RATE_LIMIT_MAX_CLIENTS", "10000"))


class RateLimitMiddleware:
    """Per-client IP sliding-window rate limiter."""

    def __init__(  # noqa: D107
        self,
        app: ASGIApp,
        max_requests: int = _DEFAULT_MAX_REQUESTS,
        window_seconds: int = _DEFAULT_WINDOW_SECONDS,
        max_clients: int = _DEFAULT_MAX_CLIENTS,
    ) -> None:
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # FIX-02: plain dict (no unbounded defaultdict) + bounded client store.
        self._timestamps: dict[str, list[float]] = {}
        self._max_clients = max_clients
        self._lock = Lock()

    def _client_ip(self, request: Request) -> str:
        """Resolve the client IP, trusting X-Forwarded-For only behind a trusted proxy.

        FIX-01: an attacker could spoof the client IP by setting X-Forwarded-For,
        defeating per-client limits. We only honour the header when the direct
        peer (request.client.host) is listed in TRUSTED_PROXIES (comma-separated
        env var, empty by default).
        """
        trusted_proxies_raw = os.getenv("TRUSTED_PROXIES", "")
        trusted_proxies = {p.strip() for p in trusted_proxies_raw.split(",") if p.strip()}

        client_host = request.client.host if request.client else "unknown"

        if trusted_proxies and client_host in trusted_proxies:
            forwarded = request.headers.get("X-Forwarded-For", "")
            if forwarded:
                return forwarded.split(",")[0].strip()

        return client_host

    def _evict_excess_clients(self) -> None:
        """Drop the oldest 10% of clients once the store exceeds _max_clients (FIX-02)."""
        if len(self._timestamps) <= self._max_clients:
            return
        sorted_clients = sorted(
            self._timestamps.items(),
            key=lambda item: min(item[1]) if item[1] else 0.0,
        )
        evict_count = max(1, len(sorted_clients) // 10)
        for client, _ in sorted_clients[:evict_count]:
            del self._timestamps[client]

    def _is_limited(self, client_ip: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            existing = self._timestamps.get(client_ip, [])
            fresh = [t for t in existing if t > cutoff]
            if not fresh:
                self._timestamps[client_ip] = [now]
                limited = False
            else:
                self._timestamps[client_ip] = fresh
                if len(fresh) >= self.max_requests:
                    limited = True
                else:
                    fresh.append(now)
                    limited = False
            # FIX-02: evict AFTER recording the new client so the store stays
            # bounded within a single call (never grows unbounded across calls).
            self._evict_excess_clients()
            return limited

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
