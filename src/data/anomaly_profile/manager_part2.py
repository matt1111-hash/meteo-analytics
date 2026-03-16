# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for AnomalyProfileManager."""

from __future__ import annotations

from .manager_support import *


class AnomalyProfileManagerPart2Mixin:
    def save_profile(self, profile_name: str, settings: Dict[str, Any]) -> bool:
        """
        Profil beállítások mentése.

        Args:
            profile_name: Profil neve
            settings: Beállítások dictionary

        Returns:
            bool: Sikeres volt-e a mentés
        """
        try:
            # Validáció
            profile_settings = AnomalyProfileSettings.from_dict(settings)
            errors = profile_settings.validate()

            if errors:
                logger.error(f"📁 Profil validációs hibák: {errors}")
                return False

            profiles = self._get_profiles_cache()
            profiles[profile_name] = profile_settings.to_dict()

            # Fájl mentése
            data = {
                "profiles": profiles,
                "active_profile": self._active_profile,
                "modified_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            success = self.storage.save_profiles(data)
            if success:
                logger.info(f"📁 Profil mentve: {profile_name}")

            return success

        except Exception as e:
            logger.error(f"📁 Profil mentési hiba: {e}")
            return False

    # CRUD műveletek delegálása a ProfileActions-ra

    def create_profile(self, profile_name: str, base_profile: str = "default") -> bool:
        """Új profil létrehozása."""
        return self._actions.create_profile(profile_name, base_profile)

    def delete_profile(self, profile_name: str) -> bool:
        """Profil törlése."""
        return self._actions.delete_profile(profile_name, self.storage)

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Profil átnevezése."""
        return self._actions.rename_profile(old_name, new_name)

    def reset_profile_to_defaults(self, profile_name: str) -> bool:
        """Profil visszaállítása alapértékekre."""
        return self._actions.reset_profile_to_defaults(profile_name)

    def get_current_settings(self) -> Dict[str, Any]:
        """
        Jelenlegi aktív beállítások betöltése.

        Returns:
            Dict[str, Any]: Aktuális beállítások
        """
        try:
            cached = self.storage.load_current_settings()
            if cached:
                return cached

            return self.load_profile(self.get_active_profile())

        except Exception as e:
            logger.warning(f"📁 Jelenlegi beállítások betöltési hiba: {e}")
            return self.load_profile("default")
