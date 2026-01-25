#!/usr/bin/env python3
"""
Multi-City Analytics Engine - Types and Constants
Type aliases, constants, and configuration mappings
"""

from typing import List, Optional, Tuple

Number = float | int
NumberOrNone = Number | None


# Hungarian regional mapping (7 statistical regions → counties)
HUNGARIAN_REGIONAL_MAPPING = {
    # 7 STATISZTIKAI RÉGIÓ → MEGYÉK MAPPING (KSH HIVATALOS)
    "Észak-Magyarország": ["Borsod-Abaúj-Zemplén", "Heves", "Nógrád"],
    "Közép-Magyarország": ["Budapest", "Pest"],
    "Észak-Alföld": ["Hajdú-Bihar", "Jász-Nagykun-Szolnok", "Szabolcs-Szatmár-Bereg"],
    "Dél-Alföld": ["Bács-Kiskun", "Békés", "Csongrád-Csanád"],
    "Dél-Dunántúl": ["Baranya", "Somogy", "Tolna"],
    "Nyugat-Dunántúl": ["Győr-Moson-Sopron", "Vas", "Zala"],
    "Közép-Dunántúl": ["Fejér", "Komárom-Esztergom", "Veszprém"],

    # MEGYÉK EGYEDI KEZELÉSE (ha valaki konkrét megyét választ)
    "Budapest": ["Budapest"],
    "Pest": ["Pest"],
    "Borsod-Abaúj-Zemplén": ["Borsod-Abaúj-Zemplén"],
    "Heves": ["Heves"],
    "Nógrád": ["Nógrád"],
    "Hajdú-Bihar": ["Hajdú-Bihar"],
    "Jász-Nagykun-Szolnok": ["Jász-Nagykun-Szolnok"],
    "Szabolcs-Szatmár-Bereg": ["Szabolcs-Szatmár-Bereg"],
    "Bács-Kiskun": ["Bács-Kiskun"],
    "Békés": ["Békés"],
    "Csongrád-Csanád": ["Csongrád-Csanád"],
    "Baranya": ["Baranya"],
    "Somogy": ["Somogy"],
    "Tolna": ["Tolna"],
    "Győr-Moson-Sopron": ["Győr-Moson-Sopron"],
    "Vas": ["Vas"],
    "Zala": ["Zala"],
    "Fejér": ["Fejér"],
    "Komárom-Esztergom": ["Komárom-Esztergom"],
    "Veszprém": ["Veszprém"]
}

# Region configuration
REGIONS = {
    "Hungary": {"name": "Magyarország", "country_codes": ["HU"], "max_cities": 165, "batch_size": 8, "rate_limit_delay": 0.2},
    "Europe": {"name": "Európa", "country_codes": ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "CH", "GB", "NO", "IS", "RS", "BA", "MK", "AL", "MD", "UA", "BY", "RU"], "max_cities": 150, "batch_size": 4, "rate_limit_delay": 0.4},
    "Global": {"name": "Globális", "country_codes": [], "max_cities": 160, "batch_size": 8, "rate_limit_delay": 0.5},
}


__all__ = [
    'Number',
    'NumberOrNone',
    'HUNGARIAN_REGIONAL_MAPPING',
    'REGIONS'
]
