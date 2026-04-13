/**
 * Provider Service - Weather data provider management API
 */
import axios from 'axios';

import { API_BASE_URL } from '../config/apiConfig';

// =============================================================================
// TYPES
// =============================================================================

/**
 * Available provider status levels
 */
export type ProviderStatus = 'healthy' | 'warning' | 'critical' | 'disabled';

/**
 * Provider identifier
 */
export type ProviderId = 'auto' | 'open-meteo' | 'meteostat';

/**
 * Information about a single weather provider
 */
export interface ProviderInfo {
  provider_id: string;
  name: string;
  description: string;
  icon: string;
  cost: string;
  limitations: string[];
  features: string[];
  routing_logic: Record<string, string>;
}

/**
 * Status information for a provider
 */
export interface ProviderStatusInfo {
  provider_id: string;
  name: string;
  status: ProviderStatus;
  is_selected: boolean;
  usage_percentage: number;
  requests_this_month: number;
  monthly_limit: number | null;
  estimated_cost_usd: number;
  last_used: string | null;
}

/**
 * Detailed usage statistics for a provider
 */
export interface ProviderUsage {
  provider_id: string;
  requests_total: number;
  requests_this_month: number;
  requests_today: number;
  errors_total: number;
  errors_this_month: number;
  average_response_time_ms: number;
  estimated_cost_usd: number;
  budget_remaining_usd: number;
  last_used: string | null;
  first_used: string | null;
  monthly_reset_date: string;
}

/**
 * Response for provider selection operation
 */
export interface ProviderSelectionResult {
  success: boolean;
  provider_id: string | null;
  previous_provider_id: string | null;
  message: string;
  timestamp: string;
}

/**
 * Response for listing all providers
 */
export interface ProviderListResponse {
  count: number;
  providers: ProviderInfo[];
  default_provider: string;
}

// =============================================================================
// API FUNCTIONS
// =============================================================================

/**
 * Get list of all available providers
 *
 * @returns List of all providers with their information
 */
export const getProviders = async (): Promise<ProviderListResponse> => {
  const response = await axios.get<ProviderListResponse>(
    `${API_BASE_URL}/api/providers/list`
  );
  return response.data;
};

/**
 * Get status information for all providers
 *
 * @returns Array of provider status information
 */
export const getProvidersStatus = async (): Promise<ProviderStatusInfo[]> => {
  const response = await axios.get<ProviderStatusInfo[]>(
    `${API_BASE_URL}/api/providers/status`
  );
  return response.data;
};

/**
 * Get status information for a specific provider
 *
 * @param providerId - Provider identifier
 * @returns Provider status information
 */
export const getProviderStatus = async (
  providerId: string
): Promise<ProviderStatusInfo> => {
  const response = await axios.get<ProviderStatusInfo>(
    `${API_BASE_URL}/api/providers/${providerId}/status`
  );
  return response.data;
};

/**
 * Get detailed usage statistics for a provider
 *
 * @param providerId - Provider identifier
 * @returns Detailed usage statistics
 */
export const getProviderUsage = async (
  providerId: string
): Promise<ProviderUsage> => {
  const response = await axios.get<ProviderUsage>(
    `${API_BASE_URL}/api/providers/${providerId}/usage`
  );
  return response.data;
};

/**
 * Select a provider as the active provider
 *
 * @param providerId - Provider identifier to select
 * @returns Selection result with success status
 */
export const selectProvider = async (
  providerId: string
): Promise<ProviderSelectionResult> => {
  const response = await axios.post<ProviderSelectionResult>(
    `${API_BASE_URL}/api/providers/${providerId}/select`
  );
  return response.data;
};

/**
 * Get the currently selected provider
 *
 * @returns Information about the selected provider
 */
export const getSelectedProvider = async (): Promise<ProviderInfo> => {
  const response = await axios.get<ProviderInfo>(
    `${API_BASE_URL}/api/providers/selected`
  );
  return response.data;
};

// =============================================================================
// CONSTANTS
// =============================================================================

/**
 * Provider display names (Hungarian)
 */
export const PROVIDER_LABELS: Record<string, string> = {
  auto: 'Automatikus',
  'open-meteo': 'Open-Meteo',
  meteostat: 'Meteostat',
};

/**
 * Provider status labels (Hungarian)
 */
export const STATUS_LABELS: Record<ProviderStatus, string> = {
  healthy: 'Egészséges',
  warning: 'Figyelmeztetés',
  critical: 'Kritikus',
  disabled: 'Letiltva',
};

/**
 * Provider status colors
 */
export const STATUS_COLORS: Record<ProviderStatus, string> = {
  healthy: '#22c55e',
  warning: '#f59e0b',
  critical: '#ef4444',
  disabled: '#6b7280',
};

/**
 * Provider status background colors (light)
 */
export const STATUS_BG_COLORS: Record<ProviderStatus, string> = {
  healthy: 'rgba(34, 197, 94, 0.1)',
  warning: 'rgba(245, 158, 11, 0.1)',
  critical: 'rgba(239, 68, 68, 0.1)',
  disabled: 'rgba(107, 114, 128, 0.1)',
};

/**
 * Sort providers by priority order
 */
export const PROVIDER_PRIORITY: string[] = ['auto', 'open-meteo', 'meteostat'];

/**
 * Format usage percentage for display
 */
export const formatUsagePercentage = (percentage: number): string => {
  return `${(percentage * 100).toFixed(1)}%`;
};

/**
 * Format cost for display
 */
export const formatCost = (costUsd: number): string => {
  if (costUsd === 0) {
    return 'Ingyenes';
  }
  return `$${costUsd.toFixed(4)}`;
};

/**
 * Format request count with locale
 */
export const formatRequestCount = (count: number): string => {
  return new Intl.NumberFormat('hu-HU').format(count);
};

/**
 * Get status icon for provider
 */
export const getStatusIcon = (status: ProviderStatus): string => {
  const icons: Record<ProviderStatus, string> = {
    healthy: '✓',
    warning: '⚠',
    critical: '✕',
    disabled: '○',
  };
  return icons[status];
};
