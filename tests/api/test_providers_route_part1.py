"""Tests split from test_providers_route.py."""

from __future__ import annotations

from starlette import status
from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.api.test_providers_route_support import *


class TestListProviders:
    """Tests for GET /api/providers/list endpoint."""

    def test_list_providers_returns_all_providers(self, client, mock_provider_config):
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


class TestGetProvidersStatus:
    """Tests for GET /api/providers/status endpoint."""

    def test_get_status_returns_all_providers(
        self, client, mock_provider_config, mock_user_preferences
    ):
        """Should return status for all providers."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                return_value="auto",
            ),
        ):
            response = client.get("/api/providers/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 3

    def test_get_status_indicates_selected_provider(self, client, mock_provider_config):
        """Should correctly mark the selected provider."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                return_value="open-meteo",
            ),
        ):
            response = client.get("/api/providers/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            providers = {p["provider_id"]: p for p in data}
            assert providers["open-meteo"]["is_selected"] is True
            assert providers["auto"]["is_selected"] is False
            assert providers["meteostat"]["is_selected"] is False

    def test_get_status_calculates_correct_status(self, client, mock_provider_config):
        """Should calculate correct health status based on usage."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                return_value="auto",
            ),
            patch.dict(
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
            ),
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
