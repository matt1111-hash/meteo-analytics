"""
Widget factory for QueryControlWidget.

Ez a modul felelős a widgetek létrehozásáért fallback logikával.
"""

import logging

logger = logging.getLogger(__name__)


def create_location_widget(location_selector_class, fallback_class):
    """
    Location widget létrehozása fallback logikával.

    Args:
        location_selector_class: Valós location selector osztály
        fallback_class: Fallback osztály

    Returns:
        Widget példány
    """
    if location_selector_class:
        return location_selector_class()
    return fallback_class()


def create_date_range_widget(date_range_class, fallback_class):
    """Date range widget létrehozása fallback logikával."""
    if date_range_class:
        return date_range_class()
    return fallback_class()


def create_parameters_widget(parameters_class, fallback_class):
    """Parameters widget létrehozása fallback logikával."""
    if parameters_class:
        return parameters_class()
    return fallback_class()


def create_provider_widget(provider_class, fallback_class):
    """Provider widget létrehozása fallback logikával."""
    if provider_class:
        return provider_class()
    return fallback_class()


class WidgetFactory:
    """
    Widget factory osztály.

    Egyszerűsített widget létrehozás with fallback support.
    """

    def __init__(self, real_widgets: dict, fallback_widgets: dict):
        """
        Factory inicializálása.

        Args:
            real_widgets: Valós widget osztályok szótára
            fallback_widgets: Fallback widget osztályok szótára
        """
        self._real = real_widgets
        self._fallback = fallback_widgets

    def create_location(self):
        """Location widget létrehozása."""
        return create_location_widget(
            self._real.get('location'),
            self._fallback['location']
        )

    def create_date_range(self):
        """Date range widget létrehozása."""
        return create_date_range_widget(
            self._real.get('date_range'),
            self._fallback['date_range']
        )

    def create_parameters(self):
        """Parameters widget létrehozása."""
        return create_parameters_widget(
            self._real.get('parameters'),
            self._fallback['parameters']
        )

    def create_provider(self):
        """Provider widget létrehozása."""
        return create_provider_widget(
            self._real.get('provider'),
            self._fallback['provider']
        )
