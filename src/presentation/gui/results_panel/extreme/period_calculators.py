#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Extreme Weather Calculator - Period Calculators (Refactored)
📅 Időszak alapú rekord számítások koordinátora

Moduláris struktúra:
- Napi számítások (kategóriák szerint)
- Havi számítások (monthly_calculator)
- Éves számítások (yearly_calculator)
"""

import logging
from typing import Dict, List

from .extreme_records import ExtremeRecord
from .monthly_calculator import MonthlyCalculator
from .yearly_calculator import YearlyCalculator

logger = logging.getLogger(__name__)


class PeriodCalculators:
    """
    📅 Időszak alapú rekord számítások koordinátora

    Felelős:
    - Delegálás a megfelelő számítónak
    - Fallback kezelése
    """

    def __init__(self, category_calculators):
        """
        Inicializálás.

        Args:
            category_calculators: Kategória számító referencia
        """
        self.category_calcs = category_calculators
        self.monthly_calc = MonthlyCalculator()
        self.yearly_calc = YearlyCalculator()

    def calculate_daily_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """
        📊 Napi rekordok számítása.

        Args:
            daily_data: Daily adatok
            dates: Dátumok listája

        Returns:
            List[ExtremeRecord]: Napi rekordok
        """
        records = []

        try:
            # Hőmérséklet rekordok
            records.extend(
                self.category_calcs.calculate_temperature_records(daily_data, dates)
            )

            # Csapadék rekordok
            records.extend(
                self.category_calcs.calculate_precipitation_records(daily_data, dates)
            )

            # Széllökés rekordok
            records.extend(
                self.category_calcs.calculate_wind_records(daily_data, dates)
            )

            # Szélsebesség rekordok (külön)
            records.extend(
                self.category_calcs.calculate_wind_speed_records(daily_data, dates)
            )

            # Páratartalom rekordok
            records.extend(
                self.category_calcs.calculate_humidity_records(daily_data, dates)
            )

            # Légnyomás rekordok
            records.extend(
                self.category_calcs.calculate_pressure_records(daily_data, dates)
            )

            # Napsütés rekordok
            records.extend(
                self.category_calcs.calculate_sunshine_records(daily_data, dates)
            )

            # UV index rekordok
            records.extend(self.category_calcs.calculate_uv_records(daily_data, dates))

            logger.info(f"Napi rekordok számítva: {len(records)} rekord")
            return records

        except Exception as e:
            logger.error(f"Napi rekordok számítási hiba: {e}")
            return []

    def calculate_monthly_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """
        📅 Havi rekordok számítása.

        Args:
            daily_data: Daily adatok
            dates: Dátumok listája

        Returns:
            List[ExtremeRecord]: Havi rekordok
        """
        return self.monthly_calc.calculate_records(
            daily_data, dates, self.calculate_daily_records
        )

    def calculate_yearly_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """
        🗓️ Éves rekordok számítása.

        Args:
            daily_data: Daily adatok
            dates: Dátumok listája

        Returns:
            List[ExtremeRecord]: Éves rekordok
        """
        return self.yearly_calc.calculate_records(daily_data, dates, self.monthly_calc)
