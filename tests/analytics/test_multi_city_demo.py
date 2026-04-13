#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_demo.py
Demo and test code for multi-city analytics
"""

import io
import sys
from unittest.mock import MagicMock, patch

from src.analytics.multi_city_demo import demo_multi_city_engine


class TestDemoMultiCityEngine:
    """Test demo_multi_city_engine function."""

    def test_demo_runs_successfully(self) -> None:
        """Demo should run without crashing."""
        mock_engine = MagicMock()
        mock_engine.db_path = MagicMock()
        mock_engine.db_path.absolute.return_value = "/path/to/cities.db"
        mock_engine.db_path.exists.return_value = True
        mock_engine.hungarian_db_path = MagicMock()
        mock_engine.hungarian_db_path.absolute.return_value = "/path/to/hungarian.db"
        mock_engine.hungarian_db_path.exists.return_value = True
        mock_engine.resolve_region_name.return_value = "Hungary"

        mock_result = MagicMock()
        mock_result.city_results = [
            MagicMock(city_name="Miskolc", value=50.0),
            MagicMock(city_name="Eger", value=40.0),
            MagicMock(city_name="Salgótarján", value=30.0),
        ]
        mock_result.statistics = {"max": 50.0}
        mock_engine.analyze_multi_city.return_value = mock_result

        with patch("src.analytics.multi_city_demo.MultiCityEngine", return_value=mock_engine):
            # Capture output
            captured_output = io.StringIO()
            sys.stdout = captured_output

            try:
                demo_multi_city_engine()
            finally:
                sys.stdout = sys.__stdout__

            output = captured_output.getvalue()
            assert "MULTI-CITY ENGINE DEMO" in output

    def test_demo_handles_engine_initialization_error(self) -> None:
        """Demo should handle engine initialization errors gracefully."""
        with patch(
            "src.analytics.multi_city_demo.MultiCityEngine",
            side_effect=Exception("Init error"),
        ):
            captured_output = io.StringIO()
            sys.stdout = captured_output

            try:
                demo_multi_city_engine()
            finally:
                sys.stdout = sys.__stdout__

            output = captured_output.getvalue()
            assert "CRITICAL ERROR" in output

    def test_demo_handles_region_mapping_errors(self) -> None:
        """Demo should handle region mapping errors gracefully."""
        mock_engine = MagicMock()
        mock_engine.db_path = MagicMock()
        mock_engine.db_path.absolute.return_value = "/path/to/cities.db"
        mock_engine.db_path.exists.return_value = True
        mock_engine.hungarian_db_path = MagicMock()
        mock_engine.hungarian_db_path.absolute.return_value = "/path/to/hungarian.db"
        mock_engine.hungarian_db_path.exists.return_value = True

        # Some regions resolve, some fail
        def resolve_side_effect(region: str) -> str:
            if region in ["HU", "Budapest"]:
                return "Hungary"
            raise ValueError(f"Unknown region: {region}")

        mock_engine.resolve_region_name.side_effect = resolve_side_effect

        mock_result = MagicMock()
        mock_result.city_results = []
        mock_result.statistics = {}
        mock_engine.analyze_multi_city.return_value = mock_result

        with patch("src.analytics.multi_city_demo.MultiCityEngine", return_value=mock_engine):
            captured_output = io.StringIO()
            sys.stdout = captured_output

            try:
                demo_multi_city_engine()
            finally:
                sys.stdout = sys.__stdout__

            output = captured_output.getvalue()
            assert "ERROR" in output

    def test_demo_handles_analytics_error(self) -> None:
        """Demo should handle analytics errors gracefully."""
        mock_engine = MagicMock()
        mock_engine.db_path = MagicMock()
        mock_engine.db_path.absolute.return_value = "/path/to/cities.db"
        mock_engine.db_path.exists.return_value = True
        mock_engine.hungarian_db_path = MagicMock()
        mock_engine.hungarian_db_path.absolute.return_value = "/path/to/hungarian.db"
        mock_engine.hungarian_db_path.exists.return_value = True
        mock_engine.resolve_region_name.return_value = "Hungary"
        mock_engine.analyze_multi_city.side_effect = Exception("Analytics error")

        with patch("src.analytics.multi_city_demo.MultiCityEngine", return_value=mock_engine):
            captured_output = io.StringIO()
            sys.stdout = captured_output

            try:
                demo_multi_city_engine()
            finally:
                sys.stdout = sys.__stdout__

            output = captured_output.getvalue()
            assert "Test error" in output

    def test_demo_prints_path_info(self) -> None:
        """Demo should print path information."""
        mock_engine = MagicMock()
        mock_engine.db_path = MagicMock()
        mock_engine.db_path.absolute.return_value = "/path/to/cities.db"
        mock_engine.db_path.exists.return_value = True
        mock_engine.hungarian_db_path = MagicMock()
        mock_engine.hungarian_db_path.absolute.return_value = "/path/to/hungarian.db"
        mock_engine.hungarian_db_path.exists.return_value = False
        mock_engine.resolve_region_name.return_value = "Hungary"

        mock_result = MagicMock()
        mock_result.city_results = []
        mock_result.statistics = {}
        mock_engine.analyze_multi_city.return_value = mock_result

        with patch("src.analytics.multi_city_demo.MultiCityEngine", return_value=mock_engine):
            captured_output = io.StringIO()
            sys.stdout = captured_output

            try:
                demo_multi_city_engine()
            finally:
                sys.stdout = sys.__stdout__

            output = captured_output.getvalue()
            assert "Script location" in output
            assert "Working directory" in output
            assert "cities.db" in output

    def test_demo_shows_windspeed_check(self) -> None:
        """Demo should show windspeed check results."""
        mock_engine = MagicMock()
        mock_engine.db_path = MagicMock()
        mock_engine.db_path.absolute.return_value = "/path/to/cities.db"
        mock_engine.db_path.exists.return_value = True
        mock_engine.hungarian_db_path = MagicMock()
        mock_engine.hungarian_db_path.absolute.return_value = "/path/to/hungarian.db"
        mock_engine.hungarian_db_path.exists.return_value = True
        mock_engine.resolve_region_name.return_value = "Hungary"

        # Results with non-zero wind speeds
        mock_result = MagicMock()
        mock_result.city_results = [
            MagicMock(city_name="Miskolc", value=50.0),
            MagicMock(city_name="Eger", value=30.0),
        ]
        mock_result.statistics = {"max": 50.0}
        mock_engine.analyze_multi_city.return_value = mock_result

        with patch("src.analytics.multi_city_demo.MultiCityEngine", return_value=mock_engine):
            captured_output = io.StringIO()
            sys.stdout = captured_output

            try:
                demo_multi_city_engine()
            finally:
                sys.stdout = sys.__stdout__

            output = captured_output.getvalue()
            assert "WINDSPEED CHECK" in output
            assert "WINDSPEED METRIC SUCCESS" in output

    def test_demo_shows_zero_windspeed_warning(self) -> None:
        """Demo should show warning when all wind speeds are zero."""
        mock_engine = MagicMock()
        mock_engine.db_path = MagicMock()
        mock_engine.db_path.absolute.return_value = "/path/to/cities.db"
        mock_engine.db_path.exists.return_value = True
        mock_engine.hungarian_db_path = MagicMock()
        mock_engine.hungarian_db_path.absolute.return_value = "/path/to/hungarian.db"
        mock_engine.hungarian_db_path.exists.return_value = True
        mock_engine.resolve_region_name.return_value = "Hungary"

        # Results with all zero wind speeds
        mock_result = MagicMock()
        mock_result.city_results = [
            MagicMock(city_name="Miskolc", value=0.0),
            MagicMock(city_name="Eger", value=0.0),
        ]
        mock_result.statistics = {"max": 0.0}
        mock_engine.analyze_multi_city.return_value = mock_result

        with patch("src.analytics.multi_city_demo.MultiCityEngine", return_value=mock_engine):
            captured_output = io.StringIO()
            sys.stdout = captured_output

            try:
                demo_multi_city_engine()
            finally:
                sys.stdout = sys.__stdout__

            output = captured_output.getvalue()
            assert "WINDSPEED METRIC FAILED" in output


class TestDemoExports:
    """Test module exports."""

    def test_all_exports_exist(self) -> None:
        """All items in __all__ should be accessible."""
        from src.analytics import multi_city_demo

        assert hasattr(multi_city_demo, "demo_multi_city_engine")
        assert "demo_multi_city_engine" in multi_city_demo.__all__
