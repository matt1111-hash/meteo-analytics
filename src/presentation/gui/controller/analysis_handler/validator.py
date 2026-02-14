#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analysis Handler - Validator

✅ Request validálás

Képességek:
- Analysis request validálás
- Koordináta validálás
- Dátum range validálás

Fájl: src/presentation/gui/controller/analysis_handler/validator.py
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _validate_analysis_request(self, request_data: Dict[str, Any]) -> bool:
    """
    Analysis request validálás - koordináta kulcsok kompatibilitással.

    Args:
        self: AnalysisHandler instance
        request_data: Kérés adatok

    Returns:
        bool: Valid-e a kérés
    """
    try:
        # Kötelező mezők ellenőrzése
        required_fields = ["analysis_type", "date_range"]
        for field in required_fields:
            if field not in request_data:
                self.analysis_failed.emit(f"Hiányzó kötelező mező: {field}")
                return False

        analysis_type = request_data.get("analysis_type")
        valid_types = ["single_location", "multi_city", "county_analysis"]

        if analysis_type not in valid_types:
            self.analysis_failed.emit(f"Érvénytelen elemzés típus: {analysis_type}")
            return False

        # Dátum range validálás
        date_range = request_data.get("date_range", {})
        if not date_range.get("start_date") or not date_range.get("end_date"):
            self.analysis_failed.emit("Hiányzó dátum tartomány")
            return False

        try:
            start_date_value = datetime.strptime(
                date_range.get("start_date", ""), "%Y-%m-%d"
            )
            end_date_value = datetime.strptime(
                date_range.get("end_date", ""), "%Y-%m-%d"
            )
        except ValueError as exc:
            self.analysis_failed.emit(f"Érvénytelen dátum formátum: {exc}")
            return False

        if (end_date_value - start_date_value).days > 60 * 365:
            error_message = "Maximum 60 éves időszak kérdezhető le"
            self.status_updated.emit(error_message)
            self.analysis_failed.emit(error_message)
            return False

        # Lokáció validálás koordináta kulcsok kompatibilitással
        if analysis_type == "single_location":
            if not _validate_single_location_coords(self, request_data):
                return False

        elif analysis_type in ["multi_city", "county_analysis"]:
            if not request_data.get("region_name") and not request_data.get(
                "county_name"
            ):
                self.analysis_failed.emit("Hiányzó régió vagy megye név")
                return False

        logger.info(f"✅ Analysis request validation OK: {analysis_type}")
        return True

    except Exception as e:
        logger.error(f"Request validation hiba: {e}")
        self.analysis_failed.emit(f"Kérés validálási hiba: {e}")
        return False


def _validate_single_location_coords(self, request_data: Dict[str, Any]) -> bool:
    """
    Single location koordináták validálása (koordináta kulcsok kompatibilitással).

    Args:
        self: AnalysisHandler instance
        request_data: Kérés adatok

    Returns:
        bool: Validak-e a koordináták
    """
    has_direct_coords = False
    has_location_data_coords = False

    # 1. Direkt koordináták ellenőrzése
    if "latitude" in request_data and "longitude" in request_data:
        has_direct_coords = True
        logger.info("🔧 Found direct coordinates: latitude/longitude")
    elif "lat" in request_data and "lon" in request_data:
        has_direct_coords = True
        logger.info("🔧 Found direct coordinates: lat/lon")

    # 2. location_data objektum ellenőrzése
    location_data = request_data.get("location_data", {})
    if location_data:
        lat_keys = ["lat", "latitude"]
        lon_keys = ["lon", "longitude"]

        has_lat = any(key in location_data for key in lat_keys)
        has_lon = any(key in location_data for key in lon_keys)

        if has_lat and has_lon:
            has_location_data_coords = True
            logger.info("🔧 Found location_data coordinates")

    # Koordináták validálása
    if not (has_direct_coords or has_location_data_coords):
        error_msg = "Hiányzó lokáció koordináták"
        logger.error(f"🔧 COORDINATE VALIDATION FAILED: {error_msg}")
        logger.error(f"🔧 Request keys: {list(request_data.keys())}")
        if location_data:
            logger.error(f"🔧 location_data keys: {list(location_data.keys())}")

        self.analysis_failed.emit(error_msg)
        return False

    logger.info("✅ Single location coordinates validation passed")
    return True
