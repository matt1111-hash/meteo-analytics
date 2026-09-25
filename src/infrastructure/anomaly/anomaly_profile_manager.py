#!/usr/bin/env python3
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

This module re-exports all components from focused sub-modules.
For backward compatibility, all original symbols remain available.
"""

# ============================================================================
# STORAGE
# ============================================================================
from src.infrastructure.anomaly.anomaly_storage import AnomalyProfileStorage
from src.infrastructure.anomaly.anomaly_types import AnomalyProfileSettings

# ============================================================================
# MANAGER
# ============================================================================
from src.infrastructure.anomaly_profile.manager import AnomalyProfileManager

__all__ = [
    "AnomalyProfileManager",
    "AnomalyProfileSettings",
    "AnomalyProfileStorage",
    "demo_anomaly_profile_manager",
]


def demo_anomaly_profile_manager() -> None:
    """Load the optional demo only when explicitly requested."""
    from src.infrastructure.anomaly.anomaly_demo import (  # noqa: PLC0415
        demo_anomaly_profile_manager as run_demo,
    )

    run_demo()


if __name__ == "__main__":
    demo_anomaly_profile_manager()
