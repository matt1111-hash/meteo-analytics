# mypy: ignore-errors
"""Global Weather Analyzer - Anomaly Profile Manager.

Main manager class for anomaly profile CRUD operations.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from src.infrastructure.anomaly.anomaly_storage import AnomalyProfileStorage
from src.infrastructure.anomaly.anomaly_types import AnomalyProfileSettings

from .default_profiles import create_profiles_data
from .profile_actions import ProfileActions

logger = logging.getLogger(__name__)


class AnomalyProfileManager:
    """
    Anomalia profilok menedzsmentje.

    FELELŐSSÉGEK:
    - Profilok CRUD muveletek
    - Predefined profilok kezelese
    - Aktiv profil tracking
    """

    def __init__(self, config_dir: Path | None = None):
        """
        Anomalia profil manager inicializalasa.

        Args:
            config_dir: Konfiguracio konyvtar (opcionalis)
        """
        self.storage = AnomalyProfileStorage(config_dir)

        # Cache
        self._profiles_cache: dict[str, dict[str, Any]] | None = None
        self._active_profile: str | None = None

        # CRUD actions
        self._actions = ProfileActions(
            save_func=self.save_profile,
            load_func=self.load_profile,
            get_available_func=self.get_available_profiles,
            get_cache_func=self._get_profiles_cache,
            active_profile_getter=self.get_active_profile,
            active_profile_setter=self._set_active_profile,
        )

        # Inicializalas
        self._load_or_create_profiles()

        logger.info("AnomalyProfileManager inicializalva")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set_active_profile(self, profile_name: str) -> None:
        """Aktiv profil beallitasa (belso)."""
        self._active_profile = profile_name

    def _load_or_create_profiles(self) -> None:
        """Profilok betoltese vagy letrehozasa."""
        data = self.storage.load_profiles()

        if not data or "profiles" not in data:
            self._create_default_profiles()
        else:
            self._profiles_cache = data.get("profiles", {})
            self._active_profile = data.get("active_profile", "default")

    def _create_default_profiles(self) -> None:
        """Alapertelmezett profilok letrehozasa."""
        profiles_data = create_profiles_data()

        self.storage.save_profiles(profiles_data)
        self._profiles_cache = profiles_data["profiles"]
        self._active_profile = "default"

        logger.info("Alapertelmezett profilok letrehozva")

    def _get_profiles_cache(self) -> dict[str, dict[str, Any]]:
        """Cache biztositasa hasznalat elott."""
        if self._profiles_cache is None:
            self._load_or_create_profiles()
        if self._profiles_cache is None:
            self._profiles_cache = {}
        return self._profiles_cache

    # ------------------------------------------------------------------
    # Profile query
    # ------------------------------------------------------------------

    def get_available_profiles(self) -> list[str]:
        """
        Elérheto profilok listaja.

        Returns:
            List[str]: Profil nevek listaja
        """
        profiles = self._get_profiles_cache()
        return list(profiles.keys())

    def get_active_profile(self) -> str:
        """
        Aktiv profil neve.

        Returns:
            str: Aktiv profil neve
        """
        if self._active_profile is None:
            self._load_or_create_profiles()

        return self._active_profile or "default"

    # ------------------------------------------------------------------
    # Profile mutation
    # ------------------------------------------------------------------

    def set_active_profile(self, profile_name: str) -> bool:
        """
        Aktiv profil beallitasa.

        Args:
            profile_name: Profil neve

        Returns:
            bool: Sikeres volt-e a beallitas
        """
        if profile_name not in self.get_available_profiles():
            logger.error(f"Ismeretlen profil: {profile_name}")
            return False

        try:
            profiles = self._get_profiles_cache()
            self._active_profile = profile_name

            # Mentes
            data = {
                "profiles": profiles,
                "active_profile": profile_name,
                "modified_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            success = self.storage.save_profiles(data)
            if success:
                # Jelenlegi beallitasok fajl frissitese
                settings = self.load_profile(profile_name)
                self.storage.save_current_settings(profile_name, settings)
                logger.info(f"Aktiv profil beallitva: {profile_name}")

            return success

        except Exception as e:
            logger.error(f"Aktiv profil beallitasi hiba: {e}")
            return False

    def load_profile(self, profile_name: str) -> dict[str, Any]:
        """
        Profil beallitasok betoltese.

        Args:
            profile_name: Profil neve

        Returns:
            Dict[str, Any]: Profil beallitasok
        """
        profiles = self._get_profiles_cache()

        if profile_name not in profiles:
            logger.warning(f"Profil nem talalhato: {profile_name}, default hasznalata")
            profile_name = "default"

        raw_settings = profiles.get(profile_name, {})
        try:
            return AnomalyProfileSettings.from_dict(raw_settings).to_dict()
        except Exception as exc:
            logger.warning(f"Profil normalizalasi hiba ({profile_name}): {exc}, default hasznalata")
            return AnomalyProfileSettings(profile_name=profile_name).to_dict()

    def save_profile(self, profile_name: str, settings: dict[str, Any]) -> bool:
        """
        Profil beallitasok mentese.

        Args:
            profile_name: Profil neve
            settings: Beallitasok dictionary

        Returns:
            bool: Sikeres volt-e a mentes
        """
        try:
            # Validacio
            profile_settings = AnomalyProfileSettings.from_dict(settings)
            errors = profile_settings.validate()

            if errors:
                logger.error(f"Profil validacios hibak: {errors}")
                return False

            profiles = self._get_profiles_cache()
            profiles[profile_name] = profile_settings.to_dict()

            # Fajl mentese
            data = {
                "profiles": profiles,
                "active_profile": self._active_profile,
                "modified_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            success = self.storage.save_profiles(data)
            if success:
                logger.info(f"Profil mentve: {profile_name}")

            return success

        except Exception as e:
            logger.error(f"Profil mentesi hiba: {e}")
            return False

    # ------------------------------------------------------------------
    # CRUD operations delegated to ProfileActions
    # ------------------------------------------------------------------

    def create_profile(self, profile_name: str, base_profile: str = "default") -> bool:
        """Új profil letrehozasa."""
        return self._actions.create_profile(profile_name, base_profile)

    def delete_profile(self, profile_name: str) -> bool:
        """Profil torlese."""
        return self._actions.delete_profile(profile_name, self.storage)

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Profil atnevezese."""
        return self._actions.rename_profile(old_name, new_name)

    def reset_profile_to_defaults(self, profile_name: str) -> bool:
        """Profil visszaallitasa alaperkekre."""
        return self._actions.reset_profile_to_defaults(profile_name)

    def get_current_settings(self) -> dict[str, Any]:
        """
        Jelenlegi aktiv beallitasok betoltese.

        Returns:
            Dict[str, Any]: Aktualis beallitasok
        """
        try:
            cached = self.storage.load_current_settings()
            if cached:
                return AnomalyProfileSettings.from_dict(cached).to_dict()

            return self.load_profile(self.get_active_profile())

        except Exception as e:
            logger.warning(f"Jelenlegi beallitasok betoltesi hiba: {e}")
            return self.load_profile("default")


__all__ = ["AnomalyProfileManager"]
