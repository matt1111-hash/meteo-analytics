"""Base chart theme handling."""

from typing import Any

from src.presentation.gui.theme_manager import get_current_colors


def apply_theme_to_axis(ax: Any, theme_manager: Any, grid_enabled: bool = True) -> None:
    """Apply theme colors to a matplotlib axis."""
    current_colors = get_current_colors()
    text_color = current_colors.get("on_surface", "#1f2937")
    border_color = current_colors.get("border", "#d1d5db")

    ax.set_facecolor(current_colors.get("surface", "#ffffff"))
    ax.tick_params(colors=text_color, which="both")

    if ax.xaxis.label.get_text():
        ax.xaxis.label.set_color(text_color)
    if ax.yaxis.label.get_text():
        ax.yaxis.label.set_color(text_color)
    if ax.title.get_text():
        ax.title.set_color(text_color)

    for spine in ax.spines.values():
        spine.set_color(border_color)

    if grid_enabled:
        grid_alpha = 0.3 if theme_manager.get_current_theme() == "light" else 0.2
        ax.grid(True, alpha=grid_alpha, color=border_color)

    legend = ax.get_legend()
    if legend:
        legend.get_frame().set_facecolor(current_colors.get("surface", "#ffffff"))
        legend.get_frame().set_edgecolor(border_color)
        for text in legend.get_texts():
            text.set_color(text_color)


def update_chart_colors(ax: Any, current_colors: dict) -> None:
    """Update all chart elements with new theme colors."""
    text_color = current_colors.get("on_surface", "#1f2937")
    border_color = current_colors.get("border", "#d1d5db")

    # Update lines
    for line in ax.get_lines():
        current_color = line.get_color()
        if current_color in ["#1f77b4", "blue", "b"]:
            line.set_color(current_colors.get("primary", "#C43939"))

    # Update bar patches
    for patch in ax.patches:
        if hasattr(patch, "_original_color_category"):
            category = patch._original_color_category
            if category in current_colors:
                patch.set_facecolor(current_colors[category])

    # Update text elements
    for text in ax.texts:
        text.set_color(text_color)

    # Update spines
    for spine in ax.spines.values():
        spine.set_color(border_color)
