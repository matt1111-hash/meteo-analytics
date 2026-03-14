#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Provider Management API routes.

@see AGENTS.md - Quality Gate: Coverage ≥85% (local)
"""

from __future__ import annotations

from unittest.mock import patch

import anyio
import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    from src.api.main import app
    return app


@pytest.fixture
def client(app):
    """Create sync wrapper around AsyncClient for API tests."""

    class SyncClientAdapter:
        def __init__(self, fastapi_app) -> None:
            self._app = fastapi_app

        def get(self, url: str, **kwargs):
            async def _request():
                async with AsyncClient(
                    transport=ASGITransport(app=self._app),
                    base_url="http://test",
                ) as async_client:
                    return await async_client.get(url, **kwargs)

            return anyio.run(_request)

        def post(self, url: str, **kwargs):
            async def _request():
                async with AsyncClient(
                    transport=ASGITransport(app=self._app),
                    base_url="http://test",
                ) as async_client:
                    return await async_client.post(url, **kwargs)

            return anyio.run(_request)

    return SyncClientAdapter(app)


@pytest.fixture
def mock_provider_config():
    """Mock provider configuration."""
    config = {
        "auto": {
            "name": "Automatikus (Smart Routing)",
            "description": "Use-case alapú automatikus provider választás",
            "icon": "🤖",
            "cost": "Optimalizált",
            "routing_logic": {
                "single_city": "open-meteo",
                "multi_city": "meteostat",
                "historical_deep": "meteostat",
                "real_time": "open-meteo",
            },
        },
        "open-meteo": {
            "name": "Open-Meteo (Ingyenes)",
            "description": "Ingyenes globális időjárási API",
            "icon": "🌍",
            "cost": "Ingyenes",
            "limitations": ["Limitált multi-city support"],
        },
        "meteostat": {
            "name": "Meteostat (Prémium)",
            "description": "Prémium API gazdag történeti adatokkal",
            "icon": "💎",
            "cost": "$10 USD/hónap",
            "features": ["10k request/hónap", "Gazdag történeti adatok"],
        },
    }
    return config


@pytest.fixture
def mock_user_preferences():
    """Mock user preferences."""
    prefs = {
        "selected_provider": "auto",
        "auto_fallback_enabled": True,
        "show_usage_warnings": True,
        "monthly_budget_usd": 10.0,
        "warning_threshold": 0.8,
    }
    return prefs


# =============================================================================
# LIST PROVIDERS TESTS
# =============================================================================


class TestListProviders:
    """Tests for GET /api/providers/list endpoint."""

    def test_list_providers_returns_all_providers(
        self, client, mock_provider_config
    ):
        """Should return list of all available providers."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ):
            response = client.get("/api/providers/list")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["count"] == 3
            assert len(data["providers"]) == 3
            assert data["default_provider"] == "auto"

    def test_list_providers_returns_correct_provider_info(
        self, client, mock_provider_config
    ):
        """Should return correct information for each provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ):
            response = client.get("/api/providers/list")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            providers = {p["provider_id"]: p for p in data["providers"]}

            # Check auto provider
            assert "auto" in providers
            assert providers["auto"]["name"] == "Automatikus (Smart Routing)"
            assert providers["auto"]["icon"] == "🤖"
            assert providers["auto"]["cost"] == "Optimalizált"

            # Check open-meteo provider
            assert "open-meteo" in providers
            assert providers["open-meteo"]["name"] == "Open-Meteo (Ingyenes)"
            assert providers["open-meteo"]["cost"] == "Ingyenes"

            # Check meteostat provider
            assert "meteostat" in providers
            assert providers["meteostat"]["name"] == "Meteostat (Prémium)"

    def test_list_providers_includes_routing_logic_for_auto(
        self, client, mock_provider_config
    ):
        """Should include routing logic for auto provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ):
            response = client.get("/api/providers/list")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            providers = {p["provider_id"]: p for p in data["providers"]}
            assert "routing_logic" in providers["auto"]
            assert providers["auto"]["routing_logic"]["single_city"] == "open-meteo"
            assert providers["auto"]["routing_logic"]["multi_city"] == "meteostat"

    def test_list_providers_handle_error(self, client):
        """Should return 500 error on exception."""
        with patch(
            "src.api.routes.providers.ProviderInfoDTO.from_config",
            side_effect=Exception("Config error"),
        ):
            response = client.get("/api/providers/list")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# =============================================================================
# GET STATUS TESTS
# =============================================================================


class TestGetProvidersStatus:
    """Tests for GET /api/providers/status endpoint."""

    def test_get_status_returns_all_providers(
        self, client, mock_provider_config, mock_user_preferences
    ):
        """Should return status for all providers."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            return_value="auto",
        ):
            response = client.get("/api/providers/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 3

    def test_get_status_indicates_selected_provider(
        self, client, mock_provider_config
    ):
        """Should correctly mark the selected provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            return_value="open-meteo",
        ):
            response = client.get("/api/providers/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            providers = {p["provider_id"]: p for p in data}
            assert providers["open-meteo"]["is_selected"] is True
            assert providers["auto"]["is_selected"] is False
            assert providers["meteostat"]["is_selected"] is False

    def test_get_status_calculates_correct_status(
        self, client, mock_provider_config
    ):
        """Should calculate correct health status based on usage."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            return_value="auto",
        ), patch.dict(
            "src.api.services.provider_usage_service._usage_service._usage_data",
            {
                "meteostat": {
                    "requests_this_month": 9000,  # 90% of 10000
                    "requests_total": 9000,
                    "requests_today": 100,
                    "errors_total": 10,
                    "errors_this_month": 10,
                    "response_times_ms": [100, 150, 120],
                    "last_used": "2024-01-15T10:00:00",
                    "first_used": "2024-01-01T00:00:00",
                }
            },
            clear=False,
        ):
            response = client.get("/api/providers/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            providers = {p["provider_id"]: p for p in data}
            # Meteostat at 90% usage should be "warning"
            assert providers["meteostat"]["status"] == "warning"
            assert providers["meteostat"]["usage_percentage"] == 0.9

    def test_get_status_handle_error(self, client):
        """Should return 500 error on exception."""
        with patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            side_effect=Exception("Preferences error"),
        ):
            response = client.get("/api/providers/status")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# =============================================================================
# GET SINGLE PROVIDER STATUS TESTS
# =============================================================================


class TestGetProviderStatus:
    """Tests for GET /api/providers/{provider_id}/status endpoint."""

    def test_get_provider_status_valid_provider(
        self, client, mock_provider_config
    ):
        """Should return status for valid provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            return_value="auto",
        ):
            response = client.get("/api/providers/open-meteo/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["provider_id"] == "open-meteo"
            assert "name" in data
            assert "status" in data
            assert "usage_percentage" in data

    def test_get_provider_status_invalid_provider(self, client, mock_provider_config):
        """Should return 404 for invalid provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.validate_provider_selection", return_value=False
        ):
            response = client.get("/api/providers/invalid/status")

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_provider_status_includes_is_selected_flag(
        self, client, mock_provider_config
    ):
        """Should include is_selected flag in response."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            return_value="meteostat",
        ):
            response = client.get("/api/providers/meteostat/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["is_selected"] is True

    def test_get_provider_status_returns_500_on_usage_service_error(
        self, client, mock_provider_config
    ):
        """Unexpected status lookup failures should return HTTP 500."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.validate_provider_selection", return_value=True
        ), patch(
            "src.api.routes.providers.get_usage_service",
            side_effect=Exception("usage service down"),
        ):
            response = client.get("/api/providers/open-meteo/status")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == (
                "Failed to retrieve status for provider 'open-meteo'"
            )


# =============================================================================
# SELECT PROVIDER TESTS
# =============================================================================


class TestSelectProvider:
    """Tests for POST /api/providers/{provider_id}/select endpoint."""

    def test_select_provider_valid_provider(self, client, mock_provider_config):
        """Should successfully select a valid provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            return_value="auto",
        ), patch(
            "src.api.routes.providers.UserPreferences.set_selected_provider",
            return_value=True,
        ):
            response = client.post("/api/providers/meteostat/select")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["provider_id"] == "meteostat"
            assert data["previous_provider_id"] == "auto"

    def test_select_provider_invalid_provider(self, client, mock_provider_config):
        """Should return 404 for invalid provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.validate_provider_selection", return_value=False
        ):
            response = client.post("/api/providers/invalid/select")

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_select_provider_handle_save_failure(
        self, client, mock_provider_config
    ):
        """Should return error when save fails."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.set_selected_provider",
            return_value=False,
        ):
            response = client.post("/api/providers/open-meteo/select")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is False
            assert "message" in data

    def test_select_provider_returns_500_on_unexpected_error(
        self, client, mock_provider_config
    ):
        """Unexpected persistence errors should return HTTP 500."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            side_effect=RuntimeError("prefs broken"),
        ):
            response = client.post("/api/providers/open-meteo/select")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == (
                "Failed to select provider 'open-meteo'"
            )


# =============================================================================
# GET SELECTED PROVIDER TESTS
# =============================================================================


class TestGetSelectedProvider:
    """Tests for GET /api/providers/selected endpoint."""

    def test_get_selected_provider_returns_correct_info(
        self, client, mock_provider_config
    ):
        """Should return information about selected provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            return_value="meteostat",
        ):
            response = client.get("/api/providers/selected")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["provider_id"] == "meteostat"
            assert data["name"] == "Meteostat (Prémium)"

    def test_get_selected_provider_defaults_to_auto_on_invalid(
        self, client, mock_provider_config
    ):
        """Should default to auto provider if selected provider is invalid."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            return_value="invalid_provider",
        ), patch(
            "src.api.routes.providers.ProviderConfig.DEFAULT_PROVIDER", "auto"
        ):
            response = client.get("/api/providers/selected")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["provider_id"] == "auto"

    def test_get_selected_provider_returns_500_on_error(
        self, client, mock_provider_config
    ):
        """Selected provider endpoint should return HTTP 500 on unexpected errors."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.get_selected_provider",
            side_effect=RuntimeError("prefs broken"),
        ):
            response = client.get("/api/providers/selected")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Failed to retrieve selected provider"


# =============================================================================
# GET PROVIDER USAGE TESTS
# =============================================================================


class TestGetProviderUsage:
    """Tests for GET /api/providers/{provider_id}/usage endpoint."""

    def test_get_provider_usage_valid_provider(
        self, client, mock_provider_config
    ):
        """Should return usage statistics for valid provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.load_provider_preferences",
            return_value={"monthly_budget_usd": 10.0},
        ):
            response = client.get("/api/providers/meteostat/usage")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["provider_id"] == "meteostat"
            assert "requests_total" in data
            assert "requests_this_month" in data
            assert "estimated_cost_usd" in data
            assert "budget_remaining_usd" in data

    def test_get_provider_usage_invalid_provider(self, client, mock_provider_config):
        """Should return 404 for invalid provider."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.validate_provider_selection", return_value=False
        ):
            response = client.get("/api/providers/invalid/usage")

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_provider_usage_calculates_cost_correctly(
        self, client, mock_provider_config
    ):
        """Should calculate cost based on usage."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.UserPreferences.load_provider_preferences",
            return_value={"monthly_budget_usd": 10.0},
        ), patch.dict(
            "src.api.services.provider_usage_service._usage_service._usage_data",
            {
                "meteostat": {
                    "requests_this_month": 5000,  # 5000 * 0.001 = $5
                    "requests_total": 5000,
                    "requests_today": 100,
                    "errors_total": 5,
                    "errors_this_month": 5,
                    "response_times_ms": [100, 150, 120],
                    "last_used": "2024-01-15T10:00:00",
                    "first_used": "2024-01-01T00:00:00",
                }
            },
            clear=False,
        ):
            response = client.get("/api/providers/meteostat/usage")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["estimated_cost_usd"] == 5.0
            assert data["budget_remaining_usd"] == 5.0

    def test_get_provider_usage_returns_500_on_usage_error(
        self, client, mock_provider_config
    ):
        """Usage endpoint should return HTTP 500 on unexpected service errors."""
        with patch(
            "src.api.routes.providers.ProviderConfig.PROVIDERS", mock_provider_config
        ), patch(
            "src.api.routes.providers.validate_provider_selection", return_value=True
        ), patch(
            "src.api.routes.providers.get_usage_service",
            side_effect=RuntimeError("usage broken"),
        ):
            response = client.get("/api/providers/meteostat/usage")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == (
                "Failed to retrieve usage for provider 'meteostat'"
            )
