#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Central Configuration
Központi konfigurációs modul minden útvonal és beállítás számára
CLEAN DUAL-API VERZIÓ: Csak Open-Meteo + Meteostat
✅ PROVIDER SELECTOR SUPPORT: User-controlled API választás + usage tracking
✅ COMPATIBILITY ALIASES: APIConstants, DataConstants backward compatibility
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Literal, List
from datetime import datetime, timedelta

# Project root directory (one level up from src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
CLIMATE_CACHE_DIR = DATA_DIR / "climate_cache"
EXPORTS_DIR = PROJECT_ROOT / "exports"
LOGS_DIR = PROJECT_ROOT / "logs"

# ✅ PROVIDER SELECTOR: User preferences directory
USER_PREFS_DIR = DATA_DIR / "user_preferences"
PROVIDER_PREFS_FILE = USER_PREFS_DIR / "provider_preferences.json"
USAGE_TRACKING_FILE = USER_PREFS_DIR / "api_usage_tracking.json"

# Database paths
WEATHER_DB_PATH = DATA_DIR / "weather.db"
CACHE_DB_PATH = DATA_DIR / "cache.db"

# Legacy compatibility
LEGACY_DB_PATH = PROJECT_ROOT / "legacy" / "meteo_data.db"

# API Configuration
class APIConfig:
    """API endpoints and configuration - CLEAN DUAL-API SYSTEM"""
    
    # Open-Meteo API (primary global data source - FREE)
    OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
    OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
    OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
    
    # Meteostat API (premium multi-city & historical data - 10k requests/month)
    METEOSTAT_BASE = "https://meteostat.p.rapidapi.com"
    METEOSTAT_API_KEY = os.getenv("METEOSTAT_API_KEY")
    METEOSTAT_MONTHLY_LIMIT = 10000  # 10k requests/month ($10 USD)
    METEOSTAT_RATE_LIMIT = 0.1  # 100ms minimum between requests
    
    # Request configuration
    REQUEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    CACHE_DURATION = 3600  # 1 hour in seconds
    
    # Data source priority for different use cases
    SINGLE_CITY_SOURCE = "open-meteo"  # Free tier for single city queries
    MULTI_CITY_SOURCE = "meteostat"    # Premium tier for multi-city analytics
    HISTORICAL_SOURCE = "meteostat"    # Premium tier for rich historical data
    
    # ✅ COMPATIBILITY: API timeouts and settings
    DEFAULT_TIMEOUT = 30  # másodperc
    MAX_RETRIES = 3
    CACHE_DURATION = 3600  # 1 óra másodpercben
    USER_AGENT = "Global Weather Analyzer/2.2.0 (Provider-Selector Edition)"
    
    # Rate Limiting Configuration
    OPENMETEO_RATE_LIMIT = 0.1  # 10 requests/second
    METEOSTAT_RATE_LIMIT = 0.1  # 100ms delay for premium API
    METEOSTAT_MONTHLY_LIMIT = 10000  # 10k requests/month
    
    # Source Display Names
    SOURCE_DISPLAY_NAMES = {
        "open-meteo": "🌍 Open-Meteo API",
        "meteostat": "💎 Meteostat API"
    }


# ✅ BACKWARD COMPATIBILITY: DataConstants class for utils.py
class DataConstants:
    """Adatkezelés konstansai - CLEAN DUAL-API VERZIÓ"""
    
    # API válasz mezők - Open-Meteo
    OPEN_METEO_DAILY_FIELDS = [
        "temperature_2m_max",
        "temperature_2m_min", 
        "temperature_2m_mean",  # ÚJ: átlag hőmérséklet
        "precipitation_sum",
        "windspeed_10m_max",
        "winddirection_10m_dominant",  # ÚJ: szélirány
        "weathercode"
    ]
    
    # 🌪️ KRITIKUS JAVÍTÁS: WIND GUSTS mezők hozzáadása
    OPEN_METEO_HOURLY_FIELDS = [
        "wind_gusts_10m",        # ÚJ: óránkénti széllökések
        "windspeed_10m"          # ÚJ: óránkénti szélsebesség
    ]
    
    # Meteostat API mezők
    METEOSTAT_DAILY_FIELDS = [
        "tavg",  # Átlag hőmérséklet
        "tmin",  # Min hőmérséklet  
        "tmax",  # Max hőmérséklet
        "prcp",  # Csapadék
        "snow",  # Hó
        "wdir",  # Szélirány
        "wspd",  # Szélsebesség
        "wpgt",  # Széllökés (KRITIKUS MEZŐ!)
        "pres",  # Légnyomás
        "tsun"   # Napsütés
    ]
    
    # 🌪️ KRITIKUS JAVÍTÁS: Processed mezők wind gusts támogatással
    PROCESSED_DAILY_FIELDS = [
        "temperature_2m_max",
        "temperature_2m_min", 
        "temperature_2m_mean",
        "precipitation_sum",
        "windspeed_10m_max",      # Backward compatibility
        "wind_gusts_max",         # ÚJ: napi maximum széllökések
        "winddirection_10m_dominant",
        "weathercode"
    ]
    
    # Export formátumok
    SUPPORTED_EXPORT_FORMATS = ["csv", "excel", "json", "pdf"]  # PDF hozzáadva
    
    # Pagination
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000
    
    # Cache beállítások
    CACHE_EXPIRY_HOURS = 24
    MAX_CACHE_SIZE_MB = 100
    
    # === ÚJ: DUAL-API ADATFORRÁS STRATÉGIA ===
    
    # Primary data source selection based on use case
    USE_CASE_SOURCE_MAPPING = {
        "single_city": "open-meteo",     # Free tier for single city
        "multi_city": "meteostat",       # Premium tier for multi-city
        "historical_deep": "meteostat",  # Rich historical data
        "real_time": "open-meteo",       # Real-time weather
        "station_based": "meteostat",    # Station-based accuracy
        "interpolated": "open-meteo"     # Grid-based interpolation
    }
    
    # Source priority order (fallback chain)
    DATA_SOURCE_PRIORITY = [
        "open-meteo",    # Elsődleges: Open-Meteo API (ingyenes)
        "meteostat"      # Másodlagos: Meteostat API (prémium backup)
    ]
    
    # Source capabilities matrix
    SOURCE_CAPABILITIES = {
        "open-meteo": {
            "historical": True,
            "real_time": True,
            "multi_city": True,
            "station_based": False,
            "cost": "free",
            "rate_limit": "10/sec",
            "wind_gusts": True,
            "rich_params": False
        },
        "meteostat": {
            "historical": True,
            "real_time": False,
            "multi_city": True,
            "station_based": True,
            "cost": "premium",
            "rate_limit": "10k/month",
            "wind_gusts": True,
            "rich_params": True  # pressure, sunshine, etc.
        }
    }


# ✅ PROVIDER SELECTOR: Provider configuration és preferences
class ProviderConfig:
    """Provider Selector configuration and user preferences"""
    
    # Supported providers
    PROVIDERS = {
        "auto": {
            "name": "Automatikus (Smart Routing)",
            "description": "Use-case alapú automatikus provider választás",
            "icon": "🤖",
            "cost": "Optimalizált",
            "routing_logic": {
                "single_city": "open-meteo",
                "multi_city": "meteostat", 
                "historical_deep": "meteostat",
                "real_time": "open-meteo"
            }
        },
        "open-meteo": {
            "name": "Open-Meteo (Ingyenes)",
            "description": "Ingyenes globális időjárási API minden funkcióhoz",
            "icon": "🌍",
            "cost": "Ingyenes",
            "limitations": ["Limitált multi-city support", "Alapszintű történeti adatok"]
        },
        "meteostat": {
            "name": "Meteostat (Prémium)",
            "description": "Prémium API gazdag történeti adatokkal és station-based accuracy",
            "icon": "💎",
            "cost": "$10 USD/hónap",
            "features": ["10k request/hónap", "Gazdag történeti adatok", "Station-based accuracy"]
        }
    }
    
    # Default provider preference
    DEFAULT_PROVIDER = "auto"
    
    # Usage tracking settings
    USAGE_RESET_DAY = 1  # Monthly usage reset on 1st day
    WARNING_THRESHOLD = 0.8  # Warn at 80% usage
    CRITICAL_THRESHOLD = 0.95  # Critical warning at 95% usage
    
    # Cost calculation
    METEOSTAT_COST_PER_REQUEST = 0.001  # $0.001 per request (rough estimate)
    MONTHLY_BUDGET_USD = 10.0  # $10 monthly budget

# GUI Configuration
class GUIConfig:
    """GUI appearance and behavior settings"""
    
    # Window settings
    DEFAULT_WINDOW_SIZE = (1200, 800)
    MIN_WINDOW_SIZE = (900, 600)
    
    # Chart settings
    DPI = 100
    FIGURE_SIZE = (5, 4)
    
    # Update intervals
    WEATHER_UPDATE_INTERVAL = 600  # 10 minutes
    WARNING_UPDATE_INTERVAL = 300  # 5 minutes
    
    # ✅ PROVIDER SELECTOR: GUI-specific settings
    PROVIDER_SELECTOR_POSITION = "control_panel"  # or "status_bar" or "both"
    SHOW_USAGE_WARNINGS = True
    SHOW_COST_ESTIMATES = True
    AUTO_FALLBACK_ON_LIMIT = True  # Automatic fallback when hitting limits

# Hardware Configuration
class HardwareConfig:
    """Hardware-specific optimizations"""
    
    # Based on user's specs: Intel i5-13400, 32GB RAM, RTX 3050 8GB
    MAX_CONCURRENT_REQUESTS = 8
    CHART_CACHE_SIZE = 50  # Number of charts to keep in memory
    DATA_CHUNK_SIZE = 10000  # Rows per processing chunk
    
    # GPU acceleration (for future features)
    USE_GPU_ACCELERATION = True
    GPU_MEMORY_LIMIT = 6  # GB (conservative limit for RTX 3050)

# Multi-City Configuration
class MultiCityConfig:
    """Multi-city analytics specific settings"""
    
    # Meteostat API optimization for multi-city
    MAX_CITIES_PER_BATCH = 20  # Cities to process in parallel
    STATION_SEARCH_RADIUS = 50000  # 50km radius for station search
    MAX_STATION_DISTANCE = 25.0  # 25km max distance from city center
    
    # Rate limiting for premium API
    METEOSTAT_CONCURRENT_REQUESTS = 5  # Conservative concurrent limit
    METEOSTAT_REQUEST_DELAY = 0.1  # 100ms delay between requests
    
    # Fallback configuration
    ENABLE_FALLBACK_TO_OPENMETEO = True  # Fallback if Meteostat fails
    FALLBACK_THRESHOLD = 0.3  # Switch to fallback if >30% failures

# Application Metadata
class AppInfo:
    """Application information and metadata"""
    
    NAME = "Global Weather Analyzer"
    VERSION = "2.2.0"  # Updated for Provider Selector feature
    DESCRIPTION = "Advanced meteorological data analysis tool with user-controlled dual-API support"
    AUTHOR = "Weather Analytics Team"
    
    # API Architecture info
    API_ARCHITECTURE = "User-Controlled Dual-API System"
    PRIMARY_API = "Open-Meteo (Free)"
    PREMIUM_API = "Meteostat (Premium)"
    
    # Provider Selector info
    PROVIDER_SELECTOR_VERSION = "1.0.0"
    PROVIDER_SELECTOR_FEATURES = [
        "User-controlled API selection",
        "Real-time usage tracking",
        "Cost monitoring",
        "Smart routing logic",
        "Automatic fallback"
    ]
    
    # Legacy compatibility
    LEGACY_NAME = "Meteo History"
    LEGACY_VERSION = "1.0.0"

# ✅ PROVIDER SELECTOR: User preferences management
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

# ✅ PROVIDER SELECTOR: Usage tracking
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

# API Key Validation
def validate_api_keys() -> Dict[str, bool]:
    """
    Validate required API keys and configuration
    
    Returns:
        Dictionary with validation results
    """
    validation = {
        "meteostat_key_present": bool(APIConfig.METEOSTAT_API_KEY),
        "meteostat_key_valid": False,
        "openmeteo_available": True  # Open-Meteo doesn't require API key
    }
    
    # Meteostat API key validation
    if APIConfig.METEOSTAT_API_KEY:
        # Basic validation - check if it's not empty and has reasonable length
        key = APIConfig.METEOSTAT_API_KEY.strip()
        if len(key) >= 32:  # RapidAPI keys are typically 32+ characters
            validation["meteostat_key_valid"] = True
    
    return validation

# Environment Configuration Check
def check_environment() -> Dict[str, Any]:
    """
    Check environment configuration and requirements
    
    Returns:
        Environment status dictionary
    """
    env_status = {
        "directories_created": False,
        "api_keys_valid": False,
        "write_permissions": False,
        "cache_available": False,
        "provider_selector_ready": False  # ✅ NEW
    }
    
    try:
        # Check directories
        ensure_directories()
        env_status["directories_created"] = True
        
        # Check API keys
        api_validation = validate_api_keys()
        env_status["api_keys_valid"] = api_validation["meteostat_key_valid"]
        
        # Check write permissions
        test_file = DATA_DIR / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            env_status["write_permissions"] = True
        except:
            pass
        
        # Check cache availability
        env_status["cache_available"] = CACHE_DIR.exists() and CACHE_DIR.is_dir()
        
        # ✅ Check Provider Selector readiness
        env_status["provider_selector_ready"] = (
            env_status["directories_created"] and
            env_status["write_permissions"] and
            USER_PREFS_DIR.exists()
        )
        
    except Exception as e:
        env_status["error"] = str(e)
    
    return env_status

# Ensure directories exist
def ensure_directories():
    """Create all necessary directories if they don't exist"""
    directories = [
        DATA_DIR,
        CACHE_DIR,
        CLIMATE_CACHE_DIR,
        EXPORTS_DIR,
        LOGS_DIR,
        USER_PREFS_DIR  # ✅ NEW - Provider Selector preferences
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Configuration validation
def validate_config() -> Dict[str, Any]:
    """Validate configuration and return status"""
    status = {
        "directories": True,
        "legacy_db": LEGACY_DB_PATH.exists(),
        "write_permissions": True,
        "api_configuration": False,
        "multi_city_ready": False,
        "provider_selector_ready": False  # ✅ NEW
    }
    
    try:
        ensure_directories()
        
        # API configuration validation
        api_validation = validate_api_keys()
        status["api_configuration"] = api_validation["openmeteo_available"]
        
        # Multi-city readiness check
        status["multi_city_ready"] = (
            api_validation["meteostat_key_valid"] and
            status["api_configuration"]
        )
        
        # ✅ Provider Selector readiness check
        status["provider_selector_ready"] = (
            status["directories"] and
            status["write_permissions"] and
            USER_PREFS_DIR.exists()
        )
        
    except PermissionError:
        status["directories"] = False
        status["write_permissions"] = False
        status["provider_selector_ready"] = False
    except Exception as e:
        status["validation_error"] = str(e)
    
    return status

# Get active data sources
def get_active_data_sources() -> Dict[str, Dict[str, Any]]:
    """
    Get information about active data sources
    
    Returns:
        Dictionary with data source information
    """
    sources = {
        "open-meteo": {
            "name": "Open-Meteo API",
            "type": "free",
            "status": "active",
            "use_cases": ["single-city", "basic-historical", "real-time"],
            "rate_limit": "10 requests/second",
            "cost": "Free"
        }
    }
    
    # Add Meteostat if API key is available
    api_validation = validate_api_keys()
    if api_validation["meteostat_key_valid"]:
        sources["meteostat"] = {
            "name": "Meteostat API",
            "type": "premium",
            "status": "active",
            "use_cases": ["multi-city", "rich-historical", "station-based"],
            "rate_limit": f"{APIConfig.METEOSTAT_MONTHLY_LIMIT} requests/month",
            "cost": "$10 USD/month"
        }
    else:
        sources["meteostat"] = {
            "name": "Meteostat API",
            "type": "premium",
            "status": "inactive - API key required",
            "use_cases": ["multi-city", "rich-historical", "station-based"],
            "rate_limit": "10000 requests/month",
            "cost": "$10 USD/month"
        }
    
    return sources

# ✅ PROVIDER SELECTOR: Get resolved provider for use case
def get_resolved_provider(use_case: str, user_override: Optional[str] = None) -> str:
    """
    Get resolved provider for specific use case
    
    Args:
        use_case: Use case ("single_city", "multi_city", "historical_deep", "real_time")
        user_override: User's provider preference override
        
    Returns:
        Resolved provider name
    """
    # User override has highest priority
    if user_override and user_override != "auto":
        return user_override
    
    # Get user's selected provider
    selected_provider = UserPreferences.get_selected_provider()
    
    if selected_provider == "auto":
        # Use smart routing
        routing = ProviderConfig.PROVIDERS["auto"]["routing_logic"]
        return routing.get(use_case, "open-meteo")
    else:
        # Use user's fixed selection
        return selected_provider


# ✅ BACKWARD COMPATIBILITY ALIASES for utils.py

# Alias for APIConstants (used by utils.py)
APIConstants = APIConfig

# Additional utilities needed by utils.py
def get_optimal_data_source(use_case: str, prefer_free: bool = True) -> str:
    """
    Optimális adatforrás meghatározása használati eset alapján.
    
    Args:
        use_case: Használati eset ("single_city", "multi_city", stb.)
        prefer_free: Ingyenes forrás preferálása
        
    Returns:
        Optimális data source azonosító
    """
    if use_case in DataConstants.USE_CASE_SOURCE_MAPPING:
        optimal_source = DataConstants.USE_CASE_SOURCE_MAPPING[use_case]
        
        # Ha ingyenes forrást preferálunk és az optimális fizetős
        if prefer_free and optimal_source == "meteostat":
            # Ellenőrizzük, hogy az open-meteo képes-e kezelni
            if DataConstants.SOURCE_CAPABILITIES["open-meteo"].get(use_case.replace("_", "-"), False):
                return "open-meteo"
        
        return optimal_source
    
    # Default fallback
    return "open-meteo"


def get_source_display_name(source_id: str) -> str:
    """
    Adatforrás megjelenítési neve.
    
    Args:
        source_id: Source azonosító
        
    Returns:
        Felhasználóbarát megjelenítési név
    """
    return APIConstants.SOURCE_DISPLAY_NAMES.get(source_id, f"Unknown Source ({source_id})")


def validate_api_source_available(source_id: str) -> bool:
    """
    API forrás elérhetőségének validálása.
    
    Args:
        source_id: Source azonosító
        
    Returns:
        Elérhető-e az API
    """
    if source_id == "open-meteo":
        return True  # Mindig elérhető (nincs API kulcs szükséges)
    
    elif source_id == "meteostat":
        # Environment variable ellenőrzése
        api_key = os.getenv("METEOSTAT_API_KEY")
        return bool(api_key and len(api_key.strip()) >= 32)
    
    return False


def get_fallback_source_chain(primary_source: str) -> List[str]:
    """
    Fallback forrás lánc meghatározása.
    
    Args:
        primary_source: Elsődleges forrás
        
    Returns:
        Fallback források listája
    """
    available_sources = [
        source for source in DataConstants.DATA_SOURCE_PRIORITY 
        if validate_api_source_available(source)
    ]
    
    # Primary source előre helyezése
    if primary_source in available_sources:
        available_sources.remove(primary_source)
        available_sources.insert(0, primary_source)
    
    return available_sources


# Initialize on import
ensure_directories()
