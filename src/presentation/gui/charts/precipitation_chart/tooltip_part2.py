# ruff: noqa: F403, F405, I001
# mypy: ignore-errors
"""Split definitions from tooltip.py."""

from __future__ import annotations

from .tooltip_support import *


PRECIPITATION_CATEGORIES = (
    (50, ("⛈️", "Viharos zápor", "Rendkívül erős")),
    (20, ("🌧️", "Erős esőzés", "Erős")),
    (10, ("🌦️", "Közepes esőzés", "Mérsékelt")),
    (5, ("🌤️", "Gyenge esőzés", "Gyenge")),
    (1, ("💧", "Szitálás", "Nagyon gyenge")),
    (0.1, ("💦", "Harmat/köd", "Minimális")),
)

METEOROLOGICAL_NOTES = (
    (25, "⚠️ Árvízveszély lehetséges"),
    (15, "🚗 Közlekedési nehézségek"),
    (10, "☂️ Esernyő szükséges"),
    (1, "🌱 Jó a növényeknek"),
)


def _format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
    """
    📝 PRECIPITATION CHART TOOLTIP FORMÁZÁS

    🌧️ PROFESSIONAL PRECIPITATION TOOLTIP:
    - Csapadék mennyiség és kategória
    - Meteorológiai jellemzők
    - Magyar weather ikonok
    - Intenzitás kategóriák

    Args:
        self: PrecipitationChart instance
        point_data: Point data dict

    Returns:
        Formatted tooltip text
    """
    date = point_data["date"]
    precipitation = point_data["precipitation"]

    date_str = date.strftime("%Y-%m-%d (%A)") if isinstance(date, datetime) else str(date)
    precip_icon, category, intensity = _categorize_precipitation(precipitation)
    meteorological_info = _build_meteorological_info(precipitation)
    contextual_info = _build_precipitation_context(self, precipitation)
    tooltip_lines = [
        f"📅 {date_str}",
        "",
        f"{precip_icon} Csapadék: {precipitation:.1f} mm",
        f"🏷️ {category}",
        f"📊 Intenzitás: {intensity}",
    ]

    # Meteorológiai információk hozzáadása
    if meteorological_info:
        tooltip_lines.append("")
        tooltip_lines.extend(meteorological_info)

    # Kontextuális információk hozzáadása
    if contextual_info:
        tooltip_lines.append("")
        tooltip_lines.extend(contextual_info)

    return "\n".join(tooltip_lines)


def _categorize_precipitation(precipitation: float) -> tuple[str, str, str]:
    """Categorize precipitation intensity and icon."""
    for threshold, category in PRECIPITATION_CATEGORIES:
        if precipitation > threshold:
            return category
    return "☀️", "Száraz nap", "Nincs csapadék"


def _build_meteorological_info(precipitation: float) -> list[str]:
    """Build meteorological notes for precipitation amount."""
    for threshold, note in METEOROLOGICAL_NOTES:
        if precipitation > threshold:
            return [note]
    return []


def _build_precipitation_context(self, precipitation: float) -> list[str]:
    """Build contextual comparison against mean precipitation."""
    if not hasattr(self, "current_data") or self.current_data.empty:
        return []
    avg_precip = self.current_data["precipitation"].mean()
    if precipitation > avg_precip * 2:
        return [f"📈 Átlag feletti ({avg_precip:.1f} mm)"]
    if precipitation < avg_precip * 0.5:
        return [f"📉 Átlag alatti ({avg_precip:.1f} mm)"]
    return [f"📊 Átlagos tartomány ({avg_precip:.1f} mm)"]
