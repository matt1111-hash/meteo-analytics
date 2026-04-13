# mypy: ignore-errors
"""Wind rose plotting."""

from typing import Any

import numpy as np
import pandas as pd
from src.presentation.gui.theme_manager import get_current_colors


def _get_wind_rose_style() -> tuple[list[int], list[str], list[str], Any, list[str], Any]:
    """Return wind rose binning and color configuration."""
    speed_bins = [0, 25, 50, 70, 100, 120, 200]
    speed_labels = ["0-25", "25-50", "50-70", "70-100", "100-120", "120+ km/h"]
    colors = ["#9ca3af", "#34d399", "#fbbf24", "#f97316", "#ef4444", "#dc2626"]
    direction_bins = np.arange(0, 361, 22.5)
    direction_labels = [
        "É",
        "ÉÉK",
        "ÉK",
        "KÉK",
        "K",
        "KDK",
        "DK",
        "DDK",
        "D",
        "DDNy",
        "DNy",
        "NyDNy",
        "Ny",
        "NyÉNy",
        "ÉNy",
        "ÉÉNy",
    ]
    theta = np.linspace(0, 2 * np.pi, len(direction_bins) - 1, endpoint=False)
    return speed_bins, speed_labels, colors, direction_bins, direction_labels, theta


def _build_wind_rose_data(
    df: pd.DataFrame, direction_bins: Any, speed_bins: list[int]
) -> list[list[int]]:
    """Aggregate dataframe into direction/speed bins."""
    wind_rose_data: list[list[int]] = []
    for index in range(len(direction_bins) - 1):
        direction_winds = df[
            (df["winddirection"] >= direction_bins[index])
            & (df["winddirection"] < direction_bins[index + 1])
        ]["windspeed"]
        if len(direction_winds) == 0:
            wind_rose_data.append([0] * len(speed_bins))
            continue
        speed_counts = [
            len(
                direction_winds[
                    (direction_winds >= speed_bins[bin_index])
                    & (direction_winds < speed_bins[bin_index + 1])
                ]
            )
            for bin_index in range(len(speed_bins) - 1)
        ]
        speed_counts.append(len(direction_winds[direction_winds >= speed_bins[-2]]))
        wind_rose_data.append(speed_counts)
    return wind_rose_data


def _plot_wind_rose_bars(
    ax: Any,
    theta: Any,
    wind_rose_data: list[list[int]],
    colors: list[str],
    speed_labels: list[str],
    border_color: str,
) -> None:
    """Plot stacked polar bars."""
    bottom = np.zeros(len(theta))
    for index, (color, label) in enumerate(zip(colors, speed_labels, strict=False)):
        values = [row[index] for row in wind_rose_data]
        ax.bar(
            theta,
            values,
            width=np.pi / 8,
            bottom=bottom,
            color=color,
            alpha=0.85,
            label=label,
            edgecolor=border_color,
            linewidth=0.5,
        )
        bottom += values


def _build_stats_text(df: pd.DataFrame) -> str:
    """Build summary stats text for wind rose."""
    total_records = len(df)
    avg_speed = df["windspeed"].mean()
    max_speed = df["windspeed"].max()
    data_source = df["_data_source"].iloc[0] if "_data_source" in df.columns else "unknown"
    if data_source == "wind_gusts_max":
        speed_label = "széllökés"
        icon = "🌪️"
    else:
        speed_label = "szélsebesség"
        icon = "💨"

    stats_text = (
        f"📊 Összesen: {total_records} mérés\n"
        f"{icon} Átlag {speed_label}: {avg_speed:.1f} km/h\n"
        f"🚨 Maximum {speed_label}: {max_speed:.1f} km/h\n"
    )
    if max_speed >= 120:
        return stats_text + "⚠️ HURRIKÁN erősségű széllökések!"
    if max_speed >= 100:
        return stats_text + "⚠️ EXTRÉM széllökések detected!"
    if max_speed >= 70:
        return stats_text + "🌪️ Viharos széllökések detected!"
    return stats_text


def plot_wind_rose(
    ax: Any,
    figure: Any,
    chart_title: str,
    df: pd.DataFrame,
    legend_enabled: bool = True,
) -> None:
    """Wind rose diagram megrajzolása."""
    if df.empty:
        plot_wind_rose_placeholder(ax, figure, chart_title)
        return

    ax = figure.add_subplot(111, projection="polar")
    current_colors = get_current_colors()
    text_color = current_colors.get("on_surface", "#1f2937")
    speed_bins, speed_labels, colors, direction_bins, direction_labels, theta = (
        _get_wind_rose_style()
    )
    wind_rose_data = _build_wind_rose_data(df, direction_bins, speed_bins)
    border_color = current_colors.get("border", "#d1d5db")
    _plot_wind_rose_bars(ax, theta, wind_rose_data, colors, speed_labels, border_color)
    ax.set_xticks(theta)
    ax.set_xticklabels(direction_labels[: len(theta)], fontweight="bold", fontsize=11)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    grid_color = current_colors.get("border", "#d1d5db")
    ax.grid(True, alpha=0.3, color=grid_color)
    ax.set_title(chart_title, fontsize=18, fontweight="bold", pad=30, color=text_color)
    ax.tick_params(colors=text_color, labelsize=10)
    for label in ax.get_yticklabels():
        label.set_fontweight("bold")

    # Legend
    if legend_enabled:
        legend = ax.legend(bbox_to_anchor=(1.2, 1), loc="upper left", fontsize=11)
        legend.get_frame().set_facecolor(current_colors.get("surface", "#ffffff"))
        legend.get_frame().set_edgecolor(border_color)
        for text in legend.get_texts():
            text.set_fontweight("bold")

    surface_variant = current_colors.get("surface_variant", "#f9fafb")
    ax.text(
        0.02,
        0.98,
        _build_stats_text(df),
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        verticalalignment="top",
        color=text_color,
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor=surface_variant,
            edgecolor=border_color,
            alpha=0.9,
        ),
    )

    figure.tight_layout()


def plot_wind_rose_placeholder(ax: Any, figure: Any, chart_title: str) -> None:
    """Wind rose placeholder."""
    ax = figure.add_subplot(111)

    current_colors = get_current_colors()
    text_color = current_colors.get("on_surface", "#1f2937")
    surface_color = current_colors.get("surface_variant", "#f9fafb")
    border_color = current_colors.get("border", "#d1d5db")

    placeholder_text = "🌹 Széllökés Rózsadiagram\n\n"
    placeholder_text += "❌ Nincs széllökés/irány adat\n\n"
    placeholder_text += "A diagram megjelenítéséhez szélirány és\n"
    placeholder_text += "széllökés adatok szükségesek:\n"
    placeholder_text += "• wind_gusts_max (elsődleges) VAGY\n"
    placeholder_text += "• windspeed_10m_max (fallback)\n"
    placeholder_text += "• winddirection_10m_dominant\n\n"
    placeholder_text += "🚨 Mock adatok használata TILOS!"

    ax.text(
        0.5,
        0.5,
        placeholder_text,
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        color=text_color,
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor=surface_color,
            edgecolor=border_color,
            alpha=0.8,
        ),
    )

    ax.set_title(chart_title, fontsize=18, fontweight="bold", pad=20, color=text_color)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
