#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WorkerManager Provider Manager - Provider routing and state management.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..core import WorkerManager


class ProviderManager:
    """Handle provider routing and state management."""

    def __init__(self, manager: 'WorkerManager'):
        """
        Initialize provider manager.

        Args:
            manager: WorkerManager instance
        """
        self._manager = manager

    def _on_provider_changed(self, new_provider: str) -> None:
        """
        Handle provider change.

        Args:
            new_provider: New provider name
        """
        from ..worker_utils import get_source_display_name

        print(f"🔄 DEBUG: Provider changed to: {get_source_display_name(new_provider)}")
        self._manager.last_successful_provider = new_provider
        self._manager.provider_changed.emit(new_provider)

    def _on_provider_fallback(self, original_provider: str, fallback_provider: str) -> None:
        """
        Handle provider fallback.

        Args:
            original_provider: Original provider name
            fallback_provider: Fallback provider name
        """
        print(f"🔄 DEBUG: Provider fallback: {original_provider} → {fallback_provider}")

        # Update provider state
        self._manager.provider_states[original_provider] = {
            "status": "failed",
            "last_attempt": datetime.now(),
            "fallback_used": fallback_provider
        }

        self._manager.provider_fallback_occurred.emit(original_provider, fallback_provider)

    def _on_provider_validation_failed(self, provider: str, error_message: str) -> None:
        """
        Handle provider validation failure.

        Args:
            provider: Provider name
            error_message: Error message
        """
        print(f"❌ DEBUG: Provider validation failed: {provider} - {error_message}")

        # Update provider state
        self._manager.provider_states[provider] = {
            "status": "validation_failed",
            "last_attempt": datetime.now(),
            "error": error_message
        }

        self._manager.provider_validation_failed.emit(provider, error_message)

    def _track_provider_usage(self, provider: str, success: bool) -> None:
        """
        Track provider usage.

        Args:
            provider: Provider name
            success: Whether the request was successful
        """
        print(f"📊 DEBUG: Provider usage tracked: {provider} - {'SUCCESS' if success else 'FAILED'}")

        # Update provider state
        if provider not in self._manager.provider_states:
            self._manager.provider_states[provider] = {}

        self._manager.provider_states[provider].update({
            "last_usage": datetime.now(),
            "last_result": "success" if success else "failed"
        })

        if success:
            self._manager.last_successful_provider = provider

        self._manager.provider_usage_tracked.emit(provider, success)

    def get_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Get provider states.

        Returns:
            Copy of provider states dictionary
        """
        self._manager.mutex.lock()
        try:
            return self._manager.provider_states.copy()
        finally:
            self._manager.mutex.unlock()

    def get_last_successful(self) -> Optional[str]:
        """
        Get last successful provider.

        Returns:
            Last successful provider name or None
        """
        return self._manager.last_successful_provider

    def reset_states(self) -> None:
        """Reset all provider states."""
        self._manager.mutex.lock()
        try:
            self._manager.provider_states.clear()
            self._manager.last_successful_provider = None
            print("🔄 DEBUG: Provider states reset")
        finally:
            self._manager.mutex.unlock()
