"""Tests for UseCaseResult error categories and route error handling."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from src.api.error_handling import raise_for_use_case_result
from src.application.use_cases.use_case_result import (
    ErrorCategory,
    ResultStatus,
    UseCaseResult,
)
from src.domain.value_objects.validation_error import ValidationError


class TestRaiseForUseCaseResult:
    """Test raise_for_use_case_result HTTP mapping."""

    def test_success_does_not_raise(self) -> None:
        result = UseCaseResult(status=ResultStatus.SUCCESS, data={"ok": True})
        raise_for_use_case_result(result)  # should not raise

    def test_validation_error_returns_400(self) -> None:
        result = UseCaseResult.validation_error("Bad input")
        with pytest.raises(HTTPException) as exc_info:
            raise_for_use_case_result(result)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Bad input"

    def test_provider_error_returns_502(self) -> None:
        result = UseCaseResult.provider_error("Meteostat down")
        with pytest.raises(HTTPException) as exc_info:
            raise_for_use_case_result(result)
        assert exc_info.value.status_code == 502
        assert exc_info.value.detail == "Meteostat down"

    def test_internal_error_returns_500_generic(self) -> None:
        result = UseCaseResult.internal_error("DB conn refused: secret@host")
        with pytest.raises(HTTPException) as exc_info:
            raise_for_use_case_result(result)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Internal server error"
        assert "secret" not in exc_info.value.detail

    def test_legacy_no_category_returns_502_generic(self) -> None:
        result = UseCaseResult(
            status=ResultStatus.ERROR,
            error_message="Database connection refused: postgres://secret@host:5432",
        )
        with pytest.raises(HTTPException) as exc_info:
            raise_for_use_case_result(result)
        assert exc_info.value.status_code == 502
        assert exc_info.value.detail == "Upstream error"
        assert "secret" not in exc_info.value.detail

    def test_null_data_raises(self) -> None:
        result = UseCaseResult(status=ResultStatus.SUCCESS, data=None)
        with pytest.raises(HTTPException) as exc_info:
            raise_for_use_case_result(result)
        assert exc_info.value.status_code == 502


class TestUseCaseResultFactories:
    """Test UseCaseResult factory methods."""

    def test_validation_error_factory(self) -> None:
        result = UseCaseResult.validation_error("missing field")
        assert result.status == ResultStatus.ERROR
        assert result.error_category == ErrorCategory.VALIDATION
        assert result.error_message == "missing field"
        assert result.data is None

    def test_provider_error_factory(self) -> None:
        result = UseCaseResult.provider_error("timeout")
        assert result.status == ResultStatus.ERROR
        assert result.error_category == ErrorCategory.PROVIDER
        assert result.error_message == "timeout"

    def test_internal_error_factory(self) -> None:
        result = UseCaseResult.internal_error("unexpected")
        assert result.status == ResultStatus.ERROR
        assert result.error_category == ErrorCategory.INTERNAL


class TestValidationError:
    """Test domain ValidationError."""

    def test_is_value_error(self) -> None:
        err = ValidationError("invalid latitude")
        assert isinstance(err, ValueError)
        assert str(err) == "invalid latitude"

    def test_can_be_caught_as_value_error(self) -> None:
        with pytest.raises(ValueError, match="bad input"):
            raise ValidationError("bad input")
