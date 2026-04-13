"""Tests split from test_city_manager_db_new.py."""

from __future__ import annotations

from src.data.city_manager_db import CityDatabaseError, CityManagerDB

# ruff: noqa: F403, F405
from tests.data.test_city_manager_db_new_support import *


class TestValidateHungarianDatabaseStructure:
    """Test _validate_hungarian_database_structure method."""

    def test_validate_hungarian_passes_with_correct_structure(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_validate_hungarian_database_structure passes when all required columns exist."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Should not raise
        manager._validate_hungarian_database_structure()

    def test_validate_hungarian_raises_with_missing_columns(
        self, cities_db: Path, incomplete_hungarian_db: Path
    ) -> None:
        """_validate_hungarian_database_structure raises when required columns are missing."""
        # The validation happens during __init__
        with pytest.raises(CityDatabaseError, match="Missing columns"):
            CityManagerDB(db_path=cities_db, hungarian_db_path=incomplete_hungarian_db)

    def test_validate_hungarian_returns_early_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """_validate_hungarian_database_structure returns early when connection is None."""
        # Create a minimal Hungarian DB to allow initialization
        hungarian_db = mock_data_dir / "hungarian_settlements.db"
        conn = sqlite3.connect(hungarian_db)
        conn.execute("""
            CREATE TABLE hungarian_settlements (
                id INTEGER,
                name TEXT,
                latitude REAL,
                longitude REAL,
                megye TEXT,
                settlement_type TEXT,
                population INTEGER,
                climate_zone TEXT,
                region_priority REAL
            )
        """)
        conn.commit()
        conn.close()

        manager = CityManagerDB(hungarian_db_path=hungarian_db)
        # Force hungarian_connection to None
        original_conn = manager.hungarian_connection
        manager.hungarian_connection = None

        # Should not raise
        manager._validate_hungarian_database_structure()

        # Restore for cleanup
        manager.hungarian_connection = original_conn


class TestGetTotalCityCount:
    """Test _get_total_city_count method."""

    def test_get_total_city_count_returns_correct_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_total_city_count returns actual city count from database."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        count = manager._get_total_city_count()

        assert count == 1  # We inserted 1 city

    def test_get_total_city_count_returns_zero_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """_get_total_city_count returns 0 when connection is None."""
        manager = CityManagerDB(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )
        manager.connection = None

        count = manager._get_total_city_count()

        assert count == 0


class TestGetTotalHungarianSettlementsCount:
    """Test _get_total_hungarian_settlements_count method."""

    def test_get_total_hungarian_count_returns_correct_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_total_hungarian_settlements_count returns actual settlement count."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        count = manager._get_total_hungarian_settlements_count()

        assert count == 1  # We inserted 1 settlement

    def test_get_total_hungarian_count_returns_zero_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """_get_total_hungarian_settlements_count returns 0 when connection is None."""
        manager = CityManagerDB(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )
        manager.hungarian_connection = None

        count = manager._get_total_hungarian_settlements_count()

        assert count == 0
