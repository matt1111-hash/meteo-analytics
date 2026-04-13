# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Split definitions from ui_builder.py."""

from __future__ import annotations

from .ui_builder_support import *


def _get_status_label_style() -> str:
    """Status label stílus."""
    return """
        color: #64748B;
        font-style: italic;
        background: #F8FAFC;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
        font-size: 12px;
    """


def _get_results_list_style() -> str:
    """Results list stílus."""
    return """
        QListWidget {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 8px;
        }
        QListWidget::item {
            background: #FFFFFF;
            color: #1E293B;
            border: 1px solid #F1F5F9;
            border-radius: 6px;
            padding: 12px;
            margin: 4px 0px;
            font-size: 13px;
        }
        QListWidget::item:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #F8FAFC, stop:1 #F1F5F9);
            border: 1px solid #CBD5E1;
            color: #1E293B;
        }
        QListWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
            border: 1px solid #1D4ED8;
        }
    """


def _get_confirm_button_style() -> str:
    """Confirm button stílus."""
    return """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3B82F6, stop:1 #2563EB);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
            padding: 12px 16px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2563EB, stop:1 #1D4ED8);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1D4ED8, stop:1 #1E40AF);
        }
        QPushButton:disabled {
            background: #E2E8F0;
            color: #94A3B8;
        }
    """
