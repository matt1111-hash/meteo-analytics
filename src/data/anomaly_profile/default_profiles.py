#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Anomaly Profile Default Definitions
Predefined anomaly profiles for different climate zones.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from ..anomaly_types import AnomalyProfileSettings


def create_default_profiles() -> Dict[str, Dict[str, Any]]:
    """
    Alapértelmezett anomália profilok létrehozása.

    Returns:
        Dict[str, Dict[str, Any]]: Profil nevek és beállításaik
    """
    return {
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


def create_profiles_data(active_profile: str = "default") -> Dict[str, Any]:
    """
    Teljes profil adat struktúra létrehozása.

    Args:
        active_profile: Aktív profil neve

    Returns:
        Dict[str, Any]: Profil adatok metaadatokkal
    """
    return {
        "profiles": create_default_profiles(),
        "active_profile": active_profile,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }


__all__ = [
    'create_default_profiles',
    'create_profiles_data'
]
