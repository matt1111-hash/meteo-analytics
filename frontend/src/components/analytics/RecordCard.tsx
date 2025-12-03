import React from 'react';
import './RecordCard.css';

interface RecordCardProps {
  icon: string;
  title: string;
  value: string | number;
  date?: string;
  unit?: string;
  className?: string;
}

const RecordCard: React.FC<RecordCardProps> = ({
  icon,
  title,
  value,
  date,
  unit,
  className = ''
}) => {
  const displayValue = typeof value === 'number' ? value.toFixed(1) : value;

  return (
    <div className={`record-card ${className}`}>
      <div className="record-icon">{icon}</div>
      <div className="record-content">
        <h4 className="record-title">{title}</h4>
        <div className="record-value">
          <span className="value-number">{displayValue}</span>
          {unit && <span className="value-unit">{unit}</span>}
        </div>
        {date && (
          <div className="record-date">
            📅 {date}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecordCard;