"""Thread-safe circuit breaker for weather provider resilience."""

from __future__ import annotations

import logging
import threading
import time
from enum import Enum, auto

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open and rejects a call."""


class CircuitBreaker:
    """Thread-safe circuit breaker with Closed / Open / Half-Open states.

    Closed  — requests pass through; consecutive failures are counted.
    Open    — requests are rejected immediately; after *reset_timeout* seconds
              the breaker transitions to Half-Open.
    Half-Open — a single probe request is allowed. On success the breaker
              closes; on failure it re-opens.

    Args:
        failure_threshold: Consecutive failures before opening (default 5).
        reset_timeout: Seconds to wait in Open state before Half-Open probe
            (default 60).
        name: Human-readable identifier for logging.
    """

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        name: str = "default",
    ) -> None:
        """Initialize circuit breaker with given thresholds."""
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if reset_timeout <= 0:
            raise ValueError("reset_timeout must be > 0")

        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._name = name

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        """Current circuit state (thread-safe read)."""
        with self._lock:
            return self._state

    @property
    def failure_count(self) -> int:
        """Current consecutive failure count."""
        with self._lock:
            return self._failure_count

    @property
    def name(self) -> str:
        """Human-readable identifier."""
        return self._name

    def allow_request(self) -> bool:
        """Check whether a request is allowed, transitioning states as needed.

        Returns True if the caller should proceed, False if the circuit is
        open and the request should be skipped.
        """
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                elapsed = time.monotonic() - self._last_failure_time
                if elapsed >= self._reset_timeout:
                    self._state = CircuitState.HALF_OPEN
                    logger.info("Circuit [%s]: OPEN → HALF_OPEN (probe allowed)", self._name)
                    return True
                return False

            # HALF_OPEN — one probe at a time
            return self._state == CircuitState.HALF_OPEN

    def record_success(self) -> None:
        """Record a successful call — resets failures, closes the circuit."""
        with self._lock:
            prev = self._state
            self._failure_count = 0
            self._state = CircuitState.CLOSED
            if prev != CircuitState.CLOSED:
                logger.info("Circuit [%s]: %s → CLOSED", self._name, prev.name)

    def record_failure(self) -> None:
        """Record a failed call — may open the circuit."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning("Circuit [%s]: HALF_OPEN → OPEN (probe failed)", self._name)
                return

            if self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    "Circuit [%s]: CLOSED → OPEN (%d consecutive failures)",
                    self._name,
                    self._failure_count,
                )

    def reset(self) -> None:
        """Forcefully reset to CLOSED state (for testing / admin)."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = 0.0
            logger.info("Circuit [%s]: manually reset to CLOSED", self._name)

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker(name={self._name!r}, state={self._state.name}, "
            f"failures={self._failure_count}/{self._failure_threshold})"
        )


__all__ = ["CircuitBreaker", "CircuitBreakerOpenError", "CircuitState"]
