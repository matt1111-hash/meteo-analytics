"""Trend statistics calculation module."""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def calculate_trend_statistics(
    weather_data: List[Dict],
    api_field: str,
    settlement_name: str,
    parameter: str,
    time_range: str,
    years: int,
) -> Optional[Dict]:
    """
    Professional trend calculation from API data.

    Args:
        weather_data: Daily API data list
        api_field: API field name (e.g., "temperature_2m_max")
        settlement_name, parameter, time_range, years: Metadata

    Returns:
        Complete trend results dictionary
    """
    # DataFrame creation
    df_data = []
    for record in weather_data:
        if record.get("date") and record.get(api_field) is not None:
            df_data.append(
                {
                    "date": pd.to_datetime(record["date"]),
                    "value": float(record[api_field]),
                }
            )

    if len(df_data) == 0:
        return None

    df = pd.DataFrame(df_data)
    df = df.sort_values("date")

    # Missing data handling
    len(df)
    df = df.dropna()
    valid_count = len(df)

    if valid_count < 30:
        return None

    # Monthly aggregation
    df["year_month"] = df["date"].dt.to_period("M")
    monthly_df = (
        df.groupby("year_month")
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
    monthly_df = monthly_df[monthly_df["day_count"] >= 5]

    if len(monthly_df) < 6:
        return None

    # Linear regression
    X = np.arange(len(monthly_df)).reshape(-1, 1)
    y = monthly_df["avg_value"].values

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    r2 = r2_score(y, y_pred)

    # Trend per decade
    monthly_trend = model.coef_[0]
    trend_per_decade = monthly_trend * 12 * 10

    # Scipy stats
    try:
        slope, intercept, r_value, p_value, std_err = stats.linregress(X.flatten(), y)
    except ValueError:
        slope = model.coef_[0]
        intercept = model.intercept_
        np.sqrt(r2)
        p_value = 0.5
        std_err = 0.0

    # Confidence interval (95%)
    try:
        n = len(y)
        t_val = stats.t.ppf(0.975, n - 2)
        y_err = np.sqrt(np.sum((y - y_pred) ** 2) / (n - 2))
        conf_interval = (
            t_val
            * y_err
            * np.sqrt(
                1
                + 1 / n
                + (X.flatten() - np.mean(X.flatten())) ** 2
                / np.sum((X.flatten() - np.mean(X.flatten())) ** 2)
            )
        )
        ci_upper = y_pred + conf_interval
        ci_lower = y_pred - conf_interval
    except Exception:
        ci_upper = y_pred + np.std(y) * 0.5
        ci_lower = y_pred - np.std(y) * 0.5

    # Basic statistics
    stats_dict = {
        "mean": float(np.mean(y)),
        "std": float(np.std(y)),
        "min": float(np.min(y)),
        "max": float(np.max(y)),
        "median": float(np.median(y)),
        "count": int(valid_count),
    }

    # Chart data
    try:
        chart_data = {
            "dates": monthly_df["date"].tolist(),
            "values": monthly_df["avg_value"].tolist(),
            "trend_line": y_pred.tolist(),
            "ci_upper": ci_upper.tolist(),
            "ci_lower": ci_lower.tolist(),
            "min_values": monthly_df["min_value"].tolist(),
            "max_values": monthly_df["max_value"].tolist(),
        }
    except Exception:
        chart_data = {
            "dates": list(monthly_df["date"]),
            "values": list(monthly_df["avg_value"]),
            "trend_line": list(y_pred),
            "ci_upper": list(ci_upper),
            "ci_lower": list(ci_lower),
            "min_values": list(monthly_df["min_value"]),
            "max_values": list(monthly_df["max_value"]),
        }

    # Significance assessment
    if p_value < 0.001:
        significance = "Nagyon szignifikáns"
    elif p_value < 0.01:
        significance = "Szignifikáns"
    elif p_value < 0.05:
        significance = "Mérsékelt szignifikáns"
    else:
        significance = "Nem szignifikáns"

    results = {
        "settlement_name": settlement_name,
        "parameter": parameter,
        "time_range": time_range,
        "api_field": api_field,
        "years": years,
        "data_source": weather_data[0].get("data_source", "unknown")
        if weather_data
        else "unknown",
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
        "monthly_points": int(len(monthly_df)),
        "significance": significance,
    }

    return results
