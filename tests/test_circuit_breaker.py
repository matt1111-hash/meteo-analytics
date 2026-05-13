"""Circuit breaker unit tests — state transitions, thread-safety, timeout."""

from __future__ import annotations

import threading
import time

import pytest
from src.infrastructure.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
)

# ---------------------------------------------------------------------------
# Construction / validation
# ---------------------------------------------------------------------------


class TestCircuitBreakerConstruction:
    def test_default_state_is_closed(self) -> None:
        cb = CircuitBreaker(name="test")
        assert cb.state == CircuitState.CLOSED

    def test_failure_count_starts_at_zero(self) -> None:
        cb = CircuitBreaker(name="test")
        assert cb.failure_count == 0

    def test_invalid_failure_threshold_raises(self) -> None:
        with pytest.raises(ValueError, match="failure_threshold"):
            CircuitBreaker(failure_threshold=0)

    def test_invalid_reset_timeout_raises(self) -> None:
        with pytest.raises(ValueError, match="reset_timeout"):
            CircuitBreaker(reset_timeout=-1)

    def test_repr_contains_state(self) -> None:
        cb = CircuitBreaker(name="om", failure_threshold=3)
        text = repr(cb)
        assert "om" in text
        assert "CLOSED" in text
        assert "0/3" in text


# ---------------------------------------------------------------------------
# Closed state
# ---------------------------------------------------------------------------


class TestClosedState:
    def test_allow_request_when_closed(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, name="t")
        assert cb.allow_request() is True

    def test_success_keeps_closed(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, name="t")
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_failures_accumulate_but_stay_closed_below_threshold(self) -> None:
        cb = CircuitBreaker(failure_threshold=5, name="t")
        for _ in range(4):
            cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 4


# ---------------------------------------------------------------------------
# Closed → Open transition
# ---------------------------------------------------------------------------


class TestClosedToOpen:
    def test_opens_after_threshold_failures(self) -> None:
        cb = CircuitBreaker(failure_threshold=3, name="t")
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_rejects_requests_when_open(self) -> None:
        cb = CircuitBreaker(failure_threshold=2, name="t")
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.allow_request() is False


# ---------------------------------------------------------------------------
# Open → Half-Open transition
# ---------------------------------------------------------------------------


class TestOpenToHalfOpen:
    def test_allows_probe_after_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=10.0, name="t")
        cb.record_failure()  # CLOSED → OPEN
        assert cb.state == CircuitState.OPEN

        now = time.monotonic()
        monkeypatch.setattr(time, "monotonic", lambda: now + 11.0)

        assert cb.allow_request() is True
        assert cb.state == CircuitState.HALF_OPEN

    def test_rejects_before_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=60.0, name="t")
        cb.record_failure()  # CLOSED → OPEN

        now = time.monotonic()
        monkeypatch.setattr(time, "monotonic", lambda: now + 5.0)

        assert cb.allow_request() is False
        assert cb.state == CircuitState.OPEN


# ---------------------------------------------------------------------------
# Half-Open state
# ---------------------------------------------------------------------------


class TestHalfOpen:
    def _open_then_halfopen(self, cb: CircuitBreaker, monkeypatch: pytest.MonkeyPatch) -> None:
        cb.record_failure()
        now = time.monotonic()
        monkeypatch.setattr(time, "monotonic", lambda: now + cb._reset_timeout + 1)
        cb.allow_request()

    def test_halfopen_to_closed_on_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=10.0, name="t")
        self._open_then_halfopen(cb, monkeypatch)
        assert cb.state == CircuitState.HALF_OPEN

        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_halfopen_to_open_on_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        cb = CircuitBreaker(failure_threshold=1, reset_timeout=10.0, name="t")
        self._open_then_halfopen(cb, monkeypatch)
        assert cb.state == CircuitState.HALF_OPEN

        cb.record_failure()
        assert cb.state == CircuitState.OPEN


# ---------------------------------------------------------------------------
# Manual reset
# ---------------------------------------------------------------------------


class TestManualReset:
    def test_reset_returns_to_closed(self) -> None:
        cb = CircuitBreaker(failure_threshold=1, name="t")
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_failures_dont_exceed_threshold(self) -> None:
        cb = CircuitBreaker(failure_threshold=10, name="t")
        barrier = threading.Barrier(10)

        def fail_n_times() -> None:
            barrier.wait()
            for _ in range(5):
                cb.record_failure()

        threads = [threading.Thread(target=fail_n_times) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert cb.state == CircuitState.OPEN
        assert cb.failure_count >= 10

    def test_concurrent_allow_and_record(self) -> None:
        cb = CircuitBreaker(failure_threshold=5, name="t")
        errors: list[str] = []

        def alternate_success_failure() -> None:
            try:
                for _ in range(100):
                    if cb.allow_request():
                        cb.record_success()
                    else:
                        cb.record_failure()
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=alternate_success_failure) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        assert cb.state in (CircuitState.CLOSED, CircuitState.OPEN, CircuitState.HALF_OPEN)
