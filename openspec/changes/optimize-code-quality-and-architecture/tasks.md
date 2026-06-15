## 1. Ruff 配置与自动修复

- [x] 1.1 在 `pyproject.toml` 末尾追加 `[tool.ruff.lint]` 配置节，启用 E/W/F/I/N/B/SIM/C/PL 规则，忽略 D400/D415/RUF002
- [x] 1.2 执行 `ruff check --select I --fix` 修复 7 个文件的 import 排序问题
- [x] 1.3 执行 `ruff check --select E302 --fix` 修复 `frontend/app.py` 中 8 处多余空行
- [x] 1.4 执行 `ruff check --select D202 --fix` 修复所有文件的 docstring 后空行问题
- [x] 1.5 验证：`ruff check .` 确认零错误

## 2. 精确手动修复

- [x] 2.1 清理 `tradingassistant/charting/aggregator.py` 导入：移除 `timedelta`、`Any`、`KlineEvent`、`BarRecord`；将 `QuoteEvent`/`TickEvent` 移至 `TYPE_CHECKING`
- [x] 2.2 为 `tradingassistant/frontend/charting.py` 中 12 处 `zip()` 调用添加 `strict=True`
- [x] 2.3 验证：`ruff check --select F401,B905 .` 确认零错误

## 3. Transport 层路由拆分

- [x] 3.1 创建 `tradingassistant/transport/ws_helpers.py`，提取 `_subscribe_topic`、`_unsubscribe_topic`、`_cleanup_connection`、`_make_sender_callback`、`_subscription_ack` 五个函数
- [x] 3.2 创建 `tradingassistant/transport/ws_chart.py`，提取 `chart_stream` WebSocket 端点
- [x] 3.3 创建 `tradingassistant/transport/ws_quote.py`，提取 `quote_stream` WebSocket 端点
- [x] 3.4 创建 `tradingassistant/transport/ws_alert.py`，提取 `alert_stream` WebSocket 端点
- [x] 3.5 重构 `create_app` 函数，从新模块导入并挂载路由，删去嵌套函数定义
- [x] 3.6 验证：`ruff check --select C901,PLR0915 tradingassistant/transport/` 确认零错误
- [x] 3.7 验证：`pytest tests/test_transport.py -v` 全绿

## 4. Frontend 层 charting.py 拆分

- [x] 4.1 创建 `tradingassistant/frontend/utils.py`：提取 12 个工具函数（`format_number`、`format_signed`、`compact_volume`、`tone_from_number`、`normalize_code`、`_seed_from_key`、`_scale_amplitude`、`_clamp_chart_index`、`_format_study_value`、`build_tape_rows`、`build_signal_rows`、`build_news_rows`）
- [x] 4.2 创建 `tradingassistant/frontend/models.py`：提取 6 个数据模型生成函数（`get_symbol_profile`、`build_market_model`、`build_quote_strip`、`build_watchlist_rows`、`build_movers_rows`、`build_snapshot_cells`、`build_instrument_metrics`），以及常量定义（`SCALE_OPTIONS`、`OVERLAY_OPTIONS`、`ROUTE_OPTIONS`、`DEPTH_MODE_OPTIONS`、`RAIL_TABS`、`MOVERS_TABS`、`DEFAULT_WATCHLIST`、`UNIVERSE_CODES`、`CHART_POINT_COUNT` 等）
- [x] 4.3 创建 `tradingassistant/frontend/studies.py`：提取 9 个技术指标计算函数（`_moving_average`、`_ema`、`_rolling_std`、`_rsi`、`_atr`、`_obv`、`_build_overlay_legend_models`、`_build_route_study_models`、`build_route_studies`、`build_analysis_cards`）
- [x] 4.4 创建 `tradingassistant/frontend/renders.py`：提取 8 个 SVG/显示渲染函数（`_line_path`、`_histogram_svg`、`build_chart_legend`、`build_chart_hover_overlay_rows`、`build_chart_hover_details`、`build_primary_chart_svg`、`to_y`、`build_depth_rows`、`build_order_book_rows`）
- [x] 4.5 将原 `tradingassistant/frontend/charting.py` 改为兼容重导出层：从四个子模块 import 所有公开符号并重导出
- [x] 4.6 验证：`python -c "from tradingassistant.frontend import charting; print(len(charting.SCALE_OPTIONS))"` 确认兼容层可用
- [x] 4.7 验证：`pytest tests/test_frontend.py -v` 全绿

## 5. Frontend 语言统一

- [x] 5.1 将 `tradingassistant/frontend/app.py` 的文件级 docstring 和 `index()` docstring 改为中文简体
- [x] 5.2 将 `tradingassistant/frontend/charting.py`（兼容层）的文件级 docstring 改为中文简体
- [x] 5.3 将 `tradingassistant/frontend/models.py`、`studies.py`、`renders.py`、`utils.py` 四个新文件的文件级和函数级 docstring 写为中文简体
- [x] 5.4 将 `tradingassistant/frontend/state.py` 的文件级 docstring 和 `_reset_hover()` docstring 改为中文简体
- [x] 5.5 将 `tradingassistant/frontend/theme.py` 的文件级 docstring 和所有 `Return ...` 风格注释改为中文简体

## 6. 最终验证

- [x] 6.1 运行 `ruff check .` 确认项目零 lint 错误
- [x] 6.2 运行 `pytest . -v` 确认全部现有测试通过
- [x] 6.3 检查 `tradingassistant/frontend/charting.py` 的重导出层确认不会破坏 `app.py` 和 `state.py` 的现有引用
