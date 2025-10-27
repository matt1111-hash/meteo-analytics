#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Geographic Utilities Module
🌍 Multi-City Analytics: Földrajzi számítások és koordináta műveletek

FUNKCIÓK:
- Haversine távolság számítás (nagy körök)
- Bounding box és régió számítások
- Koordináta validálás és normalizálás
- Geographic clustering és grouping
- Time zone detection és conversion
- Map projection utilities
- Multi-city analytics geographic support

MATEMATIKAI ALGORITMUSOK:
- Haversine formula nagy körök távolságához
- Vincenty ellipsoid formula nagy pontosságú távolsághoz
- Bounding box optimization
- Geographic center calculation
- Spherical trigonometry utilities

HASZNÁLAT:
```python
calculator = DistanceCalculator()
distance = calculator.haversine_distance(47.4979, 19.0402, 52.5200, 13.4050)  # Budapest-Berlin

geo_utils = GeoUtils()
bbox = geo_utils.calculate_bounding_box(cities_list, padding=0.1)
```

INTEGRÁCIÓ:
- CityManager coordination support
- Multi-city analytics geographic optimization
- Provider routing geographic logic
- Map visualization support
"""

import math
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

# Math és geographic imports
import math
from math import radians, sin, cos, sqrt, atan2, degrees, atan

# Config import

# Logging beállítás
logger = logging.getLogger(__name__)


class DistanceUnit(Enum):
    """Távolság mértékegységek."""
    KILOMETERS = "km"
    MILES = "miles"
    NAUTICAL_MILES = "nm"
    METERS = "m"


class CoordinateSystem(Enum):
    """Koordináta rendszerek."""
    WGS84 = "WGS84"         # GPS standard
    WGS72 = "WGS72"         # Legacy GPS
    NAD83 = "NAD83"         # North American Datum
    ETRS89 = "ETRS89"       # European standard


@dataclass
class GeoPoint:
    """Földrajzi pont adatstruktúra."""
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    name: Optional[str] = None
    
    def __post_init__(self):
        """Koordináta validálás inicializáláskor."""
        if not self.is_valid():
            raise ValueError(f"Érvénytelen koordináták: lat={self.latitude}, lon={self.longitude}")
    
    def is_valid(self) -> bool:
        """Koordináták érvényességének ellenőrzése."""
        return (-90 <= self.latitude <= 90) and (-180 <= self.longitude <= 180)
    
    def normalize(self) -> 'GeoPoint':
        """Koordináták normalizálása."""
        # Longitude wraparound (-180 to 180)
        normalized_lon = ((self.longitude + 180) % 360) - 180
        
        # Latitude clamping (-90 to 90)
        normalized_lat = max(-90, min(90, self.latitude))
        
        return GeoPoint(
            latitude=normalized_lat,
            longitude=normalized_lon,
            altitude=self.altitude,
            name=self.name
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """GeoPoint dictionary-vé alakítása."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "name": self.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeoPoint':
        """Dictionary-ből GeoPoint létrehozása."""
        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data.get("altitude"),
            name=data.get("name")
        )


@dataclass
class BoundingBox:
    """Bounding box (téglalap) adatstruktúra."""
    min_latitude: float
    max_latitude: float
    min_longitude: float
    max_longitude: float
    
    def __post_init__(self):
        """Bounding box validálás."""
        if self.min_latitude > self.max_latitude:
            raise ValueError("min_latitude nagyobb mint max_latitude")
        if self.min_longitude > self.max_longitude:
            # Longitude wraparound speciális eset (pl. dateline crossing)
            if not (self.min_longitude > 0 and self.max_longitude < 0):
                raise ValueError("min_longitude nagyobb mint max_longitude")
    
    def contains_point(self, point: GeoPoint) -> bool:
        """Ellenőrzi, hogy a pont benne van-e a bounding box-ban."""
        lat_in_range = self.min_latitude <= point.latitude <= self.max_latitude
        
        # Longitude wraparound kezelése
        if self.min_longitude <= self.max_longitude:
            lon_in_range = self.min_longitude <= point.longitude <= self.max_longitude
        else:
            # Dateline crossing case
            lon_in_range = (point.longitude >= self.min_longitude) or (point.longitude <= self.max_longitude)
        
        return lat_in_range and lon_in_range
    
    def get_center(self) -> GeoPoint:
        """Bounding box középpontjának számítása."""
        center_lat = (self.min_latitude + self.max_latitude) / 2
        
        # Longitude center calculation with wraparound
        if self.min_longitude <= self.max_longitude:
            center_lon = (self.min_longitude + self.max_longitude) / 2
        else:
            # Dateline crossing
            center_lon = ((self.min_longitude + self.max_longitude + 360) / 2) % 360
            if center_lon > 180:
                center_lon -= 360
        
        return GeoPoint(latitude=center_lat, longitude=center_lon)
    
    def expand_by_padding(self, padding_degrees: float) -> 'BoundingBox':
        """Bounding box növelése padding-gel."""
        return BoundingBox(
            min_latitude=max(-90, self.min_latitude - padding_degrees),
            max_latitude=min(90, self.max_latitude + padding_degrees),
            min_longitude=max(-180, self.min_longitude - padding_degrees),
            max_longitude=min(180, self.max_longitude + padding_degrees)
        )
    
    def to_dict(self) -> Dict[str, float]:
        """BoundingBox dictionary-vé alakítása."""
        return {
            "min_latitude": self.min_latitude,
            "max_latitude": self.max_latitude,
            "min_longitude": self.min_longitude,
            "max_longitude": self.max_longitude
        }


@dataclass
class GeographicRegion:
    """Földrajzi régió adatstruktúra."""
    name: str
    bounding_box: BoundingBox
    center_point: GeoPoint
    area_km2: Optional[float] = None
    population: Optional[int] = None
    cities_count: Optional[int] = None
    timezone: Optional[str] = None
    
    def is_point_in_region(self, point: GeoPoint) -> bool:
        """Ellenőrzi, hogy pont a régióban van-e."""
        return self.bounding_box.contains_point(point)


class DistanceCalculator:
    """
    🌍 Haversine és Vincenty távolság számító osztály.
    
    Nagy körök távolságának pontos számítása a Föld felszínén:
    - Haversine formula (gyors, jó pontosság)
    - Vincenty formula (lassabb, nagy pontosság)
    - Különböző mértékegységek támogatása
    - Batch távolság számítások
    """
    
    # Earth radius konstansok (méterben)
    EARTH_RADIUS_KM = 6371.0
    EARTH_RADIUS_MILES = 3958.8
    EARTH_RADIUS_NAUTICAL_MILES = 3440.1
    
    # WGS84 ellipsoid konstansok Vincenty formulához
    WGS84_A = 6378137.0  # Semi-major axis (m)
    WGS84_B = 6356752.314245  # Semi-minor axis (m)
    WGS84_F = 1 / 298.257223563  # Flattening
    
    def __init__(self, default_unit: DistanceUnit = DistanceUnit.KILOMETERS):
        """
        DistanceCalculator inicializálása.
        
        Args:
            default_unit: Alapértelmezett mértékegység
        """
        self.default_unit = default_unit
        self.calculation_count = 0
        
        logger.debug(f"DistanceCalculator inicializálva ({default_unit.value})")
    
    def _get_earth_radius(self, unit: DistanceUnit) -> float:
        """Föld sugár lekérdezése mértékegység alapján."""
        radius_map = {
            DistanceUnit.KILOMETERS: self.EARTH_RADIUS_KM,
            DistanceUnit.MILES: self.EARTH_RADIUS_MILES,
            DistanceUnit.NAUTICAL_MILES: self.EARTH_RADIUS_NAUTICAL_MILES,
            DistanceUnit.METERS: self.EARTH_RADIUS_KM * 1000
        }
        return radius_map[unit]
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float,
                          unit: Optional[DistanceUnit] = None) -> float:
        """
        Haversine formula távolság számítás.
        
        Nagy körök távolsága két pont között a Föld felszínén.
        Gyors és kellően pontos a legtöbb alkalmazáshoz (< 0.5% hiba).
        
        Args:
            lat1, lon1: Első pont koordinátái (fok)
            lat2, lon2: Második pont koordinátái (fok)
            unit: Mértékegység (alapértelmezett: self.default_unit)
            
        Returns:
            Távolság a megadott mértékegységben
        """
        if unit is None:
            unit = self.default_unit
        
        # Koordináták radiánba váltása
        lat1_rad, lon1_rad = radians(lat1), radians(lon1)
        lat2_rad, lon2_rad = radians(lat2), radians(lon2)
        
        # Különbségek számítása
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Távolság számítása
        earth_radius = self._get_earth_radius(unit)
        distance = earth_radius * c
        
        self.calculation_count += 1
        return distance
    
    def vincenty_distance(self, lat1: float, lon1: float, lat2: float, lon2: float,
                         unit: Optional[DistanceUnit] = None) -> float:
        """
        Vincenty formula távolság számítás.
        
        Nagy pontosságú távolság számítás WGS84 ellipsoid alapján.
        Lassabb mint Haversine, de nagyobb pontosság (< 0.01% hiba).
        
        Args:
            lat1, lon1: Első pont koordinátái (fok)
            lat2, lon2: Második pont koordinátái (fok)
            unit: Mértékegység
            
        Returns:
            Távolság a megadott mértékegységben
        """
        if unit is None:
            unit = self.default_unit
        
        # Koordináták radiánba váltása
        lat1_rad, lon1_rad = radians(lat1), radians(lon1)
        lat2_rad, lon2_rad = radians(lat2), radians(lon2)
        
        # Longitude különbség
        L = lon2_rad - lon1_rad
        
        # Auxiliary values
        U1 = atan((1 - self.WGS84_F) * math.tan(lat1_rad))
        U2 = atan((1 - self.WGS84_F) * math.tan(lat2_rad))
        
        sin_U1, cos_U1 = sin(U1), cos(U1)
        sin_U2, cos_U2 = sin(U2), cos(U2)
        
        # Iterative calculation
        lambda_val = L
        lambda_prev = 0
        iteration_limit = 100
        iteration = 0
        
        while abs(lambda_val - lambda_prev) > 1e-12 and iteration < iteration_limit:
            sin_lambda = sin(lambda_val)
            cos_lambda = cos(lambda_val)
            
            sin_sigma = sqrt((cos_U2 * sin_lambda) ** 2 + 
                           (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2)
            
            if sin_sigma == 0:
                # Co-incident points
                return 0
            
            cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
            sigma = atan2(sin_sigma, cos_sigma)
            
            sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
            cos2_alpha = 1 - sin_alpha ** 2
            
            if cos2_alpha == 0:
                # Equatorial line
                cos_2sigma_m = 0
            else:
                cos_2sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha
            
            C = self.WGS84_F / 16 * cos2_alpha * (4 + self.WGS84_F * (4 - 3 * cos2_alpha))
            
            lambda_prev = lambda_val
            lambda_val = L + (1 - C) * self.WGS84_F * sin_alpha * \
                        (sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * 
                        (-1 + 2 * cos_2sigma_m ** 2)))
            
            iteration += 1
        
        if iteration >= iteration_limit:
            # Fallback to Haversine if convergence fails
            logger.warning("Vincenty iteráció nem konvergált, Haversine fallback")
            return self.haversine_distance(lat1, lon1, lat2, lon2, unit)
        
        # Calculate distance
        u2 = cos2_alpha * (self.WGS84_A ** 2 - self.WGS84_B ** 2) / (self.WGS84_B ** 2)
        A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
        B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
        
        delta_sigma = B * sin_sigma * (cos_2sigma_m + B / 4 * 
                     (cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) - 
                     B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * 
                     (-3 + 4 * cos_2sigma_m ** 2)))
        
        distance_m = self.WGS84_B * A * (sigma - delta_sigma)
        
        # Convert to requested unit
        if unit == DistanceUnit.KILOMETERS:
            distance = distance_m / 1000
        elif unit == DistanceUnit.MILES:
            distance = distance_m / 1609.344
        elif unit == DistanceUnit.NAUTICAL_MILES:
            distance = distance_m / 1852
        else:  # METERS
            distance = distance_m
        
        self.calculation_count += 1
        return distance
    
    def batch_haversine_distances(self, center_lat: float, center_lon: float,
                                 points: List[Tuple[float, float]],
                                 unit: Optional[DistanceUnit] = None) -> List[float]:
        """
        Batch Haversine távolság számítás egy központi pontból.
        
        Args:
            center_lat, center_lon: Központi pont koordinátái
            points: [(lat, lon), ...] koordináta lista
            unit: Mértékegység
            
        Returns:
            Távolságok listája
        """
        if unit is None:
            unit = self.default_unit
        
        distances = []
        for lat, lon in points:
            distance = self.haversine_distance(center_lat, center_lon, lat, lon, unit)
            distances.append(distance)
        
        return distances
    
    def closest_point(self, reference_lat: float, reference_lon: float,
                     points: List[Tuple[float, float, Any]]) -> Tuple[float, float, Any, float]:
        """
        Legközelebbi pont keresése.
        
        Args:
            reference_lat, reference_lon: Referencia pont
            points: [(lat, lon, data), ...] pontok listája
            
        Returns:
            (lat, lon, data, distance) tuple a legközelebbi ponttal
        """
        if not points:
            raise ValueError("Pontok listája üres")
        
        min_distance = float('inf')
        closest = None
        
        for lat, lon, data in points:
            distance = self.haversine_distance(reference_lat, reference_lon, lat, lon)
            if distance < min_distance:
                min_distance = distance
                closest = (lat, lon, data, distance)
        
        return closest
    
    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Számítási statisztikák lekérdezése."""
        return {
            "total_calculations": self.calculation_count,
            "default_unit": self.default_unit.value
        }


class GeoUtils:
    """
    🌍 Geographic utilities és régió számítások.
    
    Földrajzi műveletek és koordináta számítások:
    - Bounding box kalkulációk
    - Geographic center számítás
    - Régió clustering
    - Coordinate validation és transformation
    - Multi-city analytics geographic support
    """
    
    def __init__(self, distance_calculator: Optional[DistanceCalculator] = None):
        """
        GeoUtils inicializálása.
        
        Args:
            distance_calculator: DistanceCalculator instance (opcionális)
        """
        self.distance_calculator = distance_calculator or DistanceCalculator()
        self.region_cache: Dict[str, GeographicRegion] = {}
        
        logger.debug("GeoUtils inicializálva")
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Koordináták validálása.
        
        Args:
            latitude: Szélesség (-90 to 90)
            longitude: Hosszúság (-180 to 180)
            
        Returns:
            Érvényesek-e a koordináták
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def normalize_coordinates(self, latitude: float, longitude: float) -> Tuple[float, float]:
        """
        Koordináták normalizálása.
        
        Args:
            latitude, longitude: Eredeti koordináták
            
        Returns:
            (normalized_lat, normalized_lon) tuple
        """
        # Latitude clamping
        norm_lat = max(-90, min(90, latitude))
        
        # Longitude wraparound
        norm_lon = ((longitude + 180) % 360) - 180
        
        return norm_lat, norm_lon
    
    def calculate_bounding_box(self, points: List[Tuple[float, float]],
                              padding_degrees: float = 0.0) -> BoundingBox:
        """
        Pontok bounding box-ának számítása.
        
        Args:
            points: [(lat, lon), ...] koordináta lista
            padding_degrees: Bounding box padding fokban
            
        Returns:
            BoundingBox objektum
        """
        if not points:
            raise ValueError("Pontok listája üres")
        
        latitudes = [point[0] for point in points]
        longitudes = [point[1] for point in points]
        
        bbox = BoundingBox(
            min_latitude=min(latitudes),
            max_latitude=max(latitudes),
            min_longitude=min(longitudes),
            max_longitude=max(longitudes)
        )
        
        if padding_degrees > 0:
            bbox = bbox.expand_by_padding(padding_degrees)
        
        return bbox
    
    def calculate_geographic_center(self, points: List[Tuple[float, float]]) -> GeoPoint:
        """
        Pontok földrajzi középpontjának számítása (centroid).
        
        Args:
            points: [(lat, lon), ...] koordináta lista
            
        Returns:
            GeoPoint a középponttal
        """
        if not points:
            raise ValueError("Pontok listája üres")
        
        # Spherical coordinate conversion for accurate center
        x_coords = []
        y_coords = []
        z_coords = []
        
        for lat, lon in points:
            lat_rad = radians(lat)
            lon_rad = radians(lon)
            
            x = cos(lat_rad) * cos(lon_rad)
            y = cos(lat_rad) * sin(lon_rad)
            z = sin(lat_rad)
            
            x_coords.append(x)
            y_coords.append(y)
            z_coords.append(z)
        
        # Average coordinates
        avg_x = statistics.mean(x_coords)
        avg_y = statistics.mean(y_coords)
        avg_z = statistics.mean(z_coords)
        
        # Convert back to lat/lon
        center_lon = atan2(avg_y, avg_x)
        center_lat = atan2(avg_z, sqrt(avg_x**2 + avg_y**2))
        
        return GeoPoint(
            latitude=degrees(center_lat),
            longitude=degrees(center_lon),
            name="Geographic Center"
        )
    
    def calculate_region_from_cities(self, cities_data: List[Dict[str, Any]],
                                   region_name: str) -> GeographicRegion:
        """
        Városok alapján földrajzi régió számítása.
        
        Args:
            cities_data: Városok adatai [{"lat": ..., "lon": ..., "population": ...}, ...]
            region_name: Régió neve
            
        Returns:
            GeographicRegion objektum
        """
        if not cities_data:
            raise ValueError("Városok listája üres")
        
        # Koordináták kinyerése
        coordinates = [(city["lat"], city["lon"]) for city in cities_data]
        
        # Bounding box számítása
        bbox = self.calculate_bounding_box(coordinates, padding_degrees=0.1)
        
        # Földrajzi középpont
        center = self.calculate_geographic_center(coordinates)
        
        # Összesített adatok
        total_population = sum(city.get("population", 0) for city in cities_data if city.get("population"))
        cities_count = len(cities_data)
        
        # Régió területe (rough estimation)
        area_km2 = self._estimate_bounding_box_area(bbox)
        
        region = GeographicRegion(
            name=region_name,
            bounding_box=bbox,
            center_point=center,
            area_km2=area_km2,
            population=total_population if total_population > 0 else None,
            cities_count=cities_count
        )
        
        # Cache mentése
        self.region_cache[region_name] = region
        
        return region
    
    def _estimate_bounding_box_area(self, bbox: BoundingBox) -> float:
        """
        Bounding box területének becslése km²-ben.
        
        Args:
            bbox: BoundingBox objektum
            
        Returns:
            Terület km²-ben (közelítés)
        """
        # Közelítő számítás: rectangle area with latitude correction
        lat_diff = bbox.max_latitude - bbox.min_latitude
        lon_diff = bbox.max_longitude - bbox.min_longitude
        
        # Latitude correction factor
        avg_lat = (bbox.max_latitude + bbox.min_latitude) / 2
        lat_correction = cos(radians(avg_lat))
        
        # Degrees to kilometers conversion (rough)
        lat_km = lat_diff * 111.32  # 1 degree latitude ≈ 111.32 km
        lon_km = lon_diff * 111.32 * lat_correction  # Longitude varies with latitude
        
        return abs(lat_km * lon_km)
    
    def group_cities_by_proximity(self, cities_data: List[Dict[str, Any]],
                                 max_distance_km: float = 100) -> List[List[Dict[str, Any]]]:
        """
        Városok csoportosítása földrajzi közelség alapján.
        
        Args:
            cities_data: Városok adatai
            max_distance_km: Maximum távolság km-ben csoporton belül
            
        Returns:
            Város csoportok listája
        """
        if not cities_data:
            return []
        
        groups = []
        remaining_cities = cities_data.copy()
        
        while remaining_cities:
            # Új csoport indítása az első maradék várossal
            current_group = [remaining_cities.pop(0)]
            
            # Közeli városok hozzáadása
            added_to_group = True
            while added_to_group and remaining_cities:
                added_to_group = False
                
                for group_city in current_group[:]:  # Copy to avoid modification during iteration
                    for i, city in enumerate(remaining_cities):
                        distance = self.distance_calculator.haversine_distance(
                            group_city["lat"], group_city["lon"],
                            city["lat"], city["lon"]
                        )
                        
                        if distance <= max_distance_km:
                            current_group.append(remaining_cities.pop(i))
                            added_to_group = True
                            break
                    
                    if added_to_group:
                        break
            
            groups.append(current_group)
        
        # Csoportok rendezése méret szerint
        groups.sort(key=len, reverse=True)
        
        return groups
    
    def find_optimal_cities_for_region(self, all_cities: List[Dict[str, Any]],
                                      target_count: int,
                                      region_bbox: Optional[BoundingBox] = None) -> List[Dict[str, Any]]:
        """
        Optimális városok kiválasztása régióhoz analytics célokra.
        
        Args:
            all_cities: Összes város adat
            target_count: Célszám
            region_bbox: Régió bounding box szűréshez
            
        Returns:
            Optimalizált város lista
        """
        # Régió szűrés ha van bbox
        filtered_cities = all_cities
        if region_bbox:
            filtered_cities = []
            for city in all_cities:
                point = GeoPoint(city["lat"], city["lon"])
                if region_bbox.contains_point(point):
                    filtered_cities.append(city)
        
        # Ha kevesebb város van mint a cél, visszaadjuk mind
        if len(filtered_cities) <= target_count:
            return filtered_cities
        
        # Populáció alapú pre-sorting
        cities_with_pop = [city for city in filtered_cities if city.get("population", 0) > 0]
        cities_without_pop = [city for city in filtered_cities if city.get("population", 0) <= 0]
        
        cities_with_pop.sort(key=lambda c: c.get("population", 0), reverse=True)
        
        # Geographic distribution optimization
        selected_cities = []
        remaining_cities = cities_with_pop + cities_without_pop
        
        # Első város: legnagyobb populáció
        if remaining_cities:
            selected_cities.append(remaining_cities.pop(0))
        
        # Többi város: távolság-populáció optimalizációval
        while len(selected_cities) < target_count and remaining_cities:
            best_city = None
            best_score = -1
            
            for city in remaining_cities:
                # Minimum távolság a már kiválasztottaktól
                min_distance = float('inf')
                for selected in selected_cities:
                    distance = self.distance_calculator.haversine_distance(
                        city["lat"], city["lon"],
                        selected["lat"], selected["lon"]
                    )
                    min_distance = min(min_distance, distance)
                
                # Score: távolság súlyozás + populáció súlyozás
                distance_score = min(min_distance / 1000, 1.0)  # Max 1000 km normalizálás
                population_score = min(city.get("population", 1) / 1000000, 1.0)  # Max 1M normalizálás
                
                combined_score = distance_score * 0.7 + population_score * 0.3
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_city = city
            
            if best_city:
                selected_cities.append(best_city)
                remaining_cities.remove(best_city)
            else:
                break
        
        return selected_cities
    
    # 🌍 MULTI-CITY ANALYTICS SPECIFIC METHODS
    
    def optimize_cities_for_weather_analytics(self, cities_data: List[Dict[str, Any]],
                                            analytics_type: str,
                                            max_cities: int = 50) -> List[Dict[str, Any]]:
        """
        🏙️ Városok optimalizálása időjárási analytics típusához.
        
        Args:
            cities_data: Összes város adat
            analytics_type: "temperature", "precipitation", "wind", "global"
            max_cities: Maximum városok száma
            
        Returns:
            Optimalizált város lista analytics típushoz
        """
        # Analytics típus specifikus szűrők
        filters = {
            "temperature": {"min_population": 100000, "distribution_weight": 0.8},
            "precipitation": {"min_population": 50000, "distribution_weight": 0.6},
            "wind": {"min_population": 200000, "distribution_weight": 0.9},  # Coastal preference
            "global": {"min_population": 500000, "distribution_weight": 0.7}
        }
        
        filter_config = filters.get(analytics_type, filters["global"])
        
        # Population szűrés
        filtered_cities = [
            city for city in cities_data 
            if city.get("population", 0) >= filter_config["min_population"]
        ]
        
        # Ha túl kevés város, enyhébb szűrés
        if len(filtered_cities) < max_cities // 2:
            filtered_cities = [
                city for city in cities_data 
                if city.get("population", 0) >= filter_config["min_population"] // 2
            ]
        
        # Geographic distribution optimization
        if len(filtered_cities) > max_cities:
            filtered_cities = self.find_optimal_cities_for_region(
                filtered_cities, max_cities
            )
        
        logger.info(f"Időjárási analytics városok optimalizálva ({analytics_type}): {len(filtered_cities)}")
        return filtered_cities
    
    def calculate_multi_city_coverage_area(self, cities_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Multi-city analytics lefedettségi terület számítása.
        
        Args:
            cities_data: Városok adatai
            
        Returns:
            Lefedettségi statisztikák
        """
        if not cities_data:
            return {}
        
        coordinates = [(city["lat"], city["lon"]) for city in cities_data]
        bbox = self.calculate_bounding_box(coordinates)
        center = self.calculate_geographic_center(coordinates)
        area_km2 = self._estimate_bounding_box_area(bbox)
        
        # Távolság statisztikák
        distances = []
        center_lat, center_lon = center.latitude, center.longitude
        
        for city in cities_data:
            distance = self.distance_calculator.haversine_distance(
                center_lat, center_lon, city["lat"], city["lon"]
            )
            distances.append(distance)
        
        coverage_stats = {
            "bounding_box": bbox.to_dict(),
            "geographic_center": center.to_dict(),
            "area_km2": area_km2,
            "cities_count": len(cities_data),
            "distances": {
                "max_distance_from_center": max(distances) if distances else 0,
                "avg_distance_from_center": statistics.mean(distances) if distances else 0,
                "coverage_radius_km": max(distances) if distances else 0
            }
        }
        
        return coverage_stats
    
    # 🗺️ MAP PROJECTION AND VISUALIZATION SUPPORT
    
    def convert_to_web_mercator(self, latitude: float, longitude: float) -> Tuple[float, float]:
        """
        WGS84 koordináták Web Mercator projektálásba konvertálása.
        
        Args:
            latitude, longitude: WGS84 koordináták
            
        Returns:
            (x, y) Web Mercator koordináták
        """
        # Web Mercator projection (EPSG:3857)
        x = longitude * 20037508.34 / 180
        y = math.log(math.tan((90 + latitude) * math.pi / 360)) / (math.pi / 180)
        y = y * 20037508.34 / 180
        
        return x, y
    
    def suggest_map_zoom_level(self, bbox: BoundingBox, map_width_px: int = 800) -> int:
        """
        Térképi zoom szint javaslat bounding box alapján.
        
        Args:
            bbox: Bounding box
            map_width_px: Térkép szélesség pixelben
            
        Returns:
            Javasolt zoom szint (0-18)
        """
        # Longitude span
        lon_span = abs(bbox.max_longitude - bbox.min_longitude)
        
        # World width at different zoom levels (Web Mercator)
        world_width = 256  # Zoom level 0
        
        # Calculate zoom level based on longitude span
        zoom = 0
        while zoom < 18:
            if world_width >= map_width_px * lon_span / 360:
                break
            world_width *= 2
            zoom += 1
        
        return max(0, min(18, zoom))


# 🧪 DEMO AND TESTING

def demo_geo_utils():
    """GeoUtils demo és tesztelés."""
    print("🌍 Geographic Utils Demo")
    print("=" * 50)
    
    # Distance Calculator tesztelés
    print("📏 Distance Calculator:")
    calculator = DistanceCalculator()
    
    # Budapest-Berlin távolság
    budapest = (47.4979, 19.0402)
    berlin = (52.5200, 13.4050)
    
    haversine_dist = calculator.haversine_distance(
        budapest[0], budapest[1], berlin[0], berlin[1]
    )
    vincenty_dist = calculator.vincenty_distance(
        budapest[0], budapest[1], berlin[0], berlin[1]
    )
    
    print(f"Budapest-Berlin távolság:")
    print(f"  Haversine: {haversine_dist:.2f} km")
    print(f"  Vincenty:  {vincenty_dist:.2f} km")
    print(f"  Különbség: {abs(haversine_dist - vincenty_dist):.3f} km")
    print()
    
    # GeoUtils tesztelés
    print("🗺️ Geographic Utils:")
    geo_utils = GeoUtils(calculator)
    
    # Teszt városok
    test_cities = [
        {"lat": 47.4979, "lon": 19.0402, "population": 1750000, "name": "Budapest"},
        {"lat": 47.6835, "lon": 17.6383, "population": 130000, "name": "Győr"},
        {"lat": 47.5316, "lon": 21.6273, "population": 200000, "name": "Debrecen"},
        {"lat": 46.2530, "lon": 20.1414, "population": 160000, "name": "Szeged"},
        {"lat": 46.0727, "lon": 18.2324, "population": 145000, "name": "Pécs"}
    ]
    
    # Bounding box számítás
    coordinates = [(city["lat"], city["lon"]) for city in test_cities]
    bbox = geo_utils.calculate_bounding_box(coordinates, padding_degrees=0.1)
    
    print(f"Magyar városok bounding box:")
    print(f"  Lat: {bbox.min_latitude:.4f} - {bbox.max_latitude:.4f}")
    print(f"  Lon: {bbox.min_longitude:.4f} - {bbox.max_longitude:.4f}")
    
    # Földrajzi középpont
    center = geo_utils.calculate_geographic_center(coordinates)
    print(f"  Középpont: {center.latitude:.4f}, {center.longitude:.4f}")
    print()
    
    # Régió számítás
    region = geo_utils.calculate_region_from_cities(test_cities, "Magyarország")
    print(f"Magyarország régió:")
    print(f"  Terület: {region.area_km2:.0f} km²")
    print(f"  Populáció: {region.population:,}")
    print(f"  Városok: {region.cities_count}")
    print()
    
    # Proximity grouping
    print("📍 Proximity grouping (100 km):")
    groups = geo_utils.group_cities_by_proximity(test_cities, max_distance_km=100)
    for i, group in enumerate(groups, 1):
        cities_names = [city["name"] for city in group]
        print(f"  Csoport {i}: {', '.join(cities_names)}")
    print()
    
    # Multi-city analytics optimalizálás
    print("🏙️ Multi-city analytics optimalizálás:")
    optimized = geo_utils.optimize_cities_for_weather_analytics(
        test_cities, "temperature", max_cities=3
    )
    optimized_names = [city["name"] for city in optimized]
    print(f"  Optimalizált városok (temperature): {', '.join(optimized_names)}")
    
    # Coverage area
    coverage = geo_utils.calculate_multi_city_coverage_area(test_cities)
    print(f"  Lefedettségi terület: {coverage['area_km2']:.0f} km²")
    print(f"  Maximum távolság középponttól: {coverage['distances']['max_distance_from_center']:.1f} km")
    print()
    
    # Map projection
    print("🗺️ Map projection:")
    web_mercator = geo_utils.convert_to_web_mercator(budapest[0], budapest[1])
    print(f"Budapest Web Mercator: {web_mercator[0]:.0f}, {web_mercator[1]:.0f}")
    
    zoom_level = geo_utils.suggest_map_zoom_level(bbox)
    print(f"Javasolt zoom szint: {zoom_level}")
    print()
    
    # Statistics
    stats = calculator.get_calculation_statistics()
    print(f"📊 Statisztikák: {stats['total_calculations']} távolság számítás")


if __name__ == "__main__":
    demo_geo_utils()
