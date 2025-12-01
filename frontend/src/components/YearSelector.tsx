import React from 'react';

interface YearSelectorProps {
  selectedYears: number[];
  onYearsChange: (years: number[]) => void;
  disabled?: boolean;
  minYear?: number;
  maxYear?: number;
}

const YearSelector: React.FC<YearSelectorProps> = ({
  selectedYears,
  onYearsChange,
  disabled = false,
  minYear = 2018,
  maxYear = 2025,
}) => {
  const availableYears = Array.from(
    { length: maxYear - minYear + 1 },
    (_, i) => minYear + i
  );

  const handleYearToggle = (year: number) => {
    const newYears = selectedYears.includes(year)
      ? selectedYears.filter(y => y !== year)
      : [...selectedYears, year].sort();

    onYearsChange(newYears);
  };

  const handleSelectAll = () => {
    if (selectedYears.length === availableYears.length) {
      onYearsChange([]);
    } else {
      onYearsChange([...availableYears]);
    }
  };

  const handleSelectRecent = () => {
    const recent = availableYears.slice(-3); // Last 3 years
    onYearsChange(recent);
  };

  return (
    <div className="year-selector">
      <div className="year-selector-header">
        <label className="year-selector-label">
          Select Years ({selectedYears.length} selected)
        </label>
        <div className="year-selector-actions">
          <button
            type="button"
            className="year-action-btn"
            onClick={handleSelectRecent}
            disabled={disabled}
          >
            Recent 3
          </button>
          <button
            type="button"
            className="year-action-btn"
            onClick={handleSelectAll}
            disabled={disabled}
          >
            {selectedYears.length === availableYears.length ? 'Clear All' : 'Select All'}
          </button>
        </div>
      </div>

      <div className="year-options">
        {availableYears.map((year) => (
          <label
            key={year}
            className={`year-option ${selectedYears.includes(year) ? 'selected' : ''}`}
          >
            <input
              type="checkbox"
              checked={selectedYears.includes(year)}
              onChange={() => handleYearToggle(year)}
              disabled={disabled}
              className="year-checkbox"
            />
            <span className="year-label">{year}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default YearSelector;