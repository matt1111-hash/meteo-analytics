#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for API Authentication middleware.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def client():
    """Create test client."""
    from src.api.main import app
    return TestClient(app)


# =============================================================================
# HEALTH ENDPOINT TESTS (PUBLIC)
# =============================================================================


class TestHealthEndpoint:
    """Tests for /health endpoint (always public)."""

    def test_health_no_auth_required(self, client):
        """Health endpoint should work without API key."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

    def test_health_ignores_invalid_api_key(self, client):
        """Health endpoint should ignore any provided API key."""
        response = client.get("/health", headers={"X-API-Key": "invalid"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}


# =============================================================================
# MIDDLEWARE UNIT TESTS
# =============================================================================


class TestAuthMiddlewareUnit:
    """Unit tests for auth middleware function."""

    @pytest.mark.asyncio
    async def test_allows_public_path_without_auth(self):
        """Middleware should allow public paths without authentication."""
        from src.api.main import auth_middleware

        # Mock request to health endpoint
        mock_request = MagicMock()
        mock_request.url.path = "/health"
        mock_request.method = "GET"

        # Mock call_next
        mock_call_next = AsyncMock()
        mock_call_next.return_value = MagicMock()

        await auth_middleware(mock_request, mock_call_next)

        # Should call call_next without checking auth
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_allows_options_request_without_auth(self):
        """Middleware should allow OPTIONS requests without authentication."""
        from src.api.main import auth_middleware

        # Mock OPTIONS request
        mock_request = MagicMock()
        mock_request.url.path = "/api/providers/list"
        mock_request.method = "OPTIONS"

        mock_call_next = AsyncMock()
        mock_call_next.return_value = MagicMock()

        await auth_middleware(mock_request, mock_call_next)

        # Should call call_next without checking auth
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


# =============================================================================
# VERIFY API KEY FUNCTION TESTS
# =============================================================================


class TestVerifyAPIKey:
    """Tests for verify_api_key function."""

    def test_returns_disabled_when_auth_not_enabled(self):
        """Should return 'disabled' when auth is not configured."""
        from src.api.main import verify_api_key

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = False

            result = verify_api_key(api_key=None)

            assert result == "disabled"

    def test_raises_401_when_no_key_provided(self):
        """Should raise 401 when no API key is provided."""
        from fastapi import HTTPException

        from src.api.main import verify_api_key

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "test-key"

            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(api_key=None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_raises_403_when_invalid_key(self):
        """Should raise 403 when invalid API key is provided."""
        from fastapi import HTTPException

        from src.api.main import verify_api_key

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "correct-key"

            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(api_key="wrong-key")

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_returns_key_when_valid(self):
        """Should return the API key when valid."""
        from src.api.main import verify_api_key

        with patch("src.api.main.APIConfig") as mock_config:
            mock_config.API_KEY_ENABLED = True
            mock_config.API_KEY = "correct-key"

            result = verify_api_key(api_key="correct-key")

            assert result == "correct-key"


# =============================================================================
# OPENAPI DOCS TESTS (PUBLIC)
# =============================================================================


class TestOpenAPIDocs:
    """Tests for OpenAPI documentation endpoints (public)."""

    def test_docs_endpoint_no_auth_required(self, client):
        """Docs endpoint should work without API key."""
        response = client.get("/docs")

        assert response.status_code == status.HTTP_200_OK

    def test_openapi_json_no_auth_required(self, client):
        """OpenAPI JSON should work without API key."""
        response = client.get("/openapi.json")

        assert response.status_code == status.HTTP_200_OK


# =============================================================================
# TIMING ATTACK PROTECTION TESTS
# =============================================================================


class TestTimingAttackProtection:
    """Tests for timing attack protection in API key verification."""

    def test_compare_digest_used_in_verify(self):
        """Verify that secrets.compare_digest is used for key comparison."""
        import inspect

        from src.api.main import verify_api_key

        source = inspect.getsource(verify_api_key)
        assert "compare_digest" in source

    def test_compare_digest_in_middleware(self):
        """Verify that secrets.compare_digest is used in middleware."""
        import inspect

        from src.api.main import auth_middleware

        source = inspect.getsource(auth_middleware)
        assert "compare_digest" in source


# =============================================================================
# PUBLIC PATHS TEST
# =============================================================================


class TestPublicPaths:
    """Tests for public paths configuration."""

    def test_public_paths_includes_health(self):
        """PUBLIC_PATHS should include /health."""
        from src.api.main import PUBLIC_PATHS
        assert "/health" in PUBLIC_PATHS

    def test_public_paths_includes_docs(self):
        """PUBLIC_PATHS should include /docs."""
        from src.api.main import PUBLIC_PATHS
        assert "/docs" in PUBLIC_PATHS

    def test_public_paths_includes_openapi(self):
        """PUBLIC_PATHS should include /openapi.json."""
        from src.api.main import PUBLIC_PATHS
        assert "/openapi.json" in PUBLIC_PATHS
