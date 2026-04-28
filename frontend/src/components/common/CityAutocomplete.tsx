import React, { useState, useEffect, useRef, useCallback } from 'react';
import apiClient from '../../services/apiClient';
import { logger } from '../../utils/logger';
import './CityAutocomplete.css';

interface City {
  name: string;
  country: string;
  country_code: string;
  coordinates?: {
    lat: number;
    lon: number;
  };
  population?: number;
  meteostat_station_id?: string;
  data_quality_score?: number;
}

interface CityAutocompleteProps {
  value: string;
  onChange: (cityName: string) => void;
  onCitySelect?: (city: City) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  minLength?: number;
  debounceMs?: number;
  maxResults?: number;
}

const CityAutocomplete: React.FC<CityAutocompleteProps> = ({
  value,
  onChange,
  onCitySelect,
  placeholder = 'Search for a city...',
  disabled = false,
  className = '',
  minLength = 2,
  debounceMs = 300,
  maxResults = 20,
}) => {
  const [suggestions, setSuggestions] = useState<City[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Fetch cities from API
  const fetchCities = useCallback(
    async (query: string) => {
      if (query.length < minLength) {
        setSuggestions([]);
        setIsOpen(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await apiClient.get<{ cities: City[] }>(
          `/api/cities/search?query=${encodeURIComponent(query)}&limit=${maxResults}`,
        );

        setSuggestions(response.data.cities || []);
        setIsOpen(true);
        setHighlightedIndex(-1);
      } catch (err) {
        logger.error('Error fetching cities');
        const message = err instanceof Error ? err.message : 'Failed to fetch cities';
        setError(message);
        setSuggestions([]);
        setIsOpen(false);
      } finally {
        setLoading(false);
      }
    },
    [minLength, maxResults],
  );

  // Debounced search
  const debouncedFetch = useCallback(
    (query: string) => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }

      debounceRef.current = setTimeout(() => {
        fetchCities(query);
      }, debounceMs);
    },
    [fetchCities, debounceMs],
  );

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    debouncedFetch(newValue);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0) {
          handleCityClick(suggestions[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setHighlightedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  // Handle city selection
  const handleCityClick = (city: City) => {
    logger.debug('City clicked:', city.name);
    onChange(city.name);
    setIsOpen(false);
    setHighlightedIndex(-1);
    setSuggestions([]);
    onCitySelect?.(city);
    inputRef.current?.blur();
  };

  // Handle input focus
  const handleInputFocus = () => {
    if (suggestions.length > 0) {
      setIsOpen(true);
    }
  };

  // Handle click outside
  const handleClickOutside = useCallback((e: MouseEvent) => {
    if (inputRef.current && !inputRef.current.contains(e.target as Node)) {
      // Don't close if clicking on the suggestions list
      if (listRef.current && listRef.current.contains(e.target as Node)) {
        return;
      }
      setIsOpen(false);
      setHighlightedIndex(-1);
    }
  }, []);

  // Set up click outside listener
  useEffect(() => {
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [handleClickOutside]);

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightedIndex >= 0 && listRef.current) {
      const highlightedItem = listRef.current.children[highlightedIndex] as HTMLElement;
      if (highlightedItem) {
        highlightedItem.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightedIndex]);

  // Clean up debounce on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  return (
    <div className={`city-autocomplete ${className}`}>
      <div className="autocomplete-input-wrapper">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleInputFocus}
          placeholder={placeholder}
          disabled={disabled}
          className="autocomplete-input"
          autoComplete="off"
          aria-label="City search"
          aria-haspopup="listbox"
          aria-busy={loading}
        />

        {loading && (
          <div className="autocomplete-spinner" aria-hidden="true">
            <div className="spinner"></div>
          </div>
        )}

        {error && (
          <div className="autocomplete-error" role="alert">
            ⚠️ {error}
          </div>
        )}
      </div>

      {isOpen && suggestions.length > 0 && (
        <ul
          ref={listRef}
          className="autocomplete-suggestions"
          role="listbox"
          aria-label="City suggestions"
        >
          {suggestions.map((city, index) => (
            <li
              key={`${city.name}-${city.country}-${index}`}
              className={`suggestion-item ${index === highlightedIndex ? 'highlighted' : ''}`}
              onClick={(e) => {
                e.stopPropagation();
                handleCityClick(city);
              }}
              role="option"
              aria-selected={index === highlightedIndex}
            >
              <div className="suggestion-main">
                <span className="city-name" style={{ color: '#000000', fontWeight: 'bold' }}>
                  {city.name}
                </span>
                <span className="country-name">{city.country}</span>
              </div>
              {city.coordinates && (
                <div className="suggestion-details">
                  <span className="coordinates">
                    {city.coordinates.lat.toFixed(2)}°, {city.coordinates.lon.toFixed(2)}°
                  </span>
                  {city.population && (
                    <span className="population">{city.population.toLocaleString()}</span>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      {isOpen && !loading && suggestions.length === 0 && value.length >= minLength && (
        <div className="autocomplete-no-results">No cities found for "{value}"</div>
      )}
    </div>
  );
};

export default CityAutocomplete;
