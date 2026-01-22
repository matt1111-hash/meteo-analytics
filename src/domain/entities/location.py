from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum

# Temporary import until Enums are moved to domain
from src.data.enums import RegionType

class LocationType(Enum):
    """🌍 Univerzális lokáció típusok - USER SZABADSÁG"""
    REGION = "region"                    # Klimatikus régiók (Mediterrán, Kontinentális)
    COUNTRY = "country"                  # Országok (Magyarország, Németország)
    MICRO_REGION = "micro_region"        # Magyar micro-régiók (Alföld, Nyugat-Dunántúl)
    CITY = "city"                        # Városok (Budapest, Berlin)
    COORDINATES = "coordinates"          # Koordináták (47.4979, 19.0402)
    MULTIPLE = "multiple"                # Több lokáció kombinációja
    CUSTOM = "custom"                    # User-definiált lokáció

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

def create_universal_location(
    location_type: Union[LocationType, str],
    identifier: Union[str, Tuple[float, float], List[str]],
    display_name: str,
    **kwargs
) -> UniversalLocation:
    """
    🌍 UniversalLocation factory - USER-FRIENDLY
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

def create_location(
    identifier: str,
    display_name: str,
    latitude: float,
    longitude: float,
    **kwargs
) -> Location:
    """
    🗺️ Location factory function - HungarianLocationSelector kompatibilitás.
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
    """
    return Location.from_coordinates(latitude, longitude, display_name, **kwargs)
