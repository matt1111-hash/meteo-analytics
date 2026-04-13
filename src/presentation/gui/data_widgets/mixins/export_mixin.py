#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Data Widgets - Export Mixin
Export funkciók kezelése.
"""

from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressBar


class ExportMixin:
    """
    Export funkciók kezelése.
    """

    # Signal
    export_completed = Signal(str, bool)  # filepath, success

    def _setup_export_ui(self, layout) -> None:
        """Export UI elemek létrehozása."""
        # Export progress
        self.export_progress = QProgressBar()
        self.export_progress.setVisible(False)
        self.export_progress.setMaximumWidth(200)
        layout.addWidget(self.export_progress)

    def _export_data(self, format: str) -> None:
        """Adatok exportálása."""
        if self.filtered_data is None or self.filtered_data.empty:
            QMessageBox.warning(self, "Export hiba", "Nincsenek exportálható adatok.")
            return

        if format == "csv":
            file_filter = "CSV fájlok (*.csv)"
            default_ext = ".csv"
        else:
            file_filter = "Excel fájlok (*.xlsx)"
            default_ext = ".xlsx"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"weather_data_{timestamp}{default_ext}"

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            f"Adatok exportálása ({format.upper()})",
            default_filename,
            file_filter,
        )

        if not filepath:
            return

        self._perform_export(filepath, format)

    def _perform_export(self, filepath: str, format: str) -> None:
        """Export végrehajtása."""
        try:
            self.export_progress.setVisible(True)
            self.export_progress.setRange(0, 100)
            self.export_progress.setValue(10)

            export_data = self.filtered_data.copy()
            column_names = [
                "Dátum",
                "Max hőmérséklet (°C)",
                "Min hőmérséklet (°C)",
                "Napi átlag (°C)",
                "Csapadék (mm)",
            ]

            if len(export_data.columns) > 5:  # noqa: PLR2004
                column_names.append("Szélsebesség (km/h)")

            export_data.columns = column_names[: len(export_data.columns)]

            self.export_progress.setValue(50)

            if format == "csv":
                export_data.to_csv(filepath, index=False, encoding="utf-8")
            else:
                export_data.to_excel(filepath, index=False, engine="openpyxl")

            self.export_progress.setValue(100)

            QMessageBox.information(
                self, "Export sikeres", f"Adatok sikeresen exportálva:\n{filepath}"
            )

            self.export_completed.emit(filepath, True)

        except Exception as e:
            QMessageBox.critical(self, "Export hiba", f"Hiba az export során:\n{e!s}")
            self.export_completed.emit(filepath, False)

        finally:
            self.export_progress.setVisible(False)
