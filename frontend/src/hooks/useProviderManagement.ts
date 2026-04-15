/**
 * useProviderManagement Hook - Manage provider selection and status
 */
import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { logger } from '../utils/logger';
import {
  getProviders,
  getProvidersStatus,
  getProviderUsage,
  selectProvider as apiSelectProvider,
  getSelectedProvider,
  ProviderInfo,
  ProviderStatusInfo,
  ProviderUsage,
} from '../services/providerService';

interface UseProviderManagementReturn {
  // Data
  providers: ProviderInfo[];
  providerStatuses: ProviderStatusInfo[];
  selectedProvider: ProviderInfo | null;
  selectedProviderUsage: ProviderUsage | null;

  // Loading states
  isLoadingProviders: boolean;
  isLoadingStatus: boolean;
  isLoadingUsage: boolean;
  isSelecting: boolean;

  // Error states
  error: string | null;

  // Actions
  fetchProviders: () => Promise<void>;
  fetchStatus: () => Promise<void>;
  fetchUsage: (providerId: string) => Promise<void>;
  selectProvider: (providerId: string) => Promise<boolean>;
  refreshAll: () => Promise<void>;
  clearError: () => void;
}

export const useProviderManagement = (): UseProviderManagementReturn => {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [providerStatuses, setProviderStatuses] = useState<ProviderStatusInfo[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<ProviderInfo | null>(null);
  const [selectedProviderUsage, setSelectedProviderUsage] = useState<ProviderUsage | null>(null);

  const [isLoadingProviders, setIsLoadingProviders] = useState<boolean>(false);
  const [isLoadingStatus, setIsLoadingStatus] = useState<boolean>(false);
  const [isLoadingUsage, setIsLoadingUsage] = useState<boolean>(false);
  const [isSelecting, setIsSelecting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch list of all providers
   */
  const fetchProviders = useCallback(async (): Promise<void> => {
    setIsLoadingProviders(true);
    setError(null);

    try {
      const response = await getProviders();
      setProviders(response.providers);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('Nem sikerült betölteni a szolgáltatók listáját');
      }
    } finally {
      setIsLoadingProviders(false);
    }
  }, []);

  /**
   * Fetch status for all providers
   */
  const fetchStatus = useCallback(async (): Promise<void> => {
    setIsLoadingStatus(true);
    setError(null);

    try {
      const statuses = await getProvidersStatus();
      setProviderStatuses(statuses);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('Nem sikerült betölteni a szolgáltatók állapotát');
      }
    } finally {
      setIsLoadingStatus(false);
    }
  }, []);

  /**
   * Fetch usage statistics for a specific provider
   */
  const fetchUsage = useCallback(async (providerId: string): Promise<void> => {
    setIsLoadingUsage(true);
    setError(null);

    try {
      const usage = await getProviderUsage(providerId);
      setSelectedProviderUsage(usage);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError(`Nem sikerült betölteni a használati adatokat: ${providerId}`);
      }
    } finally {
      setIsLoadingUsage(false);
    }
  }, []);

  /**
   * Select a provider as the active provider
   */
  const selectProvider = useCallback(async (providerId: string): Promise<boolean> => {
    setIsSelecting(true);
    setError(null);

    try {
      const result = await apiSelectProvider(providerId);

      if (result.success) {
        // Refresh selected provider and statuses
        const [selected, statuses] = await Promise.all([
          getSelectedProvider(),
          getProvidersStatus(),
        ]);
        setSelectedProvider(selected);
        setProviderStatuses(statuses);

        // Fetch usage for the newly selected provider
        await fetchUsage(providerId);

        return true;
      } else {
        setError(result.message);
        return false;
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.detail || err.message;
        setError(`API Error: ${errorMessage}`);
      } else {
        setError('Nem sikerült kiválasztani a szolgáltatót');
      }
      return false;
    } finally {
      setIsSelecting(false);
    }
  }, [fetchUsage]);

  /**
   * Refresh all provider data
   */
  const refreshAll = useCallback(async (): Promise<void> => {
    await Promise.all([
      fetchProviders(),
      fetchStatus(),
    ]);

    // Also fetch selected provider and its usage
    try {
      const [selected, statuses] = await Promise.all([
        getSelectedProvider(),
        getProvidersStatus().catch(() => []),
      ]);
      setSelectedProvider(selected);

      // Find selected provider ID from statuses
      const selectedStatus = statuses.find(s => s.is_selected);
      if (selectedStatus) {
        await fetchUsage(selectedStatus.provider_id);
      }
    } catch (err) {
      // Non-critical error, log but don't fail the refresh
      logger.error('Error refreshing selected provider:', err);
    }
  }, [fetchProviders, fetchStatus, fetchUsage]);

  /**
   * Clear current error
   */
  const clearError = useCallback((): void => {
    setError(null);
  }, []);

  // Initial data fetch on mount
  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  return {
    // Data
    providers,
    providerStatuses,
    selectedProvider,
    selectedProviderUsage,

    // Loading states
    isLoadingProviders,
    isLoadingStatus,
    isLoadingUsage,
    isSelecting,

    // Error
    error,

    // Actions
    fetchProviders,
    fetchStatus,
    fetchUsage,
    selectProvider,
    refreshAll,
    clearError,
  };
};
