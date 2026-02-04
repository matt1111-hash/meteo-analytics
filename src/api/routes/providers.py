#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Provider Management API routes.

This module provides REST API endpoints for managing weather data providers,
including listing providers, getting status, and selecting providers.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, status

from src.api.dto.provider_dto import (
    ProviderInfoDTO,
    ProviderListResponse,
    ProviderSelectionDTO,
    ProviderStatusDTO,
    ProviderUsageDTO,
)
from src.config.provider_config import (
    ProviderConfig,
    UserPreferences,
    validate_provider_selection,
)


LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/api/providers", tags=["providers"])


# =============================================================================
# USAGE TRACKING (in-memory for demo)
# =============================================================================

# In production, this would be stored in a database
_usage_tracker: Dict[str, Dict[str, Any]] = {
    "auto": {
        "requests_total": 0,
        "requests_this_month": 0,
        "requests_today": 0,
        "errors_total": 0,
        "errors_this_month": 0,
        "response_times_ms": [],
        "last_used": None,
        "first_used": None,
    },
    "open-meteo": {
        "requests_total": 0,
        "requests_this_month": 0,
        "requests_today": 0,
        "errors_total": 0,
        "errors_this_month": 0,
        "response_times_ms": [],
        "last_used": None,
        "first_used": None,
    },
    "meteostat": {
        "requests_total": 0,
        "requests_this_month": 0,
        "requests_today": 0,
        "errors_this_month": 0,
        "errors_total": 0,
        "response_times_ms": [],
        "last_used": None,
        "first_used": None,
    },
}

# Provider limits (from provider config)
_PROVIDER_LIMITS: Dict[str, int | None] = {
    "auto": None,  # Unlimited
    "open-meteo": None,  # Unlimited (free tier)
    "meteostat": 10000,  # 10k requests/month
}

_PROVIDER_COSTS: Dict[str, float] = {
    "auto": 0.0,
    "open-meteo": 0.0,
    "meteostat": 0.001,  # $0.001 per request
}


def _get_usage_data(provider_id: str) -> Dict[str, Any]:
    """Get usage data for a provider.

    Args:
        provider_id: Provider identifier

    Returns:
        Usage data dictionary
    """
    return _usage_tracker.get(provider_id, _usage_tracker["auto"])


def _calculate_status(
    provider_id: str, usage_data: Dict[str, Any], is_selected: bool
) -> ProviderStatusDTO:
    """Calculate provider status based on usage data.

    Args:
        provider_id: Provider identifier
        usage_data: Usage tracking data
        is_selected: Whether this is the selected provider

    Returns:
        ProviderStatusDTO with calculated status
    """
    monthly_limit = _PROVIDER_LIMITS.get(provider_id)
    requests_this_month = usage_data.get("requests_this_month", 0)

    # Calculate usage percentage
    if monthly_limit is None:
        usage_percentage = 0.0
    else:
        usage_percentage = min(requests_this_month / monthly_limit, 1.0)

    # Calculate cost
    cost_per_request = _PROVIDER_COSTS.get(provider_id, 0.0)
    estimated_cost = requests_this_month * cost_per_request

    return ProviderStatusDTO.create(
        provider_id=provider_id,
        name=ProviderConfig.PROVIDERS[provider_id]["name"],
        is_selected=is_selected,
        usage_percentage=usage_percentage,
        requests_this_month=requests_this_month,
        monthly_limit=monthly_limit,
        estimated_cost_usd=estimated_cost,
        last_used=usage_data.get("last_used"),
    )


# =============================================================================
# API ENDPOINTS
# =============================================================================


@router.get(
    "/list",
    response_model=ProviderListResponse,
    summary="List all providers",
    description="Returns a list of all available weather data providers with their information.",
)
async def list_providers() -> ProviderListResponse:
    """Get list of all available providers.

    Returns:
        ProviderListResponse with all providers
    """
    try:
        provider_dtos: List[ProviderInfoDTO] = []

        for provider_id, config in ProviderConfig.PROVIDERS.items():
            provider_dtos.append(ProviderInfoDTO.from_config(provider_id, config))

        return ProviderListResponse.create(
            providers=provider_dtos,
            default_provider=ProviderConfig.DEFAULT_PROVIDER,
        )
    except Exception as exc:
        LOGGER.exception("Error listing providers", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider list",
        ) from exc


@router.get(
    "/status",
    response_model=List[ProviderStatusDTO],
    summary="Get provider statuses",
    description="Returns status information for all providers including usage and health.",
)
async def get_providers_status() -> List[ProviderStatusDTO]:
    """Get status of all providers.

    Returns:
        List of ProviderStatusDTO for all providers
    """
    try:
        selected_provider = UserPreferences.get_selected_provider()
        status_list: List[ProviderStatusDTO] = []

        for provider_id in ProviderConfig.PROVIDERS:
            usage_data = _get_usage_data(provider_id)
            is_selected = provider_id == selected_provider
            provider_status = _calculate_status(provider_id, usage_data, is_selected)
            status_list.append(provider_status)

        return status_list
    except Exception as exc:
        LOGGER.exception("Error getting provider status", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider status",
        ) from exc


@router.get(
    "/{provider_id}/status",
    response_model=ProviderStatusDTO,
    summary="Get single provider status",
    description="Returns status information for a specific provider.",
)
async def get_provider_status(provider_id: str) -> ProviderStatusDTO:
    """Get status of a specific provider.

    Args:
        provider_id: Provider identifier

    Returns:
        ProviderStatusDTO for the requested provider

    Raises:
        HTTPException: If provider not found
    """
    if not validate_provider_selection(provider_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )

    try:
        selected_provider = UserPreferences.get_selected_provider()
        usage_data = _get_usage_data(provider_id)
        is_selected = provider_id == selected_provider

        return _calculate_status(provider_id, usage_data, is_selected)
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception(f"Error getting status for provider {provider_id}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status for provider '{provider_id}'",
        ) from exc


@router.get(
    "/{provider_id}/usage",
    response_model=ProviderUsageDTO,
    summary="Get provider usage statistics",
    description="Returns detailed usage statistics for a specific provider.",
)
async def get_provider_usage(provider_id: str) -> ProviderUsageDTO:
    """Get detailed usage statistics for a provider.

    Args:
        provider_id: Provider identifier

    Returns:
        ProviderUsageDTO with detailed usage statistics

    Raises:
        HTTPException: If provider not found
    """
    if not validate_provider_selection(provider_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )

    try:
        usage_data = _get_usage_data(provider_id)
        response_times = usage_data.get("response_times_ms", [])

        # Calculate average response time
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0.0
        )

        # Calculate cost
        requests_this_month = usage_data.get("requests_this_month", 0)
        cost_per_request = _PROVIDER_COSTS.get(provider_id, 0.0)
        estimated_cost = requests_this_month * cost_per_request

        # Get budget from preferences
        prefs = UserPreferences.load_provider_preferences()
        monthly_budget = prefs.get("monthly_budget_usd", ProviderConfig.MONTHLY_BUDGET_USD)
        budget_remaining = max(0, monthly_budget - estimated_cost)

        # Calculate monthly reset date (first day of next month)
        now = datetime.now(timezone.utc)
        if now.month == 12:
            reset_date = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            reset_date = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)

        return ProviderUsageDTO(
            provider_id=provider_id,
            requests_total=usage_data.get("requests_total", 0),
            requests_this_month=requests_this_month,
            requests_today=usage_data.get("requests_today", 0),
            errors_total=usage_data.get("errors_total", 0),
            errors_this_month=usage_data.get("errors_this_month", 0),
            average_response_time_ms=avg_response_time,
            estimated_cost_usd=estimated_cost,
            budget_remaining_usd=budget_remaining,
            last_used=usage_data.get("last_used"),
            first_used=usage_data.get("first_used"),
            monthly_reset_date=reset_date.isoformat(),
        )
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception(f"Error getting usage for provider {provider_id}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage for provider '{provider_id}'",
        ) from exc


@router.post(
    "/{provider_id}/select",
    response_model=ProviderSelectionDTO,
    summary="Select a provider",
    description="Sets the specified provider as the active provider.",
)
async def select_provider(provider_id: str) -> ProviderSelectionDTO:
    """Select a provider as the active provider.

    Args:
        provider_id: Provider identifier to select

    Returns:
        ProviderSelectionDTO with selection result

    Raises:
        HTTPException: If provider not found or selection fails
    """
    if not validate_provider_selection(provider_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )

    try:
        # Get current provider before changing
        previous_provider = UserPreferences.get_selected_provider()

        # Attempt to set the new provider
        success = UserPreferences.set_selected_provider(provider_id)

        if not success:
            return ProviderSelectionDTO.error_response(
                f"Failed to select provider '{provider_id}'"
            )

        LOGGER.info(f"Provider changed from {previous_provider} to {provider_id}")

        return ProviderSelectionDTO.success_response(provider_id, previous_provider)
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception(f"Error selecting provider {provider_id}", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to select provider '{provider_id}'",
        ) from exc


@router.get(
    "/selected",
    response_model=ProviderInfoDTO,
    summary="Get selected provider",
    description="Returns information about the currently selected provider.",
)
async def get_selected_provider() -> ProviderInfoDTO:
    """Get the currently selected provider.

    Returns:
        ProviderInfoDTO for the selected provider

    Raises:
        HTTPException: If no provider is selected
    """
    try:
        provider_id = UserPreferences.get_selected_provider()

        if provider_id not in ProviderConfig.PROVIDERS:
            # Fallback to default if selected provider is invalid
            provider_id = ProviderConfig.DEFAULT_PROVIDER

        config = ProviderConfig.PROVIDERS[provider_id]
        return ProviderInfoDTO.from_config(provider_id, config)
    except Exception as exc:
        LOGGER.exception("Error getting selected provider", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve selected provider",
        ) from exc
