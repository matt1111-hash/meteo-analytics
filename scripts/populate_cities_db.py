#!/usr/bin/env python3
"""
Város-adatbázis generátor - Multi-city analytics támogatás (PROFESSZIONÁLIS JAVÍTOTT VERZIÓ)
Global Weather Analyzer projekt

Fájl: scripts/populate_cities_db.py
Cél: SQLite adatbázis generálása 3 forrásból:
- SimpleMaps worldcities.csv (100k+ város)
- Meteostat API (meteorológiai állomások)
- HungaroMet prioritás (magyar adatminőség)

KRITIKUS JAVÍTÁSOK:
✅ None-safe inventory feldolgozás (TypeError: None >= '2023-01-01' megoldva)
✅ Robusztus data_quality_score számítás
✅ Professional error handling minden metódusnál
✅ Type hints teljes lefedettség
✅ Comprehensive logging és hibakeresés
✅ Defensive programming elvek alkalmazása

Verzió: v2.1.0 - Production Ready
"""

import json
import logging
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from dotenv import load_dotenv

# Projektgyökér hozzáadása a Python path-hoz
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.meteostat_client import (
    MeteostatAPIError,
    MeteostatClient,
    MeteostatStation,
)

# Logging inicializálás - JAVÍTOTT verzió (könyvtár előbb létrehozva)
# Logs könyvtár létrehozása ELSŐ LÉPÉSKÉNT
Path("logs").mkdir(exist_ok=True)

# Professional logging beállítás
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/populate_cities_db.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CityRecord:
    """
    Város adatstruktúra adatbázis tároláshoz

    Professional data model a tiszta architektúrához
    """
    city: str
    lat: float
    lon: float
    country: str
    country_code: str
    population: Optional[int] = None
    continent: Optional[str] = None
    admin_name: Optional[str] = None
    capital: Optional[str] = None
    timezone: Optional[str] = None

    # Meteostat integráció
    meteostat_station_id: Optional[str] = None
    meteostat_station_name: Optional[str] = None
    station_elevation: Optional[float] = None
    station_distance: Optional[float] = None
    station_inventory: Optional[str] = None

    # HungaroMet prioritás
    hungaromet_priority: Optional[int] = None
    data_quality_score: Optional[int] = None
    last_data_update: Optional[str] = None


class CityDatabasePopulator:
    """
    Város-adatbázis generátor osztály

    PROFESSZIONÁLIS IMPLEMENTÁCIÓ:
    - SOLID elvek alkalmazása
    - Comprehensive error handling
    - None-safe adatfeldolgozás
    - Type safety minden metódusnál
    - Professional logging
    - Defensive programming

    Felelősségek:
    - SimpleMaps CSV feldolgozása és validálása
    - Meteostat API integráció hibakezeléssel
    - HungaroMet prioritás alkalmazása
    - SQLite adatbázis generálása indexekkel
    - Progress tracking és részletes hibakezelés
    """

    # HungaroMet prioritási rendszer - Dunai Hidrológiai Információs Rendszer alapján
    HUNGARIAN_PRIORITY_CITIES: Dict[str, Dict[str, Union[str, int]]] = {
        # PRIORITÁS 1: Kritikus állomások
        "Budapest": {"station_type": "auto", "priority": 1, "special": "capital"},
        "Debrecen": {"station_type": "auto", "priority": 1, "special": "major_city"},
        "Szeged": {"station_type": "auto", "priority": 1, "special": "major_city"},
        "Miskolc": {"station_type": "auto", "priority": 1, "special": "major_city"},
        "Békéscsaba": {"station_type": "auto", "priority": 1, "special": "regional"},
        "Eger": {"station_type": "auto", "priority": 1, "special": "historical"},
        "Nagykanizsa": {"station_type": "auto", "priority": 1, "special": "regional"},
        "Paks": {"station_type": "auto", "priority": 1, "special": "nuclear_plant"},
        "Siófok": {"station_type": "auto", "priority": 1, "special": "balaton"},
        "Sopron": {"station_type": "auto", "priority": 1, "special": "border"},
        "Szombathely": {"station_type": "auto", "priority": 1, "special": "western"},

        # PRIORITÁS 2: Fontos regionális központok
        "Pécs": {"station_type": "auto", "priority": 2, "special": "major_city"},
        "Győr": {"station_type": "auto", "priority": 2, "special": "major_city"},
        "Nyíregyháza": {"station_type": "auto", "priority": 2, "special": "eastern"},
        "Kecskemét": {"station_type": "auto", "priority": 2, "special": "central"},
        "Székesfehérvár": {"station_type": "auto", "priority": 2, "special": "central"},
        "Szolnok": {"station_type": "auto", "priority": 2, "special": "central"},
        "Tatabánya": {"station_type": "auto", "priority": 2, "special": "industrial"},
        "Kaposvár": {"station_type": "auto", "priority": 2, "special": "southern"},
        "Veszprém": {"station_type": "auto", "priority": 2, "special": "central"},
        "Zalaegerszeg": {"station_type": "auto", "priority": 2, "special": "western"},

        # PRIORITÁS 1+: Speciális meteorológiai állomások
        "Kékestető": {"station_type": "auto", "priority": 1, "special": "highest_point"},
        "Hegyhátsál": {"station_type": "auto", "priority": 1, "special": "climate_station"},
        "Martonvásár": {"station_type": "auto", "priority": 1, "special": "agricultural"},

        # PRIORITÁS 2: Repülőtéri és turisztikai állomások
        "Ferihegy": {"station_type": "auto", "priority": 2, "special": "airport"},
        "Balaton": {"station_type": "auto", "priority": 2, "special": "lake_region"}
    }

    def __init__(self, csv_path: str, db_path: str, meteostat_api_key: str) -> None:
        """
        Inicializálás teljes validációval

        Args:
            csv_path: SimpleMaps worldcities.csv fájl elérési útja
            db_path: Cél SQLite adatbázis elérési útja
            meteostat_api_key: Meteostat API kulcs

        Raises:
            ValueError: Invalid paraméterek esetén
            FileNotFoundError: CSV fájl nem található
        """
        self.csv_path = Path(csv_path)
        self.db_path = Path(db_path)
        self.meteostat_api_key = meteostat_api_key

        # Input validáció
        if not self.meteostat_api_key or len(self.meteostat_api_key) < 10:
            raise ValueError("Érvénytelen Meteostat API kulcs")

        # Meteostat client inicializálása hibakezeléssel
        try:
            self.meteostat = MeteostatClient(meteostat_api_key)
        except Exception as e:
            logger.error(f"Meteostat client inicializálási hiba: {e}")
            raise

        # Statisztikák követése
        self.stats: Dict[str, Union[int, float]] = {
            'total_cities': 0,
            'hungarian_cities': 0,
            'cities_with_stations': 0,
            'meteostat_requests': 0,
            'processing_time': 0.0,
            'api_errors': 0,
            'validation_errors': 0
        }

        logger.info("🚀 CityDatabasePopulator inicializálva (Professional v2.1.0)")
        logger.info(f"📁 CSV fájl: {self.csv_path}")
        logger.info(f"🗄️ Adatbázis: {self.db_path}")
        logger.info(f"🔑 API kulcs hossza: {len(self.meteostat_api_key)} karakter")

    def create_database_schema(self) -> None:
        """
        SQLite adatbázis létrehozása optimalizált sémával és indexekkel

        Professional database design:
        - Normalized structure
        - Performance indexes
        - Constraint validation
        - Metadata tracking

        Raises:
            sqlite3.Error: Adatbázis műveleti hibák
        """
        logger.info("🏗️ Adatbázis séma létrehozása...")

        try:
            # Szülő könyvtár létrehozása ha nem létezik
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Régi adatbázis safe törlése
            if self.db_path.exists():
                backup_path = self.db_path.with_suffix(f'.backup_{int(time.time())}.db')
                self.db_path.rename(backup_path)
                logger.info(f"📦 Régi adatbázis archiválva: {backup_path}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Fő cities tábla optimalizált sémával
                cursor.execute('''
                    CREATE TABLE cities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        city TEXT NOT NULL,
                        lat REAL NOT NULL CHECK(lat >= -90 AND lat <= 90),
                        lon REAL NOT NULL CHECK(lon >= -180 AND lon <= 180),
                        country TEXT NOT NULL,
                        country_code TEXT NOT NULL CHECK(LENGTH(country_code) = 2),
                        population INTEGER CHECK(population >= 0),
                        continent TEXT,
                        admin_name TEXT,
                        capital TEXT,
                        timezone TEXT,

                        -- Meteostat integráció metaadatok
                        meteostat_station_id TEXT,
                        meteostat_station_name TEXT,
                        station_elevation REAL,
                        station_distance REAL CHECK(station_distance >= 0),
                        station_inventory TEXT,

                        -- HungaroMet prioritás és minőség
                        hungaromet_priority INTEGER CHECK(hungaromet_priority BETWEEN 1 AND 5),
                        data_quality_score INTEGER CHECK(data_quality_score BETWEEN 1 AND 10),
                        last_data_update DATE,

                        -- Audit trail
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        -- Constraints
                        UNIQUE(city, country_code, lat, lon)
                    )
                ''')

                # Performance indexek létrehozása
                performance_indexes = [
                    "CREATE INDEX idx_country_code ON cities (country_code)",
                    "CREATE INDEX idx_population_desc ON cities (population DESC) WHERE population IS NOT NULL",
                    "CREATE INDEX idx_data_quality_country ON cities (country_code, data_quality_score DESC) WHERE data_quality_score IS NOT NULL",
                    "CREATE INDEX idx_meteostat_stations ON cities (meteostat_station_id) WHERE meteostat_station_id IS NOT NULL",
                    "CREATE INDEX idx_coordinates ON cities (lat, lon)",
                    "CREATE INDEX idx_hungaromet_priority ON cities (country_code, hungaromet_priority) WHERE hungaromet_priority IS NOT NULL",
                    "CREATE INDEX idx_station_distance ON cities (station_distance) WHERE station_distance IS NOT NULL",
                    "CREATE INDEX idx_continent_population ON cities (continent, population DESC) WHERE continent IS NOT NULL AND population IS NOT NULL",
                    "CREATE INDEX idx_city_name_search ON cities (city COLLATE NOCASE)",
                    "CREATE INDEX idx_updated_at ON cities (updated_at DESC)"
                ]

                for index_sql in performance_indexes:
                    cursor.execute(index_sql)
                    logger.debug(f"✅ Index létrehozva: {index_sql.split()[2]}")

                # Metaadat tábla audit trail-lel
                cursor.execute('''
                    CREATE TABLE generation_metadata (
                        id INTEGER PRIMARY KEY,
                        generation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        csv_file_path TEXT NOT NULL,
                        total_cities INTEGER NOT NULL,
                        hungarian_cities INTEGER NOT NULL,
                        cities_with_stations INTEGER NOT NULL,
                        meteostat_requests INTEGER NOT NULL,
                        api_errors INTEGER DEFAULT 0,
                        validation_errors INTEGER DEFAULT 0,
                        processing_time_seconds REAL NOT NULL,
                        meteostat_api_key_hash TEXT NOT NULL,
                        version TEXT DEFAULT '2.1.0'
                    )
                ''')

                # Error log tábla hibakereséshez
                cursor.execute('''
                    CREATE TABLE processing_errors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        city_name TEXT,
                        error_type TEXT NOT NULL,
                        error_message TEXT NOT NULL,
                        processing_step TEXT
                    )
                ''')

                conn.commit()
                logger.info("✅ Adatbázis séma sikeresen létrehozva (optimalizált indexekkel)")

        except sqlite3.Error as e:
            logger.error(f"❌ Adatbázis séma létrehozási hiba: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Váratlan hiba adatbázis létrehozáskor: {e}")
            raise

    def load_simplemaps_data(self) -> pd.DataFrame:
        """
        SimpleMaps worldcities.csv betöltése és professzionális előfeldolgozása

        Professional data validation:
        - Schema validation
        - Data type conversion
        - Null handling
        - Coordinate validation
        - Duplicate detection

        Returns:
            Validált és tisztított Pandas DataFrame

        Raises:
            FileNotFoundError: CSV fájl nem található
            ValueError: Invalid CSV struktúra
            pd.errors.ParserError: CSV parsing hibák
        """
        logger.info("📊 SimpleMaps CSV betöltése és validálása...")

        if not self.csv_path.exists():
            raise FileNotFoundError(f"SimpleMaps CSV nem található: {self.csv_path}")

        try:
            # CSV betöltése robusztus parserolással
            df = pd.read_csv(
                self.csv_path,
                encoding='utf-8',
                low_memory=False,
                na_values=['', 'NULL', 'null', 'N/A', 'n/a', '#N/A'],
                keep_default_na=True
            )
            logger.info(f"📈 CSV sikeresen betöltve: {len(df):,} rekord")

            # Oszlopok standardizálása
            df.columns = df.columns.str.lower().str.strip()

            # Szükséges oszlopok validálása
            required_columns = ['city', 'lat', 'lng', 'country', 'iso2']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValueError(f"Hiányzó kötelező oszlopok: {missing_columns}")

            # Oszlopnevek normalizálása
            column_mapping = {
                'lng': 'lon',
                'iso2': 'country_code',
                'admin_name': 'admin_name',
                'capital': 'capital',
                'population': 'population'
            }

            df = df.rename(columns=column_mapping)
            logger.info("✅ Oszlopnevek normalizálva")

            # Kritikus mezők null check
            critical_nulls = df[['city', 'lat', 'lon', 'country', 'country_code']].isnull().sum()
            if critical_nulls.any():
                logger.warning(f"⚠️ Hiányzó kritikus adatok: {critical_nulls[critical_nulls > 0].to_dict()}")

            # Adattisztítás és validálás
            df = self._clean_and_validate_data(df)

            # Duplikátumok kezelése
            original_count = len(df)
            df = df.drop_duplicates(subset=['city', 'country_code', 'lat', 'lon'], keep='first')
            duplicates_removed = original_count - len(df)

            if duplicates_removed > 0:
                logger.info(f"🔄 Duplikátumok eltávolítva: {duplicates_removed}")

            self.stats['total_cities'] = len(df)
            logger.info(f"✅ SimpleMaps adatok sikeresen feldolgozva: {len(df):,} érvényes rekord")

            return df

        except pd.errors.ParserError as e:
            logger.error(f"❌ CSV parsing hiba: {e}")
            self.stats['validation_errors'] += 1
            raise
        except Exception as e:
            logger.error(f"❌ SimpleMaps betöltési hiba: {e}")
            self.stats['validation_errors'] += 1
            raise

    def _clean_and_validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adattisztítás és validálás professzionális végrehajtása

        Args:
            df: Nyers DataFrame

        Returns:
            Tisztított és validált DataFrame
        """
        logger.info("🧹 Adattisztítás és validálás...")

        original_count = len(df)

        # String mezők tisztítása
        string_columns = ['city', 'country', 'country_code', 'admin_name', 'capital']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', pd.NA)

        # Kötelező mezők null értékeinek eltávolítása
        df = df.dropna(subset=['city', 'lat', 'lon', 'country', 'country_code'])

        # Country code standardizálása
        df['country_code'] = df['country_code'].str.upper()
        df = df[df['country_code'].str.len() == 2]  # Csak ISO-2 kódok

        # Koordináták validálása
        coordinate_mask = (
            (df['lat'] >= -90) & (df['lat'] <= 90) &
            (df['lon'] >= -180) & (df['lon'] <= 180) &
            (df['lat'] != 0) & (df['lon'] != 0)  # Null Island kizárása
        )
        df = df[coordinate_mask]

        # Populáció tisztítása
        if 'population' in df.columns:
            df['population'] = pd.to_numeric(df['population'], errors='coerce')
            df['population'] = df['population'].where(df['population'] > 0)

        # Város névvalidáció
        df = df[df['city'].str.len() >= 2]  # Min 2 karakter
        df = df[~df['city'].str.contains(r'^\d+$', regex=True, na=False)]  # Nem csak számok

        invalid_count = original_count - len(df)
        if invalid_count > 0:
            logger.warning(f"⚠️ Érvénytelen rekordok eltávolítva: {invalid_count}")
            self.stats['validation_errors'] += invalid_count

        logger.info(f"✅ Adattisztítás befejezve: {len(df):,} érvényes rekord")
        return df

    def enhance_hungarian_cities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Magyar városok Meteostat állomásokkal való kiegészítése
        JAVÍTOTT None-safe implementációval

        Args:
            df: Cities DataFrame

        Returns:
            Kiegészített DataFrame Meteostat állomásadatokkal

        Raises:
            MeteostatAPIError: API kommunikációs hibák esetén
        """
        logger.info("🇭🇺 Magyar városok Meteostat állomásokkal való kiegészítése...")

        hungarian_cities = df[df['country_code'] == 'HU'].copy()
        self.stats['hungarian_cities'] = len(hungarian_cities)

        if len(hungarian_cities) == 0:
            logger.warning("⚠️ Nincsenek magyar városok a CSV-ben")
            return df

        logger.info(f"📊 Feldolgozandó magyar városok: {len(hungarian_cities)}")

        enhanced_count = 0
        error_count = 0

        for idx, city in hungarian_cities.iterrows():
            city_name = city['city']

            try:
                logger.info(f"🔍 Feldolgozás: {city_name} ({enhanced_count + 1}/{len(hungarian_cities)})")

                # JAVÍTÁS: Meteostat közeli állomások lekérdezése HELYES radius paraméterrel
                # Radius MÉTERBEN van! 50 km = 50000 méter
                nearby_stations = self.meteostat.get_nearby_stations(
                    city['lat'], city['lon'], limit=5, radius=50000  # 50 km = 50000 méter
                )
                self.stats['meteostat_requests'] += 1

                if nearby_stations and len(nearby_stations) > 0:
                    logger.info(f"  ✅ Találat: {len(nearby_stations)} közeli állomás")

                    # Legjobb állomás kiválasztása
                    best_station = self._select_best_station(nearby_stations, city.to_dict())

                    if best_station:
                        logger.info(f"  🎯 Legjobb állomás: {best_station.name} ({best_station.distance:.1f} km)")

                        # Állomás metaadatok lekérdezése
                        station_meta = self.meteostat.get_station_meta(best_station.id)
                        self.stats['meteostat_requests'] += 1

                        if station_meta:
                            # DataFrame frissítése safe módon
                            df.at[idx, 'meteostat_station_id'] = station_meta.id
                            df.at[idx, 'meteostat_station_name'] = station_meta.name
                            df.at[idx, 'station_elevation'] = station_meta.elevation
                            df.at[idx, 'station_distance'] = best_station.distance

                            # Inventory JSON formátumban safe módon
                            if station_meta.inventory:
                                try:
                                    inventory_json = json.dumps(station_meta.inventory)
                                    df.at[idx, 'station_inventory'] = inventory_json
                                except (TypeError, ValueError) as e:
                                    logger.warning(f"  ⚠️ Inventory serialization hiba: {e}")

                            # HungaroMet prioritás hozzáadása
                            hungaromet_data = self.HUNGARIAN_PRIORITY_CITIES.get(city_name, {})
                            df.at[idx, 'hungaromet_priority'] = hungaromet_data.get('priority', 3)

                            # JAVÍTOTT Adatminőség pontszám számítása None-safe módon
                            df.at[idx, 'data_quality_score'] = self._calculate_quality_score_safe(
                                station_meta, hungaromet_data, best_station.distance
                            )

                            # Utolsó frissítés timestamp
                            df.at[idx, 'last_data_update'] = datetime.now().strftime('%Y-%m-%d')

                            enhanced_count += 1
                            self.stats['cities_with_stations'] += 1

                            logger.info(f"  ✅ Állomás sikeresen párosítva: {station_meta.name} ({best_station.distance:.1f} km)")
                        else:
                            logger.warning(f"  ❌ Állomás metaadatok nem elérhetők: {best_station.id}")
                            error_count += 1
                    else:
                        logger.warning("  ❌ Nincs megfelelő állomás 50 km-es körzetben")
                        error_count += 1
                else:
                    logger.warning("  ❌ Nincs közeli állomás 50 km-es körzetben")
                    error_count += 1

                # Professional rate limiting (500 kérés/hónap limit)
                time.sleep(0.2)  # Max 5 kérés/sec

            except MeteostatAPIError as e:
                logger.error(f"❌ Meteostat API hiba {city_name}-nél: {e}")
                self._log_processing_error(city_name, "MeteostatAPIError", str(e), "station_lookup")
                self.stats['api_errors'] += 1
                error_count += 1
                continue
            except Exception as e:
                logger.error(f"❌ Váratlan hiba {city_name}-nél: {e}")
                self._log_processing_error(city_name, "UnexpectedError", str(e), "city_enhancement")
                error_count += 1
                continue

        success_rate = (enhanced_count / len(hungarian_cities)) * 100 if len(hungarian_cities) > 0 else 0

        logger.info("=" * 60)
        logger.info("🇭🇺 MAGYAR VÁROSOK KIEGÉSZÍTÉS BEFEJEZVE")
        logger.info("=" * 60)
        logger.info(f"✅ Sikeresen kiegészített városok: {enhanced_count}/{len(hungarian_cities)} ({success_rate:.1f}%)")
        logger.info(f"❌ Hibás városok: {error_count}")
        logger.info(f"🔗 Meteostat API kérések: {self.stats['meteostat_requests']}")
        logger.info(f"⚠️ API hibák: {self.stats['api_errors']}")
        logger.info("=" * 60)

        return df

    def _select_best_station(self, stations: List[MeteostatStation], city: Dict[str, Any]) -> Optional[MeteostatStation]:
        """
        Legjobb meteorológiai állomás kiválasztása városhoz
        Professional scoring algorithmusal

        Args:
            stations: Közeli állomások listája
            city: Város adatai

        Returns:
            Legjobb állomás vagy None ha nincs megfelelő
        """
        if not stations or len(stations) == 0:
            return None

        best_station = None
        best_score = -1.0

        logger.debug(f"  🔍 Állomás értékelés: {len(stations)} kandidátus")

        for station in stations:
            try:
                # Távolság validálás
                if not station.distance or station.distance > 50:  # Max 50 km
                    logger.debug(f"    ❌ Túl távoli állomás: {station.name} ({station.distance} km)")
                    continue

                # Pontszám számítása
                score = self._calculate_station_score(station, city)

                logger.debug(f"    📊 {station.name}: {score:.2f} pont ({station.distance:.1f} km)")

                if score > best_score:
                    best_score = score
                    best_station = station

            except Exception as e:
                logger.warning(f"    ⚠️ Állomás értékelési hiba {station.name}: {e}")
                continue

        if best_station:
            logger.debug(f"  🏆 Győztes állomás: {best_station.name} ({best_score:.2f} pont)")

        return best_station

    def _calculate_station_score(self, station: MeteostatStation, city: Dict[str, Any]) -> float:
        """
        Állomás pontszám számítása professzionális kritériumokkal

        Args:
            station: Meteostat állomás
            city: Város adatai

        Returns:
            Pontszám (0-10 skála)
        """
        score = 5.0  # alapértelmezett középérték

        try:
            # Távolság pontszám (minél közelebb, annál jobb)
            if station.distance is not None:
                if station.distance <= 5:
                    score += 3.0  # Nagyon közeli
                elif station.distance <= 15:
                    score += 2.0  # Közeli
                elif station.distance <= 30:
                    score += 1.0  # Elfogadható
                else:
                    score -= 1.0  # Távoli

            # Inventory alapú adatminőség bónusz
            if hasattr(station, 'inventory') and station.inventory:
                inventory = station.inventory

                # Daily data bónusz - JAVÍTOTT None-safe check
                daily_data = self._safe_inventory_check(inventory, 'daily', 'end')
                if daily_data and isinstance(daily_data, str) and daily_data >= '2020-01-01':
                    score += 2.0
                elif daily_data and isinstance(daily_data, str) and daily_data >= '2015-01-01':
                    score += 1.0

                # Hourly data bónusz
                hourly_data = self._safe_inventory_check(inventory, 'hourly', 'end')
                if hourly_data and isinstance(hourly_data, str) and hourly_data >= '2020-01-01':
                    score += 1.0

            # Ország egyezés bónusz
            if hasattr(station, 'country') and station.country == "HU":
                score += 2.0

            # Név hasonlóság bónusz
            city_name = city.get('city', '').lower()
            station_name = getattr(station, 'name', '').lower()
            if city_name and station_name and city_name in station_name:
                score += 1.0

            # Elevation információ bónusz
            if hasattr(station, 'elevation') and station.elevation is not None:
                score += 0.5

        except Exception as e:
            logger.warning(f"Állomás pontszám számítási hiba: {e}")
            score = 3.0  # Fallback score

        return max(0.0, min(10.0, score))

    def _safe_inventory_check(self, inventory: Optional[Dict[str, Any]], section: str, field: str) -> Optional[str]:
        """
        KRITIKUS JAVÍTÁS: None-safe inventory field extraction

        Ez a metódus megoldja a TypeError: None >= '2023-01-01' hibát!

        Args:
            inventory: Inventory dict (lehet None)
            section: Inventory szekció ('daily', 'hourly', stb.)
            field: Mező név ('start', 'end', stb.)

        Returns:
            Field érték vagy None ha nem létezik/érvénytelen
        """
        try:
            if not inventory or not isinstance(inventory, dict):
                return None

            section_data = inventory.get(section)
            if not section_data or not isinstance(section_data, dict):
                return None

            field_value = section_data.get(field)

            # KRITIKUS: None check és type validation
            if field_value is None:
                return None

            # String típus biztosítása
            if isinstance(field_value, str) and len(field_value) >= 10:  # YYYY-MM-DD format
                return field_value

            return None

        except (AttributeError, TypeError, KeyError) as e:
            logger.debug(f"Safe inventory check hiba: {e}")
            return None

    def _calculate_quality_score_safe(self, station: MeteostatStation, hungaromet_data: Dict[str, Any], distance: float) -> int:
        """
        KRITIKUSAN JAVÍTOTT Adatminőség pontszám számítása 1-10 skálán.
        Teljesen None-safe implementáció a TypeError elkerülésére.

        Args:
            station: Meteostat állomás
            hungaromet_data: HungaroMet prioritás adatok
            distance: Távolság km-ben

        Returns:
            Adatminőség pontszám (1-10)
        """
        try:
            score = 5  # alapértelmezett középérték

            # HungaroMet prioritás bónusz
            priority = hungaromet_data.get('priority', 3)
            if priority == 1:
                score += 3
            elif priority == 2:
                score += 1

            # Távolság alapú pontszám - KRITIKUS None-check hozzáadva
            if distance is not None:  # Hozzáadott None-check
                if distance < 5:
                    score += 2
                elif distance < 15:
                    score += 1
                elif distance > 30:
                    score -= 1
                elif distance > 45:
                    score -= 2

            # Adatok teljessége - None-safe módon
            if hasattr(station, 'inventory') and station.inventory:
                inventory = station.inventory

                # Daily data minőség - BIZTONSÁGOS ELLENŐRZÉS
                daily_end = self._safe_inventory_check(inventory, 'daily', 'end')
                if daily_end and daily_end >= '2023-01-01':  # Csak akkor hasonlítunk, ha nem None
                    score += 2
                elif daily_end and daily_end >= '2020-01-01':
                    score += 1

                # Hourly data minőség - BIZTONSÁGOS ELLENŐRZÉS
                hourly_end = self._safe_inventory_check(inventory, 'hourly', 'end')
                if hourly_end and hourly_end >= '2020-01-01':  # Csak akkor hasonlítunk, ha nem None
                    score += 1

                # Recent data availability - BIZTONSÁGOS ELLENŐRZÉS
                daily_start = self._safe_inventory_check(inventory, 'daily', 'start')
                if daily_start and daily_start <= '1990-01-01':  # Csak akkor hasonlítunk, ha nem None
                    score += 1  # Historical data bónusz

            # Elevation információ
            if hasattr(station, 'elevation') and station.elevation is not None:
                score += 1

            # Speciális állomások bónusz
            special_type = hungaromet_data.get('special')
            if special_type in ['capital', 'highest_point', 'climate_station']:
                score += 2
            elif special_type in ['major_city', 'nuclear_plant']:
                score += 1

            # Country match bónusz
            if hasattr(station, 'country') and station.country == "HU":
                score += 1

        except Exception as e:
            logger.warning(f"Quality score számítási hiba: {e}")
            score = 3  # Biztonságos fallback érték

        return max(1, min(10, int(score)))  # Biztosítjuk, hogy int legyen

    def _log_processing_error(self, city_name: str, error_type: str, error_message: str, processing_step: str) -> None:
        """
        Processing hibák naplózása adatbázisba audit trail céljából

        Args:
            city_name: Érintett város neve
            error_type: Hiba típusa
            error_message: Hiba üzenet
            processing_step: Processing lépés ahol a hiba történt
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO processing_errors (city_name, error_type, error_message, processing_step)
                    VALUES (?, ?, ?, ?)
                ''', (city_name, error_type, error_message, processing_step))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error logging hiba: {e}")

    def save_to_database(self, df: pd.DataFrame) -> None:
        """
        DataFrame mentése SQLite adatbázisba batch módban
        Professional database operations with transaction safety
        JAVÍTOTT: pandas NaType → None konverzió (SQLite compatibility)

        Args:
            df: Városadatok DataFrame

        Raises:
            sqlite3.Error: Adatbázis műveleti hibák
        """
        logger.info("💾 Adatok mentése SQLite adatbázisba...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("BEGIN TRANSACTION")

                # Cities tábla feltöltése batch módban
                records_to_insert = []

                for _, row in df.iterrows():
                    try:
                        # KRITIKUS JAVÍTÁS: pandas NaType → None konverzió minden mezőnél
                        def safe_value(value):
                            """Pandas NaType safe konverzió None-ra."""
                            if pd.isna(value):
                                return None
                            return value

                        record = (
                            safe_value(row['city']),
                            float(row['lat']),
                            float(row['lon']),
                            safe_value(row['country']),
                            safe_value(row['country_code']),
                            int(row.get('population')) if pd.notna(row.get('population')) else None,
                            safe_value(row.get('continent')),        # JAVÍTVA
                            safe_value(row.get('admin_name')),       # JAVÍTVA
                            safe_value(row.get('capital')),          # JAVÍTVA
                            safe_value(row.get('timezone')),         # JAVÍTVA - Ez volt a 9. paraméter!
                            safe_value(row.get('meteostat_station_id')),     # JAVÍTVA
                            safe_value(row.get('meteostat_station_name')),   # JAVÍTVA
                            float(row.get('station_elevation')) if pd.notna(row.get('station_elevation')) else None,
                            float(row.get('station_distance')) if pd.notna(row.get('station_distance')) else None,
                            safe_value(row.get('station_inventory')),        # JAVÍTVA
                            int(row.get('hungaromet_priority')) if pd.notna(row.get('hungaromet_priority')) else None,
                            int(row.get('data_quality_score')) if pd.notna(row.get('data_quality_score')) else None,
                            safe_value(row.get('last_data_update'))          # JAVÍTVA
                        )
                        records_to_insert.append(record)

                    except (ValueError, TypeError) as e:
                        logger.warning(f"Rekord conversion hiba {row['city']}: {e}")
                        self.stats['validation_errors'] += 1
                        continue

                # Batch insert végrehajtása
                cursor = conn.cursor()
                cursor.executemany('''
                    INSERT INTO cities (
                        city, lat, lon, country, country_code, population,
                        continent, admin_name, capital, timezone,
                        meteostat_station_id, meteostat_station_name,
                        station_elevation, station_distance, station_inventory,
                        hungaromet_priority, data_quality_score, last_data_update
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', records_to_insert)

                # Metaadat mentése
                cursor.execute('''
                    INSERT INTO generation_metadata (
                        csv_file_path, total_cities, hungarian_cities,
                        cities_with_stations, meteostat_requests, api_errors,
                        validation_errors, processing_time_seconds, meteostat_api_key_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(self.csv_path),
                    self.stats['total_cities'],
                    self.stats['hungarian_cities'],
                    self.stats['cities_with_stations'],
                    self.stats['meteostat_requests'],
                    self.stats['api_errors'],
                    self.stats['validation_errors'],
                    self.stats['processing_time'],
                    hash(self.meteostat_api_key)
                ))

                conn.execute("COMMIT")
                logger.info(f"✅ Adatbázis sikeresen mentve: {len(records_to_insert):,} rekord")

        except sqlite3.Error as e:
            logger.error(f"❌ Adatbázis mentési hiba: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Váratlan hiba mentés során: {e}")
            raise

    def validate_database(self) -> None:
        """
        Adatbázis validálása és részletes statisztikák kiírása
        Professional data quality assessment
        """
        logger.info("🔍 Adatbázis validálása és minőség ellenőrzése...")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Alapstatisztikák lekérdezése
                cursor.execute("SELECT COUNT(*) FROM cities")
                total_cities = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM cities WHERE country_code = 'HU'")
                hungarian_cities = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM cities WHERE meteostat_station_id IS NOT NULL")
                cities_with_stations = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM cities WHERE country_code = 'HU' AND meteostat_station_id IS NOT NULL")
                hungarian_cities_with_stations = cursor.fetchone()[0]

                # Adatminőség statisztikák
                cursor.execute('''
                    SELECT AVG(data_quality_score), MIN(data_quality_score), MAX(data_quality_score)
                    FROM cities
                    WHERE country_code = 'HU' AND data_quality_score IS NOT NULL
                ''')
                quality_stats = cursor.fetchone()

                # Top 10 magyar város adatminőség szerint
                cursor.execute('''
                    SELECT city, data_quality_score, meteostat_station_name,
                           ROUND(station_distance, 1) as distance
                    FROM cities
                    WHERE country_code = 'HU' AND meteostat_station_id IS NOT NULL
                    ORDER BY data_quality_score DESC, station_distance ASC
                    LIMIT 10
                ''')
                top_hungarian_cities = cursor.fetchall()

                # Error summary
                cursor.execute("SELECT COUNT(*) FROM processing_errors")
                total_errors = cursor.fetchone()[0]

                # Kontinens eloszlás
                cursor.execute('''
                    SELECT continent, COUNT(*) as count
                    FROM cities
                    WHERE continent IS NOT NULL
                    GROUP BY continent
                    ORDER BY count DESC
                    LIMIT 5
                ''')
                continent_distribution = cursor.fetchall()

                # Success rate számítás
                hungarian_success_rate = (hungarian_cities_with_stations / hungarian_cities * 100) if hungarian_cities > 0 else 0
                global_station_coverage = (cities_with_stations / total_cities * 100) if total_cities > 0 else 0

                # Eredmények megjelenítése
                logger.info("=" * 80)
                logger.info("🏆 ADATBÁZIS VALIDÁCIÓS EREDMÉNYEK - PROFESSIONAL REPORT")
                logger.info("=" * 80)
                logger.info("📊 ALAPSTATISZTIKÁK:")
                logger.info(f"   Összes város: {total_cities:,}")
                logger.info(f"   Magyar városok: {hungarian_cities}")
                logger.info(f"   Meteorológiai állomással rendelkező városok: {cities_with_stations:,}")
                logger.info(f"   Magyar városok állomásokkal: {hungarian_cities_with_stations}/{hungarian_cities} ({hungarian_success_rate:.1f}%)")
                logger.info("")
                logger.info("🌐 GLOBAL COVERAGE:")
                logger.info(f"   Állomás lefedettség: {global_station_coverage:.2f}%")
                logger.info("")
                logger.info("🔗 API STATISZTIKÁK:")
                logger.info(f"   Meteostat API kérések: {self.stats['meteostat_requests']}")
                logger.info(f"   API hibák: {self.stats['api_errors']}")
                logger.info(f"   Validációs hibák: {self.stats['validation_errors']}")
                logger.info(f"   Összes processing hiba: {total_errors}")
                logger.info(f"   Feldolgozási idő: {self.stats['processing_time']:.2f} másodperc")
                logger.info("")

                if quality_stats and quality_stats[0]:
                    logger.info("📈 MAGYAR VÁROSOK ADATMINŐSÉG:")
                    logger.info(f"   Átlagos minőség: {quality_stats[0]:.1f}/10")
                    logger.info(f"   Legalacsonyabb: {quality_stats[1]}/10")
                    logger.info(f"   Legmagasabb: {quality_stats[2]}/10")
                    logger.info("")

                logger.info("🏅 TOP 10 MAGYAR VÁROS (adatminőség szerint):")
                logger.info("-" * 80)
                for i, (city, quality, station, distance) in enumerate(top_hungarian_cities, 1):
                    logger.info(f"{i:2d}. {city:.<25} {quality}/10 | {station} ({distance} km)")
                logger.info("")

                if continent_distribution:
                    logger.info("🌍 KONTINENS ELOSZLÁS (Top 5):")
                    logger.info("-" * 40)
                    for continent, count in continent_distribution:
                        logger.info(f"   {continent}: {count:,} város")
                    logger.info("")

                logger.info("=" * 80)
                logger.info("✅ ADATBÁZIS SIKERESEN LÉTREHOZVA ÉS VALIDÁLVA!")
                logger.info("=" * 80)

        except sqlite3.Error as e:
            logger.error(f"❌ Adatbázis validációs hiba: {e}")
            raise

    def run(self) -> None:
        """
        Teljes adatbázis generálási folyamat futtatása
        Professional orchestration with comprehensive error handling

        Raises:
            Exception: Kritikus hibák esetén
        """
        start_time = time.time()

        try:
            logger.info("🚀 Város-adatbázis generálás kezdése (Professional v2.1.0)...")
            logger.info("=" * 80)

            # 1. Adatbázis séma létrehozása
            self.create_database_schema()

            # 2. SimpleMaps adatok betöltése és validálása
            df = self.load_simplemaps_data()

            # 3. Magyar városok kiegészítése Meteostat állomásokkal (JAVÍTOTT)
            df = self.enhance_hungarian_cities(df)

            # 4. Adatbázis mentése batch módban
            self.save_to_database(df)

            # 5. Adatbázis validálása és minőség ellenőrzése
            self.validate_database()

            # Feldolgozási idő frissítése
            self.stats['processing_time'] = time.time() - start_time

            logger.info("")
            logger.info("🎉 VÁROS-ADATBÁZIS GENERÁLÁS SIKERESEN BEFEJEZVE!")
            logger.info(f"⏱️ Teljes feldolgozási idő: {self.stats['processing_time']:.2f} másodperc")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ KRITIKUS HIBA a generálás során: {e}")
            logger.error("💡 Ellenőrizd a log fájlokat és az API kulcsot!")
            raise


def main() -> int:
    """
    Főprogram - parancssori futtatás professional error handling-gel

    Returns:
        Exit kód (0=success, 1=error)
    """
    try:
        # Környezeti változók betöltése
        load_dotenv()

        # Konfigurációk - JAVÍTOTT elérési útvonalak
        csv_path = "worldcities.csv"  # JAVÍTVA: scripts/ könyvtárban futtatva
        db_path = "../src/data/cities.db"  # JAVÍTVA: relatív elérési út
        api_key = os.getenv("METEOSTAT_API_KEY")

        # Input validációk
        if not api_key:
            logger.error("❌ METEOSTAT_API_KEY környezeti változó hiányzik!")
            logger.error("💡 Hozz létre .env fájlt az API kulccsal!")
            return 1

        if not Path(csv_path).exists():
            logger.error(f"❌ SimpleMaps CSV nem található: {csv_path}")
            logger.error("💡 Töltsd le a worldcities.csv fájlt a SimpleMaps-ról!")
            logger.info(f"🔍 Aktuális könyvtár: {os.getcwd()}")
            logger.info(f"📁 Keresett fájl: {Path(csv_path).absolute()}")
            return 1

        # Logs könyvtár már létrehozva modul szinten
        # Path("logs").mkdir(exist_ok=True)  # Eltávolítva, mert fentebb már megtörtént

        # Generátor létrehozása és futtatása
        populator = CityDatabasePopulator(csv_path, db_path, api_key)
        populator.run()

        logger.info("🎯 Program sikeresen befejezve!")
        return 0

    except FileNotFoundError as e:
        logger.error(f"❌ Fájl nem található: {e}")
        return 1
    except ValueError as e:
        logger.error(f"❌ Konfigurációs hiba: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Váratlan hiba: {e}")
        logger.exception("Full stacktrace:")
        return 1


if __name__ == "__main__":
    exit(main())
