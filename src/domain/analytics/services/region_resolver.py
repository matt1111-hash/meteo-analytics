"""Region name resolver with Hungarian region/county support."""
from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class RegionResolverService:
    """Resolve free-form region input to canonical region names."""

    REGION_CODE_MAPPING: Dict[str, str] = {
        "HU": "Hungary",
        "EU": "Europe",
        "GLOBAL": "Global",
        "WORLD": "Global",
        "country": "Hungary",
        "continent": "Europe",
        "global": "Global",
        "hungary": "Hungary",
        "europe": "Europe",
        "magyarország": "Hungary",
        "európa": "Europe",
        "Közép-Magyarország": "Hungary",
        "Észak-Magyarország": "Hungary",
        "Észak-Alföld": "Hungary",
        "Dél-Alföld": "Hungary",
        "Dél-Dunántúl": "Hungary",
        "Nyugat-Dunántúl": "Hungary",
        "Közép-Dunántúl": "Hungary",
        "Budapest": "Hungary",
        "Pest": "Hungary",
        "Fejér": "Hungary",
        "Komárom-Esztergom": "Hungary",
        "Veszprém": "Hungary",
        "Győr-Moson-Sopron": "Hungary",
        "Vas": "Hungary",
        "Zala": "Hungary",
        "Baranya": "Hungary",
        "Somogy": "Hungary",
        "Tolna": "Hungary",
        "Borsod-Abaúj-Zemplén": "Hungary",
        "Heves": "Hungary",
        "Nógrád": "Hungary",
        "Hajdú-Bihar": "Hungary",
        "Jász-Nagykun-Szolnok": "Hungary",
        "Szabolcs-Szatmár-Bereg": "Hungary",
        "Bács-Kiskun": "Hungary",
        "Békés": "Hungary",
        "Csongrád-Csanád": "Hungary",
        "közép-magyarország": "Hungary",
        "észak-magyarország": "Hungary",
        "észak-alföld": "Hungary",
        "dél-alföld": "Hungary",
        "dél-dunántúl": "Hungary",
        "nyugat-dunántúl": "Hungary",
        "közép-dunántúl": "Hungary",
        "budapest": "Hungary",
        "pest megye": "Hungary",
        "fejér megye": "Hungary",
    }

    HUNGARIAN_REGIONS = [
        "közép-magyarország",
        "észak-magyarország",
        "észak-alföld",
        "dél-alföld",
        "dél-dunántúl",
        "nyugat-dunántúl",
        "közép-dunántúl",
    ]

    HUNGARIAN_COUNTIES = [
        "budapest",
        "pest",
        "fejér",
        "komárom-esztergom",
        "veszprém",
        "győr-moson-sopron",
        "vas",
        "zala",
        "baranya",
        "somogy",
        "tolna",
        "borsod-abaúj-zemplén",
        "heves",
        "nógrád",
        "hajdú-bihar",
        "jász-nagykun-szolnok",
        "szabolcs-szatmár-bereg",
        "bács-kiskun",
        "békés",
        "csongrád-csanád",
    ]

    def resolve_region_name(self, region_input: str) -> str:
        """Return canonical region name or raise ValueError on unknown."""
        if not region_input:
            raise ValueError("Üres régió név")

        region_key = region_input.strip()
        if region_key in self.REGION_CODE_MAPPING:
            mapped = self.REGION_CODE_MAPPING[region_key]
            logger.info("Exact region mapping: '%s' → '%s'", region_input, mapped)
            return mapped

        region_key_lower = region_key.lower()
        for key, value in self.REGION_CODE_MAPPING.items():
            if key.lower() == region_key_lower:
                logger.info("Case-insensitive region mapping: '%s' → '%s'", region_input, value)
                return value

        if self._matches_hungarian_region(region_key_lower):
            logger.info("Partial region mapping: '%s' → 'Hungary'", region_input)
            return "Hungary"

        if self._matches_hungarian_county(region_key_lower):
            logger.info("County region mapping: '%s' → 'Hungary'", region_input)
            return "Hungary"

        samples = ", ".join(list(self.REGION_CODE_MAPPING.keys())[:10])
        error_msg = f"Ismeretlen régió: {region_input}. Támogatott példa régiók: {samples}..."
        logger.error(error_msg)
        raise ValueError(error_msg)

    def _matches_hungarian_region(self, normalized: str) -> bool:
        return any(region in normalized or normalized in region for region in self.HUNGARIAN_REGIONS)

    def _matches_hungarian_county(self, normalized: str) -> bool:
        return any(county in normalized or normalized in county for county in self.HUNGARIAN_COUNTIES)
