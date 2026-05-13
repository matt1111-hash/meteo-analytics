#!/usr/bin/env python3
"""
Global Weather Analyzer - Anomaly Profile CRUD Actions
Profile create, delete, rename, and reset operations.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from src.infrastructure.anomaly.anomaly_types import AnomalyProfileSettings

logger = logging.getLogger(__name__)


class ProfileActions:
    """
    Profil CRUD műveletek.

    Ez az osztály a profil létrehozási, törlési, átnevezési és
    visszaállítási műveleteket tartalmazza.
    """

    def __init__(
        self,
        save_func: Callable[[str, dict[str, Any]], bool],
        load_func: Callable[[str], dict[str, Any]],
        get_available_func: Callable[[], list],
        get_cache_func: Callable[[], dict[str, dict[str, Any]]],
        active_profile_getter: Callable[[], str],
        active_profile_setter: Callable[[str], None],
    ):
        """
        Inicializálás függvényekkel.

        Args:
            save_func: Profil mentése
            load_func: Profil betöltése
            get_available_func: Elérhető profilok listázása
            get_cache_func: Profil cache elérése
            active_profile_getter: Aktív profil lekérése
            active_profile_setter: Aktív profil beállítása
        """
        self._save = save_func
        self._load = load_func
        self._get_available = get_available_func
        self._get_cache = get_cache_func
        self._get_active = active_profile_getter
        self._set_active = active_profile_setter

    def create_profile(self, profile_name: str, base_profile: str = "default") -> bool:
        """
        Új profil létrehozása.

        Args:
            profile_name: Új profil neve
            base_profile: Alap profil (másolás alapja)

        Returns:
            bool: Sikeres volt-e a létrehozás
        """
        if profile_name in self._get_available():
            logger.warning(f"📁 Profil már létezik: {profile_name}")
            return False

        try:
            # Alap profil betöltése
            base_settings = self._load(base_profile)

            # Új profil létrehozása
            new_settings = AnomalyProfileSettings.from_dict(base_settings)
            new_settings.profile_name = profile_name
            new_settings.description = f"Egyedi profil - {base_profile} alapján"
            new_settings.created_at = datetime.now().isoformat()
            new_settings.modified_at = datetime.now().isoformat()

            # Mentés
            return self._save(profile_name, new_settings.to_dict())

        except Exception as e:
            logger.error(f"📁 Profil létrehozási hiba: {e}")
            return False

    def delete_profile(self, profile_name: str, storage) -> bool:
        """
        Profil törlése.

        Args:
            profile_name: Törölendő profil neve
            storage: Storage objektum mentéshez

        Returns:
            bool: Sikeres volt-e a törlés
        """
        if profile_name == "default":
            logger.warning("📁 Az alapértelmezett profil nem törölhető")
            return False

        if profile_name not in self._get_available():
            logger.warning(f"📁 Profil nem található: {profile_name}")
            return False

        try:
            profiles = self._get_cache()
            del profiles[profile_name]

            # Ha ez volt az aktív, akkor default-ra váltás
            if self._get_active() == profile_name:
                self._set_active("default")

            # Mentés
            data = {
                "profiles": profiles,
                "active_profile": self._get_active(),
                "modified_at": datetime.now().isoformat(),
                "version": "1.0",
            }

            success = storage.save_profiles(data)
            if success:
                logger.info(f"📁 Profil törölve: {profile_name}")

            return success

        except Exception as e:
            logger.error(f"📁 Profil törlési hiba: {e}")
            return False

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """
        Profil átnevezése.

        Args:
            old_name: Régi profil neve
            new_name: Új profil neve

        Returns:
            bool: Sikeres volt-e az átnevezés
        """
        if old_name == "default":
            logger.warning("📁 Az alapértelmezett profil nem nevezhető át")
            return False

        if new_name in self._get_available():
            logger.warning(f"📁 Profil már létezik: {new_name}")
            return False

        try:
            # Profil másolása új névvel
            settings = self._load(old_name)
            settings["profile_name"] = new_name
            settings["modified_at"] = datetime.now().isoformat()

            if self._save(new_name, settings):
                # Régi profil törlése
                return self.delete_profile(old_name, storage=None)

            return False

        except Exception as e:
            logger.error(f"📁 Profil átnevezési hiba: {e}")
            return False

    def reset_profile_to_defaults(self, profile_name: str) -> bool:
        """
        Profil visszaállítása alapértékekre.

        Args:
            profile_name: Profil neve

        Returns:
            bool: Sikeres volt-e a visszaállítás
        """
        try:
            default_settings = AnomalyProfileSettings(profile_name=profile_name).to_dict()
            return self._save(profile_name, default_settings)

        except Exception as e:
            logger.error(f"📁 Profil alapértékre állítási hiba: {e}")
            return False


__all__ = ["ProfileActions"]
