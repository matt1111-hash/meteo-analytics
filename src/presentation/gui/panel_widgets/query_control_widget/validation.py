"""
Validation logic for QueryControlWidget.

Ez a modul tartalmazza a lekérdezés validációs logikát.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class QueryValidator:
    """
    Query paraméterek validátora.

    Validálja a helység, dátum tartomány, paraméterek és provider adatokat.
    """

    def __init__(self, location_widget, date_range_widget,
                 parameters_widget, provider_widget):
        """
        Validator inicializálása.

        Args:
            location_widget: Helység választó widget
            date_range_widget: Dátum tartomány widget
            parameters_widget: Paraméterek widget
            provider_widget: Provider widget
        """
        self._location_widget = location_widget
        self._date_range_widget = date_range_widget
        self._parameters_widget = parameters_widget
        self._provider_widget = provider_widget

    def is_query_valid(self) -> bool:
        """
        Lekérdezés validálása.

        Returns:
            bool: True ha minden adat valid
        """
        try:
            print(f"🔍 DEBUG: Starting query validation...")

            # Location validation
            if not self._validate_location():
                return False

            # Date range validation
            if not self._validate_date_range():
                return False

            # Parameters validation
            if not self._validate_parameters():
                return False

            # Provider validation
            if not self._validate_provider():
                return False

            print("✅ DEBUG: All validations passed!")
            return True

        except Exception as e:
            logger.error(f"Query validation error: {e}")
            print(f"❌ DEBUG: Query validation exception: {e}")
            return False

    def _validate_location(self) -> bool:
        """Helység adatok validálása."""
        if not self._location_widget:
            print("❌ DEBUG: No location widget")
            return False

        try:
            current_city = self._location_widget.get_current_city()
            if not current_city or current_city == "Nincs kiválasztva":
                print(f"❌ DEBUG: No city selected - current_city: '{current_city}'")
                return False

            coordinates = self._location_widget.get_current_coordinates()
            if not coordinates or len(coordinates) != 2:
                print(f"❌ DEBUG: Invalid coordinates: {coordinates}")
                return False

            lat, lon = coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                print(f"❌ DEBUG: Invalid coordinate values: lat={lat}, lon={lon}")
                return False

            print(f"✅ DEBUG: Location validation passed - city: '{current_city}', coords: {coordinates}")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Location validation error: {e}")
            return False

    def _validate_date_range(self) -> bool:
        """Dátum tartomány validálása."""
        if not self._date_range_widget:
            print("❌ DEBUG: No date range widget")
            return False

        try:
            date_range = self._date_range_widget.get_date_range()
            if not date_range or len(date_range) != 2:
                print(f"❌ DEBUG: Invalid date range: {date_range}")
                return False
            print(f"✅ DEBUG: Date range validation passed: {date_range}")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Date range validation error: {e}")
            return False

    def _validate_parameters(self) -> bool:
        """Paraméterek validálása."""
        if not self._parameters_widget:
            print("❌ DEBUG: No parameters widget")
            return False

        try:
            parameters = self._parameters_widget.get_selected_parameters()
            if not parameters or len(parameters) == 0:
                print(f"❌ DEBUG: No parameters selected: {parameters}")
                return False
            print(f"✅ DEBUG: Parameters validation passed: {len(parameters)} parameters")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Parameters validation error: {e}")
            return False

    def _validate_provider(self) -> bool:
        """Provider validálása."""
        if not self._provider_widget:
            print("❌ DEBUG: No provider widget")
            return False

        try:
            provider = self._provider_widget.get_current_provider()
            if not provider:
                print(f"❌ DEBUG: No provider selected: {provider}")
                return False
            print(f"✅ DEBUG: Provider validation passed: {provider}")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Provider validation error: {e}")
            return False

    def emit_validation_state(self, validation_signal) -> None:
        """
        Validálási állapot küldése.

        Args:
            validation_signal: Signal objektum
        """
        is_valid = self.is_query_valid()
        validation_signal.emit(is_valid)
