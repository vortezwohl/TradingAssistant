"""Theme tokens and style helpers for the native terminal workspace."""

from __future__ import annotations

TRADING_COLORS = {
    "bg": "#030508",
    "surface": "#070b0f",
    "surface_alt": "#0b1117",
    "surface_panel": "#0f161d",
    "surface_panel_alt": "#121b24",
    "surface_panel_strong": "#091017",
    "line": "#17212b",
    "line_strong": "#22303d",
    "text": "#e2e8ef",
    "text_soft": "#9da9b5",
    "text_dim": "#65707c",
    "amber": "#ffb347",
    "blue": "#6aa7ff",
    "cyan": "#6fd4e6",
    "green": "#42d48f",
    "red": "#ff6f61",
    "yellow": "#d7dd63",
}

TRADING_FONTS = {
    "sans": '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
    "mono": '"Consolas", "SFMono-Regular", "Courier New", monospace',
}


def shell_style() -> dict[str, str]:
    """Return the fixed full-screen page shell."""

    return {
        "width": "100%",
        "height": "100vh",
        "overflow": "hidden",
        "background": TRADING_COLORS["bg"],
        "color": TRADING_COLORS["text"],
        "font_family": TRADING_FONTS["sans"],
    }



def terminal_bar_style() -> dict[str, str]:
    """Return the compact terminal top bar grid."""

    return {
        "display": "grid",
        "grid_template_columns": "270px minmax(0, 1fr) 470px",
        "height": "48px",
        "border_bottom": f"1px solid {TRADING_COLORS['line_strong']}",
        "background": TRADING_COLORS["surface"],
        "overflow": "hidden",
    }



def terminal_bar_block_style(*, border_right: bool = True, justify_end: bool = False) -> dict[str, str]:
    """Return one top-bar block style."""

    return {
        "display": "flex",
        "align_items": "center",
        "justify_content": "flex-end" if justify_end else "flex-start",
        "gap": "14px",
        "min_width": "0",
        "padding": "0 14px",
        "border_right": f"1px solid {TRADING_COLORS['line']}" if border_right else "0",
    }



def workspace_style() -> dict[str, str]:
    """Return the three-column desktop terminal grid."""

    return {
        "display": "grid",
        "grid_template_columns": "260px minmax(0, 1fr) 360px",
        "height": "calc(100vh - 48px)",
        "min_height": "0",
        "overflow": "hidden",
        "min_width": "1280px",
    }



def column_style(*, rows: str, background: str, border_right: bool = True) -> dict[str, str]:
    """Return a terminal column style."""

    return {
        "display": "grid",
        "grid_template_rows": rows,
        "min_height": "0",
        "background": background,
        "border_right": f"1px solid {TRADING_COLORS['line']}" if border_right else "0",
        "overflow": "hidden",
    }



def panel_style(*, rows: str = "36px minmax(0, 1fr)", background: str | None = None, border_bottom: bool = True) -> dict[str, str]:
    """Return the base terminal panel style."""

    return {
        "display": "grid",
        "grid_template_rows": rows,
        "min_height": "0",
        "background": background or TRADING_COLORS["surface_alt"],
        "border_bottom": f"1px solid {TRADING_COLORS['line']}" if border_bottom else "0",
        "overflow": "hidden",
    }



def panel_head_style() -> dict[str, str]:
    """Return the panel title bar style."""

    return {
        "display": "flex",
        "align_items": "center",
        "justify_content": "space-between",
        "gap": "12px",
        "padding": "0 10px 0 12px",
        "border_bottom": f"1px solid {TRADING_COLORS['line']}",
        "background": TRADING_COLORS["surface"],
        "font_size": "10px",
        "color": TRADING_COLORS["text_dim"],
        "text_transform": "uppercase",
        "letter_spacing": "0.1em",
        "min_height": "36px",
    }



def scroll_region_style(*, padding: str = "0") -> dict[str, str]:
    """Return the local-scroll region style."""

    return {
        "min_height": "0",
        "height": "100%",
        "overflow_y": "auto",
        "overflow_x": "hidden",
        "padding": padding,
        "scrollbar_width": "thin",
        "scrollbar_color": f"{TRADING_COLORS['line_strong']} {TRADING_COLORS['surface_alt']}",
    }



def terminal_button_style(*, tone: str = "amber", height: str = "26px", padding: str = "0 9px") -> dict[str, str]:
    """Return the compact terminal button base style."""

    return {
        "height": height,
        "padding": padding,
        "border": f"1px solid {TRADING_COLORS['line']}",
        "background": TRADING_COLORS["surface_panel"],
        "color": TRADING_COLORS[tone],
        "text_transform": "uppercase",
        "letter_spacing": "0.06em",
        "font_size": "10px",
        "font_family": TRADING_FONTS["mono"],
        "white_space": "nowrap",
        "flex": "0 0 auto",
        "border_radius": "0",
    }



def input_style() -> dict[str, str]:
    """Return the code-entry input style."""

    return {
        "height": "30px",
        "border": f"1px solid {TRADING_COLORS['line_strong']}",
        "background": TRADING_COLORS["bg"],
        "padding": "0 9px",
        "color": TRADING_COLORS["text"],
        "font_family": TRADING_FONTS["mono"],
        "font_size": "12px",
        "border_radius": "0",
    }



def compact_label_style() -> dict[str, str]:
    """Return dense uppercase label styling."""

    return {
        "font_size": "10px",
        "color": TRADING_COLORS["text_dim"],
        "text_transform": "uppercase",
        "letter_spacing": "0.08em",
    }



def mono_value_style(*, color: str = TRADING_COLORS["text"], size: str = "12px", weight: str = "700") -> dict[str, str]:
    """Return terminal numeric typography styling."""

    return {
        "font_family": TRADING_FONTS["mono"],
        "font_size": size,
        "font_weight": weight,
        "color": color,
        "white_space": "nowrap",
    }
