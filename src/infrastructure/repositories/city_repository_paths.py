"""City repository path handling and validation."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CityRepositoryPaths:
    """Handles database path resolution and fallbacks."""

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
            fallback = Path.cwd() / "data" / "cities.db"
            env_dir = os.environ.get("WEATHER_ANALYZER_DATA_DIR")
            env_path = Path(env_dir) / "cities.db" if env_dir else None
            if fallback.exists():
                self.db_path = fallback
            elif env_path and env_path.exists():
                self.db_path = env_path

        if not self.hungarian_db_path.exists():
            fallback = Path.cwd() / "data" / "hungarian_settlements.db"
            env_dir = os.environ.get("WEATHER_ANALYZER_DATA_DIR")
            env_path = Path(env_dir) / "hungarian_settlements.db" if env_dir else None
            if fallback.exists():
                self.hungarian_db_path = fallback
            elif env_path and env_path.exists():
                self.hungarian_db_path = env_path

    def validate_paths(self) -> None:
        """Validate that at least one database is available."""
        issues: list[str] = []
        if not self.db_path.exists():
            issues.append(f"Global cities database missing: {self.db_path}")
        if not self.hungarian_db_path.exists():
            issues.append(
                f"Hungarian settlements database missing: {self.hungarian_db_path}"
            )
        if issues and not (self.db_path.exists() or self.hungarian_db_path.exists()):
            detail = "\n".join(issues)
            raise RuntimeError(f"No databases available:\n{detail}")
        if issues:
            for issue in issues:
                logger.warning(issue)
        else:
            logger.info("CityRepository database paths validated.")


__all__ = ["CityRepositoryPaths"]
