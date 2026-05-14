"""Typed result wrapper for use case execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class ResultStatus(Enum):
    """Outcome of a use case execution."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"


class ErrorCategory(Enum):
    """Classification of use case errors for structured handling."""

    VALIDATION = "validation"
    PROVIDER = "provider"
    INTERNAL = "internal"


@dataclass(frozen=True)
class UseCaseResult(Generic[T]):  # noqa: UP046
    """Wraps use case output with explicit success/error status.

    Prevents error conditions from being silently treated as successful results.
    """

    status: ResultStatus
    data: T | None = None
    error_message: str | None = None
    error_category: ErrorCategory | None = None

    @property
    def is_success(self) -> bool:  # noqa: D102
        return self.status == ResultStatus.SUCCESS

    def unwrap(self) -> T:
        """Return data or raise RuntimeError if not successful."""
        if self.status != ResultStatus.SUCCESS or self.data is None:
            raise RuntimeError(f"UseCaseResult is not successful: {self.error_message}")
        return self.data

    @classmethod
    def validation_error(cls, message: str) -> UseCaseResult[T]:
        """Create a result for input validation failures."""
        return cls(
            status=ResultStatus.ERROR,
            error_message=message,
            error_category=ErrorCategory.VALIDATION,
        )

    @classmethod
    def provider_error(cls, message: str) -> UseCaseResult[T]:
        """Create a result for upstream provider failures."""
        return cls(
            status=ResultStatus.ERROR,
            error_message=message,
            error_category=ErrorCategory.PROVIDER,
        )

    @classmethod
    def internal_error(cls, message: str) -> UseCaseResult[T]:
        """Create a result for unexpected internal errors."""
        return cls(
            status=ResultStatus.ERROR,
            error_message=message,
            error_category=ErrorCategory.INTERNAL,
        )
