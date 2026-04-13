"""Comprehensive tests for src/config/paths_config.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


class TestEnsureDirectories:
    """Test cases for ensure_directories() function."""

    def test_ensure_directories_creates_all_directories(self, tmp_path: Path) -> None:
        """ensure_directories should create all necessary directories."""
        from src.config.paths_config import ensure_directories  # noqa: PLC0415

        with (
            patch("src.config.paths_config.DATA_DIR", tmp_path / "data"),
            patch("src.config.paths_config.CACHE_DIR", tmp_path / "data" / "cache"),
            patch(
                "src.config.paths_config.CLIMATE_CACHE_DIR",
                tmp_path / "data" / "climate_cache",
            ),
            patch("src.config.paths_config.EXPORTS_DIR", tmp_path / "exports"),
            patch("src.config.paths_config.LOGS_DIR", tmp_path / "logs"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                tmp_path / "data" / "user_preferences",
            ),
        ):
            import shutil  # noqa: PLC0415

            if tmp_path.exists():
                shutil.rmtree(tmp_path)

            ensure_directories()

            assert (tmp_path / "data").exists()
            assert (tmp_path / "data" / "cache").exists()
            assert (tmp_path / "data" / "climate_cache").exists()
            assert (tmp_path / "exports").exists()
            assert (tmp_path / "logs").exists()
            assert (tmp_path / "data" / "user_preferences").exists()

    def test_ensure_directories_idempotent(self, tmp_path: Path) -> None:
        """ensure_directories should be safe to call multiple times."""
        from src.config.paths_config import ensure_directories  # noqa: PLC0415

        with (
            patch("src.config.paths_config.DATA_DIR", tmp_path / "data"),
            patch("src.config.paths_config.CACHE_DIR", tmp_path / "data" / "cache"),
            patch(
                "src.config.paths_config.CLIMATE_CACHE_DIR",
                tmp_path / "data" / "climate_cache",
            ),
            patch("src.config.paths_config.EXPORTS_DIR", tmp_path / "exports"),
            patch("src.config.paths_config.LOGS_DIR", tmp_path / "logs"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                tmp_path / "data" / "user_preferences",
            ),
        ):
            ensure_directories()
            ensure_directories()

            assert (tmp_path / "data").exists()
            assert (tmp_path / "data" / "cache").exists()

    def test_ensure_directories_creates_nested_paths(self, tmp_path: Path) -> None:
        """ensure_directories should create parent directories when needed."""
        from src.config.paths_config import ensure_directories  # noqa: PLC0415

        nested_dir = tmp_path / "level1" / "level2" / "level3"

        with (
            patch("src.config.paths_config.DATA_DIR", nested_dir),
            patch("src.config.paths_config.CACHE_DIR", nested_dir / "cache"),
            patch(
                "src.config.paths_config.CLIMATE_CACHE_DIR",
                nested_dir / "climate_cache",
            ),
            patch("src.config.paths_config.EXPORTS_DIR", tmp_path / "exports"),
            patch("src.config.paths_config.LOGS_DIR", tmp_path / "logs"),
            patch(
                "src.config.paths_config.USER_PREFS_DIR",
                nested_dir / "user_preferences",
            ),
        ):
            ensure_directories()

            assert nested_dir.exists()
            assert nested_dir.is_dir()

    def test_ensure_directories_returns_none(self) -> None:
        """ensure_directories should not return anything."""
        from src.config.paths_config import ensure_directories  # noqa: PLC0415

        result = ensure_directories()
        assert result is None
