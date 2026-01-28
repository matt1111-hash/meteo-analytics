#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-City Widget - Regional Data

🏛️ Magyar régiók és megyék statikus adatai

Képességek:
- Magyar NUTS régiók listája
- Régió-megye mapping

Fájl: src/presentation/gui/panel_widgets/multi_city_widget/regional_data.py
"""

from typing import Dict, List


def get_hungarian_regions() -> List[str]:
    """
    Magyar NUTS régiók listája (hungarian_settlements_importer.py alapján).

    Returns:
        7 magyar statisztikai régió listája
    """
    return [
        "Közép-Magyarország",     # Budapest + Pest
        "Közép-Dunántúl",         # Fejér + Komárom-Esztergom + Veszprém
        "Nyugat-Dunántúl",        # Győr-Moson-Sopron + Vas + Zala
        "Dél-Dunántúl",           # Baranya + Somogy + Tolna
        "Észak-Magyarország",     # Borsod-Abaúj-Zemplén + Heves + Nógrád
        "Észak-Alföld",           # Hajdú-Bihar + Jász-Nagykun-Szolnok + Szabolcs-Szatmár-Bereg
        "Dél-Alföld"              # Bács-Kiskun + Békés + Csongrád-Csanád
    ]


def get_region_county_mapping() -> Dict[str, List[str]]:
    """
    Régióhoz tartozó megyék listája (hungarian_settlements_importer.py alapján).

    Returns:
        Dict mapping régió nevekhez megye listákhoz
    """
    return {
        "Közép-Magyarország": ["Budapest", "Pest"],
        "Közép-Dunántúl": ["Fejér", "Komárom-Esztergom", "Veszprém"],
        "Nyugat-Dunántúl": ["Győr-Moson-Sopron", "Vas", "Zala"],
        "Dél-Dunántúl": ["Baranya", "Somogy", "Tolna"],
        "Észak-Magyarország": ["Borsod-Abaúj-Zemplén", "Heves", "Nógrád"],
        "Észak-Alföld": ["Hajdú-Bihar", "Jász-Nagykun-Szolnok", "Szabolcs-Szatmár-Bereg"],
        "Dél-Alföld": ["Bács-Kiskun", "Békés", "Csongrád-Csanád"]
    }


def get_counties_for_region(region: str) -> List[str]:
    """
    Régióhoz tartozó megyék listája.

    Args:
        region: Régió neve

    Returns:
        Megyék listája
    """
    mapping = get_region_county_mapping()
    return mapping.get(region, [])
