#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - Region Data
Magyar Klímaanalitika MVP - Statisztikai régió adatok
"""

from typing import Dict

from ..models import HungarianRegionData, HungarianStatisticalRegion


def init_statistical_regions() -> Dict[str, HungarianRegionData]:
    """
    🔧 KRITIKUS JAVÍTÁS: Magyar 7 statisztikai régió inicializálása (Control Panel + Multi-City Engine konzisztens!)

    KSH NUTS 2 szintű régió felosztás:
    - Control Panel régió dropdown-pal 100% egyezés
    - Multi-City Engine HUNGARIAN_REGIONAL_MAPPING kompatibilitás
    - Hivatalos megyei tartozás
    """
    regions = {
        HungarianStatisticalRegion.KOZEP_MAGYARORSZAG.value: HungarianRegionData(
            name="kozep_magyarorszag",
            display_name="Közép-Magyarország",
            description="Főváros és agglomerációja, legnagyobb népességű régió",
            counties=["Budapest", "Pest"],
            administrative_center="Budapest",
            nuts_code="HU10",
            avg_temp_annual=10.4,
            avg_precipitation_annual=580,
            characteristics=[
                "Városi környezet",
                "Legnagyobb népesség",
                "Gazdasági központ",
                "Duna menti fekvés",
            ],
        ),
        HungarianStatisticalRegion.KOZEP_DUNANTUL.value: HungarianRegionData(
            name="kozep_dunantul",
            display_name="Közép-Dunántúl",
            description="Dunántúl központi területe, átmeneti jellegű régió",
            counties=["Fejér", "Komárom-Esztergom", "Veszprém"],
            administrative_center="Székesfehérvár",
            nuts_code="HU21",
            avg_temp_annual=9.9,
            avg_precipitation_annual=620,
            characteristics=[
                "Átmeneti éghajlat",
                "Balatoni régió",
                "Ipari hagyományok",
                "Középhegységi területek",
            ],
        ),
        HungarianStatisticalRegion.NYUGAT_DUNANTUL.value: HungarianRegionData(
            name="nyugat_dunantul",
            display_name="Nyugat-Dunántúl",
            description="Osztrák határ mentén, óceáni hatással",
            counties=["Győr-Moson-Sopron", "Vas", "Zala"],
            administrative_center="Győr",
            nuts_code="HU22",
            avg_temp_annual=9.8,
            avg_precipitation_annual=700,
            characteristics=[
                "Óceáni hatás",
                "Legnagyobb csapadék",
                "Nyugati határvidék",
                "Autóipar központ",
            ],
        ),
        HungarianStatisticalRegion.DEL_DUNANTUL.value: HungarianRegionData(
            name="del_dunantul",
            display_name="Dél-Dunántúl",
            description="Horvát határ mentén, mediterrán hatással",
            counties=["Baranya", "Somogy", "Tolna"],
            administrative_center="Pécs",
            nuts_code="HU23",
            avg_temp_annual=10.3,
            avg_precipitation_annual=650,
            characteristics=[
                "Mediterrán hatás",
                "Mecsek hegység",
                "Borászat",
                "Történelmi városok",
            ],
        ),
        HungarianStatisticalRegion.ESZAK_MAGYARORSZAG.value: HungarianRegionData(
            name="eszak_magyarorszag",
            display_name="Észak-Magyarország",
            description="Hegyvidéki régió, ipari hagyományokkal",
            counties=["Borsod-Abaúj-Zemplén", "Heves", "Nógrád"],
            administrative_center="Miskolc",
            nuts_code="HU31",
            avg_temp_annual=9.2,
            avg_precipitation_annual=750,
            characteristics=[
                "Hegyvidéki éghajlat",
                "Nehézipar",
                "Legmagasabb csapadék",
                "Bükk hegység",
            ],
        ),
        HungarianStatisticalRegion.ESZAK_ALFOLD.value: HungarianRegionData(
            name="eszak_alfold",
            display_name="Észak-Alföld",
            description="Alföldi régió északi része, kontinentális éghajlat",
            counties=["Hajdú-Bihar", "Jász-Nagykun-Szolnok", "Szabolcs-Szatmár-Bereg"],
            administrative_center="Debrecen",
            nuts_code="HU32",
            avg_temp_annual=10.1,
            avg_precipitation_annual=560,
            characteristics=[
                "Kontinentális éghajlat",
                "Mezőgazdaság",
                "Tiszántúl",
                "Egyetemi városok",
            ],
        ),
        HungarianStatisticalRegion.DEL_ALFOLD.value: HungarianRegionData(
            name="del_alfold",
            display_name="Dél-Alföld",
            description="Alföldi régió déli része, legszárazabb terület",
            counties=["Bács-Kiskun", "Békés", "Csongrád-Csanád"],
            administrative_center="Szeged",
            nuts_code="HU33",
            avg_temp_annual=10.8,
            avg_precipitation_annual=520,
            characteristics=[
                "Legszárazabb régió",
                "Homoktalajok",
                "Termálvíz",
                "Paprika termesztés",
            ],
        ),
    }

    return regions
