#!/usr/bin/env python3
"""
Global Weather Analyzer - Anomaly Profile Demo
Demo function for testing anomaly profile manager
"""

from pathlib import Path

from .anomaly_profile_manager import AnomalyProfileManager


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


__all__ = ["demo_anomaly_profile_manager"]
