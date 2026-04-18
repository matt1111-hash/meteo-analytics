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


@dataclass(frozen=True)
class UseCaseResult(Generic[T]):  # noqa: UP046
    """Wraps use case output with explicit success/error status.

    Prevents error conditions from being silently treated as successful results.
    """

    status: ResultStatus
    data: T | None = None
    error_message: str | None = None

    @property
    def is_success(self) -> bool:  # noqa: D102
        return self.status == ResultStatus.SUCCESS

    def unwrap(self) -> T:
        """Return data or raise RuntimeError if not successful."""
        if self.status != ResultStatus.SUCCESS or self.data is None:
            raise RuntimeError(f"UseCaseResult is not successful: {self.error_message}")
        return self.data
