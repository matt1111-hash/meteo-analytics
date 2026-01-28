#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analysis Handler - Result Processor

📊 Eredmény feldolgozás

Képességek:
- Result strukturálás
- Metadata hozzáadás
- Típus-specifikus feldolgozás

Fájl: src/presentation/gui/controller/analysis_handler/result_processor.py
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _process_analysis_result(self, result_data: Dict) -> Dict:
    """
    Analysis eredmény feldolgozása és strukturálása.

    Args:
        self: AnalysisHandler instance
        result_data: Nyers worker eredmény

    Returns:
        Feldolgozott és strukturált eredmény
    """
    try:
        analysis_type = self.analysis_state.get('analysis_type', 'unknown')

        processed_result = {
            'analysis_type': analysis_type,
            'request_data': self.analysis_state.get('request_data', {}),
            'result_data': result_data.get('result_data', {}),
            'metadata': {
                'provider': result_data.get('provider', 'unknown'),
                'timestamp': result_data.get('timestamp'),
                'duration': _calculate_analysis_duration(self),
                'success': result_data.get('success', True)
            }
        }

        # Típus-specifikus feldolgozás
        if analysis_type == 'single_location':
            pass  # Single location eredmény további feldolgozása (ha szükséges)
        elif analysis_type in ['multi_city', 'county_analysis']:
            processed_result['city_count'] = len(result_data.get('result_data', {}).get('cities', []))

        return processed_result

    except Exception as e:
        logger.error(f"Result processing hiba: {e}")
        return result_data


def _calculate_analysis_duration(self) -> float:
    """
    Analysis időtartam számítása másodpercben.

    Args:
        self: AnalysisHandler instance

    Returns:
        float: Időtartam másodpercben
    """
    start_time = self.analysis_state.get('start_time')
    if start_time:
        return (datetime.now() - start_time).total_seconds()
    return 0.0
