#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherTooltipMixin Event Manager - Manage event connections.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import WeatherTooltipMixin


class EventManager:
    """Manage tooltip event connections."""

    def __init__(self, mixin: 'WeatherTooltipMixin'):
        """
        Initialize event manager.

        Args:
            mixin: WeatherTooltipMixin instance
        """
        self._mixin = mixin

    def connect_events(self) -> None:
        """Connect tooltip event handlers."""
        if not hasattr(self._mixin, 'mpl_connect'):
            print("⚠️ DEBUG: mpl_connect nem elérhető - tooltip events skipped")
            return

        connections = [
            self._mixin.mpl_connect('motion_notify_event', self._mixin._on_tooltip_mouse_move),
            self._mixin.mpl_connect('figure_leave_event', self._mixin._on_tooltip_figure_leave),
            self._mixin.mpl_connect('button_press_event', self._mixin._on_tooltip_mouse_click)
        ]

        self._mixin._tooltip_event_connections.extend(connections)
        print(f"🔗 DEBUG: {len(connections)} tooltip event handler kapcsolva")

    def disconnect_events(self) -> None:
        """Disconnect tooltip event handlers."""
        if not hasattr(self._mixin, 'mpl_disconnect'):
            return

        for connection in self._mixin._tooltip_event_connections:
            try:
                self._mixin.mpl_disconnect(connection)
            except Exception as e:
                print(f"⚠️ DEBUG: Event disconnect hiba: {e}")

        self._mixin._tooltip_event_connections.clear()
        print("🔌 DEBUG: Tooltip event handlers lekapcsolva")
