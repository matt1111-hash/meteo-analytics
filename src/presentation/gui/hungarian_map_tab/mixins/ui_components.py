#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Map Tab UI Components - UI creation methods.

Provides UI component creation methods for HungarianMapTab.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.presentation.gui.theme_manager import register_widget_for_theming


class MapTabUIComponents:
    """
    UI component creation methods for HungarianMapTab.

    Creates the following attributes:
    - analytics_parameter_label: QLabel
    - analytics_sync_label: QLabel
    - weather_status_label: QLabel
    - folium_status_label: QLabel
    - auto_sync_check: QCheckBox
    - auto_weather_refresh_check: QCheckBox
    - refresh_weather_btn: QPushButton
    - reset_view_btn: QPushButton
    - export_map_btn: QPushButton
    - refresh_folium_btn: QPushButton
    - loading_progress: QProgressBar
    - loading_status: QLabel
    - location_selector: HungarianLocationSelector
    - map_visualizer: HungarianMapVisualizer
    """

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header section
        header_group = self._create_header_group()
        layout.addWidget(header_group)

        # Progress bar section
        self._create_progress_section(layout)

        # Main splitter with panels
        main_splitter = self._create_main_splitter()
        layout.addWidget(main_splitter)

        # Layout weights
        layout.setStretchFactor(header_group, 0)
        layout.setStretchFactor(main_splitter, 1)

    def _create_header_group(self) -> QGroupBox:
        """Create header group with status labels and action buttons."""
        header_group = QGroupBox(
            "Hungarian Interactive Map + Weather Overlay + Analytics Sync"
        )
        register_widget_for_theming(header_group, "container")
        header_layout = QHBoxLayout(header_group)

        # Title
        title_label = QLabel("Hungary Climate Map - Analytics Sync")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        register_widget_for_theming(title_label, "text")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Status labels
        self._create_status_labels(header_layout)

        # Checkboxes
        self._create_checkboxes(header_layout)

        # Action buttons
        self._create_action_buttons(header_layout)

        return header_group

    def _create_status_labels(self, layout: QHBoxLayout) -> None:
        """Create status indicator labels."""
        # Analytics parameter label
        self.analytics_parameter_label = QLabel("Parameter: None")
        self._style_status_label(self.analytics_parameter_label, "#8E44AD", bold=True)
        layout.addWidget(self.analytics_parameter_label)

        # Analytics sync label
        self.analytics_sync_label = QLabel("Analytics Sync: Ready")
        self._style_status_label(self.analytics_sync_label, "#27AE60")
        layout.addWidget(self.analytics_sync_label)

        # Weather status label
        self.weather_status_label = QLabel("Weather: No data")
        self._style_status_label(self.weather_status_label)
        layout.addWidget(self.weather_status_label)

        # Folium status label
        self.folium_status_label = QLabel("Folium: Initializing...")
        self._style_status_label(self.folium_status_label)
        layout.addWidget(self.folium_status_label)

    def _style_status_label(
        self, label: QLabel, color: str = None, bold: bool = False
    ) -> None:
        """Apply consistent styling to status labels."""
        font = label.font()
        font.setPointSize(9)
        label.setFont(font)
        if color:
            style = f"color: {color};"
            if bold:
                style += " font-weight: bold;"
            label.setStyleSheet(style)
        register_widget_for_theming(label, "text")

    def _create_checkboxes(self, layout: QHBoxLayout) -> None:
        """Create control checkboxes."""
        self.auto_sync_check = QCheckBox("Auto-sync")
        self.auto_sync_check.setChecked(True)
        self.auto_sync_check.setToolTip("Auto sync between location selector and map")
        register_widget_for_theming(self.auto_sync_check, "input")
        layout.addWidget(self.auto_sync_check)

        self.auto_weather_refresh_check = QCheckBox("Auto Weather")
        self.auto_weather_refresh_check.setChecked(True)
        self.auto_weather_refresh_check.setToolTip(
            "Auto refresh weather on parameter change"
        )
        register_widget_for_theming(self.auto_weather_refresh_check, "input")
        layout.addWidget(self.auto_weather_refresh_check)

    def _create_action_buttons(self, layout: QHBoxLayout) -> None:
        """Create action buttons."""
        self.refresh_weather_btn = QPushButton("Weather Refresh")
        self.refresh_weather_btn.setToolTip("Refresh weather overlay")
        self.refresh_weather_btn.setEnabled(False)
        register_widget_for_theming(self.refresh_weather_btn, "button")
        layout.addWidget(self.refresh_weather_btn)

        self.reset_view_btn = QPushButton("Reset View")
        self.reset_view_btn.setToolTip("Reset map to Hungary full view")
        register_widget_for_theming(self.reset_view_btn, "button")
        layout.addWidget(self.reset_view_btn)

        self.export_map_btn = QPushButton("Export Map")
        self.export_map_btn.setToolTip("Export map to HTML file")
        self.export_map_btn.setEnabled(False)
        register_widget_for_theming(self.export_map_btn, "button")
        layout.addWidget(self.export_map_btn)

        self.refresh_folium_btn = QPushButton("Refresh Map")
        self.refresh_folium_btn.setToolTip("Regenerate Folium map")
        self.refresh_folium_btn.setEnabled(False)
        register_widget_for_theming(self.refresh_folium_btn, "button")
        layout.addWidget(self.refresh_folium_btn)

    def _create_progress_section(self, layout: QVBoxLayout) -> None:
        """Create progress bar and status label."""
        self.loading_progress = QProgressBar()
        self.loading_progress.setRange(0, 100)
        self.loading_progress.setValue(0)
        self.loading_progress.setVisible(False)
        register_widget_for_theming(self.loading_progress, "input")
        layout.addWidget(self.loading_progress)

        self.loading_status = QLabel("Initializing map components...")
        register_widget_for_theming(self.loading_status, "text")
        layout.addWidget(self.loading_status)

    def _create_main_splitter(self) -> QSplitter:
        """Create main splitter with left and right panels."""
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(12)
        main_splitter.setChildrenCollapsible(False)
        register_widget_for_theming(main_splitter, "splitter")

        # Left panel - Location selector (30%)
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)

        # Right panel - Map visualizer (70%)
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)

        # Splitter configuration
        main_splitter.setStretchFactor(0, 0)  # Left fixed
        main_splitter.setStretchFactor(1, 1)  # Right expandable
        main_splitter.setSizes([380, 820])

        return main_splitter

    def _create_left_panel(self) -> QWidget:
        """Create left panel with location selector."""
        from src.presentation.gui.hungarian_location_selector import (
            HungarianLocationSelector,
        )

        left_panel = QWidget()
        left_panel.setMinimumWidth(350)
        left_panel.setMaximumWidth(500)
        register_widget_for_theming(left_panel, "container")

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        self.location_selector = HungarianLocationSelector()
        left_layout.addWidget(self.location_selector)

        return left_panel

    def _create_right_panel(self) -> QWidget:
        """Create right panel with map visualizer."""
        from src.presentation.gui.map import HungarianMapVisualizer

        right_panel = QWidget()
        right_panel.setMinimumWidth(600)
        register_widget_for_theming(right_panel, "container")

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)

        self.map_visualizer = HungarianMapVisualizer()
        right_layout.addWidget(self.map_visualizer)

        return right_panel


__all__ = ["MapTabUIComponents"]
