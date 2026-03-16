#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Control Panel - Mixins Module
Mindenh apply-edett mixin a ControlPanel osztályhoz.
"""

from .external_handlers import ExternalHandlersMixin
from .fetch_validation import FetchValidationMixin
from .public_api import PublicAPIMixin
from .request_builder import RequestBuilderMixin
from .signal_handlers import SignalHandlersMixin
from .ui_manager import UIManagerMixin

__all__ = [
    "SignalHandlersMixin",
    "UIManagerMixin",
    "FetchValidationMixin",
    "RequestBuilderMixin",
    "PublicAPIMixin",
    "ExternalHandlersMixin",
]
