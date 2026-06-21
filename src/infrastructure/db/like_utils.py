"""SQL LIKE metacharacter escaping helpers.

LIKE patterns treat ``%`` (any sequence) and ``_`` (single char) as wildcards,
and ``\\`` as the escape character. When user input is interpolated into a LIKE
pattern, those characters must be escaped so they match literally and cannot
re-shape the pattern (a defensive measure complementing parameterized queries).

Usage::

    from src.infrastructure.db.like_utils import escape_like

    cursor.execute(
        "SELECT * FROM cities WHERE city LIKE ? ESCAPE '\\'", (f"%{escape_like(term)}%",)
    )
"""

from __future__ import annotations

__all__ = ["escape_like"]


def escape_like(value: str) -> str:
    """Escape SQL LIKE metacharacters so *value* matches literally.

    The backslash is escaped first so it cannot neutralize the ``%``/``_``
    escaping that follows. Pair the result with an ``ESCAPE '\\'`` clause.

    Args:
        value: Raw user input destined for a LIKE pattern.

    Returns:
        The input with ``\\``, ``%`` and ``_`` escaped via a backslash.
    """
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
