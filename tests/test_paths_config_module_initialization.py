"""Comprehensive tests for src/config/paths_config.py."""

from __future__ import annotations


class TestModuleInitialization:
    """Test cases for module initialization behavior."""

    def test_ensure_directories_called_on_import(self) -> None:
        """ensure_directories should be called when module is imported."""
        from src.config.paths_config import DATA_DIR

        assert DATA_DIR.exists()
