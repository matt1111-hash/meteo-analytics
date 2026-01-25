#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Anomaly Profile Manager
Main manager class for anomaly profile CRUD operations
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .anomaly_types import AnomalyProfileSettings
from .anomaly_storage import AnomalyProfileStorage

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

        # Inicializálás
        self._load_or_create_profiles()

        logger.info("📁 AnomalyProfileManager inicializálva")

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
        default_profiles = {
            "default": AnomalyProfileSettings(
                profile_name="default",
                description="Általános klímájú régiókhoz optimalizált beállítások"
            ).to_dict(),

            "tropical": AnomalyProfileSettings(
                profile_name="tropical",
                temp_hot=40.0,
                temp_cold=10.0,
                precip_high=200.0,
                precip_low=2.0,
                wind_hurricane=150.0,
                description="Tropikus klímájú régiókhoz optimalizált beállítások"
            ).to_dict(),

            "arctic": AnomalyProfileSettings(
                profile_name="arctic",
                temp_hot=25.0,
                temp_cold=-30.0,
                precip_high=50.0,
                precip_low=1.0,
                wind_extreme=80.0,
                wind_hurricane=100.0,
                description="Sarkvidéki klímájú régiókhoz optimalizált beállítások"
            ).to_dict(),

            "continental": AnomalyProfileSettings(
                profile_name="continental",
                temp_hot=38.0,
                temp_cold=-20.0,
                precip_high=120.0,
                precip_low=3.0,
                wind_strong=80.0,
                wind_extreme=110.0,
                description="Kontinentális klímájú régiókhoz optimalizált beállítások"
            ).to_dict(),

            "mediterranean": AnomalyProfileSettings(
                profile_name="mediterranean",
                temp_hot=42.0,
                temp_cold=0.0,
                precip_high=80.0,
                precip_low=1.0,
                wind_normal=40.0,
                wind_strong=60.0,
                description="Mediterrán klímájú régiókhoz optimalizált beállítások"
            ).to_dict()
        }

        profiles_data = {
            "profiles": default_profiles,
            "active_profile": "default",
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }

        self.storage.save_profiles(profiles_data)
        self._profiles_cache = default_profiles
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
                "version": "1.0"
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
            logger.warning(f"📁 Profil nem található: {profile_name}, default használata")
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
                "version": "1.0"
            }

            success = self.storage.save_profiles(data)
            if success:
                logger.info(f"📁 Profil mentve: {profile_name}")

            return success

        except Exception as e:
            logger.error(f"📁 Profil mentési hiba: {e}")
            return False

    def create_profile(self, profile_name: str, base_profile: str = "default") -> bool:
        """
        Új profil létrehozása.

        Args:
            profile_name: Új profil neve
            base_profile: Alap profil (másolás alapja)

        Returns:
            bool: Sikeres volt-e a létrehozás
        """
        if profile_name in self.get_available_profiles():
            logger.warning(f"📁 Profil már létezik: {profile_name}")
            return False

        try:
            # Alap profil betöltése
            base_settings = self.load_profile(base_profile)

            # Új profil létrehozása
            new_settings = AnomalyProfileSettings.from_dict(base_settings)
            new_settings.profile_name = profile_name
            new_settings.description = f"Egyedi profil - {base_profile} alapján"
            new_settings.created_at = datetime.now().isoformat()
            new_settings.modified_at = datetime.now().isoformat()

            # Mentés
            return self.save_profile(profile_name, new_settings.to_dict())

        except Exception as e:
            logger.error(f"📁 Profil létrehozási hiba: {e}")
            return False

    def delete_profile(self, profile_name: str) -> bool:
        """
        Profil törlése.

        Args:
            profile_name: Törölendő profil neve

        Returns:
            bool: Sikeres volt-e a törlés
        """
        if profile_name == "default":
            logger.warning("📁 Az alapértelmezett profil nem törölhető")
            return False

        if profile_name not in self.get_available_profiles():
            logger.warning(f"📁 Profil nem található: {profile_name}")
            return False

        try:
            profiles = self._get_profiles_cache()
            del profiles[profile_name]

            # Ha ez volt az aktív, akkor default-ra váltás
            if self._active_profile == profile_name:
                self._active_profile = "default"

            # Mentés
            data = {
                "profiles": profiles,
                "active_profile": self._active_profile,
                "modified_at": datetime.now().isoformat(),
                "version": "1.0"
            }

            success = self.storage.save_profiles(data)
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

        if new_name in self.get_available_profiles():
            logger.warning(f"📁 Profil már létezik: {new_name}")
            return False

        try:
            # Profil másolása új névvel
            settings = self.load_profile(old_name)
            settings["profile_name"] = new_name
            settings["modified_at"] = datetime.now().isoformat()

            if self.save_profile(new_name, settings):
                # Régi profil törlése
                return self.delete_profile(old_name)

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
            return self.save_profile(profile_name, default_settings)

        except Exception as e:
            logger.error(f"📁 Profil alapértékre állítási hiba: {e}")
            return False

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


__all__ = ['AnomalyProfileManager']
