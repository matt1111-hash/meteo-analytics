"""DTOs for Provider Management API endpoints.

This module defines data transfer objects for provider-related operations
including listing providers, getting status, and managing selections.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping  # noqa: UP035


@dataclass(frozen=True)
class ProviderInfoDTO:
    """Information about a single weather provider."""

    provider_id: str
    """Unique provider identifier (e.g., "auto", "open-meteo", "meteostat")"""

    name: str
    """Human-readable provider name"""

    description: str
    """Provider description"""

    icon: str
    """Emoji icon for UI display"""

    cost: str
    """Cost information (e.g., "Ingyenes", "$10 USD/hónap")"""

    limitations: list[str] = field(default_factory=list)
    """Known limitations of this provider"""

    features: list[str] = field(default_factory=list)
    """Key features of this provider"""

    routing_logic: dict[str, str] = field(default_factory=dict)
    """Smart routing rules (for "auto" provider)"""

    @classmethod
    def from_config(cls, provider_id: str, config: Mapping[str, Any]) -> "ProviderInfoDTO":  # noqa: UP037
        """Create DTO from provider configuration.

        Args:
            provider_id: Provider identifier
            config: Provider configuration dictionary

        Returns:
            ProviderInfoDTO instance
        """
        return cls(
            provider_id=provider_id,
            name=str(config.get("name", provider_id)),
            description=str(config.get("description", "")),
            icon=str(config.get("icon", "🔧")),
            cost=str(config.get("cost", "Ismeretlen")),
            limitations=list(config.get("limitations", [])),
            features=list(config.get("features", [])),
            routing_logic=dict(config.get("routing_logic", {})),
        )


@dataclass(frozen=True)
class ProviderStatusDTO:
    """Status information for a provider."""

    provider_id: str
    """Provider identifier"""

    name: str
    """Provider name"""

    status: str
    """Current status: healthy, warning, critical, or disabled"""

    is_selected: bool
    """Whether this is the currently selected provider"""

    usage_percentage: float
    """Usage percentage (0.0 to 1.0)"""

    requests_this_month: int
    """Number of requests made this month"""

    monthly_limit: int | None
    """Monthly request limit (None if unlimited)"""

    estimated_cost_usd: float
    """Estimated cost in USD this month"""

    last_used: str | None
    """ISO timestamp of last use (None if never used)"""

    @classmethod
    def create(
        cls,
        provider_id: str,
        name: str,
        is_selected: bool,
        usage_percentage: float = 0.0,
        requests_this_month: int = 0,
        monthly_limit: int | None = None,
        estimated_cost_usd: float = 0.0,
        last_used: str | None = None,
    ) -> "ProviderStatusDTO":  # noqa: UP037
        """Create ProviderStatusDTO with automatic status calculation.

        Args:
            provider_id: Provider identifier
            name: Provider name
            is_selected: Whether this provider is currently selected
            usage_percentage: Usage as percentage (0.0 to 1.0)
            requests_this_month: Number of requests this month
            monthly_limit: Monthly request limit (None for unlimited)
            estimated_cost_usd: Estimated cost in USD
            last_used: ISO timestamp of last use

        Returns:
            ProviderStatusDTO with calculated status
        """
        # Calculate status based on usage
        if monthly_limit is None:
            status = "healthy"
        elif usage_percentage >= 0.95:  # noqa: PLR2004
            status = "critical"
        elif usage_percentage >= 0.8:  # noqa: PLR2004
            status = "warning"
        else:
            status = "healthy"

        return cls(
            provider_id=provider_id,
            name=name,
            status=status,
            is_selected=is_selected,
            usage_percentage=usage_percentage,
            requests_this_month=requests_this_month,
            monthly_limit=monthly_limit,
            estimated_cost_usd=estimated_cost_usd,
            last_used=last_used,
        )


@dataclass(frozen=True)
class ProviderUsageDTO:
    """Detailed usage statistics for a provider."""

    provider_id: str
    """Provider identifier"""

    requests_total: int
    """Total requests made"""

    requests_this_month: int
    """Requests made this month"""

    requests_today: int
    """Requests made today"""

    errors_total: int
    """Total error count"""

    errors_this_month: int
    """Error count this month"""

    average_response_time_ms: float
    """Average response time in milliseconds"""

    estimated_cost_usd: float
    """Estimated cost this month in USD"""

    budget_remaining_usd: float
    """Remaining budget in USD"""

    last_used: str | None
    """ISO timestamp of last use"""

    first_used: str | None
    """ISO timestamp of first use"""

    monthly_reset_date: str
    """ISO timestamp when monthly counter resets"""


@dataclass(frozen=True)
class ProviderSelectionDTO:
    """Response for provider selection operation."""

    success: bool
    """Whether the selection was successful"""

    provider_id: str | None
    """Selected provider ID (None if failed)"""

    previous_provider_id: str | None
    """Previously selected provider ID"""

    message: str
    """Status message"""

    timestamp: str
    """ISO timestamp of selection"""

    @classmethod
    def success_response(
        cls, provider_id: str, previous_provider_id: str | None
    ) -> "ProviderSelectionDTO":  # noqa: UP037
        """Create success response.

        Args:
            provider_id: Newly selected provider ID
            previous_provider_id: Previous provider ID

        Returns:
            ProviderSelectionDTO with success=True
        """
        return cls(
            success=True,
            provider_id=provider_id,
            previous_provider_id=previous_provider_id,
            message=f"Provider changed to {provider_id}",
            timestamp=datetime.now().isoformat(),
        )

    @classmethod
    def error_response(cls, message: str) -> "ProviderSelectionDTO":  # noqa: UP037
        """Create error response.

        Args:
            message: Error message

        Returns:
            ProviderSelectionDTO with success=False
        """
        return cls(
            success=False,
            provider_id=None,
            previous_provider_id=None,
            message=message,
            timestamp=datetime.now().isoformat(),
        )


@dataclass(frozen=True)
class ProviderListResponse:
    """Response for listing all providers."""

    count: int
    """Number of providers"""

    providers: list[ProviderInfoDTO]
    """List of provider information"""

    default_provider: str
    """Default provider ID"""

    @classmethod
    def create(
        cls, providers: list[ProviderInfoDTO], default_provider: str
    ) -> "ProviderListResponse":  # noqa: UP037
        """Create provider list response.

        Args:
            providers: List of provider DTOs
            default_provider: Default provider ID

        Returns:
            ProviderListResponse instance
        """
        return cls(
            count=len(providers),
            providers=providers,
            default_provider=default_provider,
        )


__all__ = [
    "ProviderInfoDTO",
    "ProviderListResponse",
    "ProviderSelectionDTO",
    "ProviderStatusDTO",
    "ProviderUsageDTO",
]
