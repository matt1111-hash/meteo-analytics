#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian City Selector - Database Loader Module
Magyar városok betöltése cities.db adatbázisból.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Callable, List

from PySide6.QtCore import Signal

from src.presentation.gui.hungarian_city_selector.types import (
    HungarianCity,
    HungarianRegions,
)

logger = logging.getLogger(__name__)


class HungarianCityDatabaseLoader:
    """
    Adatbázis betöltő osztály magyar városokhoz.
    """

    def __init__(self, db_path: Path):
        """
        Inicializálás.

        Args:
            db_path: Útvonal a cities.db adatbázishoz
        """
        self.db_path = db_path

    def load_cities(
        self,
        error_signal: Signal,
        stats_update_callback: Callable[[str], None]
    ) -> List[HungarianCity]:
        """
        Magyar városok betöltése a cities.db adatbázisból.

        Args:
            error_signal: Signal hiba esetén
            stats_update_callback: Statisztika frissítési callback

        Returns:
            HungarianCity objektumok listája
        """
        try:
            logger.info(f"🇭🇺 Magyar városok betöltése: {self.db_path}")

            if not self.db_path.exists():
                error_msg = f"Cities adatbázis nem található: {self.db_path}"
                logger.error(error_msg)
                error_signal.emit(error_msg)
                stats_update_callback("❌ Adatbázis hiba")
                return []

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Magyar városok lekérdezése
                query = """
                SELECT city, country, country_code, lat, lon, population,
                       admin_name, meteostat_station_id, data_quality_score
                FROM cities
                WHERE country_code = 'HU' AND country = 'Hungary'
                ORDER BY
                    CASE WHEN population IS NOT NULL THEN population ELSE 0 END DESC,
                    city ASC
                """

                cursor.execute(query)
                results = cursor.fetchall()

                # HungarianCity objektumok létrehozása
                cities = []
                for row in results:
                    city = HungarianCity(
                        city=row[0],
                        country=row[1],
                        country_code=row[2],
                        lat=row[3],
                        lon=row[4],
                        population=row[5],
                        admin_name=row[6],
                        meteostat_station_id=row[7],
                        data_quality_score=row[8],
                        region=HungarianRegions.get_region_for_city(row[0])
                    )
                    cities.append(city)

                logger.info(f"✅ {len(cities)} magyar város betöltve")
                return cities

        except Exception as e:
            error_msg = f"Hiba a magyar városok betöltésekor: {e}"
            logger.error(error_msg, exc_info=True)
            error_signal.emit(error_msg)
            stats_update_callback("❌ Betöltési hiba")
            return []

    @staticmethod
    def calculate_city_stats(cities: List[HungarianCity]) -> str:
        """
        Statisztikák számítása városok alapján.

        Args:
            cities: HungarianCity objektumok listája

        Returns:
            Statisztika szöveg
        """
        total_cities = len(cities)

        if total_cities == 0:
            return "❌ Nincsenek betöltött városok"

        # Régió statisztikák
        region_stats = {}
        population_sum = 0
        population_count = 0

        for city in cities:
            # Régió számolás
            region = city.region or 'Egyéb'
            region_stats[region] = region_stats.get(region, 0) + 1

            # Népesség számolás
            if city.population:
                population_sum += city.population
                population_count += 1

        # Statisztika szöveg összeállítása
        stats_text = "📊 MAGYAR VÁROSOK STATISZTIKA:\n"
        stats_text += f"  • Összes város: {total_cities}\n"
        stats_text += f"  • Összlakosság: {population_sum:,} fő ({population_count} városban)\n"
        stats_text += f"  • Átlaglakosság: {population_sum // population_count if population_count > 0 else 0:,} fő\n\n"

        stats_text += "📍 RÉGIÓK SZERINTI MEGOSZLÁS:\n"
        for region, count in sorted(region_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_cities) * 100
            display_name = HungarianRegions.REGION_DISPLAY_NAMES.get(region, f"❓ {region}")
            stats_text += f"  • {display_name}: {count} város ({percentage:.1f}%)\n"

        return stats_text
