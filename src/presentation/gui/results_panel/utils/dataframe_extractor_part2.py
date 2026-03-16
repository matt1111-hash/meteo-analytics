# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for DataFrameExtractor."""

from __future__ import annotations

from .dataframe_extractor_support import *


def _can_convert_string_to_float(value: str) -> bool:
    """Return whether string can be converted to float."""
    try:
        float(value)
    except (ValueError, TypeError):
        return False
    return True


def _collect_invalid_sample(
    invalid_samples: list[str], index: int, sample: str
) -> None:
    """Collect only the first debug invalid samples."""
    if index < 10:
        invalid_samples.append(sample)


def _build_dataframe_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Build baseline dataframe validation stats."""
    return {
        "valid": True,
        "rows": len(df),
        "columns": len(df.columns),
        "date_range": None,
        "missing_data": {},
        "wind_source": "unknown",
    }


def _is_valid_scalar_data(value: Any, invalid_samples: list[str], index: int) -> bool:
    """Return whether one value is acceptable scalar data."""
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        is_valid = _can_convert_string_to_float(value)
        if not is_valid:
            _collect_invalid_sample(
                invalid_samples, index, f"'{value}' (string, nem konvertálható)"
            )
        return is_valid
    _collect_invalid_sample(invalid_samples, index, f"{type(value).__name__}: {value}")
    return False


def _collect_missing_data_counts(df: pd.DataFrame) -> Dict[str, int]:
    """Collect missing-data counts by dataframe column."""
    missing_data: Dict[str, int] = {}
    for column_name in df.columns:
        missing_count = df[column_name].isna().sum()
        if missing_count > 0:
            missing_data[column_name] = missing_count
    return missing_data


def _resolve_date_range(df: pd.DataFrame) -> str | None:
    """Resolve dataframe date range string when available."""
    if "date" not in df.columns or df["date"].empty:
        return None
    return f"{df['date'].iloc[0]} - {df['date'].iloc[-1]}"


def _resolve_wind_source(df: pd.DataFrame) -> str:
    """Resolve dataframe wind source label."""
    if "wind_data_source" in df.columns and not df["wind_data_source"].empty:
        return df["wind_data_source"].iloc[0]
    return "unknown"


class DataFrameExtractorPart2Mixin:
    @staticmethod
    def _has_valid_data(data_list: list) -> bool:
        """
        Check if list contains valid numeric data (not just None values).

        🔥 KRITIKUS JAVÍTÁS: Bővített validáció, hogy kezelje a különböző adatformátumokat

        Args:
            data_list: List to check

        Returns:
            True if list contains valid numeric data
        """
        if not data_list:
            print("🔍 DEBUG: _has_valid_data - EMPTY list")
            return False

        # 🔥 KRITIKUS JAVÍTÁS: Bővített validáció, hogy kezelje a különböző számformátumokat
        valid_count = 0
        invalid_samples = []

        # 🔥 KRITIKUS JAVÍTÁS: Ellenőrizzük az összes elemet, ne csak az első 10-et
        # Ez megakadályozza, hogy az érvényes adatok elvesznek, ha csak a kezdeti elemek érvénytelenek
        for i, x in enumerate(data_list):
            if x is None:
                continue
            if _is_valid_scalar_data(x, invalid_samples, i):
                valid_count += 1

        # 🔥 KRITIKUS JAVÍTÁS: Ha van legalább 1 érvényes érték, akkor válaszunk True
        # Ez megakadályozza, hogy az összes adat elveszzen, ha csak néhány érték érvénytelen
        return valid_count > 0

    @staticmethod
    def _ensure_length(lst: List, target: int) -> List:
        """
        Lista hosszának biztosítása célérték szerint.

        Args:
            lst: Input lista
            target: Célhossz

        Returns:
            List: Megfelelő hosszúságú lista
        """
        if not lst:
            return [None] * target

        current_len = len(lst)

        if current_len == target:
            return lst
        elif current_len < target:
            # Kiegészítés None értékekkel
            return lst + [None] * (target - current_len)
        else:
            # Levágás célhosszra
            return lst[:target]

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        DataFrame validálása és minőség ellenőrzése.

        Args:
            df: Validálandó DataFrame

        Returns:
            Validációs eredmények dictionary
        """
        try:
            if df.empty:
                return {
                    "valid": False,
                    "error": "DataFrame üres",
                    "rows": 0,
                    "columns": 0,
                }

            stats = _build_dataframe_stats(df)

            stats["date_range"] = _resolve_date_range(df)
            stats["missing_data"] = _collect_missing_data_counts(df)
            stats["wind_source"] = _resolve_wind_source(df)

            logger.debug(f"DataFrame validation: {stats}")
            return stats

        except Exception as e:
            logger.error(f"DataFrame validation hiba: {e}")
            return {"valid": False, "error": str(e), "rows": 0, "columns": 0}
