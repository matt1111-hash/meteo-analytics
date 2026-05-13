#!/usr/bin/env python3
"""
Global Weather Analyzer - Anomaly Profile Storage
JSON file I/O and backup operations for anomaly profiles
"""

from __future__ import annotations

import json
import logging
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AnomalyProfileStorage:
    """
    Anomália profilok tárolása.

    🎯 FELELŐSSÉGEK:
    ✅ JSON fájl mentés/betöltés
    ✅ Backup készítése
    ✅ Thread-safe műveletek
    """

    def __init__(self, config_dir: Path | None = None):
        """
        Storage inicializálása.

        Args:
            config_dir: Konfiguráció könyvtár (opcionális)
        """
        self.config_dir = config_dir or Path("data/user_preferences")
        self.profiles_file = self.config_dir / "anomaly_profiles.json"
        self.settings_file = self.config_dir / "current_anomaly_settings.json"
        self.backup_dir = self.config_dir / "backups"

        # Thread safety
        self._lock = threading.RLock()

        # Inicializálás
        self._ensure_directories()

        logger.info(f"📁 AnomalyProfileStorage inicializálva: {self.config_dir}")

    def _ensure_directories(self) -> None:
        """Szükséges könyvtárak létrehozása."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def load_profiles(self) -> dict[str, Any]:
        """
        Profilok betöltése JSON fájlból.

        Returns:
            Dict[str, Any]: Profil adatok
        """
        if not self.profiles_file.exists():
            return {}

        try:
            with self._lock:
                with open(self.profiles_file, encoding="utf-8") as f:  # noqa: PTH123
                    data = json.load(f)

                logger.debug(f"📁 Profilok betöltve: {self.profiles_file}")
                return data

        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            logger.error(f"📁 Profilok betöltési hiba: {e}")
            return {}

    def save_profiles(self, data: dict[str, Any]) -> bool:
        """
        Profilok mentése JSON fájlba.

        Args:
            data: Mentendő adatok

        Returns:
            bool: Sikeres volt-e a mentés
        """
        try:
            with self._lock:
                # Backup készítése
                self._create_backup()

                # Mentés
                with open(self.profiles_file, "w", encoding="utf-8") as f:  # noqa: PTH123
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.profiles_file.chmod(0o600)

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
                if len(backups) > 10:  # noqa: PLR2004
                    for backup in backups[:-10]:
                        backup.unlink()

                logger.debug(f"📁 Backup készítve: {backup_file}")

            except Exception as e:
                logger.warning(f"📁 Backup készítési hiba: {e}")

    def save_current_settings(self, profile_name: str, settings: dict[str, Any]) -> bool:
        """
        Jelenlegi beállítások mentése gyors eléréshez.

        Args:
            profile_name: Profil neve
            settings: Beállítások

        Returns:
            bool: Sikeres volt-e a mentés
        """
        try:
            current_data = {
                "active_profile": profile_name,
                "settings": settings,
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.settings_file, "w", encoding="utf-8") as f:  # noqa: PTH123
                json.dump(current_data, f, indent=2, ensure_ascii=False)
            self.settings_file.chmod(0o600)

            logger.debug(f"📁 Jelenlegi beállítások mentve: {profile_name}")
            return True

        except Exception as e:
            logger.warning(f"📁 Jelenlegi beállítások mentési hiba: {e}")
            return False

    def load_current_settings(self) -> dict[str, Any] | None:
        """
        Jelenlegi beállítások betöltése.

        Returns:
            Dict[str, Any] | None: Aktuális beállítások
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, encoding="utf-8") as f:  # noqa: PTH123
                    data = json.load(f)

                settings = data.get("settings", {})
                return settings if isinstance(settings, dict) else None

            return None

        except Exception as e:
            logger.warning(f"📁 Jelenlegi beállítások betöltési hiba: {e}")
            return None


__all__ = ["AnomalyProfileStorage"]
