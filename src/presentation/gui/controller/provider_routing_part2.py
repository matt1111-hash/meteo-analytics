# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for ProviderRouting."""

from __future__ import annotations

from .provider_routing_support import *


class ProviderRoutingPart2Mixin:  # noqa: D101
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

    def get_provider_info(self) -> Dict[str, Any]:
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

    def load_user_preferences(self) -> Dict[str, Any]:
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
