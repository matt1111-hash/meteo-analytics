#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extreme Weather Calculator - Main API
📊 EXTRÉM IDŐJÁRÁSI ÉRTÉKEK SZÁMÍTÓJA - Fő API

🎯 FELELŐSSÉG:
- Publikus API biztosítása
- Delegálás a specializált moduloknak
- Backward compatibility

✅ SOLID: Single Responsibility Principle
✅ Testelhető: Pure functions, determinisztikus eredmények
✅ Reusable: Különböző időszakokra használható
"""

import logging
from typing import Dict, List

from .category_calculators import CategoryCalculators
from .extreme_records import ExtremeRecord, RecordsTextSummary
from .period_calculators import PeriodCalculators
from .text_generators import TextGenerators

logger = logging.getLogger(__name__)


class ExtremeCalculator:
    """
    📊 EXTRÉM IDŐJÁRÁSI ÉRTÉKEK SZÁMÍTÓJA

    🎯 FELELŐSSÉG: Csak rekordok számítása és szélsőértékek keresése
    ✅ SOLID: Single Responsibility Principle
    ✅ Testelhető: Pure functions, determinisztikus eredmények
    ✅ Reusable: Különböző időszakokra használható
    """

    def __init__(self):
        """Extrém értékek számítójának inicializálása."""
        logger.info("ExtremeCalculator inicializálva (REFACTORED)")

        # Komponensek inicializálása
        self.category_calcs = CategoryCalculators()
        self.period_calcs = PeriodCalculators(self.category_calcs)
        self.text_gen = TextGenerators()

    def calculate_records_by_period(
        self,
        daily_data: Dict[str, List],
        dates: List[str],
        period_type: str = "daily"
    ) -> List[ExtremeRecord]:
        """
        🏆 Rekordok számítása időszak típus szerint.

        Args:
            daily_data: OpenMeteo API daily adatok Dict[List] formátumban
            dates: Dátumok listája
            period_type: "daily", "monthly", vagy "yearly"

        Returns:
            List[ExtremeRecord]: Rekordok listája
        """
        try:
            logger.info(f"Rekordok számítása - Időszak: {period_type}, Napok: {len(dates)}")

            if period_type == "daily":
                return self.period_calcs.calculate_daily_records(daily_data, dates)
            elif period_type == "monthly":
                return self.period_calcs.calculate_monthly_records(daily_data, dates)
            elif period_type == "yearly":
                return self.period_calcs.calculate_yearly_records(daily_data, dates)
            else:
                logger.warning(f"Ismeretlen period_type: {period_type}, fallback daily-re")
                return self.period_calcs.calculate_daily_records(daily_data, dates)

        except Exception as e:
            logger.error(f"Rekordok számítási hiba: {e}")
            return []

    def generate_text_summary(
        self,
        daily_data: Dict[str, List],
        dates: List[str]
    ) -> RecordsTextSummary:
        """
        📋 Szöveges rekord összefoglaló generálása.

        Args:
            daily_data: Daily adatok Dict[List] formátumban
            dates: Dátumok listája

        Returns:
            RecordsTextSummary: Strukturált szöveges összefoglaló
        """
        return self.text_gen.generate_summary(daily_data, dates)
