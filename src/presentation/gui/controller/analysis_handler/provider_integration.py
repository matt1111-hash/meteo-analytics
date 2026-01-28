#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analysis Handler - Provider Integration

🌐 Provider routing integráció

Képességek:
- Provider routing enhancement
- Koordináta kinyerés
- Provider selection

Fájl: src/presentation/gui/controller/analysis_handler/provider_integration.py
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Tuple

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _enhance_request_with_provider_routing(self, request_data: Dict[str, Any],
                                          provider_routing) -> Dict[str, Any]:
    """
    Provider routing integráció - Kérés gazdagítása provider információkkal.

    Args:
        self: AnalysisHandler instance
        request_data: Eredeti kérés
        provider_routing: ProviderRouting példány

    Returns:
        Gazdagított kérés provider routing információkkal
    """
    try:
        enhanced_request = request_data.copy()

        # Koordináták kinyerése
        latitude, longitude = _extract_coordinates_from_request(self, request_data)

        if latitude is not None and longitude is not None:
            # Smart provider selection
            date_range = request_data.get('date_range', {})
            selected_provider = provider_routing.select_provider_for_request(
                latitude, longitude,
                date_range.get('start_date', ''),
                date_range.get('end_date', '')
            )

            # Provider információk hozzáadása
            enhanced_request['selected_provider'] = selected_provider
            enhanced_request['provider_config'] = provider_routing.provider_config.PROVIDERS.get(selected_provider, {})

            # Usage tracking
            provider_routing.track_provider_usage(selected_provider)

            logger.info(f"🌐 Provider routing: {selected_provider} selected")
        else:
            # Fallback provider
            enhanced_request['selected_provider'] = 'open-meteo'
            logger.warning("🌐 No coordinates found, using fallback provider")

        return enhanced_request

    except Exception as e:
        logger.error(f"Provider routing enhancement hiba: {e}")
        return request_data


def _extract_coordinates_from_request(self, request_data: Dict[str, Any]) -> Tuple:
    """
    Koordináták kinyerése a kérésből az elemzés típusa alapján.

    Args:
        self: AnalysisHandler instance
        request_data: Kérés adatok

    Returns:
        (latitude, longitude) tuple vagy (None, None)
    """
    analysis_type = request_data.get('analysis_type')

    if analysis_type == 'single_location':
        # 1. Direkt koordináták keresése
        if 'latitude' in request_data and 'longitude' in request_data:
            return request_data.get('latitude'), request_data.get('longitude')
        elif 'lat' in request_data and 'lon' in request_data:
            return request_data.get('lat'), request_data.get('lon')

        # 2. location_data objektum ellenőrzése
        location_data = request_data.get('location_data', {})
        if location_data:
            lat = location_data.get('latitude') or location_data.get('lat')
            lon = location_data.get('longitude') or location_data.get('lon')

            if lat is not None and lon is not None:
                return lat, lon

    elif analysis_type in ['multi_city', 'county_analysis']:
        # Multi-city esetén használjuk a jelenlegi város koordinátáit (ha van)
        # Ez a kontexterületből kellene jöjjön
        return 47.4979, 19.0402  # Budapest default

    return None, None
