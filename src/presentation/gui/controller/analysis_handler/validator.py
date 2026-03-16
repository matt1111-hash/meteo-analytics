#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

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


def _emit_analysis_error(self, message: str) -> bool:
    """Emit a validation error and return False for early exits."""
    self.analysis_failed.emit(message)
    return False


def _parse_date_range(
    self, date_range: Dict[str, Any]
) -> tuple[datetime, datetime] | None:
    """Parse and validate analysis date range."""
    if not date_range.get("start_date") or not date_range.get("end_date"):
        _emit_analysis_error(self, "Hiányzó dátum tartomány")
        return None

    try:
        return (
            datetime.strptime(date_range.get("start_date", ""), "%Y-%m-%d"),
            datetime.strptime(date_range.get("end_date", ""), "%Y-%m-%d"),
        )
    except ValueError as exc:
        _emit_analysis_error(self, f"Érvénytelen dátum formátum: {exc}")
        return None


def _validate_analysis_type(self, analysis_type: Any) -> bool:
    """Validate requested analysis type."""
    valid_types = {"single_location", "multi_city", "county_analysis"}
    if analysis_type in valid_types:
        return True
    return _emit_analysis_error(self, f"Érvénytelen elemzés típus: {analysis_type}")


def _validate_required_fields(self, request_data: Dict[str, Any]) -> bool:
    """Validate required request keys."""
    for field in ("analysis_type", "date_range"):
        if field not in request_data:
            return _emit_analysis_error(self, f"Hiányzó kötelező mező: {field}")
    return True


def _validate_region_inputs(self, request_data: Dict[str, Any]) -> bool:
    """Validate region-based analysis request fields."""
    has_region = request_data.get("region_name") or request_data.get("county_name")
    if has_region:
        return True
    return _emit_analysis_error(self, "Hiányzó régió vagy megye név")


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
        if not _validate_required_fields(self, request_data):
            return False

        analysis_type = request_data.get("analysis_type")
        if not _validate_analysis_type(self, analysis_type):
            return False

        parsed_dates = _parse_date_range(self, request_data.get("date_range", {}))
        if parsed_dates is None:
            return False
        start_date_value, end_date_value = parsed_dates

        if (end_date_value - start_date_value).days > 60 * 365:
            error_message = "Maximum 60 éves időszak kérdezhető le"
            self.status_updated.emit(error_message)
            return _emit_analysis_error(self, error_message)

        if analysis_type == "single_location":
            return _validate_single_location_coords(self, request_data)
        if analysis_type in {"multi_city", "county_analysis"}:
            return _validate_region_inputs(self, request_data)

        logger.info(f"✅ Analysis request validation OK: {analysis_type}")
        return True

    except Exception as e:
        logger.error(f"Request validation hiba: {e}")
        return _emit_analysis_error(self, f"Kérés validálási hiba: {e}")


def _has_direct_coords(request_data: Dict[str, Any]) -> bool:
    """Check whether request provides direct coordinates."""
    direct_pairs = (("latitude", "longitude"), ("lat", "lon"))
    return any(
        lat_key in request_data and lon_key in request_data
        for lat_key, lon_key in direct_pairs
    )


def _has_location_data_coords(location_data: Dict[str, Any]) -> bool:
    """Check whether location_data provides coordinates."""
    lat_keys = {"lat", "latitude"}
    lon_keys = {"lon", "longitude"}
    return any(key in location_data for key in lat_keys) and any(
        key in location_data for key in lon_keys
    )


def _validate_single_location_coords(self, request_data: Dict[str, Any]) -> bool:
    """
    Single location koordináták validálása (koordináta kulcsok kompatibilitással).

    Args:
        self: AnalysisHandler instance
        request_data: Kérés adatok

    Returns:
        bool: Validak-e a koordináták
    """
    location_data = request_data.get("location_data", {})
    has_direct_coords = _has_direct_coords(request_data)
    has_location_coords = bool(location_data) and _has_location_data_coords(
        location_data
    )

    if has_direct_coords:
        logger.info("🔧 Found direct coordinates in request")
    if has_location_coords:
        logger.info("🔧 Found location_data coordinates")

    if not (has_direct_coords or has_location_coords):
        error_msg = "Hiányzó lokáció koordináták"
        logger.error(f"🔧 COORDINATE VALIDATION FAILED: {error_msg}")
        logger.error(f"🔧 Request keys: {list(request_data.keys())}")
        if location_data:
            logger.error(f"🔧 location_data keys: {list(location_data.keys())}")
        return _emit_analysis_error(self, error_msg)

    logger.info("✅ Single location coordinates validation passed")
    return True
