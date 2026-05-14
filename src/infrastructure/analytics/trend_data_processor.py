"""Trend data processor for DataFrame preparation and aggregation."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class TrendDataProcessor:
    """Data preparation and aggregation for trend analysis."""

    # Minimum data requirements
    MIN_DAYS_PER_MONTH = 5

    def prepare_dataframe(
        self, weather_data: list[dict[str, Any]], api_field: str
    ) -> pd.DataFrame | None:
        """Prepare DataFrame from raw weather data."""
        df_data = []
        for record in weather_data:
            if record.get("date") and record.get(api_field) is not None:
                try:
                    df_data.append(
                        {
                            "date": pd.to_datetime(record["date"]),
                            "value": float(record[api_field]),
                        }
                    )
                except (ValueError, TypeError):
                    continue

        if not df_data:
            return None

        df = pd.DataFrame(df_data)
        df = df.sort_values("date")
        df = df.dropna()

        return df

    def aggregate_monthly(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """Aggregate data to monthly level."""
        df = df.copy()
        df["year_month"] = df["date"].dt.to_period("M")

        monthly_df = (
            df.groupby("year_month")
            .agg(
                {
                    "value": ["mean", "min", "max", "count"],
                    "date": "first",
                }
            )
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

        # Filter months with insufficient data
        monthly_df = monthly_df[monthly_df["day_count"] >= self.MIN_DAYS_PER_MONTH]

        if len(monthly_df) < 6:  # noqa: PLR2004
            return None

        return monthly_df

    def extract_years(self, monthly_df: pd.DataFrame) -> list[int]:
        """Extract unique years from monthly data."""
        return sorted(monthly_df["date"].dt.year.unique().tolist())

    def calculate_yearly_means(self, monthly_df: pd.DataFrame) -> list[float]:
        """Calculate mean values per year."""
        yearly = monthly_df.groupby(monthly_df["date"].dt.year)["avg_value"].mean()
        return yearly.tolist()

    def calculate_yearly_dates(self, monthly_df: pd.DataFrame) -> list[str]:
        """Calculate representative dates per year."""
        yearly_dates = monthly_df.groupby(monthly_df["date"].dt.year)["date"].first()
        return [d.strftime("%Y-%m-%d") for d in yearly_dates]


__all__ = ["TrendDataProcessor"]
