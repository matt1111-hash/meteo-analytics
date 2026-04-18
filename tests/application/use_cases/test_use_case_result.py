#!/usr/bin/env python3
"""Tests for UseCaseResult typed result wrapper."""

from __future__ import annotations

import pytest
from src.application.use_cases.use_case_result import ResultStatus, UseCaseResult


def test_is_success_returns_true_for_success_status() -> None:
    result: UseCaseResult[str] = UseCaseResult(status=ResultStatus.SUCCESS, data="ok")
    assert result.is_success is True


def test_is_success_returns_false_for_error_status() -> None:
    result: UseCaseResult[str] = UseCaseResult(
        status=ResultStatus.ERROR, error_message="something went wrong"
    )
    assert result.is_success is False


def test_unwrap_returns_data_on_success() -> None:
    result: UseCaseResult[int] = UseCaseResult(status=ResultStatus.SUCCESS, data=42)
    assert result.unwrap() == 42


def test_unwrap_raises_runtime_error_on_error_status() -> None:
    result: UseCaseResult[str] = UseCaseResult(
        status=ResultStatus.ERROR, error_message="db failure"
    )
    with pytest.raises(RuntimeError, match="UseCaseResult is not successful: db failure"):
        result.unwrap()


def test_unwrap_raises_runtime_error_when_data_is_none() -> None:
    result: UseCaseResult[str] = UseCaseResult(status=ResultStatus.SUCCESS, data=None)
    with pytest.raises(RuntimeError, match="UseCaseResult is not successful: None"):
        result.unwrap()


def test_unwrap_raises_runtime_error_on_partial_status() -> None:
    result: UseCaseResult[str] = UseCaseResult(
        status=ResultStatus.PARTIAL, data="partial", error_message="incomplete"
    )
    with pytest.raises(RuntimeError, match="UseCaseResult is not successful: incomplete"):
        result.unwrap()
