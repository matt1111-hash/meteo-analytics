"""Domain-level validation error — prevents internal detail leakage."""

from __future__ import annotations


class ValidationError(ValueError):
    """Raised when domain input validation fails.

    Designed to be safe for API responses — the message contains only
    user-facing context, never internal implementation details.
    """
