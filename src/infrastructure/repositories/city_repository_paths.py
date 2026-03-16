"""City repository path handling and validation."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CityRepositoryPaths:
    """Handles database path resolution and fallbacks."""

    @staticmethod
    def _resolve_fallback_path(filename: str) -> Optional[Path]:
        """Return the first existing fallback path for the given database file."""
        fallback_path = Path.cwd() / "data" / filename
        if fallback_path.exists():
            return fallback_path

        env_dir = os.environ.get("WEATHER_ANALYZER_DATA_DIR")
        if not env_dir:
            return None

        env_path = Path(env_dir) / filename
        if env_path.exists():
            return env_path
        return None

    def __init__(
        self,
        db_path: Optional[Path] = None,
        hungarian_db_path: Optional[Path] = None,
    ):
        """Initialize with optional custom paths."""
        project_root = Path(__file__).parent.parent.parent.parent
        self.db_path = db_path or project_root / "data" / "cities.db"
        self.hungarian_db_path = (
            hungarian_db_path or project_root / "data" / "hungarian_settlements.db"
        )
        self._apply_fallbacks()

    def _apply_fallbacks(self) -> None:
        """Apply working-directory/env fallbacks for database paths."""
        if not self.db_path.exists():
            fallback = self._resolve_fallback_path("cities.db")
            if fallback is not None:
                self.db_path = fallback

        if not self.hungarian_db_path.exists():
            fallback = self._resolve_fallback_path("hungarian_settlements.db")
            if fallback is not None:
                self.hungarian_db_path = fallback

    def _collect_missing_database_issues(self) -> list[str]:
        """Collect missing-database validation issues."""
        issues: list[str] = []
        if not self.db_path.exists():
            issues.append(f"Global cities database missing: {self.db_path}")
        if not self.hungarian_db_path.exists():
            issues.append(
                f"Hungarian settlements database missing: {self.hungarian_db_path}"
            )
        return issues

    def _has_any_database(self) -> bool:
        """Return whether at least one database exists."""
        return self.db_path.exists() or self.hungarian_db_path.exists()

    def validate_paths(self) -> None:
        """Validate that at least one database is available."""
        issues = self._collect_missing_database_issues()
        if issues and not self._has_any_database():
            detail = "\n".join(issues)
            raise RuntimeError(f"No databases available:\n{detail}")
        if issues:
            for issue in issues:
                logger.warning(issue)
        else:
            logger.info("CityRepository database paths validated.")


__all__ = ["CityRepositoryPaths"]
