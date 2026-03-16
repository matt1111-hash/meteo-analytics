# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for ApiSettingsWidget."""

from __future__ import annotations

from .api_settings_widget_support import *


class ApiSettingsWidgetPart2Mixin:
    def set_api_settings(self, settings: Dict[str, Any]) -> bool:
        """API beállítások beállítása (compatibility)."""
        try:
            state = {
                "auto_timezone": settings.get("timezone") == "auto",
                "cache_data": settings.get("cache", True),
                "api_timeout": settings.get("timeout", 60),
            }

            return self.set_state(state)

        except Exception as e:
            print(f"❌ ERROR: Failed to set API settings: {e}")
            return False

    def set_enabled(self, enabled: bool) -> None:
        """Widget engedélyezése/letiltása."""
        self.group.setEnabled(enabled)
        self.auto_timezone.setEnabled(enabled)
        self.cache_data.setEnabled(enabled)
        self.api_timeout.setEnabled(enabled)

        print(f"⚙️ DEBUG: ApiSettingsWidget enabled state: {enabled}")

    def get_timeout_value(self) -> int:
        """Timeout érték lekérdezése."""
        return self.api_timeout.value()

    def set_timeout_value(self, timeout: int) -> bool:
        """Timeout érték beállítása."""
        if 30 <= timeout <= 300:
            self.api_timeout.setValue(timeout)
            return True
        return False

    def is_cache_enabled(self) -> bool:
        """Cache engedélyezve van-e."""
        return self.cache_data.isChecked()

    def set_cache_enabled(self, enabled: bool) -> None:
        """Cache engedélyezése/letiltása."""
        self.cache_data.setChecked(enabled)

    def is_auto_timezone_enabled(self) -> bool:
        """Auto timezone engedélyezve van-e."""
        return self.auto_timezone.isChecked()

    def set_auto_timezone_enabled(self, enabled: bool) -> None:
        """Auto timezone engedélyezése/letiltása."""
        self.auto_timezone.setChecked(enabled)

    # === SIZE HINT ===

    def sizeHint(self):
        """Preferált méret."""
        return self.group.sizeHint()

    def minimumSizeHint(self):
        """Minimum méret."""
        return self.group.minimumSizeHint()
