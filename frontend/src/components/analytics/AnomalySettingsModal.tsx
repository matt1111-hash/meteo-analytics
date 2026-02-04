/**
 * AnomalySettingsModal Component
 *
 * Modal for configuring anomaly detection thresholds and settings.
 * Uses the base Modal component for accessibility and functionality.
 */
import React, { useState, useCallback, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { useModal } from '../../hooks/useModal';
import './AnomalySettingsModal.css';

// =============================================================================
// TYPES
// =============================================================================

/**
 * Anomaly detection thresholds
 */
export interface AnomalyThresholds {
  /** Temperature threshold for hot anomalies (°C) */
  temp_hot?: number;
  /** Temperature threshold for cold anomalies (°C) */
  temp_cold?: number;
  /** Precipitation threshold for high anomalies (mm) */
  precip_high?: number;
  /** Precipitation threshold for low anomalies (mm) */
  precip_low?: number;
  /** Wind speed threshold for normal (km/h) */
  wind_normal?: number;
  /** Wind speed threshold for strong (km/h) */
  wind_strong?: number;
  /** Wind speed threshold for extreme (km/h) */
  wind_extreme?: number;
  /** Wind speed threshold for hurricane (km/h) */
  wind_hurricane?: number;
}

/**
 * Detection method for anomaly detection
 */
export type DetectionMethod = 'zscore' | 'iqr' | 'isolation_forest' | 'custom';

/**
 * Preset threshold configurations
 */
export type ThresholdPreset = 'default' | 'sensitive' | 'strict' | 'custom';

// =============================================================================
// DEFAULTS
// =============================================================================

const DEFAULT_THRESHOLDS: AnomalyThresholds = {
  temp_hot: 35,
  temp_cold: -10,
  precip_high: 50,
  precip_low: 0,
  wind_normal: 20,
  wind_strong: 50,
  wind_extreme: 90,
  wind_hurricane: 120,
};

const PRESETS: Record<ThresholdPreset, AnomalyThresholds> = {
  default: DEFAULT_THRESHOLDS,
  sensitive: {
    temp_hot: 30,
    temp_cold: -5,
    precip_high: 30,
    precip_low: 1,
    wind_normal: 15,
    wind_strong: 40,
    wind_extreme: 70,
    wind_hurricane: 100,
  },
  strict: {
    temp_hot: 40,
    temp_cold: -15,
    precip_high: 80,
    precip_low: 0,
    wind_normal: 25,
    wind_strong: 60,
    wind_extreme: 100,
    wind_hurricane: 140,
  },
  custom: {} as AnomalyThresholds,
};

// =============================================================================
// PROPS
// =============================================================================

export interface AnomalySettingsModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Callback when modal closes */
  onClose: () => void;
  /** Callback when settings are saved */
  onSave: (thresholds: AnomalyThresholds, method: DetectionMethod) => void;
  /** Initial thresholds */
  initialThresholds?: AnomalyThresholds;
  /** Initial detection method */
  initialMethod?: DetectionMethod;
  /** Custom CSS class name */
  className?: string;
}

// =============================================================================
// COMPONENT
// =============================================================================

export const AnomalySettingsModal: React.FC<AnomalySettingsModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialThresholds = DEFAULT_THRESHOLDS,
  initialMethod = 'zscore',
  className = '',
}) => {
  const [thresholds, setThresholds] = useState<AnomalyThresholds>(initialThresholds);
  const [method, setMethod] = useState<DetectionMethod>(initialMethod);
  const [preset, setPreset] = useState<ThresholdPreset>('default');
  const [errors, setErrors] = useState<Partial<Record<keyof AnomalyThresholds, string>>>({});

  // Reset form when modal opens with new initial values
  useEffect(() => {
    if (isOpen) {
      setThresholds(initialThresholds);
      setMethod(initialMethod);
      setPreset('default');
      setErrors({});
    }
  }, [isOpen, initialThresholds, initialMethod]);

  // Handle preset change
  const handlePresetChange = useCallback((newPreset: ThresholdPreset) => {
    setPreset(newPreset);
    if (newPreset !== 'custom') {
      setThresholds(PRESETS[newPreset]);
    }
  }, []);

  // Handle threshold value change
  const handleThresholdChange = useCallback((key: keyof AnomalyThresholds, value: string) => {
    const numValue = parseFloat(value);

    if (isNaN(numValue)) {
      setThresholds(prev => ({ ...prev, [key]: undefined }));
      setErrors(prev => ({ ...prev, [key]: undefined }));
    } else {
      setThresholds(prev => ({ ...prev, [key]: numValue }));

      // Validate
      const newErrors = { ...errors };
      switch (key) {
        case 'temp_hot':
          if (numValue < -50 || numValue > 60) {
            newErrors[key] = 'Érvénytelen tartomány (-50 to 60°C)';
          } else {
            delete newErrors[key];
          }
          break;
        case 'temp_cold':
          if (numValue < -50 || numValue > 40) {
            newErrors[key] = 'Érvénytelen tartomány (-50 to 40°C)';
          } else {
            delete newErrors[key];
          }
          break;
        case 'precip_high':
          if (numValue < 0 || numValue > 500) {
            newErrors[key] = 'Érvénytelen tartomány (0 to 500mm)';
          } else {
            delete newErrors[key];
          }
          break;
        case 'wind_hurricane':
          if (numValue < 100 || numValue > 200) {
            newErrors[key] = 'Érvénytelen tartomány (100 to 200km/h)';
          } else {
            delete newErrors[key];
          }
          break;
        default:
          delete newErrors[key];
      }
      setErrors(newErrors);
    }
  }, [errors]);

  // Validate all thresholds
  const hasErrors = Object.keys(errors).length > 0;

  // Handle save
  const handleSave = useCallback(() => {
    if (hasErrors) return;
    onSave(thresholds, method);
    onClose();
  }, [thresholds, method, onSave, onClose, hasErrors]);

  // Handle reset to defaults
  const handleReset = useCallback(() => {
    setThresholds(DEFAULT_THRESHOLDS);
    setMethod('zscore');
    setPreset('default');
    setErrors({});
  }, []);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="⚙️ Anomália detektálás beállítások"
      size="medium"
      className={`anomaly-settings-modal ${className}`}
      footer={
        <>
          <button
            type="button"
            className="modal-button modal-button-secondary"
            onClick={handleReset}
          >
            Alaphelyzet
          </button>
          <div className="modal-footer-spacer" />
          <button
            type="button"
            className="modal-button modal-button-secondary"
            onClick={onClose}
          >
            Mégse
          </button>
          <button
            type="button"
            className="modal-button modal-button-primary"
            onClick={handleSave}
            disabled={hasErrors}
          >
            Mentés
          </button>
        </>
      }
    >
      {/* Preset selection */}
      <div className="settings-section">
        <label className="settings-label">Előbeállítás</label>
        <div className="preset-buttons">
          <button
            type="button"
            className={`preset-button ${preset === 'default' ? 'active' : ''}`}
            onClick={() => handlePresetChange('default')}
          >
            Alapértelmezett
          </button>
          <button
            type="button"
            className={`preset-button ${preset === 'sensitive' ? 'active' : ''}`}
            onClick={() => handlePresetChange('sensitive')}
          >
            Érzékeny
          </button>
          <button
            type="button"
            className={`preset-button ${preset === 'strict' ? 'active' : ''}`}
            onClick={() => handlePresetChange('strict')}
          >
            Szigorú
          </button>
        </div>
      </div>

      {/* Detection method */}
      <div className="settings-section">
        <label className="settings-label">Detektálási módszer</label>
        <select
          className="settings-select"
          value={method}
          onChange={(e) => setMethod(e.target.value as DetectionMethod)}
        >
          <option value="zscore">Z-score (Statisztikai)</option>
          <option value="iqr">IQR (Interquartile Range)</option>
          <option value="isolation_forest">Isolation Forest (ML)</option>
          <option value="custom">Egyedi</option>
        </select>
        <p className="settings-hint">
          {method === 'zscore' && 'Statisztikai eltérés a szórás alapján'}
          {method === 'iqr' && 'Negyedérték-tartományon alapuló detektálás'}
          {method === 'isolation_forest' && 'Gépi tanulás alapú anomália detektálás'}
          {method === 'custom' && 'Egyedi küszöbértékek használata'}
        </p>
      </div>

      {/* Temperature thresholds */}
      <div className="settings-section">
        <h4 className="settings-group-title">🌡️ Hőmérséklet küszöbértékek</h4>
        <div className="settings-row">
          <div className="settings-field">
            <label className="field-label" htmlFor="temp-hot">Forró (°C)</label>
            <input
              id="temp-hot"
              type="number"
              className={`settings-input ${errors.temp_hot ? 'input-error' : ''}`}
              value={thresholds.temp_hot ?? ''}
              onChange={(e) => handleThresholdChange('temp_hot', e.target.value)}
              placeholder="35"
              step={1}
            />
            {errors.temp_hot && <span className="field-error">{errors.temp_hot}</span>}
          </div>
          <div className="settings-field">
            <label className="field-label" htmlFor="temp-cold">Hideg (°C)</label>
            <input
              id="temp-cold"
              type="number"
              className={`settings-input ${errors.temp_cold ? 'input-error' : ''}`}
              value={thresholds.temp_cold ?? ''}
              onChange={(e) => handleThresholdChange('temp_cold', e.target.value)}
              placeholder="-10"
              step={1}
            />
            {errors.temp_cold && <span className="field-error">{errors.temp_cold}</span>}
          </div>
        </div>
      </div>

      {/* Precipitation thresholds */}
      <div className="settings-section">
        <h4 className="settings-group-title">🌧️ Csapadék küszöbértékek</h4>
        <div className="settings-row">
          <div className="settings-field">
            <label className="field-label" htmlFor="precip-high">Magas (mm)</label>
            <input
              id="precip-high"
              type="number"
              className={`settings-input ${errors.precip_high ? 'input-error' : ''}`}
              value={thresholds.precip_high ?? ''}
              onChange={(e) => handleThresholdChange('precip_high', e.target.value)}
              placeholder="50"
              step={5}
            />
            {errors.precip_high && <span className="field-error">{errors.precip_high}</span>}
          </div>
          <div className="settings-field">
            <label className="field-label" htmlFor="precip-low">Alacsony (mm)</label>
            <input
              id="precip-low"
              type="number"
              className="settings-input"
              value={thresholds.precip_low ?? ''}
              onChange={(e) => handleThresholdChange('precip_low', e.target.value)}
              placeholder="0"
              step={1}
            />
          </div>
        </div>
      </div>

      {/* Wind thresholds */}
      <div className="settings-section">
        <h4 className="settings-group-title">💨 Szélsebesség küszöbértékek</h4>
        <div className="settings-row settings-row-4">
          <div className="settings-field">
            <label className="field-label" htmlFor="wind-normal">Normál (km/h)</label>
            <input
              id="wind-normal"
              type="number"
              className="settings-input"
              value={thresholds.wind_normal ?? ''}
              onChange={(e) => handleThresholdChange('wind_normal', e.target.value)}
              placeholder="20"
              step={5}
            />
          </div>
          <div className="settings-field">
            <label className="field-label" htmlFor="wind-strong">Erős (km/h)</label>
            <input
              id="wind-strong"
              type="number"
              className="settings-input"
              value={thresholds.wind_strong ?? ''}
              onChange={(e) => handleThresholdChange('wind_strong', e.target.value)}
              placeholder="50"
              step={5}
            />
          </div>
          <div className="settings-field">
            <label className="field-label" htmlFor="wind-extreme">Extrém (km/h)</label>
            <input
              id="wind-extreme"
              type="number"
              className="settings-input"
              value={thresholds.wind_extreme ?? ''}
              onChange={(e) => handleThresholdChange('wind_extreme', e.target.value)}
              placeholder="90"
              step={5}
            />
          </div>
          <div className="settings-field">
            <label className="field-label" htmlFor="wind-hurricane">Hurrikán (km/h)</label>
            <input
              id="wind-hurricane"
              type="number"
              className={`settings-input ${errors.wind_hurricane ? 'input-error' : ''}`}
              value={thresholds.wind_hurricane ?? ''}
              onChange={(e) => handleThresholdChange('wind_hurricane', e.target.value)}
              placeholder="120"
              step={5}
            />
            {errors.wind_hurricane && <span className="field-error">{errors.wind_hurricane}</span>}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default AnomalySettingsModal;
