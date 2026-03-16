"""Tests split from test_providers_route.py."""

from __future__ import annotations

from starlette import status
from unittest.mock import patch

# ruff: noqa: F403, F405
from tests.api.test_providers_route_support import *


class TestGetProviderUsage:
    """Tests for GET /api/providers/{provider_id}/usage endpoint."""

    def test_get_provider_usage_valid_provider(self, client, mock_provider_config):
        """Should return usage statistics for valid provider."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.load_provider_preferences",
                return_value={"monthly_budget_usd": 10.0},
            ),
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
            response = client.get("/api/providers/invalid/usage")

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_provider_usage_calculates_cost_correctly(
        self, client, mock_provider_config
    ):
        """Should calculate cost based on usage."""
        with (
            patch(
                "src.api.routes.providers.ProviderConfig.PROVIDERS",
                mock_provider_config,
            ),
            patch(
                "src.api.routes.providers.UserPreferences.load_provider_preferences",
                return_value={"monthly_budget_usd": 10.0},
            ),
            patch.dict(
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
            ),
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
                side_effect=RuntimeError("usage broken"),
            ),
        ):
            response = client.get("/api/providers/meteostat/usage")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"] == (
                "Failed to retrieve usage for provider 'meteostat'"
            )
