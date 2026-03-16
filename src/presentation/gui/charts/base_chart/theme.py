# mypy: ignore-errors
"""Base chart theme handling."""

from typing import Any

from src.presentation.gui.theme_manager import get_current_colors


def _set_axis_label_colors(ax: Any, text_color: str) -> None:
    """Apply text color to axis labels and title when present."""
    if ax.xaxis.label.get_text():
        ax.xaxis.label.set_color(text_color)
    if ax.yaxis.label.get_text():
        ax.yaxis.label.set_color(text_color)
    if ax.title.get_text():
        ax.title.set_color(text_color)


def _set_spine_colors(ax: Any, border_color: str) -> None:
    """Apply border color to all axis spines."""
    for spine in ax.spines.values():
        spine.set_color(border_color)


def _update_legend_theme(
    ax: Any, current_colors: dict[str, str], border_color: str, text_color: str
) -> None:
    """Apply theme colors to chart legend."""
    legend = ax.get_legend()
    if not legend:
        return
    legend.get_frame().set_facecolor(current_colors.get("surface", "#ffffff"))
    legend.get_frame().set_edgecolor(border_color)
    for text in legend.get_texts():
        text.set_color(text_color)


def _update_line_colors(ax: Any, current_colors: dict[str, str]) -> None:
    """Refresh standard line colors to the current theme."""
    for line in ax.get_lines():
        if line.get_color() in ["#1f77b4", "blue", "b"]:
            line.set_color(current_colors.get("primary", "#C43939"))


def _update_patch_colors(ax: Any, current_colors: dict[str, str]) -> None:
    """Refresh patch colors using preserved semantic categories."""
    for patch in ax.patches:
        if not hasattr(patch, "_original_color_category"):
            continue
        category = patch._original_color_category
        if category in current_colors:
            patch.set_facecolor(current_colors[category])


def _update_text_colors(ax: Any, text_color: str) -> None:
    """Refresh free text elements on the axis."""
    for text in ax.texts:
        text.set_color(text_color)


def apply_theme_to_axis(ax: Any, theme_manager: Any, grid_enabled: bool = True) -> None:
    """Apply theme colors to a matplotlib axis."""
    current_colors = get_current_colors()
    text_color = current_colors.get("on_surface", "#1f2937")
    border_color = current_colors.get("border", "#d1d5db")

    ax.set_facecolor(current_colors.get("surface", "#ffffff"))
    ax.tick_params(colors=text_color, which="both")
    _set_axis_label_colors(ax, text_color)
    _set_spine_colors(ax, border_color)

    if grid_enabled:
        grid_alpha = 0.3 if theme_manager.get_current_theme() == "light" else 0.2
        ax.grid(True, alpha=grid_alpha, color=border_color)
    _update_legend_theme(ax, current_colors, border_color, text_color)


def update_chart_colors(ax: Any, current_colors: dict) -> None:
    """Update all chart elements with new theme colors."""
    text_color = current_colors.get("on_surface", "#1f2937")
    border_color = current_colors.get("border", "#d1d5db")
    _update_line_colors(ax, current_colors)
    _update_patch_colors(ax, current_colors)
    _update_text_colors(ax, text_color)
    _set_spine_colors(ax, border_color)
