#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Provider Management API routes.

This module provides REST API endpoints for managing weather data providers,
including listing providers, getting status, and selecting providers.
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status

from src.api.dto.provider_dto import (
    ProviderInfoDTO,
    ProviderListResponse,
    ProviderSelectionDTO,
    ProviderStatusDTO,
    ProviderUsageDTO,
)
from src.api.services.provider_usage_service import get_usage_service
from src.config.provider_config import (
    ProviderConfig,
    UserPreferences,
    validate_provider_selection,
)

LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/api/providers", tags=["providers"])


# =============================================================================
# API ENDPOINTS
# =============================================================================


@router.get(
    "/list",
    response_model=ProviderListResponse,
    summary="List all providers",
    description="Returns a list of all available weather data providers.",
)
async def list_providers() -> ProviderListResponse:
    """Get list of all available providers."""
    try:
        provider_dtos: List[ProviderInfoDTO] = [
            ProviderInfoDTO.from_config(provider_id, config)
            for provider_id, config in ProviderConfig.PROVIDERS.items()
        ]
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
    description="Returns status information for all providers.",
)
async def get_providers_status() -> List[ProviderStatusDTO]:
    """Get status of all providers."""
    try:
        usage_service = get_usage_service()
        selected_provider = UserPreferences.get_selected_provider()

        return [
            usage_service.calculate_status(
                provider_id, provider_id == selected_provider
            )
            for provider_id in ProviderConfig.PROVIDERS
        ]
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

    Raises:
        HTTPException: If provider not found
    """
    if not validate_provider_selection(provider_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )

    try:
        usage_service = get_usage_service()
        selected_provider = UserPreferences.get_selected_provider()
        return usage_service.calculate_status(
            provider_id, provider_id == selected_provider
        )
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception(
            f"Error getting status for provider {provider_id}", exc_info=exc
        )
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

    Raises:
        HTTPException: If provider not found
    """
    if not validate_provider_selection(provider_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )

    try:
        usage_service = get_usage_service()
        return usage_service.get_detailed_usage(provider_id)
    except HTTPException:
        raise
    except Exception as exc:
        LOGGER.exception(
            f"Error getting usage for provider {provider_id}", exc_info=exc
        )
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

    Raises:
        HTTPException: If provider not found or selection fails
    """
    if not validate_provider_selection(provider_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_id}' not found",
        )

    try:
        previous_provider = UserPreferences.get_selected_provider()
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

    Raises:
        HTTPException: If no provider is selected
    """
    try:
        provider_id = UserPreferences.get_selected_provider()

        if provider_id not in ProviderConfig.PROVIDERS:
            provider_id = ProviderConfig.DEFAULT_PROVIDER

        config = ProviderConfig.PROVIDERS[provider_id]
        return ProviderInfoDTO.from_config(provider_id, config)
    except Exception as exc:
        LOGGER.exception("Error getting selected provider", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve selected provider",
        ) from exc
