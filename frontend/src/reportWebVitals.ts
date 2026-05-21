import type { MetricType } from 'web-vitals';

type ReportHandler = (metric: MetricType) => void;

const reportWebVitals = (onPerfEntry?: ReportHandler): void => {
  if (typeof onPerfEntry === 'function') {
    import('web-vitals').then(({ onCLS, onFCP, onINP, onLCP, onTTFB }) => {
      onCLS(onPerfEntry);
      onFCP(onPerfEntry);
      onINP(onPerfEntry);
      onLCP(onPerfEntry);
      onTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
