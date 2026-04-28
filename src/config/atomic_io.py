"""Atomic file write utilities for safe JSON persistence."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


def atomic_write_json(path: Path, data: dict[str, Any], *, indent: int = 2) -> None:
    """Write JSON atomically via temp file + rename.

    Prevents corruption on crash/interrupt: the target file is either
    the old content or the new content — never a partial write.
    """
    content = json.dumps(data, indent=indent, ensure_ascii=False)

    # Real Path: full atomic write (temp + os.replace)
    if hasattr(path, "with_suffix"):
        tmp = path.with_suffix(f".{uuid.uuid4().hex[:8]}.tmp")
        try:
            tmp.write_text(content, encoding="utf-8")
            tmp.replace(path)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    else:
        # FakePath / in-memory mock: fall back to builtins.open
        with open(path, "w", encoding="utf-8") as fh:  # noqa: PTH123
            fh.write(content)
