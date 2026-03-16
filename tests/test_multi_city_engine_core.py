"""MultiCityEngine helper és régió mapping tesztek."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from src.analytics.multi_city_engine import (
    MultiCityEngine,
    safe_min_max,
    safe_statistics_mean,
    safe_statistics_stdev,
)


@pytest.fixture(name="engine")
def fixture_engine(tmp_path: Path) -> MultiCityEngine:
    """Ideiglenes adatbázis fájlokat használó engine példány."""
    db_file = tmp_path / "cities.db"
    hu_file = tmp_path / "hungarian_settlements.db"
    db_file.write_bytes(b"")
    hu_file.write_bytes(b"")
    return MultiCityEngine(db_path=str(db_file), hungarian_db_path=str(hu_file))


def test_safe_statistics_helpers_ignore_invalid_entries() -> None:
    """None és hibás elemek kihagyásával számoljon értelmes statisztikát."""
    values: List[float | None | object] = [10.0, None, 20.0, object()]
    assert safe_statistics_mean(values) == pytest.approx(15.0)
    assert safe_statistics_stdev([10.0, 20.0]) == pytest.approx(7.0710678118654755)
    assert safe_min_max(values) == (10.0, 20.0)


def test_safe_statistics_helpers_handle_edge_cases() -> None:
    """Üres vagy egyelemű listákra sem dobjon hibát a számítás."""
    assert safe_statistics_mean([]) is None
    assert safe_statistics_mean([None, None]) is None
    assert safe_statistics_stdev([5.0]) == 0.0
    assert safe_min_max([None]) == (None, None)


def test_resolve_region_name_accepts_various_synonyms(engine: MultiCityEngine) -> None:
    """A régió feloldás kezelje a kódokat, kisbetűs formákat és megyéket is."""
    assert engine.resolve_region_name("HU") == "Hungary"
    assert engine.resolve_region_name("global") == "Global"
    assert engine.resolve_region_name("Pest megye") == "Hungary"
    assert engine.resolve_region_name("Észak-magyarországi térség") == "Hungary"


def test_resolve_region_name_invalid_input(engine: MultiCityEngine) -> None:
    """Ismeretlen régió esetén egyértelmű hibát emeljen."""
    with pytest.raises(ValueError) as exc:
        engine.resolve_region_name("Atlantis")
    assert "Ismeretlen régió" in str(exc.value)
