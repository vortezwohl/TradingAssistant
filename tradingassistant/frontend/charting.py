"""前端图表模块兼容重导出层。

本文件从四个子模块（models、studies、renders、utils）重导出所有公开符号，
保持 `app.py` 和 `state.py` 中的现有引用路径不变。
"""

__all__ = [
    "CHART_POINT_COUNT", "DEFAULT_WATCHLIST", "DEPTH_MODE_OPTIONS",
    "MACRO_STRIP", "MOVERS_TABS", "OVERLAY_OPTIONS", "PRIMARY_CHART_HEIGHT",
    "PRIMARY_CHART_WIDTH", "RAIL_TABS", "ROUTE_DESCRIPTIONS", "ROUTE_OPTIONS",
    "SCALE_OPTIONS", "STUDY_CHART_HEIGHT", "STUDY_CHART_WIDTH",
    "SYMBOL_PROFILES", "TONE_COLORS", "UNIVERSE_CODES",
    "build_analysis_cards", "build_chart_hover_details",
    "build_chart_hover_overlay_rows", "build_chart_legend",
    "build_depth_rows", "build_instrument_metrics", "build_market_model",
    "build_movers_rows", "build_news_rows", "build_order_book_rows",
    "build_primary_chart_svg", "build_quote_strip", "build_route_studies",
    "build_signal_rows", "build_snapshot_cells", "build_tape_rows",
    "build_watchlist_rows", "compact_volume", "format_number",
    "format_signed", "get_symbol_profile", "normalize_code",
    "tone_from_number",
]

from .models import (  # noqa: E402, F401
    CHART_POINT_COUNT,
    DEFAULT_WATCHLIST,
    DEPTH_MODE_OPTIONS,
    MACRO_STRIP,
    MOVERS_TABS,
    OVERLAY_OPTIONS,
    PRIMARY_CHART_HEIGHT,
    PRIMARY_CHART_WIDTH,
    RAIL_TABS,
    ROUTE_DESCRIPTIONS,
    ROUTE_OPTIONS,
    SCALE_OPTIONS,
    STUDY_CHART_HEIGHT,
    STUDY_CHART_WIDTH,
    SYMBOL_PROFILES,
    TONE_COLORS,
    UNIVERSE_CODES,
    build_instrument_metrics,
    build_market_model,
    build_movers_rows,
    build_quote_strip,
    build_snapshot_cells,
    build_watchlist_rows,
    get_symbol_profile,
)
from .renders import (  # noqa: E402, F401
    build_chart_hover_details,
    build_chart_hover_overlay_rows,
    build_chart_legend,
    build_depth_rows,
    build_order_book_rows,
    build_primary_chart_svg,
)
from .studies import (  # noqa: E402, F401
    build_analysis_cards,
    build_route_studies,
)
from .utils import (  # noqa: E402, F401
    build_news_rows,
    build_signal_rows,
    build_tape_rows,
    compact_volume,
    format_number,
    format_signed,
    normalize_code,
    tone_from_number,
)
