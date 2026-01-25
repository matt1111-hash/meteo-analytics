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

This module re-exports all components from focused sub-modules.
For backward compatibility, all original symbols remain available.
"""

# ============================================================================
# TYPES
# ============================================================================
from .anomaly_types import AnomalyProfileSettings

# ============================================================================
# STORAGE
# ============================================================================
from .anomaly_storage import AnomalyProfileStorage

# ============================================================================
# MANAGER
# ============================================================================
from .anomaly_profile import AnomalyProfileManager

# ============================================================================
# DEMO
# ============================================================================
from .anomaly_demo import demo_anomaly_profile_manager


__all__ = [
    'AnomalyProfileSettings',
    'AnomalyProfileStorage',
    'AnomalyProfileManager',
    'demo_anomaly_profile_manager'
]


if __name__ == "__main__":
    demo_anomaly_profile_manager()
