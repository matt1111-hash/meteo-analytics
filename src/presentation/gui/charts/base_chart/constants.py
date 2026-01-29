"""Chart constants and configuration."""
import matplotlib

# Matplotlib backend configuration
MATPLOTLIB_BACKEND = 'QtAgg'

# Default figure settings
DEFAULT_FIGSIZE = (12, 8)
DEFAULT_DPI = 100

# Emoji font fallbacks
EMOJI_FONT_FALLBACKS = [
    'Segoe UI Emoji',
    'Apple Color Emoji',
    'Noto Color Emoji',
    'Noto Emoji',
    'Symbola',
    'DejaVu Sans',
    'sans-serif'
]

# Matplotlib default parameters
MATPLOTLIB_PARAMS = {
    'font.family': EMOJI_FONT_FALLBACKS,
    'font.sans-serif': EMOJI_FONT_FALLBACKS,
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 12,
    'figure.titlesize': 18,
    'lines.linewidth': 2.5,
    'axes.linewidth': 1.2,
    'grid.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.unicode_minus': False,
    'font.stretch': 'normal',
    'font.weight': 'normal'
}

# Chart default settings
CHART_DEFAULTS = {
    'chart_title': "",
    'x_label': "Dátum",
    'y_label': "",
    'grid_enabled': True,
    'legend_enabled': True
}

# Default export settings
EXPORT_DEFAULTS = {
    'format': 'png',
    'dpi': 300
}
