# ruff: noqa: F403, F405,noqa: I001  # noqa: RUF100
# mypy: ignore-errors
"""Split definitions from provider_dto.py."""

from __future__ import annotations

from .provider_dto_support import *


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

    limitations: List[str] = field(default_factory=list)
    """Known limitations of this provider"""

    features: List[str] = field(default_factory=list)
    """Key features of this provider"""

    routing_logic: Dict[str, str] = field(default_factory=dict)
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
