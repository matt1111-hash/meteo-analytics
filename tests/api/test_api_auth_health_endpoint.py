#!/usr/bin/env python3

"""
Tests for API Authentication middleware.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient


class TestHealthEndpoint:
    """Tests for /health endpoint (always public)."""

    @pytest.mark.anyio
    async def test_health_no_auth_required(self, app):
        """Health endpoint should work without API key."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

    @pytest.mark.anyio
    async def test_health_ignores_invalid_api_key(self, app):
        """Health endpoint should ignore any provided API key."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health", headers={"X-API-Key": "invalid"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}
