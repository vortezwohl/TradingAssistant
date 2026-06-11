"""封装 Reflex 看盘页使用的浏览器图表组件。

本模块负责：
1. 定义 bootstrap 快照、增量更新与指标面板的前端输入契约；
2. 生成基于 ECharts CDN 的浏览器图表容器；
3. 把高频 K 线与指标更新留在浏览器内处理，避免写回 Reflex State。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import reflex as rx


ECHARTS_CDN_URL = "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"


def _compact_json(payload: dict[str, Any]) -> str:
    """返回稳定、紧凑的 JSON 字符串。"""

    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


@dataclass(slots=True)
class ChartBootstrapPayload:
    """描述图表 bootstrap 输入契约。"""

    topic: str
    symbol: str
    period: str
    bars: list[dict[str, Any]] = field(default_factory=list)
    indicators: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ChartBootstrapPayload":
        """从 REST 返回值构造 bootstrap 契约对象。"""

        return cls(
            topic=str(payload.get("topic", "")),
            symbol=str(payload.get("symbol", "")),
            period=str(payload.get("period", "")),
            bars=list(payload.get("bars", [])),
            indicators=dict(payload.get("indicators", {})),
            metadata=dict(payload.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        """返回可序列化的 bootstrap 结构。"""

        return {
            "topic": self.topic,
            "symbol": self.symbol,
            "period": self.period,
            "bars": self.bars,
            "indicators": self.indicators,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class ChartIncrementalPayload:
    """描述图表增量更新输入契约。"""

    topic: str
    payload_type: str
    symbol: str
    period: str
    provisional: bool
    bar: dict[str, Any] = field(default_factory=dict)
    indicators: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ChartIncrementalPayload":
        """从 WebSocket 返回值构造增量更新契约对象。"""

        return cls(
            topic=str(payload.get("topic", "")),
            payload_type=str(payload.get("payload_type", "")),
            symbol=str(payload.get("symbol", "")),
            period=str(payload.get("period", "")),
            provisional=bool(payload.get("provisional", False)),
            bar=dict(payload.get("bar", {})),
            indicators=dict(payload.get("indicators", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        """返回可序列化的增量结构。"""

        return {
            "topic": self.topic,
            "payload_type": self.payload_type,
            "symbol": self.symbol,
            "period": self.period,
            "provisional": self.provisional,
            "bar": self.bar,
            "indicators": self.indicators,
        }


def _chart_runtime_script(container_id: str) -> str:
    """生成浏览器侧图表运行时代码。"""

    return f"""
(function() {{
  const CONTAINER_ID = {json.dumps(container_id, ensure_ascii=False)};
  const MAX_BARS = 240;

  function readJsonAttribute(node, name, fallback) {{
    const rawValue = node.getAttribute(name);
    if (!rawValue) {{
      return fallback;
    }}
    try {{
      return JSON.parse(rawValue);
    }} catch (_error) {{
      return fallback;
    }}
  }}

  function normalizeNumber(value) {{
    if (value === null || value === undefined || value === "") {{
      return null;
    }}
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }}

  function normalizeBar(rawBar, fallbackSymbol, fallbackPeriod) {{
    if (!rawBar || typeof rawBar !== "object") {{
      return null;
    }}
    if (!rawBar.bar_time) {{
      return null;
    }}
    return {{
      symbol: rawBar.symbol || fallbackSymbol || "",
      period: rawBar.period || fallbackPeriod || "",
      bar_time: String(rawBar.bar_time),
      open_price: normalizeNumber(rawBar.open_price),
      high_price: normalizeNumber(rawBar.high_price),
      low_price: normalizeNumber(rawBar.low_price),
      close_price: normalizeNumber(rawBar.close_price),
      volume: normalizeNumber(rawBar.volume) || 0,
      turnover: normalizeNumber(rawBar.turnover) || 0,
      provisional: Boolean(rawBar.provisional),
    }};
  }}

  function normalizeBars(bars, fallbackSymbol, fallbackPeriod) {{
    if (!Array.isArray(bars)) {{
      return [];
    }}
    return bars
      .map((bar) => normalizeBar(bar, fallbackSymbol, fallbackPeriod))
      .filter((bar) => bar !== null);
  }}

  function normalizeIndicatorSnapshot(rawIndicators) {{
    if (!rawIndicators || typeof rawIndicators !== "object") {{
      return {{ values: {{}}, provisional: false }};
    }}
    if (rawIndicators.values && typeof rawIndicators.values === "object") {{
      return {{
        values: rawIndicators.values,
        provisional: Boolean(rawIndicators.provisional),
      }};
    }}
    return {{
      values: rawIndicators,
      provisional: false,
    }};
  }}

  function buildSeriesData(metricBars, indicatorSnapshot) {{
    const values = indicatorSnapshot.values || {{}};
    return {{
      categoryData: metricBars.map((bar) => bar.bar_time.slice(11, 16)),
      candleData: metricBars.map((bar) => [
        normalizeNumber(bar.open_price),
        normalizeNumber(bar.close_price),
        normalizeNumber(bar.low_price),
        normalizeNumber(bar.high_price),
      ]),
      volumeData: metricBars.map((bar) => normalizeNumber(bar.volume) || 0),
      ma5Data: metricBars.map((_bar, index) => {{
        const latestIndex = metricBars.length - 1;
        return index === latestIndex ? normalizeNumber(values.ma5) : null;
      }}),
      ma20Data: metricBars.map((_bar, index) => {{
        const latestIndex = metricBars.length - 1;
        return index === latestIndex ? normalizeNumber(values.ma20) : null;
      }}),
      macdData: metricBars.map((_bar, index) => {{
        const latestIndex = metricBars.length - 1;
        return index === latestIndex ? normalizeNumber(values.macd_histogram) : null;
      }}),
      rsiData: metricBars.map((_bar, index) => {{
        const latestIndex = metricBars.length - 1;
        return index === latestIndex ? normalizeNumber(values.rsi14) : null;
      }}),
    }};
  }}

  function buildOption(runtimeState) {{
    const seriesData = buildSeriesData(runtimeState.bars, runtimeState.indicators);
    const indicatorStatus = runtimeState.indicators.provisional ? "PROVISIONAL" : "FINALIZED";
    return {{
      animation: false,
      backgroundColor: "transparent",
      color: ["#1f6feb", "#f97316", "#22c55e", "#ef4444", "#0f766e", "#eab308"],
      grid: [
        {{ left: 56, right: 24, top: 52, height: "46%" }},
        {{ left: 56, right: 24, top: "60%", height: "14%" }},
        {{ left: 56, right: 24, top: "79%", height: "12%" }},
        {{ left: 56, right: 24, top: "93%", height: "7%" }},
      ],
      legend: {{
        top: 10,
        left: 18,
        textStyle: {{ color: "#0f172a", fontSize: 12 }},
      }},
      tooltip: {{
        trigger: "axis",
        axisPointer: {{ type: "cross" }},
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        borderWidth: 0,
        textStyle: {{ color: "#f8fafc" }},
      }},
      axisPointer: {{
        link: [{{ xAxisIndex: "all" }}],
        label: {{ backgroundColor: "#334155" }},
      }},
      dataZoom: [
        {{
          type: "inside",
          xAxisIndex: [0, 1, 2, 3],
          filterMode: "none",
          zoomOnMouseWheel: true,
          moveOnMouseMove: true,
        }},
        {{
          type: "slider",
          xAxisIndex: [0, 1, 2, 3],
          bottom: 6,
          height: 18,
        }},
      ],
      xAxis: [
        {{
          type: "category",
          data: seriesData.categoryData,
          boundaryGap: true,
          axisLine: {{ lineStyle: {{ color: "#94a3b8" }} }},
          axisLabel: {{ color: "#475569" }},
          min: "dataMin",
          max: "dataMax",
        }},
        {{
          type: "category",
          gridIndex: 1,
          data: seriesData.categoryData,
          boundaryGap: true,
          axisLine: {{ lineStyle: {{ color: "#94a3b8" }} }},
          axisLabel: {{ show: false }},
        }},
        {{
          type: "category",
          gridIndex: 2,
          data: seriesData.categoryData,
          boundaryGap: true,
          axisLine: {{ lineStyle: {{ color: "#94a3b8" }} }},
          axisLabel: {{ show: false }},
        }},
        {{
          type: "category",
          gridIndex: 3,
          data: seriesData.categoryData,
          boundaryGap: true,
          axisLine: {{ lineStyle: {{ color: "#94a3b8" }} }},
          axisLabel: {{ color: "#475569", fontSize: 11 }},
        }},
      ],
      yAxis: [
        {{
          scale: true,
          axisLine: {{ lineStyle: {{ color: "#94a3b8" }} }},
          splitLine: {{ lineStyle: {{ color: "#e2e8f0" }} }},
          axisLabel: {{ color: "#475569" }},
        }},
        {{
          gridIndex: 1,
          scale: true,
          splitNumber: 2,
          axisLine: {{ lineStyle: {{ color: "#94a3b8" }} }},
          splitLine: {{ lineStyle: {{ color: "#e2e8f0" }} }},
          axisLabel: {{ color: "#475569" }},
        }},
        {{
          gridIndex: 2,
          scale: true,
          splitNumber: 2,
          axisLine: {{ lineStyle: {{ color: "#94a3b8" }} }},
          splitLine: {{ lineStyle: {{ color: "#e2e8f0" }} }},
          axisLabel: {{ color: "#475569" }},
        }},
        {{
          gridIndex: 3,
          min: 0,
          max: 100,
          splitNumber: 2,
          axisLine: {{ lineStyle: {{ color: "#94a3b8" }} }},
          splitLine: {{ lineStyle: {{ color: "#e2e8f0" }} }},
          axisLabel: {{ color: "#475569" }},
        }},
      ],
      series: [
        {{
          name: "K线",
          type: "candlestick",
          data: seriesData.candleData,
          itemStyle: {{
            color: "#ef4444",
            color0: "#22c55e",
            borderColor: "#ef4444",
            borderColor0: "#22c55e",
          }},
        }},
        {{
          name: "MA5",
          type: "line",
          data: seriesData.ma5Data,
          symbol: "none",
          smooth: true,
          lineStyle: {{ width: 2 }},
        }},
        {{
          name: "MA20",
          type: "line",
          data: seriesData.ma20Data,
          symbol: "none",
          smooth: true,
          lineStyle: {{ width: 2 }},
        }},
        {{
          name: "成交量",
          type: "bar",
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: seriesData.volumeData,
          itemStyle: {{
            color: "#94a3b8",
          }},
        }},
        {{
          name: "MACD",
          type: "bar",
          xAxisIndex: 2,
          yAxisIndex: 2,
          data: seriesData.macdData,
          itemStyle: {{
            color: function(params) {{
              return (params.data || 0) >= 0 ? "#ef4444" : "#22c55e";
            }},
          }},
        }},
        {{
          name: "RSI14",
          type: "line",
          xAxisIndex: 3,
          yAxisIndex: 3,
          data: seriesData.rsiData,
          symbol: "none",
          smooth: true,
          lineStyle: {{ width: 2, color: "#0f766e" }},
        }},
      ],
      graphic: [
        {{
          type: "text",
          right: 24,
          top: 14,
          style: {{
            text: indicatorStatus,
            fill: runtimeState.indicators.provisional ? "#ea580c" : "#15803d",
            fontWeight: 700,
            fontSize: 12,
          }},
        }},
      ],
    }};
  }}

  function setPanelText(root, selector, value) {{
    const target = root.querySelector(selector);
    if (!target) {{
      return;
    }}
    target.textContent = value;
  }}

  function formatIndicatorValue(value) {{
    const numeric = normalizeNumber(value);
    return numeric === null ? "--" : numeric.toFixed(2);
  }}

  function renderIndicatorPanel(root, runtimeState) {{
    const values = runtimeState.indicators.values || {{}};
    const statusText = runtimeState.indicators.provisional ? "形成中" : "已确认";
    const barStatus = runtimeState.bars.length && runtimeState.bars[runtimeState.bars.length - 1].provisional
      ? "当前K线: forming"
      : "当前K线: closed";
    setPanelText(root, "[data-role='indicator-status']", "指标状态: " + statusText);
    setPanelText(root, "[data-role='bar-status']", barStatus);
    setPanelText(root, "[data-role='indicator-ma5']", formatIndicatorValue(values.ma5));
    setPanelText(root, "[data-role='indicator-ma20']", formatIndicatorValue(values.ma20));
    setPanelText(root, "[data-role='indicator-macd']", formatIndicatorValue(values.macd_histogram));
    setPanelText(root, "[data-role='indicator-rsi']", formatIndicatorValue(values.rsi14));
    setPanelText(root, "[data-role='bootstrap-summary']", runtimeState.bootstrapSummary);
    setPanelText(root, "[data-role='stream-status']", runtimeState.streamStatus);
  }}

  function applyChart(root, runtimeState) {{
    if (!window.echarts) {{
      return;
    }}
    const chartNode = root.querySelector("[data-role='chart-canvas']");
    if (!chartNode) {{
      return;
    }}
    if (!runtimeState.chart) {{
      runtimeState.chart = window.echarts.init(chartNode, null, {{ renderer: "canvas" }});
      window.addEventListener("resize", function() {{
        if (runtimeState.chart) {{
          runtimeState.chart.resize();
        }}
      }});
    }}
    runtimeState.chart.setOption(buildOption(runtimeState), true);
    renderIndicatorPanel(root, runtimeState);
  }}

  function applyIncremental(runtimeState, rawPayload) {{
    const payload = rawPayload || {{}};
    if (payload.payload_type !== "bar_update") {{
      return;
    }}
    if (payload.topic !== runtimeState.activeTopic) {{
      return;
    }}
    const nextBar = normalizeBar(
      payload.bar,
      payload.symbol || runtimeState.symbol,
      payload.period || runtimeState.period,
    );
    if (!nextBar) {{
      return;
    }}
    nextBar.provisional = Boolean(payload.provisional);
    const lastBar = runtimeState.bars[runtimeState.bars.length - 1];
    if (lastBar && lastBar.bar_time === nextBar.bar_time) {{
      runtimeState.bars[runtimeState.bars.length - 1] = nextBar;
    }} else {{
      runtimeState.bars.push(nextBar);
      if (runtimeState.bars.length > MAX_BARS) {{
        runtimeState.bars = runtimeState.bars.slice(-MAX_BARS);
      }}
    }}
    runtimeState.indicators = normalizeIndicatorSnapshot(payload.indicators);
    runtimeState.streamStatus = nextBar.provisional
      ? "实时推送: forming bar 已更新"
      : "实时推送: closed bar 已确认";
  }}

  function ensureEchartsLoaded() {{
    if (window.echarts) {{
      return Promise.resolve(window.echarts);
    }}
    return new Promise((resolve, reject) => {{
      const existing = document.querySelector("script[data-tradingassistant-echarts='true']");
      if (existing) {{
        existing.addEventListener("load", () => resolve(window.echarts));
        existing.addEventListener("error", reject);
        return;
      }}
      const script = document.createElement("script");
      script.src = {json.dumps(ECHARTS_CDN_URL, ensure_ascii=False)};
      script.async = true;
      script.defer = true;
      script.setAttribute("data-tradingassistant-echarts", "true");
      script.addEventListener("load", () => resolve(window.echarts));
      script.addEventListener("error", reject);
      document.head.appendChild(script);
    }});
  }}

  function getEndpoint(baseUrl, path) {{
    const normalizedBase = (baseUrl || window.location.origin).replace(/\\/$/, "");
    const normalizedPath = path.startsWith("http")
      ? path
      : normalizedBase + path;
    return normalizedPath;
  }}

  function buildWsUrl(baseUrl, path) {{
    if (path.startsWith("ws://") || path.startsWith("wss://")) {{
      return path;
    }}
    const normalizedBase = (baseUrl || window.location.origin).replace(/\\/$/, "");
    const wsBase = normalizedBase.startsWith("https://")
      ? normalizedBase.replace("https://", "wss://")
      : normalizedBase.replace("http://", "ws://");
    return wsBase + path;
  }}

  function updateRootStatus(root, kind, message) {{
    root.setAttribute("data-status", kind);
    setPanelText(root, "[data-role='stream-status']", message);
  }}

  async function bootstrapAndSubscribe(root, runtimeState) {{
    if (runtimeState.socket) {{
      try {{
        if (runtimeState.activeTopic) {{
          runtimeState.socket.send(JSON.stringify({{
            action: "unsubscribe",
            symbol: runtimeState.symbol,
            period: runtimeState.period,
          }}));
        }}
        runtimeState.socket.close();
      }} catch (_error) {{
      }}
      runtimeState.socket = null;
    }}

    updateRootStatus(root, "loading", "正在加载 bootstrap...");
    const bootstrapUrl = getEndpoint(runtimeState.apiBaseUrl, runtimeState.bootstrapPath);
    let response;
    try {{
      response = await fetch(bootstrapUrl, {{
        headers: {{
          "Accept": "application/json",
        }},
      }});
    }} catch (error) {{
      root.setAttribute("data-status", "error");
      setPanelText(root, "[data-role='chart-message']", "bootstrap 请求失败");
      runtimeState.streamStatus = "加载失败: " + String(error);
      renderIndicatorPanel(root, runtimeState);
      return;
    }}

    if (!response.ok) {{
      root.setAttribute("data-status", "error");
      setPanelText(root, "[data-role='chart-message']", "bootstrap 返回错误状态");
      runtimeState.streamStatus = "HTTP " + response.status;
      renderIndicatorPanel(root, runtimeState);
      return;
    }}

    let bootstrapPayload;
    try {{
      bootstrapPayload = await response.json();
    }} catch (_error) {{
      root.setAttribute("data-status", "error");
      setPanelText(root, "[data-role='chart-message']", "bootstrap 数据不是合法 JSON");
      runtimeState.streamStatus = "非法 payload";
      renderIndicatorPanel(root, runtimeState);
      return;
    }}

    const bars = normalizeBars(bootstrapPayload.bars, bootstrapPayload.symbol, bootstrapPayload.period);
    if (!bars.length) {{
      root.setAttribute("data-status", "empty");
      setPanelText(root, "[data-role='chart-message']", "当前 bootstrap 没有可展示的 bars");
      runtimeState.bars = [];
      runtimeState.indicators = normalizeIndicatorSnapshot(bootstrapPayload.indicators);
      runtimeState.bootstrapSummary = "bars: 0";
      runtimeState.streamStatus = "等待新的上下文";
      renderIndicatorPanel(root, runtimeState);
      return;
    }}

    runtimeState.symbol = String(bootstrapPayload.symbol || runtimeState.symbol);
    runtimeState.period = String(bootstrapPayload.period || runtimeState.period);
    runtimeState.activeTopic = String(bootstrapPayload.topic || runtimeState.activeTopic);
    runtimeState.bars = bars.slice(-MAX_BARS);
    runtimeState.indicators = normalizeIndicatorSnapshot(bootstrapPayload.indicators);
    runtimeState.bootstrapSummary = "bars: " + runtimeState.bars.length + " / topic: " + runtimeState.activeTopic;
    runtimeState.streamStatus = "bootstrap 完成，等待实时增量";
    root.setAttribute("data-status", "ready");
    setPanelText(root, "[data-role='chart-message']", "");
    applyChart(root, runtimeState);

    const socketUrl = buildWsUrl(runtimeState.apiBaseUrl, runtimeState.chartSocketPath);
    const socket = new WebSocket(socketUrl);
    runtimeState.socket = socket;
    socket.addEventListener("open", function() {{
      updateRootStatus(root, "ready", "图表通道已连接，正在订阅...");
      socket.send(JSON.stringify({{
        action: "subscribe",
        symbol: runtimeState.symbol,
        period: runtimeState.period,
      }}));
    }});
    socket.addEventListener("message", function(event) {{
      let payload;
      try {{
        payload = JSON.parse(event.data);
      }} catch (_error) {{
        return;
      }}
      if (payload.payload_type === "subscription_ack") {{
        if (payload.topic && payload.topic !== runtimeState.activeTopic) {{
          return;
        }}
        runtimeState.streamStatus = "订阅已确认: " + String(payload.topic || runtimeState.activeTopic);
        renderIndicatorPanel(root, runtimeState);
        return;
      }}
      applyIncremental(runtimeState, payload);
      applyChart(root, runtimeState);
    }});
    socket.addEventListener("close", function() {{
      runtimeState.streamStatus = "图表通道已关闭";
      renderIndicatorPanel(root, runtimeState);
    }});
    socket.addEventListener("error", function() {{
      runtimeState.streamStatus = "图表通道异常";
      renderIndicatorPanel(root, runtimeState);
    }});
  }}

  function createRuntimeState(root) {{
    return {{
      symbol: root.getAttribute("data-symbol") || "",
      period: root.getAttribute("data-period") || "1m",
      indicatorKeys: readJsonAttribute(root, "data-indicators", []),
      bootstrapPath: root.getAttribute("data-bootstrap-url") || "",
      chartSocketPath: root.getAttribute("data-chart-socket-url") || "",
      apiBaseUrl: root.getAttribute("data-api-base-url") || window.location.origin,
      activeTopic: "",
      bars: [],
      indicators: {{ values: {{}}, provisional: false }},
      socket: null,
      chart: null,
      bootstrapSummary: "--",
      streamStatus: "尚未初始化",
    }};
  }}

  function boot() {{
    const root = document.getElementById(CONTAINER_ID);
    if (!root) {{
      return;
    }}
    const chartCanvas = root.querySelector("[data-role='chart-canvas']");
    if (!chartCanvas) {{
      return;
    }}
    const contextKey = [
      root.getAttribute("data-symbol") || "",
      root.getAttribute("data-period") || "",
      root.getAttribute("data-indicators") || "[]",
    ].join("|");
    if (root.dataset.contextKey === contextKey && root.__tradingassistantRuntime) {{
      return;
    }}
    root.dataset.contextKey = contextKey;
    if (root.__tradingassistantRuntime && root.__tradingassistantRuntime.socket) {{
      try {{
        root.__tradingassistantRuntime.socket.close();
      }} catch (_error) {{
      }}
    }}
    const runtimeState = createRuntimeState(root);
    root.__tradingassistantRuntime = runtimeState;
    ensureEchartsLoaded()
      .then(() => bootstrapAndSubscribe(root, runtimeState))
      .catch(() => {{
        root.setAttribute("data-status", "error");
        setPanelText(root, "[data-role='chart-message']", "ECharts 加载失败");
      }});
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", boot, {{ once: true }});
  }} else {{
    boot();
  }}
}})();
"""


def chart_canvas(
    *,
    container_id: str,
    bootstrap_url: Any,
    chart_socket_url: Any,
    api_base_url: Any,
    symbol: Any,
    period: Any,
    indicators_json: Any,
) -> rx.Component:
    """构造浏览器图表容器与运行时代码。"""

    return rx.fragment(
        rx.box(
            rx.box(
                rx.text(
                    "正在准备图表容器...",
                    size="2",
                    color_scheme="gray",
                    data_role="chart-message",
                ),
                rx.box(
                    width="100%",
                    height="100%",
                    data_role="chart-canvas",
                ),
                position="relative",
                width="100%",
                height="100%",
            ),
            id=container_id,
            data_bootstrap_url=bootstrap_url,
            data_chart_socket_url=chart_socket_url,
            data_api_base_url=api_base_url,
            data_symbol=symbol,
            data_period=period,
            data_indicators=indicators_json,
            data_status="idle",
            width="100%",
            height="100%",
        ),
        rx.script(_chart_runtime_script(container_id)),
    )


def indicator_summary_card() -> rx.Component:
    """构造图表页右侧指标状态面板。"""

    return rx.card(
        rx.vstack(
            rx.heading("指标面板", size="4"),
            rx.text("指标状态: --", data_role="indicator-status", size="2"),
            rx.text("当前K线: --", data_role="bar-status", size="2"),
            rx.divider(),
            rx.hstack(
                rx.text("MA5", weight="bold"),
                rx.spacer(),
                rx.code("--", data_role="indicator-ma5"),
                width="100%",
            ),
            rx.hstack(
                rx.text("MA20", weight="bold"),
                rx.spacer(),
                rx.code("--", data_role="indicator-ma20"),
                width="100%",
            ),
            rx.hstack(
                rx.text("MACD", weight="bold"),
                rx.spacer(),
                rx.code("--", data_role="indicator-macd"),
                width="100%",
            ),
            rx.hstack(
                rx.text("RSI14", weight="bold"),
                rx.spacer(),
                rx.code("--", data_role="indicator-rsi"),
                width="100%",
            ),
            rx.divider(),
            rx.text("bars: --", data_role="bootstrap-summary", size="2"),
            rx.text("通道状态: --", data_role="stream-status", size="2"),
            spacing="3",
            align="stretch",
        ),
        size="3",
        width="100%",
        height="100%",
    )


def example_bootstrap_payload() -> ChartBootstrapPayload:
    """返回用于测试与文档的示例 bootstrap 契约。"""

    return ChartBootstrapPayload(
        topic="chart:HK.00700:1m",
        symbol="HK.00700",
        period="1m",
        bars=[
            {
                "symbol": "HK.00700",
                "period": "1m",
                "bar_time": "2026-06-07T09:30:00+00:00",
                "open_price": 500.0,
                "high_price": 501.0,
                "low_price": 499.0,
                "close_price": 500.5,
                "volume": 1000,
                "turnover": 500000,
                "provisional": False,
            }
        ],
        indicators={
            "values": {
                "ma5": 500.5,
                "ma20": 500.5,
                "macd_histogram": 0.1,
                "rsi14": 52.0,
            },
            "provisional": False,
        },
        metadata={"source": "bootstrap", "bar_count": 1},
    )


def example_incremental_payload() -> ChartIncrementalPayload:
    """返回用于测试与文档的示例增量契约。"""

    return ChartIncrementalPayload(
        topic="chart:HK.00700:1m",
        payload_type="bar_update",
        symbol="HK.00700",
        period="1m",
        provisional=True,
        bar={
            "bar_time": "2026-06-07T09:31:00+00:00",
            "open_price": 500.5,
            "high_price": 501.2,
            "low_price": 500.1,
            "close_price": 500.9,
            "volume": 1200,
            "turnover": 520000,
        },
        indicators={
            "values": {
                "ma5": 500.7,
                "ma20": 500.6,
                "macd_histogram": 0.2,
                "rsi14": 53.4,
            },
            "provisional": True,
        },
    )


def indicators_json_literal(indicators: list[str]) -> str:
    """把指标列表编码为浏览器组件可消费的 JSON 文本。"""

    return _compact_json({"enabled": indicators})
