# mypy: ignore-errors
"""Anomaly Settings UI Builder - re-export for backward compatibility."""

from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.buttons import (
    create_buttons_section,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.categories import (
    create_categories_grid,
    create_categories_tab,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.header import (
    create_header_section,
    create_profile_section,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.preview import (
    create_preview_tab,
    create_test_section,
)
from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds import (
    create_main_tabs,
    create_thresholds_tab,
)


class AnomalySettingsUIBuilder:
    """UI építő osztály az AnomalySettingsDialoghoz."""

    def __init__(self, dialog: object):
        """Inicializálás."""
        self.dialog = dialog

    def create_header_section(self) -> object:
        """Fejléc szekció."""
        return create_header_section(self.dialog)

    def create_profile_section(self) -> object:
        """Profil választó."""
        return create_profile_section(self.dialog)

    def create_main_tabs(self) -> object:
        """Főbb beállítási tab-ok."""
        return create_main_tabs(self.dialog)

    def create_thresholds_tab(self) -> object:
        """Küszöbértékek tab."""
        return create_thresholds_tab(self.dialog)

    def create_temperature_section(self) -> object:
        """Hőmérséklet szekció."""
        from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds import (  # noqa: PLC0415
            create_temperature_section,
        )

        return create_temperature_section(self.dialog)

    def create_precipitation_section(self) -> object:
        """Csapadék szekció."""
        from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds import (  # noqa: PLC0415
            create_precipitation_section,
        )

        return create_precipitation_section(self.dialog)

    def create_wind_section(self) -> object:
        """Szél szekció."""
        from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder.thresholds import (  # noqa: PLC0415
            create_wind_section,
        )

        return create_wind_section(self.dialog)

    def create_categories_tab(self) -> object:
        """Kategóriák tab."""
        return create_categories_tab(self.dialog)

    def create_categories_grid(self) -> object:
        """Kategóriák grid."""
        return create_categories_grid(self.dialog)

    def create_preview_tab(self) -> object:
        """Előnézet tab."""
        return create_preview_tab(self.dialog)

    def create_test_section(self) -> object:
        """Teszt szekció."""
        return create_test_section(self.dialog)

    def create_buttons_section(self) -> object:
        """Gombok szekció."""
        return create_buttons_section(self.dialog)
