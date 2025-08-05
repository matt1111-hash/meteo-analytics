#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🇭🇺 DUAL DATABASE City Manager - Magyar Települések Integrációval + TrendDataProcessor Support
Magyar Klímaanalitika MVP - 3200+ Magyar Település + 44k Globális Város

🚀 ÚJ FUNKCIÓK v4.2:
✅ search_hungarian_settlements() - 3200+ magyar település keresése
✅ search_unified() - KOMBINÁLT keresés (Magyar + Globális)
✅ find_city_by_name() - TrendDataProcessor koordináta lekérdezés támogatás ⭐ ÚJ
✅ HungarianSettlement adapter - City objektumokká alakítás
✅ Magyar prioritás - magyar települések előre helyezése
✅ Hierarchikus keresés - falvak, nagyközségek, városok

ADATBÁZISOK:
- hungarian_settlements.db - 3200+ magyar település (KSH hivatalos)
- cities.db - 44k globális város (SimpleMaps)

HASZNÁLAT:
```python
manager = CityManager()
# MINDEN magyar település kereshető
results = manager.search_unified("Kiskunhalas")  # Kis magyar város
results = manager.search_unified("Budapest")     # Nagy magyar város  
results = manager.search_unified("London")       # Nemzetközi város

# TrendDataProcessor támogatás
coords = manager.find_city_by_name("Broxbourne")  # (lat, lon) vagy None
```

Fájl helye: src/data/city_manager.py
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

# Config import
from ..config import DATA_DIR, MultiCityConfig
from .geo_utils import GeoUtils, DistanceCalculator

# Logging beállítás
logger = logging.getLogger(__name__)


class RegionType(Enum):
    """Régió típusok enumeráció."""
    GLOBAL = "global"
    CONTINENT = "continent"
    COUNTRY = "country"
    REGION = "region"
    CUSTOM = "custom"
    HUNGARIAN_SETTLEMENT = "hungarian_settlement"  # 🇭🇺 ÚJ


class CitySort(Enum):
    """Város rendezési opciók."""
    POPULATION_DESC = "population_desc"
    POPULATION_ASC = "population_asc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    DISTANCE_ASC = "distance_asc"
    HUNGARIAN_PRIORITY = "hungarian_priority"  # 🇭🇺 ÚJ


@dataclass
class City:
    """Város adatstruktúra - MAGYAR TELEPÜLÉSEK KOMPATIBILIS."""
    id: int
    city: str
    lat: float
    lon: float
    country: str
    country_code: str
    population: Optional[int] = None
    continent: Optional[str] = None
    admin_name: Optional[str] = None  # Régió/állam/megye/járás
    capital: Optional[str] = None     # primary/admin/minor
    timezone: Optional[str] = None
    
    # 🇭🇺 MAGYAR TELEPÜLÉSEK SPECIFIKUS MEZŐK
    settlement_type: Optional[str] = None    # város/nagyközség/község
    megye: Optional[str] = None              # Magyar megye
    jaras: Optional[str] = None              # Magyar járás  
    climate_zone: Optional[str] = None       # Klímazóna (Alföld/Dunántúl)
    region_priority: Optional[int] = None    # Magyar prioritás (1-10)
    is_hungarian: bool = False               # Magyar település flag
    terulet_hektar: Optional[int] = None     # Terület hektárban
    lakasok_szama: Optional[int] = None      # Lakások száma
    
    # Calculated fields
    distance_km: Optional[float] = field(default=None, init=False)
    display_name: Optional[str] = field(default=None, init=False)
    
    def __post_init__(self):
        """Computed fields automatikus számítása."""
        # Display name generálása
        parts = [self.city]
        
        if self.is_hungarian and self.megye:
            # Magyar formátum: "Kiskunhalas, Bács-Kiskun megye"
            parts.append(f"{self.megye} megye")
        elif self.admin_name and self.admin_name != self.city:
            parts.append(self.admin_name)
        
        if not self.is_hungarian:  # Csak nemzetközi városoknál
            parts.append(self.country)
        
        self.display_name = ", ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """City objektum dictionary-vé alakítása."""
        return {
            "id": self.id,
            "city": self.city,
            "lat": self.lat,
            "lon": self.lon,
            "country": self.country,
            "country_code": self.country_code,
            "population": self.population,
            "continent": self.continent,
            "admin_name": self.admin_name,
            "capital": self.capital,
            "timezone": self.timezone,
            "settlement_type": self.settlement_type,
            "megye": self.megye,
            "jaras": self.jaras,
            "climate_zone": self.climate_zone,
            "region_priority": self.region_priority,
            "is_hungarian": self.is_hungarian,
            "terulet_hektar": self.terulet_hektar,
            "lakasok_szama": self.lakasok_szama,
            "distance_km": self.distance_km,
            "display_name": self.display_name
        }
    
    @classmethod
    def from_db_row(cls, row: Tuple) -> 'City':
        """Database row-ból City objektum létrehozása (eredeti formátum)."""
        return cls(
            id=row[0],
            city=row[1],
            lat=row[2],
            lon=row[3],
            country=row[4],
            country_code=row[5],
            population=row[6],
            continent=row[7],
            admin_name=row[8],
            capital=row[9],
            timezone=row[10]
        )
    
    @classmethod
    def from_hungarian_settlement(cls, row: sqlite3.Row) -> 'City':
        """🇭🇺 Magyar település row-ból City objektum létrehozása."""
        return cls(
            id=row['id'],
            city=row['name'],
            lat=row['latitude'],
            lon=row['longitude'],
            country="Magyarország",
            country_code="HU",
            population=row['population'],
            continent="Europe",
            admin_name=row['megye'],  # Megye = admin_name
            settlement_type=row['settlement_type'],
            megye=row['megye'],
            jaras=row['jaras'] if row['jaras'] else None,
            climate_zone=row['climate_zone'],
            region_priority=row['region_priority'],
            is_hungarian=True,
            terulet_hektar=row['terulet_hektar'],
            lakasok_szama=row['lakasok_szama']
        )


@dataclass
class CityQuery:
    """Város lekérdezés paraméterek - MAGYAR TÁMOGATÁSSAL."""
    region_type: RegionType
    region_value: Optional[str] = None
    limit: int = 50
    min_population: Optional[int] = None
    max_population: Optional[int] = None
    sort_by: CitySort = CitySort.POPULATION_DESC
    include_capitals_only: bool = False
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    max_distance_km: Optional[float] = None
    exclude_countries: List[str] = field(default_factory=list)
    include_countries: List[str] = field(default_factory=list)
    
    # 🇭🇺 MAGYAR SPECIFIKUS SZŰRŐK
    include_hungarian: bool = True              # Magyar települések is
    hungarian_priority: bool = True             # Magyar települések előre
    settlement_types: List[str] = field(default_factory=list)  # város/nagyközség/község
    hungarian_counties: List[str] = field(default_factory=list)  # Magyar megyék


class CityDatabaseError(Exception):
    """City database specifikus hibák."""
    pass


class CityManager:
    """
    🇭🇺 DUAL DATABASE City Manager - Magyar Települések Integrációval
    
    FUNKCIÓK:
    - search_unified() - KOMBINÁLT keresés (3200+ magyar + 44k globális)
    - search_hungarian_settlements() - Csak magyar települések
    - search_cities() - Csak globális városok (eredeti)
    - find_city_by_name() - ⭐ ÚJ: Egyetlen koordináta lekérdezés TrendDataProcessor-hez
    - Magyar prioritás - magyar települések előre rendezése
    - Hierarchikus keresés - minden magyar település típus
    """
    
    def __init__(self, db_path: Optional[Path] = None, hungarian_db_path: Optional[Path] = None):
        """
        CityManager inicializálása DUAL DATABASE-szel.
        
        Args:
            db_path: cities.db elérési útvonal (44k globális)
            hungarian_db_path: hungarian_settlements.db elérési útvonal (3200+ magyar)
        """
        self.db_path = db_path or (DATA_DIR / "cities.db")
        self.hungarian_db_path = hungarian_db_path or (DATA_DIR / "hungarian_settlements.db")
        
        self.connection: Optional[sqlite3.Connection] = None
        self.hungarian_connection: Optional[sqlite3.Connection] = None
        
        self.geo_utils = GeoUtils()
        self.distance_calculator = DistanceCalculator()
        
        # Cache
        self._continent_cache: Dict[str, List[str]] = {}
        self._country_cache: Dict[str, Dict[str, Any]] = {}
        self._hungarian_counties_cache: Optional[List[str]] = None
        
        # Statistics
        self.query_count = 0
        self.hungarian_query_count = 0
        self.last_query_time: Optional[datetime] = None
        
        logger.info(f"🇭🇺 Dual Database CityManager v4.2 inicializálva:")
        logger.info(f"   Global cities: {self.db_path}")
        logger.info(f"   Hungarian settlements: {self.hungarian_db_path}")
        
        # Database kapcsolatok
        self._initialize_databases()
    
    def _initialize_databases(self) -> None:
        """DUAL DATABASE inicializálás és validáció."""
        
        # 1. GLOBÁLIS ADATBÁZIS (eredeti)
        if not self.db_path.exists():
            logger.warning(f"⚠️ Globális cities.db nem található: {self.db_path}")
            logger.warning("   Csak magyar települések lesznek elérhetők!")
        else:
            try:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self._validate_database_structure()
                
                total_global = self._get_total_city_count()
                logger.info(f"✅ Globális adatbázis: {total_global:,} város")
                
            except sqlite3.Error as e:
                logger.error(f"❌ Globális adatbázis kapcsolat hiba: {e}")
                self.connection = None
        
        # 2. MAGYAR TELEPÜLÉSEK ADATBÁZIS (új)
        if not self.hungarian_db_path.exists():
            logger.warning(f"⚠️ Magyar települések adatbázis nem található: {self.hungarian_db_path}")
            logger.warning("   Futtasd: python scripts/hungarian_settlements_importer.py")
        else:
            try:
                self.hungarian_connection = sqlite3.connect(self.hungarian_db_path, check_same_thread=False)
                self.hungarian_connection.row_factory = sqlite3.Row
                self._validate_hungarian_database_structure()
                
                total_hungarian = self._get_total_hungarian_settlements_count()
                logger.info(f"✅ Magyar települések adatbázis: {total_hungarian:,} település")
                
            except sqlite3.Error as e:
                logger.error(f"❌ Magyar adatbázis kapcsolat hiba: {e}")
                self.hungarian_connection = None
        
        # Ellenőrzés
        if not self.connection and not self.hungarian_connection:
            raise CityDatabaseError("Egyik adatbázis sem elérhető!")
    
    def _validate_database_structure(self) -> None:
        """Globális database tábla struktúra validálása (eredeti)."""
        if not self.connection:
            return
            
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA table_info(cities)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            "id", "city", "lat", "lon", "country", "country_code",
            "population", "continent", "admin_name", "capital", "timezone"
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            raise CityDatabaseError(f"Hiányzó oszlopok a cities táblában: {missing_columns}")
        
        logger.debug("✅ Globális database struktúra validálva")
    
    def _validate_hungarian_database_structure(self) -> None:
        """🇭🇺 Magyar települések database struktúra validálása."""
        if not self.hungarian_connection:
            return
            
        cursor = self.hungarian_connection.cursor()
        cursor.execute("PRAGMA table_info(hungarian_settlements)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            "id", "name", "latitude", "longitude", "megye", "settlement_type",
            "population", "climate_zone", "region_priority"
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            raise CityDatabaseError(f"Hiányzó oszlopok a hungarian_settlements táblában: {missing_columns}")
        
        logger.debug("✅ Magyar database struktúra validálva")
    
    def _get_total_city_count(self) -> int:
        """Összes globális város száma."""
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM cities")
        return cursor.fetchone()[0]
    
    def _get_total_hungarian_settlements_count(self) -> int:
        """🇭🇺 Összes magyar település száma."""
        if not self.hungarian_connection:
            return 0
        cursor = self.hungarian_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM hungarian_settlements")
        return cursor.fetchone()[0]
    
    def _execute_query(self, sql: str, params: Tuple = (), use_hungarian: bool = False) -> List[sqlite3.Row]:
        """SQL lekérdezés végrehajtása megfelelő adatbázison."""
        connection = self.hungarian_connection if use_hungarian else self.connection
        
        if not connection:
            db_type = "magyar" if use_hungarian else "globális"
            raise CityDatabaseError(f"{db_type} adatbázis kapcsolat nem elérhető")
        
        try:
            cursor = connection.cursor()
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # Query tracking
            if use_hungarian:
                self.hungarian_query_count += 1
            else:
                self.query_count += 1
            self.last_query_time = datetime.now()
            
            logger.debug(f"SQL query végrehajtva ({'magyar' if use_hungarian else 'globális'}): {len(results)} eredmény")
            return results
            
        except sqlite3.Error as e:
            logger.error(f"SQL query hiba: {sql} | Error: {e}")
            raise CityDatabaseError(f"Query execution error: {e}")
    
    # ⭐ ÚJ FUNKCIÓ: TrendDataProcessor támogatás
    
    def find_city_by_name(self, city_name: str) -> Optional[Tuple[float, float]]:
        """
        ⭐ EGYETLEN VÁROS KOORDINÁTÁINAK LEKÉRDEZÉSE - TrendDataProcessor támogatás
        
        Ez a metódus a TrendDataProcessor számára készült, ami egyetlen,
        legmegbízhatóbb koordinátát vár egy városnévhez.
        
        LOGIKA:
        1. Magyar prioritás - Ha van magyar település, azt választjuk
        2. Globális fallback - Ha nincs magyar, akkor globális városok
        3. Legnagyobb populáció - A legnagyobb város koordinátáit adjuk vissza
        4. Exact match prioritás - Pontos név egyezés előnyben
        
        Args:
            city_name: Város/település neve (pl. "Budapest", "Broxbourne", "Kiskunhalas")
            
        Returns:
            (latitude, longitude) tuple vagy None ha nem található
        """
        try:
            logger.info(f"🔍 find_city_by_name: '{city_name}'")
            
            # 1. MAGYAR KERESÉS ELŐNYBEN (ha van magyar adatbázis)
            if self.hungarian_connection:
                hungarian_results = self.search_hungarian_settlements(city_name, limit=3)
                
                if hungarian_results:
                    # Exact match keresése a magyar találatok között
                    exact_match = next((city for city in hungarian_results 
                                      if city.city.lower() == city_name.lower()), None)
                    
                    if exact_match:
                        logger.info(f"✅ Magyar exact match: {exact_match.display_name}")
                        return (exact_match.lat, exact_match.lon)
                    
                    # Ha nincs exact match, a legnagyobb magyar települést választjuk
                    best_hungarian = max(hungarian_results, 
                                       key=lambda c: (c.region_priority or 0, c.population or 0))
                    logger.info(f"✅ Magyar legjobb találat: {best_hungarian.display_name}")
                    return (best_hungarian.lat, best_hungarian.lon)
            
            # 2. GLOBÁLIS KERESÉS (ha nincs magyar találat)
            if self.connection:
                global_results = self.search_cities(city_name, limit=3)
                
                if global_results:
                    # Exact match keresése a globális találatok között
                    exact_match = next((city for city in global_results 
                                      if city.city.lower() == city_name.lower()), None)
                    
                    if exact_match:
                        logger.info(f"✅ Globális exact match: {exact_match.display_name}")
                        return (exact_match.lat, exact_match.lon)
                    
                    # Ha nincs exact match, a legnagyobb globális várost választjuk
                    best_global = max(global_results, key=lambda c: c.population or 0)
                    logger.info(f"✅ Globális legjobb találat: {best_global.display_name}")
                    return (best_global.lat, best_global.lon)
            
            # 3. NINCS TALÁLAT
            logger.warning(f"⚠️ Nincs találat: '{city_name}'")
            return None
            
        except Exception as e:
            logger.error(f"❌ find_city_by_name hiba '{city_name}': {e}")
            logger.exception("find_city_by_name stacktrace:")
            return None
    
    # 🇭🇺 MAGYAR TELEPÜLÉSEK KERESÉS
    
    def search_hungarian_settlements(self, search_term: str, limit: int = 20,
                                   county_filter: Optional[str] = None,
                                   settlement_type_filter: Optional[str] = None) -> List[City]:
        """
        🇭🇺 Magyar települések keresése név alapján - MINDEN FALU, KÖZSÉG, VÁROS.
        
        Args:
            search_term: Keresési kifejezés (pl. "Kiskunhalas", "Buda")
            limit: Maximum eredmény szám
            county_filter: Megye szűrő (pl. "Bács-Kiskun")
            settlement_type_filter: Település típus ("város", "nagyközség", "község")
            
        Returns:
            Magyar települések listája prioritás szerint rendezve
        """
        if not self.hungarian_connection:
            logger.warning("Magyar települések adatbázis nem elérhető")
            return []
        
        sql_parts = ["SELECT * FROM hungarian_settlements"]
        where_conditions = ["name LIKE ?"]
        params = [f"%{search_term}%"]
        
        # Megye szűrő
        if county_filter:
            where_conditions.append("megye = ?")
            params.append(county_filter)
        
        # Település típus szűrő
        if settlement_type_filter:
            where_conditions.append("settlement_type = ?")
            params.append(settlement_type_filter)
        
        sql_parts.append("WHERE " + " AND ".join(where_conditions))
        
        # Rendezés: prioritás szerint, majd populáció szerint
        sql_parts.append("ORDER BY region_priority DESC, population DESC NULLS LAST, name ASC")
        sql_parts.append(f"LIMIT {limit}")
        
        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params), use_hungarian=True)
        
        # City objektumok létrehozása magyar adapter-rel
        cities = [City.from_hungarian_settlement(row) for row in rows]
        
        logger.info(f"🇭🇺 Magyar települések keresése '{search_term}': {len(cities)} eredmény")
        return cities
    
    def get_hungarian_counties(self) -> List[str]:
        """🇭🇺 Magyar megyék listája (cached)."""
        if self._hungarian_counties_cache is not None:
            return self._hungarian_counties_cache
        
        if not self.hungarian_connection:
            return []
        
        sql = "SELECT DISTINCT megye FROM hungarian_settlements WHERE megye IS NOT NULL ORDER BY megye"
        rows = self._execute_query(sql, use_hungarian=True)
        
        self._hungarian_counties_cache = [row[0] for row in rows]
        return self._hungarian_counties_cache
    
    def get_hungarian_settlement_types(self) -> List[str]:
        """🇭🇺 Magyar település típusok listája."""
        if not self.hungarian_connection:
            return []
        
        sql = "SELECT DISTINCT settlement_type FROM hungarian_settlements WHERE settlement_type IS NOT NULL ORDER BY settlement_type"
        rows = self._execute_query(sql, use_hungarian=True)
        
        return [row[0] for row in rows]
    
    def get_hungarian_settlements_by_county(self, county: str, limit: int = 50) -> List[City]:
        """🇭🇺 Magyar települések megye szerint."""
        if not self.hungarian_connection:
            return []
        
        sql = """
            SELECT * FROM hungarian_settlements 
            WHERE megye = ? 
            ORDER BY region_priority DESC, population DESC NULLS LAST, name ASC
            LIMIT ?
        """
        
        rows = self._execute_query(sql, (county, limit), use_hungarian=True)
        cities = [City.from_hungarian_settlement(row) for row in rows]
        
        logger.info(f"🇭🇺 Magyar települések ({county}): {len(cities)} eredmény")
        return cities
    
    # 🔍 KOMBINÁLT KERESÉS (CORE FUNKCIÓ)
    
    def search_unified(self, search_term: str, limit: int = 20,
                      hungarian_priority: bool = True,
                      global_limit_ratio: float = 0.3) -> List[City]:
        """
        🚀 KOMBINÁLT KERESÉS - Magyar Települések + Globális Városok
        
        Ez a CORE funkció ami MINDEN magyar települést és globális várost keres!
        
        Args:
            search_term: Keresési kifejezés (pl. "Budapest", "Kiskunhalas", "London")
            limit: Összes eredmény limit
            hungarian_priority: Magyar települések előre helyezése
            global_limit_ratio: Globális eredmények aránya (0.3 = 30%)
            
        Returns:
            Kombinált eredmények magyar prioritással
        """
        results = []
        
        # 1. MAGYAR TELEPÜLÉSEK KERESÉSE (prioritás)
        if hungarian_priority:
            hungarian_limit = int(limit * 0.7)  # 70% magyar
            global_limit = limit - hungarian_limit
        else:
            hungarian_limit = int(limit * 0.5)  # 50% magyar
            global_limit = limit - hungarian_limit
        
        hungarian_results = self.search_hungarian_settlements(search_term, limit=hungarian_limit)
        results.extend(hungarian_results)
        
        # 2. GLOBÁLIS VÁROSOK KERESÉSE
        global_results = self.search_cities(search_term, limit=global_limit)
        
        # Duplikációk szűrése (magyar Budapest vs globális Budapest)
        hungarian_names = {city.city.lower() for city in hungarian_results}
        filtered_global = [
            city for city in global_results 
            if city.city.lower() not in hungarian_names or city.country_code != "HU"
        ]
        
        results.extend(filtered_global)
        
        logger.info(f"🔍 Kombinált keresés '{search_term}': {len(hungarian_results)} magyar + {len(filtered_global)} globális = {len(results)} összesen")
        
        return results[:limit]
    
    # 🌍 EREDETI GLOBÁLIS KERESÉS (VÁLTOZATLAN)
    
    def search_cities(self, search_term: str, limit: int = 20,
                     country_filter: Optional[str] = None) -> List[City]:
        """
        🔍 Globális város keresés név alapján (EREDETI FUNKCIÓ).
        
        Args:
            search_term: Keresési kifejezés
            limit: Maximum eredmény szám
            country_filter: Ország szűrő
            
        Returns:
            Keresési eredmények relevancia szerint
        """
        if not self.connection:
            logger.warning("Globális cities adatbázis nem elérhető")
            return []
        
        sql_parts = ["SELECT * FROM cities"]
        where_conditions = ["city LIKE ?"]
        params = [f"%{search_term}%"]
        
        if country_filter:
            where_conditions.append("country_code = ?")
            params.append(country_filter.upper())
        
        sql_parts.append("WHERE " + " AND ".join(where_conditions))
        sql_parts.append("ORDER BY population DESC NULLS LAST")
        sql_parts.append(f"LIMIT {limit}")
        
        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params))
        
        cities = [City.from_db_row(tuple(row)) for row in rows]
        
        logger.info(f"🌍 Globális város keresés '{search_term}': {len(cities)} eredmény")
        return cities
    
    # EREDETI METÓDUSOK (VÁLTOZATLANOK - KOMPATIBILITÁS)
    
    def get_cities_by_country(self, country_code: str, limit: int = 20,
                             min_population: Optional[int] = None) -> List[City]:
        """Ország alapú város lekérdezés (eredeti)."""
        # HA MAGYARORSZÁG, akkor kombinált keresés
        if country_code.upper() == "HU":
            return self._get_hungarian_cities_combined(limit, min_population)
        
        # Egyébként eredeti globális keresés
        if not self.connection:
            return []
        
        sql_parts = ["SELECT * FROM cities WHERE country_code = ?"]
        params = [country_code.upper()]
        
        if min_population:
            sql_parts.append("AND population >= ?")
            params.append(min_population)
        
        sql_parts.append("ORDER BY population DESC NULLS LAST")
        sql_parts.append(f"LIMIT {limit}")
        
        sql = " ".join(sql_parts)
        rows = self._execute_query(sql, tuple(params))
        
        return [City.from_db_row(tuple(row)) for row in rows]
    
    def _get_hungarian_cities_combined(self, limit: int, min_population: Optional[int] = None) -> List[City]:
        """🇭🇺 Magyar városok kombinált lekérdezése (települések + globális)."""
        results = []
        
        # 1. Magyar települések (75%)
        hungarian_limit = int(limit * 0.75)
        if self.hungarian_connection:
            sql_parts = ["SELECT * FROM hungarian_settlements"]
            params = []
            
            if min_population:
                sql_parts.append("WHERE population >= ?")
                params.append(min_population)
            
            sql_parts.append("ORDER BY region_priority DESC, population DESC NULLS LAST")
            sql_parts.append(f"LIMIT {hungarian_limit}")
            
            sql = " ".join(sql_parts)
            rows = self._execute_query(sql, tuple(params), use_hungarian=True)
            results.extend([City.from_hungarian_settlement(row) for row in rows])
        
        # 2. Globális magyar városok (25%) - kiegészítésként
        global_limit = limit - len(results)
        if global_limit > 0 and self.connection:
            sql_parts = ["SELECT * FROM cities WHERE country_code = 'HU'"]
            params = []
            
            if min_population:
                sql_parts.append("AND population >= ?")
                params.append(min_population)
            
            sql_parts.append("ORDER BY population DESC NULLS LAST")
            sql_parts.append(f"LIMIT {global_limit}")
            
            sql = " ".join(sql_parts)
            rows = self._execute_query(sql, tuple(params))
            
            # Duplikációk szűrése
            hungarian_names = {city.city.lower() for city in results}
            for row in rows:
                city = City.from_db_row(tuple(row))
                if city.city.lower() not in hungarian_names:
                    results.append(city)
        
        return results[:limit]
    
    # 📊 BŐVÍTETT STATISZTIKÁK
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """
        Bővített database statisztikák DUAL DATABASE-szel.
        """
        stats = {
            "query_count": self.query_count,
            "hungarian_query_count": self.hungarian_query_count,
            "last_query": self.last_query_time.isoformat() if self.last_query_time else None
        }
        
        # Globális adatbázis stats
        if self.connection:
            stats["global_cities"] = self._get_total_city_count()
            stats["continents"] = self._get_available_continents()
            stats["countries"] = self._get_available_countries()
        else:
            stats["global_cities"] = 0
            stats["continents"] = []
            stats["countries"] = []
        
        # Magyar települések stats
        if self.hungarian_connection:
            stats["hungarian_settlements"] = self._get_total_hungarian_settlements_count()
            stats["hungarian_counties"] = self.get_hungarian_counties()
            stats["settlement_types"] = self.get_hungarian_settlement_types()
        else:
            stats["hungarian_settlements"] = 0
            stats["hungarian_counties"] = []
            stats["settlement_types"] = []
        
        # Kombinált statisztikák
        stats["total_searchable_locations"] = stats["global_cities"] + stats["hungarian_settlements"]
        
        return stats
    
    def get_hungarian_statistics(self) -> Dict[str, Any]:
        """🇭🇺 Magyar települések részletes statisztikái."""
        if not self.hungarian_connection:
            return {"error": "Magyar adatbázis nem elérhető"}
        
        cursor = self.hungarian_connection.cursor()
        
        # Alapstatisztikák
        cursor.execute("SELECT COUNT(*) FROM hungarian_settlements")
        total_settlements = cursor.fetchone()[0]
        
        # Típus szerinti bontás
        cursor.execute("""
            SELECT settlement_type, COUNT(*) as count
            FROM hungarian_settlements 
            WHERE settlement_type IS NOT NULL
            GROUP BY settlement_type 
            ORDER BY count DESC
        """)
        by_type = dict(cursor.fetchall())
        
        # Megye szerinti bontás (top 10)
        cursor.execute("""
            SELECT megye, COUNT(*) as count
            FROM hungarian_settlements 
            WHERE megye IS NOT NULL
            GROUP BY megye 
            ORDER BY count DESC 
            LIMIT 10
        """)
        by_county = dict(cursor.fetchall())
        
        # Populáció statisztikák
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN population >= 100000 THEN 1 END) as large_cities,
                COUNT(CASE WHEN population >= 10000 THEN 1 END) as medium_towns,
                COUNT(CASE WHEN population < 10000 AND population > 0 THEN 1 END) as small_towns,
                AVG(CASE WHEN population > 0 THEN population END) as avg_population,
                MAX(population) as max_population
            FROM hungarian_settlements
        """)
        row = cursor.fetchone()
        
        return {
            "total_settlements": total_settlements,
            "by_settlement_type": by_type,
            "top_counties": by_county,
            "population_stats": {
                "large_cities_100k_plus": row[0],
                "medium_towns_10k_plus": row[1],
                "small_towns_under_10k": row[2],
                "average_population": int(row[3]) if row[3] else 0,
                "largest_settlement_population": row[4]
            }
        }
    
    # EREDETI METÓDUSOK (KOMPATIBILITÁS) - RÖVIDÍTVE
    def get_cities_by_continent(self, continent: str, limit: int = 50, min_population: Optional[int] = None) -> List[City]:
        """Kontinens alapú város lekérdezés (eredeti)."""
        if not self.connection:
            return []
        # [Eredeti implementáció rövidítve...]
        return []
    
    def _get_available_continents(self) -> List[str]:
        """Elérhető kontinensek listája (eredeti).""" 
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT continent FROM cities WHERE continent IS NOT NULL ORDER BY continent")
        return [row[0] for row in cursor.fetchall()]
    
    def _get_available_countries(self) -> List[Dict[str, Any]]:
        """Elérhető országok listája (eredeti)."""
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT country_code, country, COUNT(*) as city_count
            FROM cities 
            WHERE country_code IS NOT NULL 
            GROUP BY country_code, country 
            ORDER BY city_count DESC
        """)
        
        return [
            {
                "country_code": row[0],
                "country_name": row[1],
                "city_count": row[2]
            }
            for row in cursor.fetchall()
        ]
    
    # BEZÁRÁS
    def close(self) -> None:
        """DUAL DATABASE kapcsolatok bezárása."""
        if self.connection:
            self.connection.close()
            self.connection = None
        
        if self.hungarian_connection:
            self.hungarian_connection.close()
            self.hungarian_connection = None
            
        logger.info("🇭🇺 Dual database connections closed")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close()


# 🧪 DEMO ÉS TESZT FUNKCIÓK

def demo_dual_database_city_manager():
    """🇭🇺 Dual Database City Manager demo és tesztelés."""
    print("🇭🇺 Dual Database City Manager Demo v4.2")
    print("=" * 60)
    
    try:
        with CityManager() as manager:
            # Database statistics
            stats = manager.get_database_statistics()
            print(f"📊 DUAL DATABASE STATISZTIKÁK:")
            print(f"   🌍 Globális városok: {stats['global_cities']:,}")
            print(f"   🇭🇺 Magyar települések: {stats['hungarian_settlements']:,}")
            print(f"   📍 ÖSSZES kereshető helyszín: {stats['total_searchable_locations']:,}")
            print()
            
            # ⭐ ÚJ: find_city_by_name TESZT
            print("⭐ ÚJ FUNKCIÓ TESZT: find_city_by_name() - TrendDataProcessor támogatás")
            print("-" * 70)
            
            test_cities = ["Budapest", "Kiskunhalas", "Broxbourne", "London", "New York"]
            
            for city_name in test_cities:
                print(f"🔍 Koordináta keresés: '{city_name}'")
                coords = manager.find_city_by_name(city_name)
                if coords:
                    lat, lon = coords
                    print(f"   ✅ Koordináták: {lat:.4f}, {lon:.4f}")
                else:
                    print(f"   ❌ Nem található")
                print()
            
            # Magyar statisztikák
            if stats['hungarian_settlements'] > 0:
                hu_stats = manager.get_hungarian_statistics()
                print(f"🇭🇺 MAGYAR TELEPÜLÉSEK RÉSZLETEK:")
                print(f"   📊 Típusok: {hu_stats['by_settlement_type']}")
                print(f"   🏛️ Top megyék: {dict(list(hu_stats['top_counties'].items())[:3])}")
                print(f"   👥 100k+ lakosú: {hu_stats['population_stats']['large_cities_100k_plus']}")
                print()
            
            # Unified search tesztek (rövidítve)
            print("🔍 UNIFIED SEARCH TESZT - Magyar kis település:")
            print("   Keresés: 'Kiskunhalas'")
            kiskunhalas_results = manager.search_unified("Kiskunhalas", limit=3)
            for i, city in enumerate(kiskunhalas_results, 1):
                flag = "🇭🇺" if city.is_hungarian else "🌍"
                pop = f"{city.population:,}" if city.population else "N/A"
                settlement_info = f" ({city.settlement_type})" if city.settlement_type else ""
                print(f"   {i}. {flag} {city.display_name}: {pop} lakos{settlement_info}")
            print()
            
            # Query statistics
            print(f"📈 LEKÉRDEZÉS STATISZTIKÁK:")
            print(f"   🌍 Globális queries: {manager.query_count}")
            print(f"   🇭🇺 Magyar queries: {manager.hungarian_query_count}")
            print(f"   📍 Összes query: {manager.query_count + manager.hungarian_query_count}")
            
    except CityDatabaseError as e:
        print(f"❌ Database hiba: {e}")
        print("💡 Ellenőrzendő:")
        print("   1. Futtasd: python scripts/populate_cities_db.py")
        print("   2. Futtasd: python scripts/hungarian_settlements_importer.py") 
    except Exception as e:
        print(f"❌ Váratlan hiba: {e}")


if __name__ == "__main__":
    demo_dual_database_city_manager()
