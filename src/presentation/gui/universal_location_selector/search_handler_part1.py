# ruff: noqa: F403, F405, I001
# mypy: ignore-errors
"""Mixin part 1 for SearchHandler."""

from __future__ import annotations

from .search_handler_support import *


CITY_NORMALIZATION_FIELDS = [
    "city",
    "name",
    "lat",
    "lon",
    "country",
    "country_code",
    "population",
    "continent",
    "admin_name",
    "capital",
    "timezone",
    "settlement_type",
    "megye",
    "jaras",
    "climate_zone",
    "region_priority",
    "is_hungarian",
    "terulet_hektar",
    "lakasok_szama",
    "display_name",
]


def _build_status_message(results: List[Dict[str, Any]]) -> str:
    """Build status label message for normalized results."""
    if not results:
        return ""
    hungarian_count = sum(1 for city in results if city.get("is_hungarian"))
    return _build_count_message(hungarian_count, len(results))


def _build_count_message(hungarian_count: int, total_results: int) -> str:
    """Build count-based search result status message."""
    global_count = total_results - hungarian_count
    if hungarian_count > 0 and global_count > 0:
        return (
            f"✅ {hungarian_count} magyar + {global_count} globális = " f"{total_results} találat"
        )
    if hungarian_count > 0:
        return f"✅ {hungarian_count} magyar találat"
    return f"✅ {global_count} globális találat"


def _extract_city_attributes(city: Any) -> Dict[str, Any]:
    """Extract supported fields from a city-like object."""
    city_dict: Dict[str, Any] = {}
    for field in CITY_NORMALIZATION_FIELDS:
        if hasattr(city, field):
            city_dict[field] = getattr(city, field)
    return city_dict


def _normalize_city_name_fields(city_dict: Dict[str, Any]) -> bool:
    """Normalize city/name aliases and report whether a city name exists."""
    if "city" not in city_dict and "name" in city_dict:
        city_dict["city"] = city_dict["name"]
    return "city" in city_dict


def _apply_city_defaults(city_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default coordinates and flags to city payload."""
    city_dict.setdefault("lat", 0.0)
    city_dict.setdefault("lon", 0.0)
    city_dict.setdefault("is_hungarian", False)
    return city_dict


def _normalize_city_via_to_dict(city: Any) -> Optional[Dict[str, Any]]:
    """Try normalizing a city object using its to_dict method."""
    if not (hasattr(city, "to_dict") and callable(city.to_dict)):
        return None
    try:
        return city.to_dict()
    except Exception as error:
        logger.warning("to_dict hiba: %s", error)
        return None


def _normalize_city_object(city: Any) -> Optional[Dict[str, Any]]:
    """Normalize generic city-like object to dict payload."""
    city_dict = _extract_city_attributes(city)
    if not _normalize_city_name_fields(city_dict):
        return None
    return _apply_city_defaults(city_dict)


class SearchHandlerPart1Mixin:  # noqa: D101
    def __init__(
        self,
        city_manager: CityManagerPort,
        search_input: QLineEdit,
        status_label: QLabel,
        results_list: QListWidget,
        search_requested_callback: Callable[[str], None],
    ):
        """
        SearchHandler inicializálása.

        Args:
            city_manager: CityManager instance
            search_input: Search input widget
            status_label: Status label widget
            results_list: Results list widget
            search_requested_callback: Callback when search is requested
        """
        self.city_manager = city_manager
        self.search_input = search_input
        self.status_label = status_label
        self.results_list = results_list
        self.search_requested_callback = search_requested_callback

        # Search timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)

    def on_search_text_changed(self, text: str) -> None:
        """
        Keresés szöveg változáskor.

        Args:
            text: Új kereső szöveg
        """
        if len(text) < 2:  # noqa: PLR2004
            self.results_list.clear()
            self.status_label.setText("💡 Legalább 2 karakter szükséges...")
            return

        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms késleltetés
        self.status_label.setText("🔍 Keresés...")

    def _perform_search(self) -> None:
        """KOMBINÁLT KERESÉS - Magyar + Globális"""
        query = self.search_input.text().strip()
        if len(query) < 2:  # noqa: PLR2004
            return

        try:
            self.search_requested_callback(query)
            raw_results = self.city_manager.search_unified(query, limit=20, hungarian_priority=True)
            results = self._normalize_results(raw_results)

            self._display_results(results)

            if not results:
                self.status_label.setText(f"❌ Nincs találat a '{query}' keresésre")
            else:
                self.status_label.setText(_build_status_message(results))

        except Exception as e:
            logger.error(f"Keresési hiba: {e}")
            self.status_label.setText("❌ Keresési hiba történt")

    def _normalize_results(self, results: Iterable[Any]) -> List[Dict[str, Any]]:
        """
        Eredmények normalizálása dict formátumra.

        Args:
            results: Vegyes típusú eredmények (dict vagy objektum)

        Returns:
            List[Dict[str, Any]]: Normalizált eredmények
        """
        normalized: List[Dict[str, Any]] = []
        for result in results:
            city_dict = self._normalize_city(result)
            if city_dict is not None:
                normalized.append(city_dict)
            else:
                logger.warning("Eredmény normalizálása sikertelen: %s", result)
        return normalized

    def _normalize_city(self, city: Any) -> Optional[Dict[str, Any]]:
        """
        Egyetlen város objektum normalizálása dict formátumra.

        Args:
            city: City objektum vagy dict

        Returns:
            Normalizált dict vagy None
        """
        if isinstance(city, dict):
            return city
        normalized = _normalize_city_via_to_dict(city)
        if normalized is not None:
            return normalized
        return _normalize_city_object(city)
