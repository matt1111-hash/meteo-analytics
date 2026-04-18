/**
 * BeaufortLegend - Display the Beaufort wind force scale
 * Shows all 12 levels with colors, names, and speed ranges
 */
import React from 'react';
import { BEAUFORT_LEVELS } from '../../constants/windConstants';
import './BeaufortLegend.css';

interface BeaufortLegendProps {
  /**
   * Show compact version (horizontal, smaller icons)
   */
  compact?: boolean;

  /**
   * Highlight a specific level
   */
  highlightLevel?: number;

  /**
   * Additional CSS class name
   */
  className?: string;
}

const BeaufortLegend: React.FC<BeaufortLegendProps> = ({
  compact = false,
  highlightLevel,
  className = '',
}) => {
  const containerClass = `beaufort-legend ${compact ? 'compact' : ''} ${className}`.trim();

  return (
    <div className={containerClass}>
      <div className="beaufort-legend-title">
        <h4>🌬️ Beaufort Skála</h4>
        {!compact && <span className="beaufort-subtitle">Szélereősség skála (km/h)</span>}
      </div>

      <div className="beaufort-scale">
        {BEAUFORT_LEVELS.map((level) => {
          const isHighlighted = highlightLevel === level.level;
          const itemClass = `beaufort-level ${isHighlighted ? 'highlighted' : ''}`;

          return (
            <div
              key={level.level}
              className={itemClass}
              style={{ '--level-color': level.color } as React.CSSProperties}
              title={`${level.name} (${level.nameHu}): ${level.description}`}
            >
              <div className="beaufort-indicator">
                <span className="beaufort-icon">{level.icon}</span>
                {!compact && <span className="beaufort-level-number">{level.level}</span>}
              </div>

              {!compact ? (
                <div className="beaufort-details">
                  <span className="beaufort-name">{level.nameHu}</span>
                  <span className="beaufort-range">
                    {level.speedRange.min === 0
                      ? `0-${level.speedRange.max}`
                      : `${level.speedRange.min}-${level.speedRange.max}`}
                  </span>
                </div>
              ) : (
                <span className="beaufort-compact-label">{level.level}</span>
              )}
            </div>
          );
        })}
      </div>

      {!compact && (
        <div className="beaufort-footer">
          <small>
            <strong>0</strong>: Szélcsend | <strong>6</strong>: Erős szél | <strong>10</strong>:
            Vihar | <strong>12</strong>: Orkán
          </small>
        </div>
      )}
    </div>
  );
};

export default BeaufortLegend;
