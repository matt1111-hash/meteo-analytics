#!/usr/bin/env python3

"""Tests for security headers middleware."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


class TestSecurityHeadersDevMode:
    """Security headers in development mode."""

    @pytest.mark.anyio
    async def test_x_content_type_options(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    @pytest.mark.anyio
    async def test_x_frame_options(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.headers["X-Frame-Options"] == "DENY"

    @pytest.mark.anyio
    async def test_x_xss_protection(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    @pytest.mark.anyio
    async def test_no_hsts_in_dev(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert "Strict-Transport-Security" not in response.headers

    @pytest.mark.anyio
    async def test_no_csp_in_dev(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")
        assert "Content-Security-Policy" not in response.headers


class TestSecurityHeadersProductionMode:
    """Additional headers in production mode."""

    @pytest.mark.asyncio
    async def test_hsts_in_production(self):
        from src.api.main import security_headers_middleware  # noqa: PLC0415

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_call_next = AsyncMock(return_value=mock_response)

        with patch("src.api.main.APIConfig.APP_ENV", "production"):
            result = await security_headers_middleware(mock_request, mock_call_next)

        assert result.headers["Strict-Transport-Security"] == (
            "max-age=63072000; includeSubDomains; preload"
        )

    @pytest.mark.asyncio
    async def test_csp_in_production(self):
        from src.api.main import security_headers_middleware  # noqa: PLC0415

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_call_next = AsyncMock(return_value=mock_response)

        with patch("src.api.main.APIConfig.APP_ENV", "production"):
            result = await security_headers_middleware(mock_request, mock_call_next)

        assert result.headers["Content-Security-Policy"] == "default-src 'self'"

    @pytest.mark.asyncio
    async def test_base_headers_in_production(self):
        from src.api.main import security_headers_middleware  # noqa: PLC0415

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_call_next = AsyncMock(return_value=mock_response)

        with patch("src.api.main.APIConfig.APP_ENV", "production"):
            result = await security_headers_middleware(mock_request, mock_call_next)

        assert result.headers["X-Content-Type-Options"] == "nosniff"
        assert result.headers["X-Frame-Options"] == "DENY"
        assert result.headers["X-XSS-Protection"] == "1; mode=block"
