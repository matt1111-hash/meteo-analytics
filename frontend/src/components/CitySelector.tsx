/**
 * CitySelector - Dropdown with Hungarian cities preset + custom input option
 */
import React, { useState, useEffect, useMemo } from 'react';
import { HUNGARIAN_CITIES, EUROPEAN_CITIES, CUSTOM_CITY_VALUE } from '../constants/cities';
import './CitySelector.css';

interface CitySelectorProps {
  value: string;
  onChange: (city: string) => void;
  disabled?: boolean;
  label?: string;
  placeholder?: string;
  id?: string;
}

const CitySelector: React.FC<CitySelectorProps> = ({
  value,
  onChange,
  disabled = false,
  label = 'Város',
  placeholder = 'Válassz várost...',
  id = 'city-selector',
}) => {
  const allPresetCities = useMemo(() => [...HUNGARIAN_CITIES, ...EUROPEAN_CITIES], []);
  const isPresetCity = allPresetCities.some((c) => c.name === value);
  const [isCustomMode, setIsCustomMode] = useState<boolean>(!isPresetCity && value !== '');
  const [customValue, setCustomValue] = useState<string>(isCustomMode ? value : '');

  useEffect(() => {
    const cityIsPreset = allPresetCities.some((c) => c.name === value);
    if (!cityIsPreset && value !== '' && value !== CUSTOM_CITY_VALUE) {
      setIsCustomMode(true);
      setCustomValue(value);
    }
  }, [value, allPresetCities]);

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;
    if (selectedValue === CUSTOM_CITY_VALUE) {
      setIsCustomMode(true);
      setCustomValue('');
      onChange('');
    } else {
      setIsCustomMode(false);
      setCustomValue('');
      onChange(selectedValue);
    }
  };

  const handleCustomInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setCustomValue(newValue);
    onChange(newValue);
  };

  const handleBackToPreset = () => {
    setIsCustomMode(false);
    setCustomValue('');
    onChange('');
  };

  return (
    <div className="city-selector">
      {label && <label htmlFor={id}>{label}</label>}

      {!isCustomMode ? (
        <select
          id={id}
          value={value}
          onChange={handleSelectChange}
          disabled={disabled}
          className="city-select"
        >
          <option value="">{placeholder}</option>

          <optgroup label="Magyar városok">
            {HUNGARIAN_CITIES.map((city) => (
              <option key={city.name} value={city.name}>
                {city.name}
              </option>
            ))}
          </optgroup>

          <optgroup label="Európai városok">
            {EUROPEAN_CITIES.map((city) => (
              <option key={city.name} value={city.name}>
                {city.name} ({city.country})
              </option>
            ))}
          </optgroup>

          <optgroup label="Egyéb">
            <option value={CUSTOM_CITY_VALUE}>Egyéb város...</option>
          </optgroup>
        </select>
      ) : (
        <div className="custom-input-wrapper">
          <input
            type="text"
            id={id}
            value={customValue}
            onChange={handleCustomInputChange}
            disabled={disabled}
            placeholder="Írj be egy város nevet..."
            className="city-custom-input"
          />
          <button
            type="button"
            onClick={handleBackToPreset}
            disabled={disabled}
            className="back-to-preset-btn"
            title="Vissza a listához"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
};

export default CitySelector;
