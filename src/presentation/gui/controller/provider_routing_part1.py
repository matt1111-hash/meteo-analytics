# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for ProviderRouting."""

from __future__ import annotations

from .provider_routing_support import *


def _is_non_default_provider(provider_name: str) -> bool:
    """Return whether provider is not the default free provider."""
    return provider_name != "open-meteo"


def _is_critical_usage(usage_summary: Dict[str, Any]) -> bool:
    """Return whether usage summary indicates critical warning level."""
    return usage_summary.get("warning_level") == "critical"


def _analyze_request_window(start_date: str, end_date: str) -> tuple[int, bool, bool]:
    """Analyze request duration and historical range."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days_requested = (end - start).days + 1
    historical_threshold = datetime.now() - timedelta(days=60)
    is_historical = start < historical_threshold
    is_large_request = days_requested > 90  # noqa: PLR2004
    return days_requested, is_historical, is_large_request


def _build_provider_usage_result(usage_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Build normalized provider usage summary payload."""
    return {
        "meteostat": {
            "requests": usage_summary.get("meteostat_requests", 0),
            "limit": usage_summary.get("meteostat_limit", 10000),
        },
        "open-meteo": {
            "requests": usage_summary.get("openmeteo_requests", 0),
            "limit": float("inf"),
        },
    }


def _log_provider_warning(
    logger_obj: Any, provider_name: str, usage_summary: Dict[str, Any]
) -> None:
    """Log provider usage warning when applicable."""
    if not _is_non_default_provider(provider_name):
        return
    warning_level = usage_summary.get("warning_level", "normal")
    usage_percent = usage_summary.get("meteostat_percentage", 0)
    if warning_level == "critical":
        logger_obj.critical(f"🚨 Provider {provider_name} usage critical: {usage_percent:.1f}%")
    elif warning_level == "warning":
        logger_obj.warning(f"⚠️ Provider {provider_name} usage warning: {usage_percent:.1f}%")


class ProviderRoutingPart1Mixin:  # noqa: D101
    def __init__(self, provider_config, user_preferences, usage_tracker):
        """
        ProviderRouting inicializálása.

        Args:
            provider_config: ProviderConfig objektum
            user_preferences: UserPreferences objektum
            usage_tracker: UsageTracker objektum
        """
        self.provider_config = provider_config
        self.user_preferences = user_preferences
        self.usage_tracker = usage_tracker
        self._logger = logging.getLogger(__name__)

        self._logger.info("🌐 Provider routing komponensek betöltve:")
        self._logger.info(f"🌐 - Default provider: {self.user_preferences.get_selected_provider()}")
        self._logger.info(
            f"🌐 - Available providers: {list(self.provider_config.PROVIDERS.keys())}"
        )

    def select_provider_for_request(
        self,
        latitude: float,  # noqa: ARG002
        longitude: float,  # noqa: ARG002
        start_date: str,
        end_date: str,
    ) -> str:
        """
        Smart provider selection a kérés alapján.

        Args:
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            start_date: Kezdő dátum
            end_date: Befejező dátum

        Returns:
            Választott provider neve
        """
        try:
            user_provider = self.user_preferences.get_selected_provider()
            if user_provider != "auto":
                return self._select_user_forced_provider(user_provider)

            self._logger.info("🌐 Automatic provider routing...")
            days_requested, is_historical, is_large_request = _analyze_request_window(
                start_date, end_date
            )
            self._logger.info("🌐 Request analysis:")
            self._logger.info(f"🌐 - Days requested: {days_requested}")
            self._logger.info(f"🌐 - Is historical: {is_historical}")
            self._logger.info(f"🌐 - Is large request: {is_large_request}")
            return self._select_automatic_provider(is_historical, is_large_request)

        except Exception as e:
            self._logger.error(f"Provider selection error: {e}")
            return "open-meteo"  # Fallback to free provider

    def _select_user_forced_provider(self, user_provider: str) -> str:
        """Select provider when user explicitly forced one."""
        self._logger.info(f"🌐 User forced provider: {user_provider}")
        if not _is_non_default_provider(user_provider):
            return user_provider
        usage_summary = self.usage_tracker.get_usage_summary()
        if _is_critical_usage(usage_summary):
            self._logger.warning(
                f"⚠️ Provider {user_provider} rate limit exceeded, fallback to open-meteo"
            )
            return "open-meteo"
        return user_provider

    def _select_automatic_provider(self, is_historical: bool, is_large_request: bool) -> str:
        """Select provider automatically for request profile."""
        if not (is_historical or is_large_request):
            self._logger.info("🌐 Selected Open-Meteo for recent data")
            return "open-meteo"
        usage_summary = self.usage_tracker.get_usage_summary()
        if not _is_critical_usage(usage_summary):
            self._logger.info("🌐 Selected Meteostat for historical/large request")
            return "meteostat"
        self._logger.info("🌐 Meteostat rate limited, fallback to Open-Meteo")
        return "open-meteo"

    def track_provider_usage(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Provider használat tracking.

        Args:
            provider_name: Provider neve

        Returns:
            Usage summary dictionary vagy None
        """
        try:
            updated_usage = self.usage_tracker.track_request(provider_name)
            if not updated_usage:
                self._logger.warning(f"⚠️ Failed to track usage for {provider_name}")
                return None
            self._logger.info(f"🌐 Tracked usage for {provider_name}")
            usage_summary = self.usage_tracker.get_usage_summary()
            _log_provider_warning(self._logger, provider_name, usage_summary)
            return _build_provider_usage_result(usage_summary)

        except Exception as e:
            self._logger.error(f"Usage tracking error: {e}")
            return None
