"""Standardized UseCaseResult → HTTP response conversion."""

from __future__ import annotations

from fastapi import HTTPException

from src.application.use_cases.use_case_result import ErrorCategory, UseCaseResult


def raise_for_use_case_result(result: UseCaseResult) -> None:
    """Raise HTTPException if *result* is not successful.

    Maps ErrorCategory to appropriate HTTP status codes:
    - VALIDATION → 400  (user-facing message)
    - PROVIDER   → 502  (user-facing message)
    - INTERNAL   → 500  (generic message, hides details)
    - None       → 502  (generic "Upstream error", hides details)
    """
    if result.is_success and result.data is not None:
        return

    category = result.error_category

    if category == ErrorCategory.VALIDATION:
        raise HTTPException(
            status_code=400,
            detail=result.error_message or "Validation error",
        )
    if category == ErrorCategory.PROVIDER:
        raise HTTPException(
            status_code=502,
            detail=result.error_message or "Upstream error",
        )
    if category == ErrorCategory.INTERNAL:
        raise HTTPException(status_code=500, detail="Internal server error")

    # Legacy: no category → hide details, return generic upstream error
    raise HTTPException(status_code=502, detail="Upstream error")
