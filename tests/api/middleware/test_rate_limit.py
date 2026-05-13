#!/usr/bin/env python3

"""Tests for rate limiting middleware."""

from __future__ import annotations

import time

import pytest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from httpx import ASGITransport, AsyncClient
from src.api.middleware.rate_limit import RateLimitMiddleware


def _create_app(max_requests: int = 3, window_seconds: int = 60) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware, max_requests=max_requests, window_seconds=window_seconds
    )

    @app.get("/test")
    async def test_endpoint() -> PlainTextResponse:
        return PlainTextResponse("ok")

    return app


class TestRateLimitAllows:
    """Requests within the limit should succeed."""

    @pytest.mark.anyio
    async def test_under_limit_returns_200(self):
        app = _create_app(max_requests=3, window_seconds=60)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for _ in range(3):
                response = await client.get("/test")
                assert response.status_code == 200


class TestRateLimitBlocks:
    """Requests exceeding the limit should get 429."""

    @pytest.mark.anyio
    async def test_over_limit_returns_429(self):
        app = _create_app(max_requests=2, window_seconds=60)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.get("/test")
            await client.get("/test")
            response = await client.get("/test")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    @pytest.mark.anyio
    async def test_window_expiry_allows_again(self):
        app = _create_app(max_requests=1, window_seconds=1)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response1 = await client.get("/test")
            assert response1.status_code == 200

            response2 = await client.get("/test")
            assert response2.status_code == 429

            time.sleep(1.1)

            response3 = await client.get("/test")
            assert response3.status_code == 200


class TestRateLimitPerClient:
    """Different IPs have separate counters."""

    @pytest.mark.anyio
    async def test_different_clients_independent(self):
        app = _create_app(max_requests=1, window_seconds=60)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response1 = await client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
            assert response1.status_code == 200

            # Same IP — blocked
            response2 = await client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
            assert response2.status_code == 429

            # Different IP — allowed
            response3 = await client.get("/test", headers={"X-Forwarded-For": "5.6.7.8"})
            assert response3.status_code == 200


class TestRateLimitMemoryEviction:
    """IP entries with stale timestamps must be cleaned up."""

    def test_stale_timestamps_evicted_on_return(self):
        """When an IP returns after window expiry, old data is replaced with fresh entry."""
        rl = RateLimitMiddleware(app=FastAPI(), max_requests=5, window_seconds=1)
        old_t = time.monotonic() - 10.0
        rl._timestamps["10.0.0.1"] = [old_t, old_t, old_t]
        rl._timestamps["10.0.0.2"] = [old_t, old_t]

        rl._is_limited("10.0.0.1")
        rl._is_limited("10.0.0.2")

        assert all(t != old_t for t in rl._timestamps["10.0.0.1"])
        assert all(t != old_t for t in rl._timestamps["10.0.0.2"])
        assert len(rl._timestamps["10.0.0.1"]) == 1
        assert len(rl._timestamps["10.0.0.2"]) == 1
