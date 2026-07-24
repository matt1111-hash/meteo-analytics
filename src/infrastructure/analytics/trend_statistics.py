"""Trend statistics calculator for linear regression analysis."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class TrendStatisticsCalculator:
    """Linear regression and confidence interval calculations."""

    def calculate_linear_regression(self, monthly_df: pd.DataFrame) -> dict[str, Any] | None:
        """Calculate linear regression statistics.

        Uses ``scipy.stats.linregress`` as the single source of truth for slope,
        intercept, r, p and std_err; ``r_squared`` is ``r_value ** 2`` (numerically
        identical to ``sklearn.metrics.r2_score`` for ordinary least squares, which
        the heavy scikit-learn dependency was previously pulled in to compute).
        """
        X = np.arange(len(monthly_df)).reshape(-1, 1)
        y = monthly_df["avg_value"].values
        x_flat = X.flatten()

        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_flat, y)
            r2 = float(r_value) ** 2
        except ValueError:
            # Degenerate input (e.g. <2 points or constant x): safe fallback.
            slope = 0.0
            intercept = float(np.mean(y)) if len(y) else 0.0
            r2 = 0.0
            p_value = 0.5
            std_err = 0.0

        # Guard against NaN r_squared from edge-case inputs (e.g. constant y).
        if not np.isfinite(r2):
            r2 = 0.0

        # Predicted values for the confidence-interval calculation.
        y_pred = intercept + slope * x_flat

        # Confidence interval (95%)
        confidence_interval = self._calculate_confidence_interval(X, y, y_pred)

        # Slope per decade (12 months per year, 10 years per decade)
        slope_per_decade = float(slope * 12 * 10)

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r2,
            "p_value": p_value,
            "std_error": std_err,
            "slope_per_decade": slope_per_decade,
            "confidence_interval": confidence_interval,
        }

    def _calculate_confidence_interval(
        self, X: np.ndarray, y: np.ndarray, y_pred: np.ndarray
    ) -> tuple[float, float]:
        """Calculate 95% confidence interval for the slope."""
        try:
            n = len(y)
            t_val = stats.t.ppf(0.975, n - 2)
            y_err = np.sqrt(np.sum((y - y_pred) ** 2) / (n - 2))

            x_mean = np.mean(X.flatten())
            x_sum_sq = np.sum((X.flatten() - x_mean) ** 2)

            # Standard error of prediction
            se_pred = y_err * np.sqrt(1 + 1 / n + (X.flatten() - x_mean) ** 2 / x_sum_sq)

            # Use the mean confidence interval width
            ci_mean = np.mean(se_pred) * t_val

            return (-ci_mean, ci_mean)

        except Exception:
            # Fallback: use standard deviation
            return (-np.std(y) * 0.5, np.std(y) * 0.5)


__all__ = ["TrendStatisticsCalculator"]
