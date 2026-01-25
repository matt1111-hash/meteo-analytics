#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Usage Configuration
User preferences and API usage tracking
"""

import json
from datetime import datetime
from typing import Any, Dict

from .config_paths import PROVIDER_PREFS_FILE, USAGE_TRACKING_FILE, ensure_directories
from .config_provider import ProviderConfig
from .config_api import APIConfig


class UserPreferences:
    """User preferences management for Provider Selector"""

    @staticmethod
    def load_provider_preferences() -> Dict[str, Any]:
        """
        Load user's provider preferences from file

        Returns:
            Dictionary with user preferences
        """
        default_prefs = {
            "selected_provider": ProviderConfig.DEFAULT_PROVIDER,
            "auto_fallback_enabled": True,
            "show_usage_warnings": True,
            "show_cost_estimates": True,
            "monthly_budget_usd": ProviderConfig.MONTHLY_BUDGET_USD,
            "warning_threshold": ProviderConfig.WARNING_THRESHOLD,
            "last_updated": datetime.now().isoformat()
        }

        try:
            if PROVIDER_PREFS_FILE.exists():
                with open(PROVIDER_PREFS_FILE, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    # Merge with defaults for missing keys
                    return {**default_prefs, **prefs}
            else:
                return default_prefs
        except Exception as e:
            print(f"Error loading provider preferences: {e}")
            return default_prefs

    @staticmethod
    def save_provider_preferences(preferences: Dict[str, Any]) -> bool:
        """
        Save user's provider preferences to file

        Args:
            preferences: Dictionary with user preferences

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            ensure_directories()
            preferences["last_updated"] = datetime.now().isoformat()

            with open(PROVIDER_PREFS_FILE, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving provider preferences: {e}")
            return False

    @staticmethod
    def get_selected_provider() -> str:
        """Get user's currently selected provider"""
        prefs = UserPreferences.load_provider_preferences()
        return prefs.get("selected_provider", ProviderConfig.DEFAULT_PROVIDER)

    @staticmethod
    def set_selected_provider(provider: str) -> bool:
        """
        Set user's selected provider

        Args:
            provider: Provider name ("auto", "open-meteo", "meteostat")

        Returns:
            True if set successfully, False otherwise
        """
        if provider not in ProviderConfig.PROVIDERS:
            return False

        prefs = UserPreferences.load_provider_preferences()
        prefs["selected_provider"] = provider
        return UserPreferences.save_provider_preferences(prefs)


class UsageTracker:
    """API usage tracking for Provider Selector"""

    @staticmethod
    def load_usage_data() -> Dict[str, Any]:
        """
        Load API usage tracking data

        Returns:
            Dictionary with usage statistics
        """
        current_month = datetime.now().strftime("%Y-%m")

        default_usage = {
            "current_month": current_month,
            "meteostat": {
                "requests_this_month": 0,
                "estimated_cost_usd": 0.0,
                "last_request": None,
                "daily_breakdown": {}
            },
            "open_meteo": {
                "requests_this_month": 0,
                "last_request": None,
                "daily_breakdown": {}
            },
            "total_requests": 0,
            "month_start_date": f"{current_month}-01",
            "last_updated": datetime.now().isoformat()
        }

        try:
            if USAGE_TRACKING_FILE.exists():
                with open(USAGE_TRACKING_FILE, 'r', encoding='utf-8') as f:
                    usage = json.load(f)

                    # Reset if new month
                    if usage.get("current_month") != current_month:
                        usage = UsageTracker._reset_monthly_usage(usage, current_month)

                    return {**default_usage, **usage}
            else:
                return default_usage
        except Exception as e:
            print(f"Error loading usage data: {e}")
            return default_usage

    @staticmethod
    def save_usage_data(usage_data: Dict[str, Any]) -> bool:
        """
        Save usage tracking data

        Args:
            usage_data: Usage statistics dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            ensure_directories()
            usage_data["last_updated"] = datetime.now().isoformat()

            with open(USAGE_TRACKING_FILE, 'w', encoding='utf-8') as f:
                json.dump(usage_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving usage data: {e}")
            return False

    @staticmethod
    def track_request(provider: str, request_count: int = 1) -> Dict[str, Any]:
        """
        Track API request usage

        Args:
            provider: Provider name ("open-meteo" or "meteostat")
            request_count: Number of requests to track

        Returns:
            Updated usage statistics
        """
        usage = UsageTracker.load_usage_data()
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().isoformat()

        if provider in usage:
            # Update provider-specific stats
            usage[provider]["requests_this_month"] += request_count
            usage[provider]["last_request"] = now

            # Update daily breakdown
            if "daily_breakdown" not in usage[provider]:
                usage[provider]["daily_breakdown"] = {}

            if today not in usage[provider]["daily_breakdown"]:
                usage[provider]["daily_breakdown"][today] = 0
            usage[provider]["daily_breakdown"][today] += request_count

            # Update Meteostat cost estimation
            if provider == "meteostat":
                cost_per_request = ProviderConfig.METEOSTAT_COST_PER_REQUEST
                usage[provider]["estimated_cost_usd"] = (
                    usage[provider]["requests_this_month"] * cost_per_request
                )

        # Update total
        usage["total_requests"] += request_count

        # Save and return
        UsageTracker.save_usage_data(usage)
        return usage

    @staticmethod
    def get_usage_summary() -> Dict[str, Any]:
        """
        Get usage summary for display

        Returns:
            Dictionary with usage summary
        """
        usage = UsageTracker.load_usage_data()

        meteostat_requests = usage.get("meteostat", {}).get("requests_this_month", 0)
        meteostat_limit = APIConfig.METEOSTAT_MONTHLY_LIMIT
        meteostat_percentage = (meteostat_requests / meteostat_limit) * 100

        return {
            "meteostat_requests": meteostat_requests,
            "meteostat_limit": meteostat_limit,
            "meteostat_percentage": meteostat_percentage,
            "meteostat_cost": usage.get("meteostat", {}).get("estimated_cost_usd", 0.0),
            "openmeteo_requests": usage.get("open_meteo", {}).get("requests_this_month", 0),
            "total_requests": usage.get("total_requests", 0),
            "warning_level": UsageTracker._get_warning_level(meteostat_percentage),
            "days_remaining": UsageTracker._get_days_remaining_in_month()
        }

    @staticmethod
    def _reset_monthly_usage(old_usage: Dict[str, Any], new_month: str) -> Dict[str, Any]:
        """Reset usage data for new month"""
        old_usage["current_month"] = new_month
        old_usage["month_start_date"] = f"{new_month}-01"

        # Reset monthly counters but keep historical data
        for provider in ["meteostat", "open_meteo"]:
            if provider in old_usage:
                old_usage[provider]["requests_this_month"] = 0
                old_usage[provider]["daily_breakdown"] = {}
                if provider == "meteostat":
                    old_usage[provider]["estimated_cost_usd"] = 0.0

        old_usage["total_requests"] = 0
        return old_usage

    @staticmethod
    def _get_warning_level(percentage: float) -> str:
        """Get warning level based on usage percentage"""
        if percentage >= ProviderConfig.CRITICAL_THRESHOLD * 100:
            return "critical"
        elif percentage >= ProviderConfig.WARNING_THRESHOLD * 100:
            return "warning"
        else:
            return "normal"

    @staticmethod
    def _get_days_remaining_in_month() -> int:
        """Get number of days remaining in current month"""
        now = datetime.now()
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)

        return (next_month - now).days


__all__ = [
    'UserPreferences',
    'UsageTracker'
]
