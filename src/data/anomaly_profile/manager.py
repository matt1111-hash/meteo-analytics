#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Anomaly Profile Manager
Main manager class for anomaly profile CRUD operations.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..anomaly_storage import AnomalyProfileStorage
from ..anomaly_types import AnomalyProfileSettings
from .default_profiles import create_profiles_data
from .profile_actions import ProfileActions

logger = logging.getLogger(__name__)


class AnomalyProfileManager:
    """
    Anomália profilok menedzsmentje.

    🎯 FELELŐSSÉGEK:
    ✅ Profilok CRUD műveletek
    ✅ Predefined profilok kezelése
    ✅ Aktív profil tracking
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Anomália profil manager inicializálása.

        Args:
            config_dir: Konfiguráció könyvtár (opcionális)
        """
        self.storage = AnomalyProfileStorage(config_dir)

        # Cache
        self._profiles_cache: Optional[Dict[str, Dict[str, Any]]] = None
        self._active_profile: Optional[str] = None

        # CRUD actions
        self._actions = ProfileActions(
            save_func=self.save_profile,
            load_func=self.load_profile,
            get_available_func=self.get_available_profiles,
            get_cache_func=self._get_profiles_cache,
            active_profile_getter=self.get_active_profile,
            active_profile_setter=self._set_active_profile,
        )

        # Inicializálás
        self._load_or_create_profiles()

        logger.info("📁 AnomalyProfileManager inicializálva")

    def _set_active_profile(self, profile_name: str) -> None:
        """Aktív profil beállítása (belső)."""
        self._active_profile = profile_name

    def _load_or_create_profiles(self) -> None:
        """Profilok betöltése vagy létrehozása."""
        data = self.storage.load_profiles()

        if not data or "profiles" not in data:
            self._create_default_profiles()
        else:
            self._profiles_cache = data.get("profiles", {})
            self._active_profile = data.get("active_profile", "default")

    def _create_default_profiles(self) -> None:
        """Alapértelmezett profilok létrehozása."""
        profiles_data = create_profiles_data()

        self.storage.save_profiles(profiles_data)
        self._profiles_cache = profiles_data["profiles"]
        self._active_profile = "default"

        logger.info("📁 Alapértelmezett profilok létrehozva")

    def _get_profiles_cache(self) -> Dict[str, Dict[str, Any]]:
        """Cache biztosítása használat előtt."""
        if self._profiles_cache is None:
            self._load_or_create_profiles()
        if self._profiles_cache is None:
            self._profiles_cache = {}
        return self._profiles_cache

    def get_available_profiles(self) -> List[str]:
        """
        Elérhető profilok listája.

        Returns:
            List[str]: Profil nevek listája
        """
        profiles = self._get_profiles_cache()
        return list(profiles.keys())

    def get_active_profile(self) -> str:
        """
        Aktív profil neve.

        Returns:
            str: Aktív profil neve
        """
        if self._active_profile is None:
            self._load_or_create_profiles()

        return self._active_profile or "default"

    def set_active_profile(self, profile_name: str) -> bool:
        """
        Aktív profil beállítása.

        Args:
            profile_name: Profil neve

        Returns:
            bool: Sikeres volt-e a beállítás
        """
        if profile_name not in self.get_available_profiles():
            logger.error(f"📁 Ismeretlen profil: {profile_name}")
            return False

        try:
            profiles = self._get_profiles_cache()
            self._active_profile = profile_name

            # Mentés
            data = {
                "profiles": profiles,
                "active_profile": profile_name,
                "modified_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            success = self.storage.save_profiles(data)
            if success:
                # Jelenlegi beállítások fájl frissítése
                settings = self.load_profile(profile_name)
                self.storage.save_current_settings(profile_name, settings)
                logger.info(f"📁 Aktív profil beállítva: {profile_name}")

            return success

        except Exception as e:
            logger.error(f"📁 Aktív profil beállítási hiba: {e}")
            return False

    def load_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Profil beállítások betöltése.

        Args:
            profile_name: Profil neve

        Returns:
            Dict[str, Any]: Profil beállítások
        """
        profiles = self._get_profiles_cache()

        if profile_name not in profiles:
            logger.warning(
                f"📁 Profil nem található: {profile_name}, default használata"
            )
            profile_name = "default"

        return profiles.get(profile_name, {}).copy()

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


__all__ = ["AnomalyProfileManager"]
