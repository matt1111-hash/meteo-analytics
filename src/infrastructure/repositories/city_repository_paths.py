"""City repository path handling and validation."""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Trusted base directories for database files.
_TRUSTED_BASES: list[Path] = [
    Path(__file__).parent.parent.parent.parent / "data",  # project_root/data
    Path.cwd() / "data",
]


class CityRepositoryPaths:
    """Handles database path resolution and fallbacks with path-traversal protection."""

    @staticmethod
    def _validate_path(path: Path) -> Path:
        """Canonicalize path and ensure it resides under a trusted base directory."""
        resolved = path.resolve(strict=False)
        for base in _TRUSTED_BASES:
            try:
                base_resolved = base.resolve(strict=False)
                resolved.relative_to(base_resolved)
                return resolved
            except ValueError:
                continue
        raise ValueError(
            f"Database path '{path}' resolves outside trusted directories: "
            f"{[str(b) for b in _TRUSTED_BASES]}"
        )

    @staticmethod
    def _resolve_fallback_path(filename: str) -> Path | None:
        """Return the first existing fallback path for the given database file."""
        fallback_path = Path.cwd() / "data" / filename
        if fallback_path.exists():
            return CityRepositoryPaths._validate_path(fallback_path)

        env_dir = os.environ.get("WEATHER_ANALYZER_DATA_DIR")
        if not env_dir:
            return None

        env_path = Path(env_dir) / filename
        if env_path.exists():
            # Add env_dir to trusted bases dynamically
            resolved_env = Path(env_dir).resolve(strict=False)
            if resolved_env not in [b.resolve(strict=False) for b in _TRUSTED_BASES]:
                _TRUSTED_BASES.append(resolved_env)
            return CityRepositoryPaths._validate_path(env_path)
        return None

    def __init__(
        self,
        db_path: Path | None = None,
        hungarian_db_path: Path | None = None,
    ):
        """Initialize with optional custom paths."""
        project_root = Path(__file__).parent.parent.parent.parent
        raw_db = db_path or project_root / "data" / "cities.db"
        raw_hungarian = hungarian_db_path or project_root / "data" / "hungarian_settlements.db"
        # Explicit custom paths (e.g. test fixtures) are trusted as-is;
        # only default/env-resolved paths go through traversal validation.
        if db_path is not None:
            self.db_path = raw_db.resolve(strict=False)
        else:
            self.db_path = self._validate_path(raw_db)
        if hungarian_db_path is not None:
            self.hungarian_db_path = raw_hungarian.resolve(strict=False)
        else:
            self.hungarian_db_path = self._validate_path(raw_hungarian)
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
            issues.append(f"Hungarian settlements database missing: {self.hungarian_db_path}")
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
