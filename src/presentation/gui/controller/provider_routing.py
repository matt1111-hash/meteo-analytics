# mypy: ignore-errors
"""Provider Routing - Smart provider selection és routing."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any


def _is_non_default_provider(provider_name: str) -> bool:
    """Return whether provider is not the default free provider."""
    return provider_name != "open-meteo"


def _is_critical_usage(usage_summary: dict[str, Any]) -> bool:
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


def _build_provider_usage_result(usage_summary: dict[str, Any]) -> dict[str, Any]:
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
    logger_obj: Any, provider_name: str, usage_summary: dict[str, Any]
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


class ProviderRouting:
    """
    Provider routing kezelése.

    Felelőségek:
    - Smart provider selection (historical vs recent adatok)
    - Usage tracking és cost monitoring
    - Provider fallback strategies
    - Rate limit kezelés
    """

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

    def track_provider_usage(self, provider_name: str) -> dict[str, Any] | None:
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

    def handle_provider_change(self, provider_name: str) -> str:
        """
        Provider változás kezelése GUI-ból.

        Args:
            provider_name: Új provider neve

        Returns:
            Státusz üzenet
        """
        try:
            self._logger.info(f"🌐 Provider change request: {provider_name}")

            # User preferences frissítése
            self.user_preferences.set_selected_provider(provider_name)

            # Státusz üzenet generálása
            if provider_name == "auto":
                status_msg = "🤖 Automatikus provider routing bekapcsolva"
            else:
                provider_info = self.provider_config.PROVIDERS.get(provider_name, {})
                provider_display = provider_info.get("name", provider_name)
                status_msg = f"🌐 Provider beállítva: {provider_display}"

            self._logger.info(f"✅ Provider changed to: {provider_name}")
            return status_msg

        except Exception as e:
            self._logger.error(f"Provider change error: {e}")
            return f"Provider váltási hiba: {e}"

    def get_provider_info(self) -> dict[str, Any]:
        """
        Provider információk lekérdezése GUI számára.

        Returns:
            Provider információk és statistics
        """
        try:
            current_provider = self.user_preferences.get_selected_provider()
            usage_summary = self.usage_tracker.get_usage_summary()

            return {
                "current_provider": current_provider,
                "usage_summary": usage_summary,
                "available_providers": list(self.provider_config.PROVIDERS.keys()),
                "provider_configs": self.provider_config.PROVIDERS,
            }
        except Exception as e:
            self._logger.error(f"Provider info hiba: {e}")
            return {}

    def load_user_preferences(self) -> dict[str, Any]:
        """
        User preferences betöltése és signalok adatainak visszaadása.

        Returns:
            Dictionary a preference adatokkal
        """
        try:
            selected_provider = self.user_preferences.get_selected_provider()
            self._logger.info(f"🌐 User selected provider: {selected_provider}")

            # Usage statistics signal
            usage_summary = self.usage_tracker.get_usage_summary()
            usage_data = {
                "meteostat": {
                    "requests": usage_summary.get("meteostat_requests", 0),
                    "limit": usage_summary.get("meteostat_limit", 10000),
                },
                "open-meteo": {
                    "requests": usage_summary.get("openmeteo_requests", 0),
                    "limit": float("inf"),  # Unlimited
                },
            }

            # Warning ellenőrzés
            warning_level = usage_summary.get("warning_level", "normal")
            usage_percent = usage_summary.get("meteostat_percentage", 0)

            warning_data = None
            if warning_level in ["critical", "warning"]:
                warning_data = ("meteostat", int(usage_percent))

            self._logger.info("✅ User preferences betöltve")

            return {
                "selected_provider": selected_provider,
                "usage_data": usage_data,
                "warning_data": warning_data,
            }

        except Exception as e:
            self._logger.error(f"User preferences betöltési hiba: {e}")
            return {}

    def save_preferences(self) -> None:
        """User preferences mentése."""
        try:
            self.user_preferences.save()
            self.usage_tracker.save()
            self._logger.info("✅ Provider preferences saved")
        except Exception as e:
            self._logger.error(f"Preferences mentési hiba: {e}")
