# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for AnomalyProfileManager."""

from __future__ import annotations

from .manager_support import *


class AnomalyProfileManagerPart1Mixin:  # noqa: D101
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
            logger.warning(f"📁 Profil nem található: {profile_name}, default használata")
            profile_name = "default"

        raw_settings = profiles.get(profile_name, {})
        try:
            return AnomalyProfileSettings.from_dict(raw_settings).to_dict()
        except Exception as exc:
            logger.warning(
                f"📁 Profil normalizálási hiba ({profile_name}): {exc}, default használata"
            )
            return AnomalyProfileSettings(profile_name=profile_name).to_dict()
