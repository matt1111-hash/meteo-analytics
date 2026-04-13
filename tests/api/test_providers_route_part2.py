"""Tests split from test_providers_route.py."""

from __future__ import annotations

from unittest.mock import patch

from starlette import status

# ruff: noqa: F403, F405
from tests.api.test_providers_route_support import *


class TestGetProviderStatus:
    """Tests for GET /api/providers/{provider_id}/status endpoint."""

    def test_get_provider_status_valid_provider(self, client, mock_provider_config):
        """Should return status for valid provider."""
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
            response = client.get("/api/providers/open-meteo/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["provider_id"] == "open-meteo"
            assert "name" in data
            assert "status" in data
            assert "usage_percentage" in data

    def test_get_provider_status_invalid_provider(self, client, mock_provider_config):
        """Should return 404 for invalid provider."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.validate_provider_selection",
                return_value=False,
            ),
        ):
            response = client.get("/api/providers/invalid/status")

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_provider_status_includes_is_selected_flag(self, client, mock_provider_config):
        """Should include is_selected flag in response."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                return_value="meteostat",
            ),
        ):
            response = client.get("/api/providers/meteostat/status")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["is_selected"] is True

    def test_get_provider_status_returns_500_on_usage_service_error(
        self, client, mock_provider_config
    ):
        """Unexpected status lookup failures should return HTTP 500."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.validate_provider_selection",
                return_value=True,
            ),
            patch(
                "src.api.routes.providers.get_usage_service",
                side_effect=Exception("usage service down"),
            ),
        ):
            response = client.get("/api/providers/open-meteo/status")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == (
                "Failed to retrieve status for provider 'open-meteo'"
            )


class TestSelectProvider:
    """Tests for POST /api/providers/{provider_id}/select endpoint."""

    def test_select_provider_valid_provider(self, client, mock_provider_config):
        """Should successfully select a valid provider."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                return_value="auto",
            ),
            patch(
                "src.api.routes.providers.UserPreferences.set_selected_provider",
                return_value=True,
            ),
        ):
            response = client.post("/api/providers/meteostat/select")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["provider_id"] == "meteostat"
            assert data["previous_provider_id"] == "auto"

    def test_select_provider_invalid_provider(self, client, mock_provider_config):
        """Should return 404 for invalid provider."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.validate_provider_selection",
                return_value=False,
            ),
        ):
            response = client.post("/api/providers/invalid/select")

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_select_provider_handle_save_failure(self, client, mock_provider_config):
        """Should return error when save fails."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.set_selected_provider",
                return_value=False,
            ),
        ):
            response = client.post("/api/providers/open-meteo/select")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is False
            assert "message" in data

    def test_select_provider_returns_500_on_unexpected_error(self, client, mock_provider_config):
        """Unexpected persistence errors should return HTTP 500."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                side_effect=RuntimeError("prefs broken"),
            ),
        ):
            response = client.post("/api/providers/open-meteo/select")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == ("Failed to select provider 'open-meteo'")


class TestGetSelectedProvider:
    """Tests for GET /api/providers/selected endpoint."""

    def test_get_selected_provider_returns_correct_info(self, client, mock_provider_config):
        """Should return information about selected provider."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                return_value="meteostat",
            ),
        ):
            response = client.get("/api/providers/selected")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["provider_id"] == "meteostat"
            assert data["name"] == "Meteostat (Prémium)"

    def test_get_selected_provider_defaults_to_auto_on_invalid(self, client, mock_provider_config):
        """Should default to auto provider if selected provider is invalid."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                return_value="invalid_provider",
            ),
            patch("src.api.routes.providers.ProviderConfig.DEFAULT_PROVIDER", "auto"),
        ):
            response = client.get("/api/providers/selected")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["provider_id"] == "auto"

    def test_get_selected_provider_returns_500_on_error(self, client, mock_provider_config):
        """Selected provider endpoint should return HTTP 500 on unexpected errors."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.get_selected_provider",
                side_effect=RuntimeError("prefs broken"),
            ),
        ):
            response = client.get("/api/providers/selected")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == "Failed to retrieve selected provider"
