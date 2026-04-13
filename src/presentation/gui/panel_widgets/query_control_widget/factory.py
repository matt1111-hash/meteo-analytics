# mypy: ignore-errors
"""
Factory functions for QueryControlWidget.

Ez a modul tartalmazza a QueryControlWidget létrehozó függvényeit.
"""

import logging

logger = logging.getLogger(__name__)


def create_query_control_widget():
    """
    Factory: QueryControlWidget létrehozása default beállításokkal.

    Returns:
        Fully configured QueryControlWidget instance
    """
    from .core import QueryControlWidget  # noqa: PLC0415

    widget = QueryControlWidget()

    logger.info("✅ QueryControlWidget created via factory method")
    return widget
