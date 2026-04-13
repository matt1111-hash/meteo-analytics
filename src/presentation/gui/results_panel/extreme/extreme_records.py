#!/usr/bin/env python3
# mypy: ignore-errors

"""
Extreme Weather Calculator - Data Structures
🏆 Rekord adatstruktúrák és szöveges összefoglalók
"""

from dataclasses import dataclass


@dataclass
class ExtremeRecord:
    """
    🏆 Extrém időjárási rekord adatstruktúra
    """

    category: str  # 'temperature', 'precipitation', 'wind'
    record_type: str  # 'Legmelegebb nap', 'Legnagyobb széllökés', stb.
    value: str  # Formázott érték (pl. "35.2°C", "91.4km/h")
    date: str  # Dátum string
    raw_value: float | None = None  # Nyers érték számításokhoz


@dataclass
class RecordsTextSummary:
    """
    📋 Rekordok szöveges összefoglalója
    """

    temperature_text: str
    precipitation_text: str
    wind_text: str

    def get_full_text(self) -> str:
        """Teljes szöveges összefoglaló generálása."""
        return f"""📊 IDŐJÁRÁSI REKORDOK ÉS SZÉLSŐÉRTÉKEK
{"=" * 50}

{self.temperature_text}
{self.precipitation_text}
{self.wind_text}"""
