#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Anomaly Profile Types
Dataclass definitions for anomaly profile settings
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List


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


__all__ = ['AnomalyProfileSettings']
