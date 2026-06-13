"""定义看盘页共用的暗色主题令牌与布局样式助手。

本模块负责：
1. 集中定义交易工作区使用的背景、面板、边框、强调色与状态色；
2. 为页面骨架、命令条、摘要栏和 diagnostics 区提供可复用样式；
3. 降低样式散落在组件树中的重复与回归风险。
"""

from __future__ import annotations

import reflex as rx


TRADING_COLORS = {
    "bg": "#05070b",
    "bg_canvas": "radial-gradient(circle at top left, rgba(31, 111, 235, 0.18), transparent 28%), radial-gradient(circle at top right, rgba(249, 115, 22, 0.12), transparent 24%), linear-gradient(180deg, #05070b 0%, #0a0f16 52%, #0e1521 100%)",
    "surface": "rgba(10, 15, 22, 0.94)",
    "surface_strong": "rgba(15, 22, 34, 0.98)",
    "surface_soft": "rgba(18, 26, 40, 0.78)",
    "border": "rgba(120, 144, 172, 0.28)",
    "border_strong": "rgba(151, 176, 203, 0.36)",
    "text": "#f3f7fb",
    "text_soft": "#9fb2c8",
    "text_muted": "#72849a",
    "accent": "#f68b2c",
    "accent_soft": "rgba(246, 139, 44, 0.16)",
    "bull": "#31c48d",
    "bear": "#ff6b57",
    "info": "#49a7ff",
    "warning": "#f4b740",
}

TRADING_SHADOW = "0 18px 48px rgba(0, 0, 0, 0.38)"
TRADING_RADIUS = "22px"
TRADING_GAP = "1.25rem"


def shell_box_style() -> dict[str, str]:
    """返回页面外层画布样式。"""

    return {
        "width": "100%",
        "min_height": "100vh",
        "background": TRADING_COLORS["bg_canvas"],
        "color": TRADING_COLORS["text"],
    }


def workspace_container_style() -> dict[str, str]:
    """返回页面主容器样式。"""

    return {
        "width": "100%",
        "max_width": "1480px",
        "margin": "0 auto",
        "padding": "1.25rem 1rem 2.5rem",
    }


def glass_panel_style() -> dict[str, str]:
    """返回暗色面板基础样式。"""

    return {
        "background": TRADING_COLORS["surface"],
        "border": f"1px solid {TRADING_COLORS['border']}",
        "border_radius": TRADING_RADIUS,
        "box_shadow": TRADING_SHADOW,
        "backdrop_filter": "blur(18px)",
    }


def top_bar_style() -> dict[str, str]:
    """返回顶部命令条样式。"""

    style = glass_panel_style()
    style.update(
        {
            "padding": "1rem 1.15rem",
            "position": "sticky",
            "top": "0.75rem",
            "z_index": "20",
            "background": "rgba(8, 12, 18, 0.88)",
        }
    )
    return style


def hero_panel_style() -> dict[str, str]:
    """返回主图工作区面板样式。"""

    style = glass_panel_style()
    style.update(
        {
            "padding": "1.2rem",
            "background": "linear-gradient(180deg, rgba(12, 18, 28, 0.98) 0%, rgba(8, 12, 19, 0.98) 100%)",
        }
    )
    return style


def summary_panel_style() -> dict[str, str]:
    """返回右侧摘要栏样式。"""

    style = glass_panel_style()
    style.update(
        {
            "padding": "1rem",
            "background": "linear-gradient(180deg, rgba(14, 20, 31, 0.96) 0%, rgba(10, 15, 24, 0.98) 100%)",
            "height": "100%",
        }
    )
    return style


def diagnostics_panel_style() -> dict[str, str]:
    """返回 diagnostics 区样式。"""

    style = glass_panel_style()
    style.update(
        {
            "padding": "0.9rem 1rem",
            "background": "rgba(8, 12, 18, 0.76)",
        }
    )
    return style


def metric_row_style() -> dict[str, str]:
    """返回摘要指标行样式。"""

    return {
        "padding": "0.72rem 0.82rem",
        "border": f"1px solid {TRADING_COLORS['border']}",
        "border_radius": "14px",
        "background": "rgba(12, 18, 27, 0.74)",
    }


def subtle_code_style() -> dict[str, str]:
    """返回 diagnostics 代码块样式。"""

    return {
        "width": "100%",
        "display": "block",
        "padding": "0.7rem 0.82rem",
        "border_radius": "12px",
        "background": "rgba(5, 9, 14, 0.92)",
        "border": f"1px solid {TRADING_COLORS['border']}",
        "color": TRADING_COLORS["text_soft"],
        "font_size": "0.78rem",
        "white_space": "pre-wrap",
        "overflow_wrap": "anywhere",
    }


def command_select_style() -> dict[str, str]:
    """返回顶部选择器样式。"""

    return {
        "width": "100%",
        "min_width": "0",
        "background": "rgba(5, 9, 14, 0.88)",
        "border": f"1px solid {TRADING_COLORS['border']}",
        "border_radius": "14px",
        "color": TRADING_COLORS["text"],
    }


def muted_text_style() -> dict[str, str]:
    """返回次级文字样式。"""

    return {
        "color": TRADING_COLORS["text_soft"],
    }


def eyebrow_badge(text: str, *, color: str | None = None, background: str | None = None) -> rx.Component:
    """构造统一风格的小型状态徽标。"""

    return rx.badge(
        text,
        variant="soft",
        radius="full",
        style={
            "background": background or TRADING_COLORS["accent_soft"],
            "color": color or TRADING_COLORS["accent"],
            "border": f"1px solid {TRADING_COLORS['border']}",
            "padding": "0.25rem 0.55rem",
            "letter_spacing": "0.04em",
        },
    )