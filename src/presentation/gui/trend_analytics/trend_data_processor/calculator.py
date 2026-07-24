# mypy: ignore-errors
"""Trend statistics calculation module."""

import numpy as np
import pandas as pd
from scipy import stats


def _build_dataframe(weather_data: list[dict], api_field: str) -> pd.DataFrame | None:
    """Build a clean dataframe from weather API records."""
    df_data = [
        {
            "date": pd.to_datetime(record["date"]),
            "value": float(record[api_field]),
        }
        for record in weather_data
        if record.get("date") and record.get(api_field) is not None
    ]
    if not df_data:
        return None
    df = pd.DataFrame(df_data).sort_values("date")
    df = df.dropna()
    if len(df) < 30:  # noqa: PLR2004
        return None
    return df


def _build_monthly_dataframe(df: pd.DataFrame) -> pd.DataFrame | None:
    """Aggregate daily values to monthly statistics."""
    monthly_df = (
        df.assign(year_month=df["date"].dt.to_period("M"))
        .groupby("year_month")
        .agg({"value": ["mean", "min", "max", "count"], "date": "first"})
        .reset_index()
    )
    monthly_df.columns = [
        "year_month",
        "avg_value",
        "min_value",
        "max_value",
        "day_count",
        "date",
    ]
    monthly_df = monthly_df[monthly_df["day_count"] >= 5]  # noqa: PLR2004
    if len(monthly_df) < 6:  # noqa: PLR2004
        return None
    return monthly_df


def _calculate_regression(
    monthly_df: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, float, float, float, float, float, float]:
    """Calculate linear regression values for the monthly series (scipy-only).

    A single ``stats.linregress`` call yields slope, intercept, r, p and std_err;
    ``r_squared`` is ``r_value ** 2`` (identical to ``sklearn`` r2_score for
    ordinary least squares), removing the heavy scikit-learn dependency.
    Returns (x_values, y_values, slope, intercept, r2, trend_per_decade,
    p_value, std_err).
    """
    x_values = np.arange(len(monthly_df)).reshape(-1, 1)
    y_values = monthly_df["avg_value"].values
    try:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_values.flatten(), y_values)
        r2 = float(r_value) ** 2
    except ValueError:
        # Degenerate input (e.g. <2 points or constant x): safe fallback.
        slope = 0.0
        intercept = float(np.mean(y_values)) if len(y_values) else 0.0
        r2 = 0.0
        p_value = 0.5
        std_err = 0.0
    if not np.isfinite(r2):
        r2 = 0.0
    trend_per_decade = float(slope) * 12 * 10
    return (
        x_values,
        y_values,
        float(slope),
        float(intercept),
        r2,
        trend_per_decade,
        float(p_value),
        float(std_err),
    )


def _calculate_confidence_bounds(
    y_values: np.ndarray, y_pred: np.ndarray, x_values: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate 95% confidence bounds for the regression line."""
    try:
        n_values = len(y_values)
        t_value = stats.t.ppf(0.975, n_values - 2)
        y_error = np.sqrt(np.sum((y_values - y_pred) ** 2) / (n_values - 2))
        x_flat = x_values.flatten()
        conf_interval = (
            t_value
            * y_error
            * np.sqrt(
                1
                + 1 / n_values
                + (x_flat - np.mean(x_flat)) ** 2 / np.sum((x_flat - np.mean(x_flat)) ** 2)
            )
        )
        return y_pred - conf_interval, y_pred + conf_interval
    except Exception:
        fallback = np.std(y_values) * 0.5
        return y_pred - fallback, y_pred + fallback


def _build_chart_data(
    monthly_df: pd.DataFrame,
    y_pred: np.ndarray,
    ci_lower: np.ndarray,
    ci_upper: np.ndarray,
) -> dict[str, list]:
    """Build chart series in a list-safe format."""
    return {
        "dates": monthly_df["date"].tolist(),
        "values": monthly_df["avg_value"].tolist(),
        "trend_line": y_pred.tolist(),
        "ci_upper": ci_upper.tolist(),
        "ci_lower": ci_lower.tolist(),
        "min_values": monthly_df["min_value"].tolist(),
        "max_values": monthly_df["max_value"].tolist(),
    }


def _resolve_significance_label(p_value: float) -> str:
    """Resolve localized significance label."""
    if p_value < 0.001:  # noqa: PLR2004
        return "Nagyon szignifikáns"
    if p_value < 0.01:  # noqa: PLR2004
        return "Szignifikáns"
    if p_value < 0.05:  # noqa: PLR2004
        return "Mérsékelt szignifikáns"
    return "Nem szignifikáns"


def calculate_trend_statistics(
    weather_data: list[dict],
    api_field: str,
    settlement_name: str,
    parameter: str,
    time_range: str,
    years: int,
) -> dict | None:
    """
    Professional trend calculation from API data.

    Args:
        weather_data: Daily API data list
        api_field: API field name (e.g., "temperature_2m_max")
        settlement_name, parameter, time_range, years: Metadata

    Returns:
        Complete trend results dictionary
    """
    df = _build_dataframe(weather_data, api_field)
    if df is None:
        return None
    valid_count = len(df)
    monthly_df = _build_monthly_dataframe(df)
    if monthly_df is None:
        return None

    (
        x_values,
        y_values,
        slope,
        intercept,
        r2,
        trend_per_decade,
        p_value,
        std_err,
    ) = _calculate_regression(monthly_df)
    y_pred = slope * x_values.flatten() + intercept
    ci_lower, ci_upper = _calculate_confidence_bounds(y_values, y_pred, x_values)

    stats_dict = {
        "mean": float(np.mean(y_values)),
        "std": float(np.std(y_values)),
        "min": float(np.min(y_values)),
        "max": float(np.max(y_values)),
        "median": float(np.median(y_values)),
        "count": int(valid_count),
    }
    chart_data = _build_chart_data(monthly_df, y_pred, ci_lower, ci_upper)
    significance = _resolve_significance_label(p_value)

    results = {
        "settlement_name": settlement_name,
        "parameter": parameter,
        "time_range": time_range,
        "api_field": api_field,
        "years": years,
        "data_source": weather_data[0].get("data_source", "unknown") if weather_data else "unknown",
        "r_squared": float(r2),
        "trend_per_decade": float(trend_per_decade),
        "p_value": float(p_value),
        "slope": float(slope),
        "intercept": float(intercept),
        "std_error": float(std_err),
        "statistics": stats_dict,
        "chart_data": chart_data,
        "start_date": df["date"].min().strftime("%Y-%m-%d"),
        "end_date": df["date"].max().strftime("%Y-%m-%d"),
        "total_days": int(valid_count),
        "monthly_points": len(monthly_df),
        "significance": significance,
    }

    return results
