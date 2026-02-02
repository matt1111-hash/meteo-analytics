"""
QueryControlWidget modul.

Ez a modul tartalmazza a QueryControlWidget komponenst és
azzal kapcsolatos segédosztályokat.

Main export:
- QueryControlWidget: Fő query control widget
"""

from .core import QueryControlWidget
from .factory import create_query_control_widget
from .testing import run_standalone_test

__all__ = [
    "QueryControlWidget",
    "create_query_control_widget",
    "run_standalone_test",
]

# Version info
__version__ = "4.0.0"
