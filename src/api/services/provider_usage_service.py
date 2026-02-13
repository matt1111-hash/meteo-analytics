#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Provider Usage Tracking Service.

Handles tracking and retrieval of provider usage statistics.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from src.api.dto.provider_dto import ProviderStatusDTO, ProviderUsageDTO
from src.config.provider_config import ProviderConfig, UserPreferences


class ProviderUsageService:
    """Service for tracking and managing provider usage statistics."""

    # Provider limits (requests per month, None = unlimited)
    PROVIDER_LIMITS: Dict[str, int | None] = {
        "auto": None,
        "open-meteo": None,
        "meteostat": 10000,
    }

    # Cost per request in USD
    PROVIDER_COSTS: Dict[str, float] = {
        "auto": 0.0,
        "open-meteo": 0.0,
        "meteostat": 0.001,
    }

    def __init__(self) -> None:
        """Initialize usage tracker with default data."""
        self._usage_data = self._create_default_usage_data()

    def _create_default_usage_data(self) -> Dict[str, Dict[str, Any]]:
        """Create default usage data structure for all providers."""
        default = {
            "requests_total": 0,
            "requests_this_month": 0,
            "requests_today": 0,
            "errors_total": 0,
            "errors_this_month": 0,
            "response_times_ms": [],
            "last_used": None,
            "first_used": None,
        }
        return {provider_id: default.copy() for provider_id in self.PROVIDER_LIMITS}

    def get_usage_data(self, provider_id: str) -> Dict[str, Any]:
        """Get usage data for a provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Usage data dictionary
        """
        return self._usage_data.get(provider_id, self._usage_data["auto"])

    def get_monthly_limit(self, provider_id: str) -> int | None:
        """Get monthly request limit for a provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Monthly limit or None if unlimited
        """
        return self.PROVIDER_LIMITS.get(provider_id)

    def get_cost_per_request(self, provider_id: str) -> float:
        """Get cost per request for a provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Cost per request in USD
        """
        return self.PROVIDER_COSTS.get(provider_id, 0.0)

    def calculate_usage_percentage(self, provider_id: str) -> float:
        """Calculate usage percentage for a provider.

        Args:
            provider_id: Provider identifier

        Returns:
            Usage percentage (0.0 to 1.0)
        """
        monthly_limit = self.get_monthly_limit(provider_id)
        if monthly_limit is None:
            return 0.0

        usage_data = self.get_usage_data(provider_id)
        requests_this_month = usage_data.get("requests_this_month", 0)
        return min(requests_this_month / monthly_limit, 1.0)

    def calculate_estimated_cost(self, provider_id: str) -> float:
        """Calculate estimated cost for a provider this month.

        Args:
            provider_id: Provider identifier

        Returns:
            Estimated cost in USD
        """
        usage_data = self.get_usage_data(provider_id)
        requests_this_month = usage_data.get("requests_this_month", 0)
        cost_per_request = self.get_cost_per_request(provider_id)
        return requests_this_month * cost_per_request

    def calculate_status(
        self, provider_id: str, is_selected: bool
    ) -> ProviderStatusDTO:
        """Calculate provider status based on usage data.

        Args:
            provider_id: Provider identifier
            is_selected: Whether this is the selected provider

        Returns:
            ProviderStatusDTO with calculated status
        """
        usage_data = self.get_usage_data(provider_id)
        monthly_limit = self.get_monthly_limit(provider_id)
        requests_this_month = usage_data.get("requests_this_month", 0)

        return ProviderStatusDTO.create(
            provider_id=provider_id,
            name=ProviderConfig.PROVIDERS[provider_id]["name"],
            is_selected=is_selected,
            usage_percentage=self.calculate_usage_percentage(provider_id),
            requests_this_month=requests_this_month,
            monthly_limit=monthly_limit,
            estimated_cost_usd=self.calculate_estimated_cost(provider_id),
            last_used=usage_data.get("last_used"),
        )

    def calculate_monthly_reset_date(self) -> str:
        """Calculate the next monthly reset date.

        Returns:
            ISO format date string for the reset date
        """
        now = datetime.now(timezone.utc)
        if now.month == 12:
            reset_date = now.replace(
                year=now.year + 1,
                month=1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        else:
            reset_date = now.replace(
                month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
        return reset_date.isoformat()

    def get_detailed_usage(self, provider_id: str) -> ProviderUsageDTO:
        """Get detailed usage statistics for a provider.

        Args:
            provider_id: Provider identifier

        Returns:
            ProviderUsageDTO with detailed statistics
        """
        usage_data = self.get_usage_data(provider_id)
        response_times = usage_data.get("response_times_ms", [])

        # Calculate average response time
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0.0
        )

        # Get budget from preferences
        prefs = UserPreferences.load_provider_preferences()
        monthly_budget = prefs.get(
            "monthly_budget_usd", ProviderConfig.MONTHLY_BUDGET_USD
        )
        estimated_cost = self.calculate_estimated_cost(provider_id)
        budget_remaining = max(0, monthly_budget - estimated_cost)

        return ProviderUsageDTO(
            provider_id=provider_id,
            requests_total=usage_data.get("requests_total", 0),
            requests_this_month=usage_data.get("requests_this_month", 0),
            requests_today=usage_data.get("requests_today", 0),
            errors_total=usage_data.get("errors_total", 0),
            errors_this_month=usage_data.get("errors_this_month", 0),
            average_response_time_ms=avg_response_time,
            estimated_cost_usd=estimated_cost,
            budget_remaining_usd=budget_remaining,
            last_used=usage_data.get("last_used"),
            first_used=usage_data.get("first_used"),
            monthly_reset_date=self.calculate_monthly_reset_date(),
        )


# Singleton instance for use across the application
_usage_service = ProviderUsageService()


def get_usage_service() -> ProviderUsageService:
    """Get the singleton usage service instance."""
    return _usage_service
