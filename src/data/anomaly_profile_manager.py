#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Anomália Profil Manager
📁 PROFIL KEZELÉS: JSON alapú mentés/betöltés, predefined profilok
🔧 BEÁLLÍTÁSOK: Testreszabható küszöbök menedzsmentje
⚙️ VALIDATION: Beállítások validálása és hibakezélés

🚀 FUNKCIONALITÁS:
✅ JSON fájl alapú profil mentés/betöltés
✅ Predefined profilok (default, tropical, arctic, continental)
✅ Profil CRUD műveletek (create, read, update, delete)
✅ Aktív profil kezelés
✅ Beállítások validálása
✅ Backup és helyreállítás
✅ Thread-safe file operations
"""

from __future__ import annotations

import json
import logging
import shutil
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AnomalyProfileSettings:
    """
    Anomália profil beállítások adatstruktúra.

    🎯 STRUKTURÁLT ADATOK:
    ✅ Type hints minden mezőhöz
    ✅ Default értékek
    ✅ Validáció support
    ✅ JSON serialization
    """
    # Hőmérséklet küszöbök
    temp_hot: float = 35.0
    temp_cold: float = -10.0

    # Csapadék küszöbök
    precip_high: float = 100.0
    precip_low: float = 5.0

    # Szél küszöbök
    wind_high: float = 70.0
    wind_normal: float = 50.0
    wind_strong: float = 70.0
    wind_extreme: float = 100.0
    wind_hurricane: float = 120.0

    # Metaadatok
    profile_name: str = "default"
    created_at: str = ""
    modified_at: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        """Post-init validáció és timestamp beállítás."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.modified_at = datetime.now().isoformat()

    def validate(self) -> List[str]:
        """
        Beállítások validálása.

        Returns:
            List[str]: Hibák listája (üres ha nincs hiba)
        """
        errors = []

        # Hőmérséklet validáció
        if self.temp_hot <= self.temp_cold:
            errors.append("Meleg küszöb nem lehet kisebb vagy egyenlő a hideg küszöbnél")

        if not (-50.0 <= self.temp_hot <= 60.0):
            errors.append("Meleg küszöb tartománya: -50°C és 60°C között")

        if not (-50.0 <= self.temp_cold <= 40.0):
            errors.append("Hideg küszöb tartománya: -50°C és 40°C között")

        # Csapadék validáció
        if self.precip_high <= self.precip_low:
            errors.append("Magas csapadék küszöb nem lehet kisebb vagy egyenlő az alacsony küszöbnél")

        if not (0.0 <= self.precip_low <= 50.0):
            errors.append("Alacsony csapadék küszöb tartománya: 0-50mm")

        if not (10.0 <= self.precip_high <= 500.0):
            errors.append("Magas csapadék küszöb tartománya: 10-500mm")

        # Szél validáció
        wind_values = [self.wind_normal, self.wind_strong, self.wind_extreme, self.wind_hurricane]
        if wind_values != sorted(wind_values):
            errors.append("Szél küszöbök nem növekvő sorrendben vannak")

        for wind_val in wind_values:
            if not (10.0 <= wind_val <= 300.0):
                errors.append(f"Szél küszöb tartománya: 10-300km/h (hibás érték: {wind_val})")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Konvertálás dictionary-vé."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnomalyProfileSettings':
        """Létrehozás dictionary-ből."""
        return cls(**data)


class AnomalyProfileManager:
    """
    Anomália profilok menedzsmentje.

    🎯 FELELŐSSÉGEK:
    ✅ Profilok CRUD műveletek
    ✅ JSON fájl mentés/betöltés
    ✅ Predefined profilok kezelése
    ✅ Aktív profil tracking
    ✅ Backup és helyreállítás
    ✅ Thread-safe műveletek
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Anomália profil manager inicializálása.

        Args:
            config_dir: Konfiguráció könyvtár (opcionális)
        """
        self.config_dir = config_dir or Path("data/user_preferences")
        self.profiles_file = self.config_dir / "anomaly_profiles.json"
        self.settings_file = self.config_dir / "current_anomaly_settings.json"
        self.backup_dir = self.config_dir / "backups"

        # Thread safety
        self._lock = threading.RLock()

        # Cache
        self._profiles_cache: Optional[Dict[str, Dict[str, Any]]] = None
        self._active_profile: Optional[str] = None

        # Inicializálás
        self._ensure_directories()
        self._load_predefined_profiles()

        logger.info(f"📁 AnomalyProfileManager inicializálva: {self.config_dir}")

    def _ensure_directories(self) -> None:
        """Szükséges könyvtárak létrehozása."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _load_predefined_profiles(self) -> None:
        """Predefined profilok betöltése/létrehozása."""
        if not self.profiles_file.exists():
            self._create_default_profiles()
        else:
            self._load_profiles_from_file()

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

        self._save_profiles_to_file(profiles_data)
        self._profiles_cache = default_profiles
        self._active_profile = "default"

        logger.info("📁 Alapértelmezett profilok létrehozva")

    def _load_profiles_from_file(self) -> None:
        """Profilok betöltése JSON fájlból."""
        try:
            with self._lock:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self._profiles_cache = data.get("profiles", {})
                self._active_profile = data.get("active_profile", "default")

                logger.info(f"📁 Profilok betöltve: {len(self._profiles_cache)} profil")

        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            logger.error(f"📁 Profilok betöltési hiba: {e}")
            self._create_default_profiles()

    def _get_profiles_cache(self) -> Dict[str, Dict[str, Any]]:
        """Cache biztosítása használat előtt."""
        if self._profiles_cache is None:
            self._load_profiles_from_file()
        if self._profiles_cache is None:
            self._profiles_cache = {}
        return self._profiles_cache

    def _save_profiles_to_file(self, data: Dict[str, Any]) -> bool:
        """Profilok mentése JSON fájlba."""
        try:
            with self._lock:
                # Backup készítése
                self._create_backup()

                # Mentés
                with open(self.profiles_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.debug(f"📁 Profilok mentve: {self.profiles_file}")
                return True

        except Exception as e:
            logger.error(f"📁 Profilok mentési hiba: {e}")
            return False

    def _create_backup(self) -> None:
        """Backup készítése a jelenlegi profilokról."""
        if self.profiles_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"anomaly_profiles_backup_{timestamp}.json"

            try:
                shutil.copy2(self.profiles_file, backup_file)

                # Régi backup-ok törlése (csak utolsó 10 db maradjon)
                backups = sorted(self.backup_dir.glob("anomaly_profiles_backup_*.json"))
                if len(backups) > 10:
                    for backup in backups[:-10]:
                        backup.unlink()

                logger.debug(f"📁 Backup készítve: {backup_file}")

            except Exception as e:
                logger.warning(f"📁 Backup készítési hiba: {e}")

    # ===== PUBLIC API =====

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
            self._load_profiles_from_file()

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

            success = self._save_profiles_to_file(data)
            if success:
                # Jelenlegi beállítások fájl frissítése
                self._save_current_settings(profile_name)
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

            success = self._save_profiles_to_file(data)
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

            success = self._save_profiles_to_file(data)
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

    def _save_current_settings(self, profile_name: str) -> None:
        """Jelenlegi beállítások mentése gyors eléréshez."""
        try:
            settings = self.load_profile(profile_name)
            current_data = {
                "active_profile": profile_name,
                "settings": settings,
                "updated_at": datetime.now().isoformat()
            }

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"📁 Jelenlegi beállítások mentve: {profile_name}")

        except Exception as e:
            logger.warning(f"📁 Jelenlegi beállítások mentési hiba: {e}")

    def get_current_settings(self) -> Dict[str, Any]:
        """
        Jelenlegi aktív beállítások betöltése.

        Returns:
            Dict[str, Any]: Aktuális beállítások
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                settings = data.get("settings", {})
                return settings if isinstance(settings, dict) else {}

            return self.load_profile(self.get_active_profile())

        except Exception as e:
            logger.warning(f"📁 Jelenlegi beállítások betöltési hiba: {e}")
            return self.load_profile("default")


# 🧪 DEMO FUNKCIÓ
def demo_anomaly_profile_manager() -> None:
    """Demo: Anomália profil manager tesztelése."""
    print("🧪 ANOMÁLIA PROFIL MANAGER DEMO")
    print("=" * 50)

    # Manager inicializálása
    manager = AnomalyProfileManager(Path("demo_data/user_preferences"))

    # Elérhető profilok
    profiles = manager.get_available_profiles()
    print(f"📁 Elérhető profilok: {profiles}")

    # Aktív profil
    active = manager.get_active_profile()
    print(f"🎯 Aktív profil: {active}")

    # Profil betöltése
    settings = manager.load_profile("default")
    print(f"⚙️ Default beállítások: {settings}")

    # Új profil létrehozása
    success = manager.create_profile("test_profile", "default")
    print(f"🆕 Új profil létrehozva: {success}")

    # Beállítások módosítása
    modified_settings = settings.copy()
    modified_settings["temp_hot"] = 40.0
    modified_settings["precip_high"] = 150.0

    success = manager.save_profile("test_profile", modified_settings)
    print(f"💾 Profil mentve: {success}")

    # Profil aktiválása
    success = manager.set_active_profile("test_profile")
    print(f"🎯 Profil aktiválva: {success}")

    # Profil törlése
    success = manager.delete_profile("test_profile")
    print(f"🗑️ Profil törölve: {success}")

    print("\n✅ DEMO BEFEJEZVE!")


if __name__ == "__main__":
    demo_anomaly_profile_manager()
