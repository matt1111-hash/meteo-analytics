#!/usr/bin/env python3

"""
Tests for API Authentication middleware.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status


class TestAuthMiddlewareUnit:
    """Unit tests for auth middleware function."""

    @pytest.mark.asyncio
    async def test_allows_public_path_without_auth(self):
        """Middleware should allow public paths without authentication."""
        from src.api.main import auth_middleware

        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.method = "GET"

        mock_call_next = AsyncMock()
        mock_call_next.return_value = MagicMock()

        await auth_middleware(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_allows_options_request_without_auth(self):
        """Middleware should allow OPTIONS requests without authentication."""
        from src.api.main import auth_middleware

        mock_request = MagicMock()
        mock_request.url.path = "/api/providers/list"
        mock_request.method = "OPTIONS"

        mock_call_next = AsyncMock()
        mock_call_next.return_value = MagicMock()

        await auth_middleware(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_allows_all_when_auth_disabled(self):
        """Middleware should allow all requests when auth is disabled."""
        from src.api.main import auth_middleware

        mock_request = MagicMock()
        mock_request.url.path = "/api/providers/list"
        mock_request.method = "GET"

        mock_call_next = AsyncMock()
        mock_call_next.return_value = MagicMock()

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = False

            await auth_middleware(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_rejects_missing_api_key_when_enabled(self):
        """Middleware should reject requests without API key when auth enabled."""
        from fastapi import HTTPException
        from src.api.main import auth_middleware

        mock_request = MagicMock()
        mock_request.url.path = "/api/providers/list"
        mock_request.method = "GET"
        mock_request.headers = {}

        mock_call_next = AsyncMock()

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "test-key"

            with pytest.raises(HTTPException) as exc_info:
                await auth_middleware(mock_request, mock_call_next)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_rejects_invalid_api_key_when_enabled(self):
        """Middleware should reject requests with invalid API key."""
        from fastapi import HTTPException
        from src.api.main import auth_middleware

        mock_request = MagicMock()
        mock_request.url.path = "/api/providers/list"
        mock_request.method = "GET"
        mock_request.headers = {"X-API-Key": "wrong-key"}
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"

        mock_call_next = AsyncMock()

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "correct-key"

            with pytest.raises(HTTPException) as exc_info:
                await auth_middleware(mock_request, mock_call_next)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_allows_valid_api_key_when_enabled(self):
        """Middleware should allow requests with valid API key."""
        from src.api.main import auth_middleware

        mock_request = MagicMock()
        mock_request.url.path = "/api/providers/list"
        mock_request.method = "GET"
        mock_request.headers = {"X-API-Key": "correct-key"}

        mock_call_next = AsyncMock()
        mock_call_next.return_value = MagicMock()

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "correct-key"

            await auth_middleware(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)
