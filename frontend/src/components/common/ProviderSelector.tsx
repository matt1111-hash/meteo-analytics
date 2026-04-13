/**
 * ProviderSelector Component
 *
 * Dropdown UI for selecting weather data providers.
 * Displays provider information including icon, name, description, cost, and status.
 */
import React, { useState } from 'react';
import { useProviderManagement } from '../../hooks/useProviderManagement';
import {
  PROVIDER_LABELS,
  STATUS_LABELS,
  STATUS_COLORS,
  STATUS_BG_COLORS,
  getStatusIcon,
} from '../../services/providerService';
import './ProviderSelector.css';

export interface ProviderSelectorProps {
  /** Currently selected provider ID (controlled) */
  value?: string;
  /** Callback when provider is selected */
  onChange?: (providerId: string) => void;
  /** Additional CSS class name */
  className?: string;
  /** Whether to show the status indicator */
  showStatus?: boolean;
  /** Whether to show the cost information */
  showCost?: boolean;
  /** Whether the selector is disabled */
  disabled?: boolean;
  /** Custom label for the selector */
  label?: string;
}

export const ProviderSelector: React.FC<ProviderSelectorProps> = ({
  value,
  onChange,
  className = '',
  showStatus = true,
  showCost = true,
  disabled = false,
  label = 'Adatszolgáltató',
}) => {
  const {
    providers,
    providerStatuses,
    selectedProvider,
    selectProvider,
    isLoadingProviders,
    isSelecting,
    error,
    clearError,
  } = useProviderManagement();

  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);

  // Get status for a specific provider
  const getStatusForProvider = (providerId: string) => {
    return providerStatuses.find(s => s.provider_id === providerId);
  };

  // Handle provider selection
  const handleSelectProvider = async (providerId: string): Promise<void> => {
    if (disabled || isSelecting) return;

    setIsOpen(false);
    setHighlightedIndex(-1);

    const success = await selectProvider(providerId);
    if (success && onChange) {
      onChange(providerId);
    }
  };

  // Handle keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent): void => {
    if (disabled) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
        } else {
          setHighlightedIndex(prev =>
            prev < providers.length - 1 ? prev + 1 : prev
          );
        }
        break;
      case 'ArrowUp':
        event.preventDefault();
        if (isOpen) {
          setHighlightedIndex(prev => (prev > 0 ? prev - 1 : 0));
        }
        break;
      case 'Enter':
        event.preventDefault();
        if (isOpen && highlightedIndex >= 0) {
          handleSelectProvider(providers[highlightedIndex].provider_id);
        } else {
          setIsOpen(!isOpen);
        }
        break;
      case 'Escape':
        event.preventDefault();
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
      case 'Tab':
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  // Get current display value
  const currentValue = value ?? selectedProvider?.provider_id ?? 'auto';
  const currentProvider = providers.find(p => p.provider_id === currentValue);
  const currentStatus = getStatusForProvider(currentValue);

  return (
    <div className={`provider-selector ${className} ${disabled ? 'disabled' : ''}`}>
      {label && <label className="provider-selector-label">{label}</label>}

      <button
        type="button"
        className="provider-selector-trigger"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={`${label}: ${currentProvider?.name || currentValue}`}
      >
        <span className="provider-selector-value">
          <span className="provider-selector-icon">
            {currentProvider?.icon || '🔧'}
          </span>
          <span className="provider-selector-name">
            {currentProvider?.name || PROVIDER_LABELS[currentValue] || currentValue}
          </span>
          {showStatus && currentStatus && (
            <span
              className="provider-selector-status"
              style={{
                backgroundColor: STATUS_BG_COLORS[currentStatus.status],
                color: STATUS_COLORS[currentStatus.status],
              }}
              title={STATUS_LABELS[currentStatus.status]}
            >
              {getStatusIcon(currentStatus.status)}
            </span>
          )}
        </span>
        <span className="provider-selector-arrow">
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points={`4 ${isOpen ? '2' : '6'} 8 10 ${isOpen ? '14' : '6'}`} />
          </svg>
        </span>
      </button>

      {isOpen && (
        <ul
          className="provider-selector-dropdown"
          role="listbox"
          aria-label={`${label} lehetőségek`}
        >
          {isLoadingProviders ? (
            <li className="provider-selector-option loading" role="option" aria-selected={false}>
              <span className="spinner" /> Betöltés...
            </li>
          ) : error ? (
            <li className="provider-selector-option error" role="option" aria-selected={false}>
              <span className="error-icon">⚠</span>
              <span>{error}</span>
              <button
                type="button"
                className="retry-button"
                onClick={(e) => {
                  e.stopPropagation();
                  clearError();
                }}
              >
                Újra
              </button>
            </li>
          ) : providers.length === 0 ? (
            <li className="provider-selector-option empty" role="option" aria-selected={false}>
              Nincs elérhető szolgáltató
            </li>
          ) : (
            providers.map((provider, index) => {
              const status = getStatusForProvider(provider.provider_id);
              const isSelected = provider.provider_id === currentValue;
              const isHighlighted = index === highlightedIndex;

              return (
                <li
                  key={provider.provider_id}
                  className={`provider-selector-option ${isSelected ? 'selected' : ''} ${
                    isHighlighted ? 'highlighted' : ''
                  } ${status?.status === 'critical' ? 'critical' : ''}`}
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => handleSelectProvider(provider.provider_id)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                >
                  <div className="provider-option-header">
                    <span className="provider-option-icon">{provider.icon}</span>
                    <span className="provider-option-name">{provider.name}</span>
                    {showStatus && status && (
                      <span
                        className="provider-option-status"
                        style={{
                          backgroundColor: STATUS_BG_COLORS[status.status],
                          color: STATUS_COLORS[status.status],
                        }}
                        title={STATUS_LABELS[status.status]}
                      >
                        {getStatusIcon(status.status)}
                      </span>
                    )}
                    {isSelected && (
                      <span className="provider-option-check" aria-hidden="true">
                        ✓
                      </span>
                    )}
                  </div>
                  <div className="provider-option-description">
                    {provider.description}
                  </div>
                  {showCost && (
                    <div className="provider-option-cost">{provider.cost}</div>
                  )}
                  {status && status.monthly_limit && (
                    <div className="provider-option-usage">
                      {Math.round(status.usage_percentage * 100)}% használva
                      ({status.requests_this_month} / {status.monthly_limit})
                    </div>
                  )}
                  {provider.features && provider.features.length > 0 && (
                    <div className="provider-option-features">
                      {provider.features.slice(0, 3).map((feature, i) => (
                        <span key={i} className="feature-tag">
                          {feature}
                        </span>
                      ))}
                    </div>
                  )}
                </li>
              );
            })
          )}
        </ul>
      )}

      {isSelecting && (
        <div className="provider-selector-loading-overlay">
          <span className="spinner" />
        </div>
      )}
    </div>
  );
};

export default ProviderSelector;
