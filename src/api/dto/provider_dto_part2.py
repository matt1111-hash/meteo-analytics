# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from provider_dto.py."""

from __future__ import annotations

from .provider_dto_part1 import ProviderInfoDTO
from .provider_dto_support import *


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
    ) -> "ProviderSelectionDTO":
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
    def error_response(cls, message: str) -> "ProviderSelectionDTO":
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

    providers: List[ProviderInfoDTO]
    """List of provider information"""

    default_provider: str
    """Default provider ID"""

    @classmethod
    def create(
        cls, providers: List[ProviderInfoDTO], default_provider: str
    ) -> "ProviderListResponse":
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
