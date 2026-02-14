#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian City Selector - Types Module
Magyar város adatstruktúrák és régió osztályozás.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HungarianCity:
    """Magyar város adatstruktúra"""

    city: str
    country: str
    country_code: str
    lat: float
    lon: float
    population: Optional[int] = None
    admin_name: Optional[str] = None
    meteostat_station_id: Optional[str] = None
    data_quality_score: Optional[float] = None
    region: Optional[str] = None


class HungarianRegions:
    """
    🇭🇺 Magyar régiók osztályozása és mappingje
    """

    # Régió mappingek népszerű városok alapján
    REGION_MAPPING = {
        # Alföld
        "Debrecen": "Alföld",
        "Szeged": "Alföld",
        "Kecskemét": "Alföld",
        "Nyíregyháza": "Alföld",
        "Békéscsaba": "Alföld",
        "Szolnok": "Alföld",
        "Orosháza": "Alföld",
        "Cegléd": "Alföld",
        "Hodmezovasarhely": "Alföld",
        "Jászberény": "Alföld",
        # Dunántúl
        "Pécs": "Dunántúl",
        "Győr": "Dunántúl",
        "Székesfehérvár": "Dunántúl",
        "Szombathely": "Dunántúl",
        "Kaposvár": "Dunántúl",
        "Veszprém": "Dunántúl",
        "Zalaegerszeg": "Dunántúl",
        "Nagykanizsa": "Dunántúl",
        "Sopron": "Dunántúl",
        "Tatabánya": "Dunántúl",
        "Dunaújváros": "Dunántúl",
        "Ajka": "Dunántúl",
        # Közép-Magyarország
        "Budapest": "Közép-Magyarország",
        "Gödöllő": "Közép-Magyarország",
        "Vác": "Közép-Magyarország",
        "Szentendre": "Közép-Magyarország",
        # Északi-régió
        "Miskolc": "Északi-régió",
        "Eger": "Északi-régió",
        "Salgótarján": "Északi-régió",
        "Gyöngyös": "Északi-régió",
        "Balassagyarmat": "Északi-régió",
    }

    REGION_DISPLAY_NAMES = {
        "Alföld": "🌾 Alföld",
        "Dunántúl": "🏔️ Dunántúl",
        "Közép-Magyarország": "🏛️ Közép-Magyarország",
        "Északi-régió": "⛰️ Északi-régió",
        "Egyéb": "🏘️ Egyéb",
    }

    REGION_DESCRIPTIONS = {
        "Alföld": "Nagy Magyar Alföld - síkvidéki klíma",
        "Dunántúl": "Dunántúli-dombság és középhegység",
        "Közép-Magyarország": "Főváros és agglomeráció",
        "Északi-régió": "Északi-középhegység vidéke",
        "Egyéb": "Egyéb területek",
    }

    @classmethod
    def get_region_for_city(cls, city_name: str) -> str:
        """
        Város régió besorolásának meghatározása.

        Args:
            city_name: Magyar város neve

        Returns:
            Régió neve vagy 'Egyéb'
        """
        return cls.REGION_MAPPING.get(city_name, "Egyéb")

    @classmethod
    def get_all_regions(cls) -> List[str]:
        """Összes régió listája"""
        return list(cls.REGION_DISPLAY_NAMES.keys())

    @classmethod
    def get_cities_by_region(
        cls, region: str, cities: List[HungarianCity]
    ) -> List[HungarianCity]:
        """
        Városok szűrése régió alapján.

        Args:
            region: Régió neve
            cities: Összes város listája

        Returns:
            Szűrt városok listája
        """
        if region == "Összes":
            return cities

        filtered_cities = []
        for city in cities:
            city_region = cls.get_region_for_city(city.city)
            if city_region == region:
                filtered_cities.append(city)

        return filtered_cities
