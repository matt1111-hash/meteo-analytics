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
    async def test_different_clients_independent(self, monkeypatch: pytest.MonkeyPatch):
        """When the direct peer is a trusted proxy, X-Forwarded-For keys the bucket.

        FIX-01: X-Forwarded-For is only honoured behind TRUSTED_PROXIES. The httpx
        ASGITransport presents request.client.host as "127.0.0.1", so that is the
        direct peer we must whitelist for this transport-level test.
        """
        monkeypatch.setenv("TRUSTED_PROXIES", "127.0.0.1")
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


class TestRateLimitXffSpoofingProtection:
    """FIX-01: X-Forwarded-For must be ignored without a trusted proxy."""

    @pytest.mark.anyio
    async def test_xff_ignored_without_trusted_proxy(self, monkeypatch: pytest.MonkeyPatch):
        """Without TRUSTED_PROXIES, spoofed X-Forwarded-For cannot bypass limits.

        All requests resolve to the same client (no trusted proxy → header ignored),
        so the per-client limit applies across forged headers.
        """
        monkeypatch.delenv("TRUSTED_PROXIES", raising=False)
        app = _create_app(max_requests=1, window_seconds=60)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First request with a forged header — allowed
            response1 = await client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
            assert response1.status_code == 200

            # Second request with a DIFFERENT forged header — still blocked, because
            # the header is ignored and both requests share the same real client.
            response2 = await client.get("/test", headers={"X-Forwarded-For": "9.9.9.9"})
            assert response2.status_code == 429


class TestRateLimitMemoryEviction:
    """FIX-02: the per-client store must stay bounded and self-clean stale entries."""

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

    def test_missing_client_creates_fresh_entry(self):
        """A brand-new client is recorded without raising (plain dict, not defaultdict)."""
        rl = RateLimitMiddleware(app=FastAPI(), max_requests=5, window_seconds=60)
        assert "never-seen" not in rl._timestamps

        limited = rl._is_limited("never-seen")

        assert limited is False
        assert len(rl._timestamps["never-seen"]) == 1

    def test_max_clients_eviction(self):
        """When the client store exceeds _max_clients, the oldest clients are evicted.

        Eviction runs inside _is_limited: once an 11th distinct client arrives, the
        oldest 10% (1 client) is dropped before the new entry is recorded.
        """
        rl = RateLimitMiddleware(app=FastAPI(), max_requests=5, window_seconds=60, max_clients=10)
        # Fill the store with 10 clients, each with a distinct (monotonic) oldest stamp.
        base = time.monotonic() - 100.0
        for i in range(10):
            rl._timestamps[f"client-{i:02d}"] = [base + i]

        # An 11th distinct client arrives via the real code path → triggers eviction.
        rl._is_limited("client-overflow")

        # Eviction removes the oldest 10% (1 client). The oldest (client-00) must go,
        # while the newest overflow client is retained.
        assert "client-00" not in rl._timestamps
        assert "client-overflow" in rl._timestamps
        assert len(rl._timestamps) <= 10
