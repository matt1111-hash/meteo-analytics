/**
 * StatusBar Component
 *
 * Displays current provider status and usage statistics.
 * Shows visual status indicators and supports auto-refresh.
 */
import React, { useEffect, useState, useCallback } from 'react';
import { useProviderManagement } from '../../hooks/useProviderManagement';
import {
  STATUS_LABELS,
  STATUS_COLORS,
  STATUS_BG_COLORS,
  formatUsagePercentage,
  formatCost,
  formatRequestCount,
  getStatusIcon,
} from '../../services/providerService';
import './StatusBar.css';

export interface StatusBarProps {
  /** Auto-refresh interval in milliseconds (0 to disable) */
  refreshInterval?: number;
  /** Whether to show detailed usage statistics */
  showDetails?: boolean;
  /** Whether to show the provider name */
  showProviderName?: boolean;
  /** Whether to show the status indicator */
  showStatus?: boolean;
  /** Additional CSS class name */
  className?: string;
  /** Whether to show the cost information */
  showCost?: boolean;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  refreshInterval = 30000,
  showDetails = true,
  showProviderName = true,
  showStatus = true,
  className = '',
  showCost = true,
}) => {
  const {
    providerStatuses,
    selectedProvider,
    selectedProviderUsage,
    isLoadingStatus,
    isLoadingUsage,
    error,
    refreshAll,
  } = useProviderManagement();

  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Get selected provider status
  const selectedStatus = providerStatuses.find(s => s.is_selected);

  // Auto-refresh effect
  useEffect(() => {
    if (refreshInterval <= 0) return;

    const interval = setInterval(async () => {
      await refreshAll();
      setLastRefresh(new Date());
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval, refreshAll]);

  // Manual refresh handler
  const handleRefresh = useCallback(async () => {
    await refreshAll();
    setLastRefresh(new Date());
  }, [refreshAll]);

  // Get status color and label
  const status = selectedStatus?.status || 'healthy';
  const statusLabel = STATUS_LABELS[status];
  const statusColor = STATUS_COLORS[status];
  const statusBgColor = STATUS_BG_COLORS[status];
  const statusIcon = getStatusIcon(status);

  // Render loading state
  if (isLoadingStatus && !selectedStatus) {
    return (
      <div className={`status-bar status-bar-loading ${className}`}>
        <span className="status-bar-spinner" />
        <span className="status-bar-text">Betöltés...</span>
      </div>
    );
  }

  // Render error state
  if (error && !selectedStatus) {
    return (
      <div className={`status-bar status-bar-error ${className}`}>
        <span className="status-bar-icon">⚠</span>
        <span className="status-bar-text">{error}</span>
        <button
          type="button"
          className="status-bar-retry"
          onClick={handleRefresh}
          aria-label="Újratöltés"
        >
          ↻
        </button>
      </div>
    );
  }

  return (
    <div className={`status-bar ${className}`}>
      {/* Provider info section */}
      <div className="status-bar-provider">
        {showProviderName && selectedProvider && (
          <>
            <span className="status-bar-icon">{selectedProvider.icon}</span>
            <span className="status-bar-name">{selectedProvider.name}</span>
          </>
        )}
        {showStatus && selectedStatus && (
          <span
            className="status-bar-status"
            style={{
              backgroundColor: statusBgColor,
              color: statusColor,
            }}
            title={statusLabel}
          >
            {statusIcon}
            <span className="status-bar-status-label">{statusLabel}</span>
          </span>
        )}
      </div>

      {/* Usage statistics section */}
      {showDetails && selectedStatus && (
        <div className="status-bar-usage">
          {/* Request count */}
          <span className="status-bar-stat">
            <span className="status-bar-stat-label">Kérések:</span>
            <span className="status-bar-stat-value">
              {formatRequestCount(selectedStatus.requests_this_month)}
            </span>
            {selectedStatus.monthly_limit && (
              <span className="status-bar-stat-max">
                {' '} / {formatRequestCount(selectedStatus.monthly_limit)}
              </span>
            )}
          </span>

          {/* Usage percentage with progress bar */}
          {selectedStatus.monthly_limit && (
            <span className="status-bar-stat status-bar-stat-progress">
              <span className="status-bar-stat-label">Használat:</span>
              <div className="status-bar-progress-bar">
                <div
                  className="status-bar-progress-fill"
                  style={{
                    width: `${selectedStatus.usage_percentage * 100}%`,
                    backgroundColor: statusColor,
                  }}
                  aria-label={`${formatUsagePercentage(selectedStatus.usage_percentage)} használva`}
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(selectedStatus.usage_percentage * 100)}
                />
              </div>
              <span className="status-bar-stat-value">
                {formatUsagePercentage(selectedStatus.usage_percentage)}
              </span>
            </span>
          )}

          {/* Cost */}
          {showCost && (
            <span className="status-bar-stat">
              <span className="status-bar-stat-label">Költség:</span>
              <span className="status-bar-stat-value">
                {formatCost(selectedStatus.estimated_cost_usd)}
              </span>
            </span>
          )}

          {/* Last used timestamp */}
          {selectedStatus.last_used && (
            <span className="status-bar-stat status-bar-stat-time">
              <span className="status-bar-stat-label">Utolsó használat:</span>
              <span className="status-bar-stat-value">
                {new Date(selectedStatus.last_used).toLocaleTimeString('hu-HU', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </span>
          )}
        </div>
      )}

      {/* Detailed usage (if available) */}
      {showDetails && selectedProviderUsage && (
        <div className="status-bar-detailed">
          {/* Average response time */}
          <span className="status-bar-stat">
            <span className="status-bar-stat-label">Válaszidő:</span>
            <span className="status-bar-stat-value">
              {selectedProviderUsage.average_response_time_ms.toFixed(0)} ms
            </span>
          </span>

          {/* Error rate */}
          {selectedProviderUsage.requests_this_month > 0 && (
            <span className="status-bar-stat">
              <span className="status-bar-stat-label">Hibaráta:</span>
              <span className="status-bar-stat-value">
                {(
                  (selectedProviderUsage.errors_this_month /
                    selectedProviderUsage.requests_this_month) *
                  100
                ).toFixed(1)}
                %
              </span>
            </span>
          )}

          {/* Budget remaining */}
          {showCost && selectedProviderUsage.budget_remaining_usd < 10 && (
            <span className="status-bar-stat status-bar-stat-warning">
              <span className="status-bar-stat-label">Keret marad:</span>
              <span className="status-bar-stat-value">
                ${selectedProviderUsage.budget_remaining_usd.toFixed(2)}
              </span>
            </span>
          )}
        </div>
      )}

      {/* Refresh button */}
      <button
        type="button"
        className="status-bar-refresh"
        onClick={handleRefresh}
        disabled={isLoadingStatus || isLoadingUsage}
        aria-label="Frissítés"
        title={`Frissítés (Utolsó: ${lastRefresh.toLocaleTimeString('hu-HU')})`}
      >
        <span
          className={`status-bar-refresh-icon ${isLoadingStatus || isLoadingUsage ? 'spinning' : ''}`}
        >
          ↻
        </span>
      </button>
    </div>
  );
};

export default StatusBar;
