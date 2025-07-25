#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Data Models
🎯 CLEAN ARCHITECTURE - Központi adatmodellek

REFAKTOR CÉL:
- city_analytics.py modellek kiemelése
- Type-safe data structures
- Clean separation of concerns
- Reusable data classes

🌍 UNIVERSAL WEATHER RESEARCH PLATFORM v5.2:
- UniversalLocation: bármilyen lokáció típus kezelés
- UniversalTimeRange: tetszőleges időintervallum
- UniversalQuery: központi user-centric query modell
- USER DÖNT MINDENRŐL paradigma támogatása

🗺️ LOCATION COMPATIBILITY FIX:
- Location osztály hozzáadva HungarianLocationSelector kompatibilitás miatt
- Backward compatibility biztosítva

HASZNÁLAT:
```python
from src.data.models import AnalyticsResult, CityWeatherResult, AnalyticsQuestion
from src.data.models import UniversalLocation, UniversalQuery, LocationType, Location
from src.data.enums import RegionScope, AnalyticsMetric, QuestionType
```
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, date
from enum import Enum
from .enums import (
    RegionScope, AnalyticsMetric, QuestionType, AnomalySeverity, 
    AnomalyType, DataSource, RegionType
)


# =============================================================================
# UNIVERSAL WEATHER RESEARCH PLATFORM - NEW ENUMS
# =============================================================================

class LocationType(Enum):
    """🌍 Univerzális lokáció típusok - USER SZABADSÁG"""
    REGION = "region"                    # Klimatikus régiók (Mediterrán, Kontinentális)
    COUNTRY = "country"                  # Országok (Magyarország, Németország)
    MICRO_REGION = "micro_region"        # Magyar micro-régiók (Alföld, Nyugat-Dunántúl)
    CITY = "city"                        # Városok (Budapest, Berlin)
    COORDINATES = "coordinates"          # Koordináták (47.4979, 19.0402)
    MULTIPLE = "multiple"                # Több lokáció kombinációja
    CUSTOM = "custom"                    # User-definiált lokáció


class TimeGranularity(Enum):
    """⏰ Időbeli granularitás - USER IDŐSZABADSÁG"""
    DAILY = "daily"                      # Napi szint
    WEEKLY = "weekly"                    # Heti szint
    MONTHLY = "monthly"                  # Havi szint
    YEARLY = "yearly"                    # Éves szint
    SEASONAL = "seasonal"                # Szezonális
    CUSTOM_INTERVAL = "custom_interval"  # User-definiált intervallum
    MULTI_YEAR = "multi_year"           # Évtizedes (1980-2024)


class AnalysisType(Enum):
    """🔬 Elemzési típusok - USER ANALYTICS SZABADSÁG"""
    CURRENT_CONDITIONS = "current_conditions"    # Jelenlegi állapot
    TREND_ANALYSIS = "trend_analysis"           # Trend elemzés
    ANOMALY_DETECTION = "anomaly_detection"     # Anomália detektálás
    COMPARATIVE = "comparative"                 # Összehasonlító elemzés
    STATISTICAL = "statistical"                # Statisztikai elemzés
    PATTERN_RECOGNITION = "pattern_recognition" # Minta felismerés
    FORECAST = "forecast"                      # Előrejelzés
    CUSTOM = "custom"                          # User-definiált elemzés


# =============================================================================
# LOCATION COMPATIBILITY - HUNGARIAN LOCATION SELECTOR FIX
# =============================================================================

@dataclass
class Location:
    """
    🗺️ Egyszerű lokáció modell - HungarianLocationSelector kompatibilitás.
    
    Ez egy backward compatibility osztály a magyar térképes komponensekhez.
    A HungarianLocationSelector ezt a formátumot várja.
    
    Attributes:
        identifier: Lokáció azonosító (város név, régió kód, stb.)
        display_name: Megjelenítendő név (felhasználó-barát)
        latitude: Földrajzi szélesség
        longitude: Földrajzi hosszúság
        country_code: Ország kód (ISO alpha-2, pl. "HU")
        timezone: Időzóna (pl. "Europe/Budapest")
        metadata: További információk dictionary-ben
    """
    identifier: str
    display_name: str
    latitude: float
    longitude: float
    country_code: str = "HU"
    timezone: str = "Europe/Budapest"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return f"{self.display_name} ({self.latitude:.4f}, {self.longitude:.4f})"
    
    def get_coordinates(self) -> Tuple[float, float]:
        """Koordináták tuple-ként."""
        return (self.latitude, self.longitude)
    
    def get_region(self) -> Optional[str]:
        """Régió név lekérdezése metadata-ból."""
        return self.metadata.get('region')
    
    def get_county(self) -> Optional[str]:
        """Megye név lekérdezése metadata-ból."""
        return self.metadata.get('county')
    
    def get_climate_zone(self) -> Optional[str]:
        """Éghajlati zóna lekérdezése metadata-ból."""
        return self.metadata.get('climate_zone')
    
    def get_source(self) -> Optional[str]:
        """Adatforrás lekérdezése metadata-ból."""
        return self.metadata.get('source')
    
    def get_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """Területi határok lekérdezése metadata-ból (minx, miny, maxx, maxy)."""
        return self.metadata.get('bounds')
    
    def is_hungarian_location(self) -> bool:
        """Magyar lokáció-e."""
        return self.country_code.upper() == "HU"
    
    def to_universal_location(self) -> 'UniversalLocation':
        """
        Konverzió UniversalLocation-né.
        
        Returns:
            UniversalLocation objektum
        """
        # Location type meghatározása
        if self.get_county():
            location_type = LocationType.MICRO_REGION  # Magyar megye szint
        else:
            location_type = LocationType.CITY  # Általános város/pont
        
        return UniversalLocation(
            type=location_type,
            identifier=self.identifier,
            display_name=self.display_name,
            coordinates=(self.latitude, self.longitude),
            country_code=self.country_code,
            timezone=self.timezone,
            climate_zone=self.get_climate_zone()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'identifier': self.identifier,
            'display_name': self.display_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'country_code': self.country_code,
            'timezone': self.timezone,
            'metadata': self.metadata,
            'coordinates': self.get_coordinates(),
            'region': self.get_region(),
            'county': self.get_county(),
            'climate_zone': self.get_climate_zone(),
            'source': self.get_source(),
            'bounds': self.get_bounds(),
            'is_hungarian': self.is_hungarian_location()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """
        Dictionary-ből Location objektum létrehozása.
        
        Args:
            data: Dictionary adatok
            
        Returns:
            Location objektum
        """
        # Kötelező mezők kinyerése
        identifier = data['identifier']
        display_name = data['display_name']
        latitude = data['latitude']
        longitude = data['longitude']
        
        # Opcionális mezők
        country_code = data.get('country_code', 'HU')
        timezone = data.get('timezone', 'Europe/Budapest')
        metadata = data.get('metadata', {})
        
        # Régi formátum kompatibilitás - ha a metadata üres, de vannak extra mezők
        if not metadata:
            extra_fields = ['region', 'county', 'climate_zone', 'source', 'bounds']
            for field in extra_fields:
                if field in data and data[field] is not None:
                    metadata[field] = data[field]
        
        return cls(
            identifier=identifier,
            display_name=display_name,
            latitude=latitude,
            longitude=longitude,
            country_code=country_code,
            timezone=timezone,
            metadata=metadata
        )
    
    @classmethod
    def from_coordinates(
        cls, 
        latitude: float, 
        longitude: float, 
        display_name: Optional[str] = None,
        **kwargs
    ) -> 'Location':
        """
        Koordinátákból Location objektum létrehozása.
        
        Args:
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            display_name: Megjelenítendő név (opcionális)
            **kwargs: További paraméterek
            
        Returns:
            Location objektum
        """
        if not display_name:
            display_name = f"Koordináta ({latitude:.4f}, {longitude:.4f})"
        
        identifier = f"coord_{latitude:.4f}_{longitude:.4f}"
        
        return cls(
            identifier=identifier,
            display_name=display_name,
            latitude=latitude,
            longitude=longitude,
            **kwargs
        )
    
    @classmethod
    def from_city_info(cls, city_info: 'CityInfo') -> 'Location':
        """
        CityInfo objektumból Location létrehozása.
        
        Args:
            city_info: CityInfo objektum
            
        Returns:
            Location objektum
        """
        return cls(
            identifier=city_info.city,
            display_name=city_info.get_display_name(),
            latitude=city_info.latitude,
            longitude=city_info.longitude,
            country_code=city_info.country_code,
            timezone=city_info.timezone or "Europe/Budapest",
            metadata={
                'city_id': city_info.id,
                'population': city_info.population,
                'continent': city_info.continent,
                'admin_name': city_info.admin_name,
                'capital': city_info.capital,
                'source': 'city_manager'
            }
        )


# =============================================================================
# UNIVERSAL WEATHER RESEARCH PLATFORM - NEW DATA MODELS
# =============================================================================

@dataclass
class UniversalLocation:
    """
    🌍 Univerzális lokáció modell - TELJES USER SZABADSÁG
    
    Képes reprezentálni bármilyen lokáció típust:
    - Klimatikus régiókat (Mediterrán, Kontinentális)
    - Országokat (Magyarország, Németország) 
    - Magyar micro-régiókat (Alföld, Nyugat-Dunántúl)
    - Városokat (Budapest, Berlin)
    - Koordinátákat (47.4979, 19.0402)
    - Több lokáció kombinációját
    """
    type: LocationType
    identifier: Union[str, Tuple[float, float], List[str]]
    display_name: str
    
    # Geo információk (ha elérhető)
    coordinates: Optional[Tuple[float, float]] = None
    country_code: Optional[str] = None
    region_code: Optional[str] = None
    
    # Hierarchikus információk
    parent_location: Optional['UniversalLocation'] = None
    child_locations: List['UniversalLocation'] = field(default_factory=list)
    
    # Metadata
    population: Optional[int] = None
    area_km2: Optional[float] = None
    timezone: Optional[str] = None
    climate_zone: Optional[str] = None
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return f"{self.display_name} ({self.type.value})"
    
    def is_geographical_point(self) -> bool:
        """Pont lokáció-e (város vagy koordináta)."""
        return self.type in [LocationType.CITY, LocationType.COORDINATES]
    
    def is_area_location(self) -> bool:
        """Terület lokáció-e (régió, ország)."""
        return self.type in [LocationType.REGION, LocationType.COUNTRY, LocationType.MICRO_REGION]
    
    def get_coordinates_list(self) -> List[Tuple[float, float]]:
        """
        Koordináták listája a lokációhoz.
        
        Returns:
            Lista koordinátákról - pont esetén 1 elem, terület esetén több
        """
        if self.type == LocationType.COORDINATES:
            if isinstance(self.identifier, tuple) and len(self.identifier) == 2:
                return [self.identifier]
        elif self.coordinates:
            return [self.coordinates]
        elif self.child_locations:
            coords = []
            for child in self.child_locations:
                coords.extend(child.get_coordinates_list())
            return coords
        
        return []
    
    def contains_location(self, other: 'UniversalLocation') -> bool:
        """Tartalmazza-e a másik lokációt (hierarchikus)."""
        if self.type == LocationType.MULTIPLE:
            return other in self.child_locations
        
        # Hierarchikus ellenőrzés
        current = other.parent_location
        while current:
            if current == self:
                return True
            current = current.parent_location
        
        return False
    
    def to_simple_location(self) -> Location:
        """
        Konverzió egyszerű Location objektummá.
        
        Returns:
            Location objektum
        """
        # Coordinates meghatározása
        coords = self.coordinates or (0.0, 0.0)
        if isinstance(self.identifier, tuple) and len(self.identifier) == 2:
            coords = self.identifier
        
        return Location(
            identifier=str(self.identifier),
            display_name=self.display_name,
            latitude=coords[0],
            longitude=coords[1],
            country_code=self.country_code or "HU",
            timezone=self.timezone or "Europe/Budapest",
            metadata={
                'location_type': self.type.value,
                'climate_zone': self.climate_zone,
                'population': self.population,
                'area_km2': self.area_km2,
                'region_code': self.region_code,
                'source': 'universal_location'
            }
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'type': self.type.value,
            'identifier': self.identifier,
            'display_name': self.display_name,
            'coordinates': self.coordinates,
            'country_code': self.country_code,
            'region_code': self.region_code,
            'population': self.population,
            'area_km2': self.area_km2,
            'timezone': self.timezone,
            'climate_zone': self.climate_zone,
            'child_locations_count': len(self.child_locations)
        }


@dataclass
class UniversalTimeRange:
    """
    ⏰ Univerzális időtartomány modell - TELJES IDŐSZABADSÁG
    
    Képes reprezentálni bármilyen időintervallumot:
    - Napokat (2025-07-21)
    - Heteket (utolsó 7 nap)
    - Hónapokat (2024 július)
    - Éveket (2023)
    - Évtizedeket (1980-2024)
    - Custom intervallumokat (1995.06.15 - 2003.08.30)
    """
    start_date: date
    end_date: date
    granularity: TimeGranularity
    
    # Leíró információk
    description: str = ""
    
    # Speciális beállítások
    include_partial_periods: bool = True      # Részleges időszakok belefoglalása
    exclude_weekends: bool = False            # Hétvégék kizárása
    seasonal_filter: Optional[List[str]] = None # Szezonális szűrő ['summer', 'winter']
    
    # Metadata
    total_days: int = field(init=False)
    is_historical: bool = field(init=False)
    is_future: bool = field(init=False)
    
    def __post_init__(self):
        """Post-init számítások."""
        self.total_days = (self.end_date - self.start_date).days + 1
        today = date.today()
        self.is_historical = self.end_date < today
        self.is_future = self.start_date > today
        
        # Automatikus leírás generálás ha üres
        if not self.description:
            self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """Automatikus leírás generálás."""
        if self.total_days == 1:
            return f"Egy nap ({self.start_date})"
        elif self.total_days <= 7:
            return f"{self.total_days} nap ({self.start_date} - {self.end_date})"
        elif self.total_days <= 31:
            return f"~{self.total_days // 7} hét ({self.start_date} - {self.end_date})"
        elif self.total_days <= 365:
            return f"~{self.total_days // 30} hónap ({self.start_date} - {self.end_date})"
        else:
            years = self.total_days // 365
            return f"~{years} év ({self.start_date} - {self.end_date})"
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return f"{self.description} [{self.granularity.value}]"
    
    def overlaps_with(self, other: 'UniversalTimeRange') -> bool:
        """Átfed-e másik időtartománnyal."""
        return not (self.end_date < other.start_date or self.start_date > other.end_date)
    
    def contains_date(self, check_date: date) -> bool:
        """Tartalmazza-e a megadott dátumot."""
        return self.start_date <= check_date <= self.end_date
    
    def get_months_list(self) -> List[str]:
        """Érintett hónapok listája (YYYY-MM formátumban)."""
        months = []
        current = self.start_date.replace(day=1)  # Hónap eleje
        
        while current <= self.end_date:
            months.append(current.strftime('%Y-%m'))
            # Következő hónap
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return months
    
    def get_years_list(self) -> List[int]:
        """Érintett évek listája."""
        return list(range(self.start_date.year, self.end_date.year + 1))
    
    def split_by_years(self) -> List['UniversalTimeRange']:
        """Évenkénti bontás."""
        if self.start_date.year == self.end_date.year:
            return [self]
        
        yearly_ranges = []
        for year in self.get_years_list():
            year_start = max(self.start_date, date(year, 1, 1))
            year_end = min(self.end_date, date(year, 12, 31))
            
            yearly_range = UniversalTimeRange(
                start_date=year_start,
                end_date=year_end,
                granularity=TimeGranularity.YEARLY,
                description=f"{year} év részlet"
            )
            yearly_ranges.append(yearly_range)
        
        return yearly_ranges
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'granularity': self.granularity.value,
            'description': self.description,
            'total_days': self.total_days,
            'is_historical': self.is_historical,
            'is_future': self.is_future,
            'include_partial_periods': self.include_partial_periods,
            'exclude_weekends': self.exclude_weekends,
            'seasonal_filter': self.seasonal_filter
        }


@dataclass
class UniversalQuery:
    """
    🎯 UNIVERZÁLIS LEKÉRDEZÉS MODELL - USER-CENTRIC PARADIGMA
    
    A teljes "User dönt mindenről" filozofia központi modellje.
    Bármilyen lokációt, időtartamot, paramétert képes kezelni.
    
    PÉLDÁK:
    - "Budapest hőmérséklet trend 1980-2024"
    - "Mediterrán régió csapadék anomáliák nyáron"
    - "Koordináta [47.5, 19.0] szélsebesség utolsó 30 nap"
    - "Magyarország vs Németország összehasonlítás 2023"
    """
    # Alapvető query komponensek
    locations: List[UniversalLocation]
    time_range: UniversalTimeRange
    parameters: List[str]                   # Weather paraméterek (temperature_2m_max, stb.)
    analysis_type: AnalysisType
    
    # Query metaadatok
    query_id: str = field(default_factory=lambda: f"universal_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    user_description: str = ""              # User-friendly leírás
    
    # Végrehajtási beállítások
    data_sources: List[DataSource] = field(default_factory=list)  # Preferred APIs
    quality_threshold: float = 0.8          # Minimum adat minőség
    max_results_per_location: int = 1000    # Performance limit
    
    # Szűrési opciók
    anomaly_detection: bool = False         # Anomália detektálás bekapcsolása
    statistical_analysis: bool = True       # Statisztikai elemzés
    trend_analysis: bool = False           # Trend elemzés
    comparative_mode: bool = False         # Összehasonlító mód
    
    # Anomália specifikus beállítások (ha anomaly_detection=True)
    anomaly_severity_filter: List[AnomalySeverity] = field(default_factory=list)
    anomaly_threshold_override: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Végrehajtási státusz
    is_executed: bool = False
    execution_time: Optional[float] = None
    total_data_points: int = 0
    
    def __post_init__(self):
        """Post-init validáció és automatikus beállítások."""
        # Automatikus leírás generálás ha üres
        if not self.user_description:
            self.user_description = self._generate_description()
        
        # Automatikus comparative mode detektálás
        if len(self.locations) > 1:
            self.comparative_mode = True
        
        # Data sources validáció
        if not self.data_sources:
            self.data_sources = [DataSource.AUTO]  # Default auto selection
    
    def _generate_description(self) -> str:
        """Automatikus user-friendly leírás generálás."""
        # Lokációk
        if len(self.locations) == 1:
            location_desc = self.locations[0].display_name
        elif len(self.locations) <= 3:
            location_desc = " vs ".join([loc.display_name for loc in self.locations])
        else:
            location_desc = f"{len(self.locations)} lokáció"
        
        # Paraméterek
        if len(self.parameters) == 1:
            param_desc = self.parameters[0].replace('_', ' ')
        elif len(self.parameters) <= 3:
            param_desc = ", ".join([p.replace('_', ' ') for p in self.parameters])
        else:
            param_desc = f"{len(self.parameters)} paraméter"
        
        # Időtartam
        time_desc = self.time_range.description
        
        # Elemzés típus
        analysis_desc = self.analysis_type.value.replace('_', ' ')
        
        return f"{location_desc}: {param_desc} {analysis_desc} ({time_desc})"
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return f"UniversalQuery[{self.query_id}]: {self.user_description}"
    
    def get_total_locations(self) -> int:
        """Összes lokáció száma (hierarchikus bontással)."""
        total = 0
        for location in self.locations:
            if location.type == LocationType.MULTIPLE:
                total += len(location.child_locations)
            else:
                total += 1
        return total
    
    def get_all_coordinates(self) -> List[Tuple[float, float]]:
        """Összes koordináta a query-ből."""
        all_coords = []
        for location in self.locations:
            all_coords.extend(location.get_coordinates_list())
        return all_coords
    
    def is_multi_location_query(self) -> bool:
        """Multi-lokáció query-e."""
        return len(self.locations) > 1 or any(
            loc.type == LocationType.MULTIPLE for loc in self.locations
        )
    
    def is_long_term_analysis(self) -> bool:
        """Hosszú távú elemzés-e (>1 év)."""
        return self.time_range.total_days > 365
    
    def is_historical_query(self) -> bool:
        """Historikus query-e."""
        return self.time_range.is_historical
    
    def get_estimated_complexity(self) -> str:
        """Becsült query komplexitás."""
        score = 0
        
        # Lokációk száma
        score += self.get_total_locations() * 2
        
        # Paraméterek száma
        score += len(self.parameters) * 3
        
        # Időtartam
        score += min(self.time_range.total_days // 30, 50)  # Max 50 pont
        
        # Elemzés típus bonyolultsága
        if self.analysis_type in [AnalysisType.TREND_ANALYSIS, AnalysisType.ANOMALY_DETECTION]:
            score += 20
        elif self.analysis_type in [AnalysisType.PATTERN_RECOGNITION, AnalysisType.FORECAST]:
            score += 30
        
        # Comparative mode
        if self.comparative_mode:
            score += 15
        
        # Kategorizálás
        if score < 20:
            return "simple"
        elif score < 50:
            return "medium"
        elif score < 100:
            return "complex"
        else:
            return "very_complex"
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Query validáció.
        
        Returns:
            (valid: bool, error_messages: List[str])
        """
        errors = []
        
        # Lokációk validáció
        if not self.locations:
            errors.append("Legalább egy lokáció megadása kötelező!")
        
        # Paraméterek validáció  
        if not self.parameters:
            errors.append("Legalább egy paraméter megadása kötelező!")
        
        # Időtartam validáció
        if self.time_range.start_date > self.time_range.end_date:
            errors.append("A kezdő dátum nem lehet későbbi a záró dátumnál!")
        
        # Performance validáció
        estimated_complexity = self.get_estimated_complexity()
        if estimated_complexity == "very_complex" and self.max_results_per_location < 100:
            errors.append("Nagyon komplex query esetén növelje a max_results_per_location értékét!")
        
        # Anomália beállítások validáció
        if self.anomaly_detection:
            if self.anomaly_threshold_override and self.anomaly_threshold_override <= 0:
                errors.append("Anomália küszöb pozitív szám kell legyen!")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'query_id': self.query_id,
            'user_description': self.user_description,
            'locations': [loc.to_dict() for loc in self.locations],
            'time_range': self.time_range.to_dict(),
            'parameters': self.parameters,
            'analysis_type': self.analysis_type.value,
            'data_sources': [ds.value for ds in self.data_sources],
            'quality_threshold': self.quality_threshold,
            'max_results_per_location': self.max_results_per_location,
            'anomaly_detection': self.anomaly_detection,
            'statistical_analysis': self.statistical_analysis,
            'trend_analysis': self.trend_analysis,
            'comparative_mode': self.comparative_mode,
            'estimated_complexity': self.get_estimated_complexity(),
            'total_locations': self.get_total_locations(),
            'is_multi_location': self.is_multi_location_query(),
            'is_long_term': self.is_long_term_analysis(),
            'is_historical': self.is_historical_query(),
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags
        }


# =============================================================================
# ORIGINAL MODELS (PRESERVED FOR BACKWARD COMPATIBILITY)
# =============================================================================

@dataclass
class CityWeatherResult:
    """
    Egyetlen város időjárási eredménye.
    
    Multi-city analytics alapegysége.
    """
    city_name: str
    country: str
    country_code: str
    latitude: float
    longitude: float
    
    # Weather data
    value: float                    # Fő metrika értéke
    metric: AnalyticsMetric        # Metrika típusa
    date: date                     # Adat dátuma
    rank: Optional[int] = None     # 🔧 FIX: UI compatibility - eredmény rangsor
    
    # Additional data
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    data_source: DataSource = DataSource.AUTO
    quality_score: float = 1.0     # 0.0-1.0 adat minőség
    confidence: float = 1.0        # 0.0-1.0 megbízhatóság
    
    # Geographical context
    population: Optional[int] = None
    elevation: Optional[float] = None
    timezone: Optional[str] = None
    admin_name: Optional[str] = None  # Régió/állam
    
    def __str__(self) -> str:
        """String reprezentáció."""
        unit = self._get_metric_unit()
        return f"{self.city_name}: {self.value:.1f}{unit}"
    
    def _get_metric_unit(self) -> str:
        """Metrika mértékegység lekérdezése."""
        from .enums import get_metric_unit
        return get_metric_unit(self.metric)
    
    def get_display_name(self) -> str:
        """Teljes display név."""
        return f"{self.city_name}, {self.country}"
    
    def get_coordinates(self) -> tuple[float, float]:
        """Koordináták tuple-ként."""
        return (self.latitude, self.longitude)
    
    @property
    def city(self) -> 'City':
        """
        🔧 FIX: UI Compatibility - VALÓDI City objektum generálása.
        
        A UI city_manager.City class-t várja, nem CityInfo-t!
        Ez a root cause minden compatibility hibának.
        
        Returns:
            city_manager.City objektum a meglévő adatokból
        """
        # Import here to avoid circular dependency
        from .city_manager import City
        
        # Create City object with matching structure
        city_obj = City(
            id=0,  # Placeholder, nem használt
            city=self.city_name,
            lat=self.latitude,
            lon=self.longitude,
            country=self.country,
            country_code=self.country_code,
            population=self.population,
            continent=None,  # Nem elérhető
            admin_name=self.admin_name,
            capital=None,    # Nem elérhető
            timezone=self.timezone
        )
        
        # Trigger __post_init__ to generate display_name
        city_obj.__post_init__()
        
        return city_obj
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'city_name': self.city_name,
            'country': self.country,
            'country_code': self.country_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'value': self.value,
            'metric': self.metric.value,
            'date': self.date.isoformat(),
            'rank': self.rank,  # 🔧 FIX: rank mező hozzáadva
            'additional_data': self.additional_data,
            'data_source': self.data_source.value,
            'quality_score': self.quality_score,
            'confidence': self.confidence,
            'population': self.population,
            'elevation': self.elevation,
            'timezone': self.timezone,
            'admin_name': self.admin_name
        }


@dataclass
class AnalyticsQuestion:
    """
    Analytics kérdés definíció.
    
    Multi-city analytics kérdések specifikációja.
    """
    question_text: str
    question_type: QuestionType
    region_scope: RegionScope
    metric: AnalyticsMetric
    
    # Query parameters
    region_value: Optional[str] = None      # Konkrét régió (pl. "HU", "Europe")
    date_filter: Optional[str] = None       # Dátum szűrő
    ascending_order: bool = False           # Rendezési irány
    max_cities: int = 50                    # Maximum városok száma
    
    # Additional filters
    min_population: Optional[int] = None    # Minimum népesség
    include_capitals_only: bool = False     # Csak fővárosok
    exclude_islands: bool = False           # Szigetek kizárása
    climate_zones: Optional[List[str]] = None # Éghajlati zónák
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return self.question_text
    
    def get_region_display(self) -> str:
        """Régió display név."""
        if self.region_value:
            return f"{self.region_scope.value}: {self.region_value}"
        return self.region_scope.value
    
    def validate(self) -> tuple[bool, List[str]]:
        """
        Kérdés validálása.
        
        Returns:
            (valid, error_messages)
        """
        errors = []
        
        if not self.question_text.strip():
            errors.append("Kérdés szövege nem lehet üres")
        
        if self.max_cities <= 0:
            errors.append("Maximum városok száma pozitív kell legyen")
        
        if self.max_cities > 1000:
            errors.append("Maximum városok száma nem lehet 1000-nél több")
        
        if self.region_scope in [RegionScope.COUNTRY, RegionScope.REGION] and not self.region_value:
            errors.append(f"{self.region_scope.value} scope esetén region_value kötelező")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'question_text': self.question_text,
            'question_type': self.question_type.value,
            'region_scope': self.region_scope.value,
            'metric': self.metric.value,
            'region_value': self.region_value,
            'date_filter': self.date_filter,
            'ascending_order': self.ascending_order,
            'max_cities': self.max_cities,
            'min_population': self.min_population,
            'include_capitals_only': self.include_capitals_only,
            'exclude_islands': self.exclude_islands,
            'climate_zones': self.climate_zones,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags
        }


@dataclass
class AnalyticsResult:
    """
    Multi-city analytics eredmény.
    
    Teljes analytics lekérdezés eredménye.
    """
    question: AnalyticsQuestion
    city_results: List[CityWeatherResult]
    
    # Execution metadata
    execution_time: float                   # Végrehajtási idő (sec)
    total_cities_found: int                 # Találatok összes száma
    data_sources_used: List[DataSource]     # Használt adatforrások
    
    # Statistics
    statistics: Dict[str, float] = field(default_factory=dict)
    
    # Provider statistics
    provider_statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    average_quality_score: float = 1.0
    average_confidence: float = 1.0
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)
    
    def __len__(self) -> int:
        """Eredmények száma."""
        return len(self.city_results)
    
    def get_top_results(self, n: int = 10) -> List[CityWeatherResult]:
        """
        Top N eredmény lekérdezése.
        
        Args:
            n: Eredmények száma
            
        Returns:
            Top N CityWeatherResult
        """
        return self.city_results[:n]
    
    def get_bottom_results(self, n: int = 10) -> List[CityWeatherResult]:
        """
        Bottom N eredmény lekérdezése.
        
        Args:
            n: Eredmények száma
            
        Returns:
            Bottom N CityWeatherResult
        """
        return self.city_results[-n:]
    
    def get_results_by_country(self, country_code: str) -> List[CityWeatherResult]:
        """
        Ország szerinti szűrés.
        
        Args:
            country_code: ISO country code
            
        Returns:
            Ország eredményei
        """
        return [r for r in self.city_results if r.country_code == country_code]
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        Statisztikai összefoglaló.
        
        Returns:
            Statisztikai adatok
        """
        if not self.city_results:
            return {}
        
        values = [r.value for r in self.city_results]
        
        import statistics
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'range': max(values) - min(values)
        }
    
    def get_countries_represented(self) -> List[str]:
        """
        Képviselt országok listája.
        
        Returns:
            Ország kódok listája
        """
        return list(set(r.country_code for r in self.city_results))
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'question': self.question.to_dict(),
            'city_results': [r.to_dict() for r in self.city_results],
            'execution_time': self.execution_time,
            'total_cities_found': self.total_cities_found,
            'data_sources_used': [ds.value for ds in self.data_sources_used],
            'statistics': self.statistics,
            'provider_statistics': self.provider_statistics,
            'average_quality_score': self.average_quality_score,
            'average_confidence': self.average_confidence,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class AnomalyResult:
    """
    Anomália detektálási eredmény.
    
    Parameter-based analytics anomália eredménye.
    """
    date: date
    metric: AnalyticsMetric
    value: float
    expected_value: float
    deviation: float                # Standard deviáció
    severity: AnomalySeverity
    anomaly_type: AnomalyType      # HIGH/LOW
    
    # Context
    description: str
    confidence: float = 1.0
    
    # Statistical context
    percentile: Optional[float] = None
    z_score: Optional[float] = None
    
    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)
    detection_method: str = "statistical"
    
    def __str__(self) -> str:
        """String reprezentáció."""
        return f"{self.date}: {self.description}"
    
    def get_severity_color(self) -> str:
        """Súlyosság színkód."""
        from .enums import get_severity_color
        return get_severity_color(self.severity)
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'date': self.date.isoformat(),
            'metric': self.metric.value,
            'value': self.value,
            'expected_value': self.expected_value,
            'deviation': self.deviation,
            'severity': self.severity.value,
            'anomaly_type': self.anomaly_type.value,
            'description': self.description,
            'confidence': self.confidence,
            'percentile': self.percentile,
            'z_score': self.z_score,
            'detected_at': self.detected_at.isoformat(),
            'detection_method': self.detection_method
        }


@dataclass
class QueryResults:
    """
    Parameter-based query eredmények.
    
    ParameterSelectorWidget query eredményeinek tárolása.
    """
    query_parameters: Dict[str, Any]
    anomalies: Dict[str, List[AnomalyResult]]  # parameter_name -> anomalies
    
    # Execution metadata
    execution_time: float
    total_records_analyzed: int
    date_range: tuple[date, date]
    
    # Statistics
    anomaly_summary: Dict[str, int] = field(default_factory=dict)
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_total_anomalies(self) -> int:
        """Összes anomália száma."""
        return sum(len(anomaly_list) for anomaly_list in self.anomalies.values())
    
    def get_anomalies_by_severity(self) -> Dict[str, int]:
        """
        Anomáliák súlyosság szerint.
        
        Returns:
            {severity: count} dict
        """
        severity_counts = {}
        
        for anomaly_list in self.anomalies.values():
            for anomaly in anomaly_list:
                severity = anomaly.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return severity_counts
    
    def get_most_active_days(self, n: int = 10) -> List[tuple[date, int]]:
        """
        Legaktívabb napok anomália szempontjából.
        
        Args:
            n: Top N nap
            
        Returns:
            [(date, anomaly_count), ...]
        """
        day_counts = {}
        
        for anomaly_list in self.anomalies.values():
            for anomaly in anomaly_list:
                day = anomaly.date
                day_counts[day] = day_counts.get(day, 0) + 1
        
        # Rendezés anomália szám szerint
        sorted_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_days[:n]
    
    def get_anomalies_for_parameter(self, parameter: str) -> List[AnomalyResult]:
        """
        Paraméter-specifikus anomáliák.
        
        Args:
            parameter: Paraméter neve
            
        Returns:
            Anomáliák listája
        """
        return self.anomalies.get(parameter, [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'query_parameters': self.query_parameters,
            'anomalies': {
                param: [a.to_dict() for a in anomalies] 
                for param, anomalies in self.anomalies.items()
            },
            'execution_time': self.execution_time,
            'total_records_analyzed': self.total_records_analyzed,
            'date_range': [self.date_range[0].isoformat(), self.date_range[1].isoformat()],
            'anomaly_summary': self.anomaly_summary,
            'created_at': self.created_at.isoformat()
        }


@dataclass 
class CityInfo:
    """
    Város információ modell.
    
    CityManager adatbázis rekord reprezentáció.
    """
    id: int
    city: str
    latitude: float
    longitude: float
    country: str
    country_code: str
    
    # Optional fields
    population: Optional[int] = None
    continent: Optional[str] = None
    admin_name: Optional[str] = None
    capital: Optional[str] = None
    timezone: Optional[str] = None
    
    def get_display_name(self) -> str:
        """Display név."""
        return f"{self.city}, {self.country}"
    
    def get_coordinates(self) -> tuple[float, float]:
        """Koordináták."""
        return (self.latitude, self.longitude)
    
    def is_capital(self) -> bool:
        """Főváros-e."""
        return self.capital == "primary"
    
    def to_location(self) -> Location:
        """
        Konverzió Location objektummá.
        
        Returns:
            Location objektum
        """
        return Location.from_city_info(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary konverzió."""
        return {
            'id': self.id,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'country': self.country,
            'country_code': self.country_code,
            'population': self.population,
            'continent': self.continent,
            'admin_name': self.admin_name,
            'capital': self.capital,
            'timezone': self.timezone
        }


# =============================================================================
# UNIVERSAL FACTORY FUNCTIONS - USER-FRIENDLY BUILDERS
# =============================================================================

def create_universal_location(
    location_type: Union[LocationType, str],
    identifier: Union[str, Tuple[float, float], List[str]],
    display_name: str,
    **kwargs
) -> UniversalLocation:
    """
    🌍 UniversalLocation factory - USER-FRIENDLY
    
    Args:
        location_type: Lokáció típus (enum vagy string)
        identifier: Azonosító (string, koordináta, vagy lista)
        display_name: Megjelenítendő név
        **kwargs: További paraméterek
        
    Returns:
        UniversalLocation objektum
        
    Examples:
        ```python
        # Város
        budapest = create_universal_location(
            LocationType.CITY, "Budapest", "Budapest, Magyarország",
            coordinates=(47.4979, 19.0402), country_code="HU"
        )
        
        # Koordináta
        custom_point = create_universal_location(
            LocationType.COORDINATES, (47.5, 19.0), "Custom Location"
        )
        
        # Régió
        mediterranean = create_universal_location(
            LocationType.REGION, "mediterranean", "Mediterrán Régió",
            climate_zone="Mediterranean"
        )
        ```
    """
    # String to enum conversion
    if isinstance(location_type, str):
        location_type = LocationType(location_type.lower())
    
    return UniversalLocation(
        type=location_type,
        identifier=identifier,
        display_name=display_name,
        **kwargs
    )


def create_universal_time_range(
    start_date: Union[str, date],
    end_date: Union[str, date],
    granularity: Union[TimeGranularity, str] = TimeGranularity.DAILY,
    **kwargs
) -> UniversalTimeRange:
    """
    ⏰ UniversalTimeRange factory - USER-FRIENDLY
    
    Args:
        start_date: Kezdő dátum (string vagy date)
        end_date: Záró dátum (string vagy date)
        granularity: Granularitás (enum vagy string)
        **kwargs: További paraméterek
        
    Returns:
        UniversalTimeRange objektum
        
    Examples:
        ```python
        # Egy hét
        last_week = create_universal_time_range(
            "2025-07-14", "2025-07-21", TimeGranularity.WEEKLY
        )
        
        # Évtizedek
        climate_era = create_universal_time_range(
            "1980-01-01", "2024-12-31", TimeGranularity.MULTI_YEAR,
            description="Klímaváltozás elemzési időszak"
        )
        ```
    """
    # String to date conversion
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # String to enum conversion
    if isinstance(granularity, str):
        granularity = TimeGranularity(granularity.lower())
    
    return UniversalTimeRange(
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        **kwargs
    )


def create_universal_query(
    locations: List[UniversalLocation],
    time_range: UniversalTimeRange,
    parameters: List[str],
    analysis_type: Union[AnalysisType, str] = AnalysisType.CURRENT_CONDITIONS,
    **kwargs
) -> UniversalQuery:
    """
    🎯 UniversalQuery factory - USER-FRIENDLY
    
    Args:
        locations: Lokációk listája
        time_range: Időtartomány
        parameters: Weather paraméterek
        analysis_type: Elemzés típus (enum vagy string)
        **kwargs: További paraméterek
        
    Returns:
        UniversalQuery objektum
        
    Examples:
        ```python
        query = create_universal_query(
            locations=[budapest, berlin],
            time_range=last_week,
            parameters=["temperature_2m_max", "precipitation_sum"],
            analysis_type=AnalysisType.COMPARATIVE,
            anomaly_detection=True
        )
        ```
    """
    # String to enum conversion
    if isinstance(analysis_type, str):
        analysis_type = AnalysisType(analysis_type.lower())
    
    return UniversalQuery(
        locations=locations,
        time_range=time_range,
        parameters=parameters,
        analysis_type=analysis_type,
        **kwargs
    )


# LEGACY FACTORY FUNCTIONS (PRESERVED)

def create_analytics_question(
    question_text: str,
    question_type: QuestionType,
    region_scope: RegionScope, 
    metric: AnalyticsMetric,
    **kwargs
) -> AnalyticsQuestion:
    """
    AnalyticsQuestion factory function.
    
    Args:
        question_text: Kérdés szövege
        question_type: Kérdés típusa
        region_scope: Régió hatókör
        metric: Analytics metrika
        **kwargs: További paraméterek
        
    Returns:
        AnalyticsQuestion instance
    """
    return AnalyticsQuestion(
        question_text=question_text,
        question_type=question_type,
        region_scope=region_scope,
        metric=metric,
        **kwargs
    )


def create_city_weather_result(
    city_name: str,
    country: str,
    country_code: str,
    latitude: float,
    longitude: float,
    value: float,
    metric: AnalyticsMetric,
    result_date: date,
    **kwargs
) -> CityWeatherResult:
    """
    CityWeatherResult factory function.
    
    Args:
        city_name: Város neve
        country: Ország neve
        country_code: Ország kódja
        latitude: Szélesség
        longitude: Hosszúság
        value: Metrika értéke
        metric: Analytics metrika
        result_date: Eredmény dátuma
        **kwargs: További paraméterek
        
    Returns:
        CityWeatherResult instance
    """
    return CityWeatherResult(
        city_name=city_name,
        country=country,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        value=value,
        metric=metric,
        date=result_date,
        **kwargs
    )


# LOCATION FACTORY FUNCTIONS - HUNGARIAN MAP COMPATIBILITY

def create_location(
    identifier: str,
    display_name: str,
    latitude: float,
    longitude: float,
    **kwargs
) -> Location:
    """
    🗺️ Location factory function - HungarianLocationSelector kompatibilitás.
    
    Args:
        identifier: Lokáció azonosító
        display_name: Megjelenítendő név
        latitude: Földrajzi szélesség
        longitude: Földrajzi hosszúság
        **kwargs: További paraméterek (country_code, timezone, metadata)
        
    Returns:
        Location objektum
        
    Examples:
        ```python
        budapest = create_location(
            "Budapest", "Budapest, Magyarország",
            47.4979, 19.0402,
            country_code="HU", timezone="Europe/Budapest",
            metadata={'county': 'Budapest', 'region': 'west_border'}
        )
        ```
    """
    return Location(
        identifier=identifier,
        display_name=display_name,
        latitude=latitude,
        longitude=longitude,
        **kwargs
    )


def create_location_from_coordinates(
    latitude: float,
    longitude: float,
    display_name: Optional[str] = None,
    **kwargs
) -> Location:
    """
    🗺️ Koordinátákból Location létrehozása - térképes komponensekhez.
    
    Args:
        latitude: Földrajzi szélesség
        longitude: Földrajzi hosszúság
        display_name: Megjelenítendő név (opcionális)
        **kwargs: További paraméterek
        
    Returns:
        Location objektum
    """
    return Location.from_coordinates(latitude, longitude, display_name, **kwargs)


# =============================================================================
# EXPORT API - UNIVERSAL + LEGACY + LOCATION COMPATIBILITY
# =============================================================================

__all__ = [
    # Location Compatibility - HUNGARIAN MAP SUPPORT
    'Location',
    'create_location',
    'create_location_from_coordinates',
    
    # Universal Weather Research Platform - NEW
    'LocationType', 'TimeGranularity', 'AnalysisType',
    'UniversalLocation', 'UniversalTimeRange', 'UniversalQuery',
    'create_universal_location', 'create_universal_time_range', 'create_universal_query',
    
    # Legacy Models - PRESERVED
    'CityWeatherResult',
    'AnalyticsQuestion', 
    'AnalyticsResult',
    'AnomalyResult',
    'QueryResults',
    'CityInfo',
    'create_analytics_question',
    'create_city_weather_result'
]