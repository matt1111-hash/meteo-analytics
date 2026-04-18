#!/usr/bin/env python3

"""Tests for OpenAPI documentation endpoint visibility by environment."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from httpx import ASGITransport, AsyncClient


class TestOpenAPIDocsDevMode:
    """Docs endpoints are public in development mode (default)."""

    @pytest.mark.anyio
    async def test_docs_endpoint_no_auth_required(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.anyio
    async def test_openapi_json_no_auth_required(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK


class TestOpenAPIDocsProductionMode:
    """Docs endpoints require auth in production mode (unit tests)."""

    @pytest.mark.asyncio
    async def test_docs_blocked_in_production(self):
        from src.api.main import auth_middleware  # noqa: PLC0415

        mock_request = MagicMock()
        mock_request.url.path = "/docs"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_call_next = AsyncMock()

        with (
            patch("src.api.main.PUBLIC_PATHS", {"/health"}),
            patch("src.api.main.APIConfig") as mock_cfg,
        ):
            mock_cfg.API_KEY_ENABLED = True
            mock_cfg.API_KEY = "secret"  # pragma: allowlist secret
            with pytest.raises(HTTPException) as exc_info:
                await auth_middleware(mock_request, mock_call_next)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_openapi_json_blocked_in_production(self):
        from src.api.main import auth_middleware  # noqa: PLC0415

        mock_request = MagicMock()
        mock_request.url.path = "/openapi.json"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_call_next = AsyncMock()

        with (
            patch("src.api.main.PUBLIC_PATHS", {"/health"}),
            patch("src.api.main.APIConfig") as mock_cfg,
        ):
            mock_cfg.API_KEY_ENABLED = True
            mock_cfg.API_KEY = "secret"  # pragma: allowlist secret
            with pytest.raises(HTTPException) as exc_info:
                await auth_middleware(mock_request, mock_call_next)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_redoc_blocked_in_production(self):
        from src.api.main import auth_middleware  # noqa: PLC0415

        mock_request = MagicMock()
        mock_request.url.path = "/redoc"
        mock_request.method = "GET"
        mock_request.headers = {}
        mock_call_next = AsyncMock()

        with (
            patch("src.api.main.PUBLIC_PATHS", {"/health"}),
            patch("src.api.main.APIConfig") as mock_cfg,
        ):
            mock_cfg.API_KEY_ENABLED = True
            mock_cfg.API_KEY = "secret"  # pragma: allowlist secret
            with pytest.raises(HTTPException) as exc_info:
                await auth_middleware(mock_request, mock_call_next)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_health_still_public_in_production(self):
        from src.api.main import auth_middleware  # noqa: PLC0415

        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.method = "GET"
        mock_call_next = AsyncMock()
        mock_call_next.return_value = MagicMock()

        with patch("src.api.main.PUBLIC_PATHS", {"/health"}):
            await auth_middleware(mock_request, mock_call_next)
        mock_call_next.assert_called_once_with(mock_request)
