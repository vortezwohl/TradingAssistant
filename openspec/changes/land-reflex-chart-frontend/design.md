## Context

当前仓库已经具备以下基础：

- 后端已经实现 `FastAPI` bootstrap / WebSocket 门面，可返回历史图表快照并推送图表、行情、告警增量。
- 图表数据链路已经具备 forming bar、closed bar、指标快照和 `provisional / finalized` 语义。
- `Reflex` 项目已经可以启动，但前端页面仍只是状态边界和订阅意图展示，没有真正的图表渲染闭环。

这次变更的核心不是继续增强后端，而是把“后端已准备好的图表协议”真正消费到浏览器里，并保持 Python 技术闭环。这里的难点不在于单纯把一张图画出来，而在于：

- 如何在不手写 Node/NPM 工程的前提下，引入适合 K 线和分时的浏览器图表能力；
- 如何让高频增量停留在浏览器侧而不是重新回灌到 Reflex State；
- 如何把 forming / closed bar 和 provisional / finalized 指标语义稳定映射到前端；
- 如何在 symbol / period / indicator 切换时，既保持页面交互简单，又不把 transport 资源管理做乱。

## Goals / Non-Goals

**Goals:**

- 为 Reflex 页面提供真正可见的分时图 / K 线图落地能力。
- 让页面通过 bootstrap 获取首屏数据，并通过 WebSocket 接收图表增量更新。
- 把高频图表状态留在浏览器图表组件内，只把低频交互状态留在 Reflex State。
- 支持 symbol 切换、周期切换、指标开关和重新订阅闭环。
- 为后续继续增强专业图表体验保留稳定组件边界。

**Non-Goals:**

- 这次设计不要求一次完成全部专业画图能力，例如画线工具、模板系统、多窗口同步。
- 这次设计不要求前端立即覆盖所有 OpenTrade 指标，只覆盖当前后端已提供的首批指标显示。
- 这次设计不实现完整的多页面布局系统或桌面终端级工作台。
- 这次设计不改变后端主数据模型或把实时状态迁回 Reflex State。

## Decisions

### 1. 采用“Reflex 页面 + 浏览器图表引擎包装组件”的双层前端结构

**Decision**

前端使用 Reflex 负责页面状态、布局和交互编排，具体高频绘图由一个浏览器侧图表引擎包装组件负责。Reflex 只下发 bootstrap 数据、订阅意图和低频控制参数，不直接持有所有实时 bar 状态。

**Rationale**

- 这与现有后端“高频运行态不进入 Reflex State”的设计完全一致。
- 浏览器图表引擎天然适合管理高频 series 更新、局部重绘和交互缩放。
- 这样可以把页面框架和图表渲染解耦，后续替换图表库时影响面更小。

**Alternatives considered**

- 方案 A：把每次图表增量都同步进 Reflex State，再由页面重渲染。
  - 放弃原因：会重新引入高频状态膨胀和序列化负担，违背已有架构边界。
- 方案 B：在页面里拼接零散原生脚本，不建立组件包装层。
  - 放弃原因：维护成本高，难以测试，也不利于后续扩展指标和多图表实例。

### 2. 首选 ECharts 作为前端图表引擎包装目标

**Decision**

优先采用 ECharts 作为前端图表引擎，并通过 Reflex 自定义组件或包装层接入，而不是手工维护独立 Node 工程。

**Rationale**

- ECharts 原生支持 K 线、折线、柱状、多个 grid / axis / dataZoom，适合“主图 + 副图指标”的结构。
- 与纯 K 线引擎相比，ECharts 对 MACD、RSI、BOLL、成交量等多面板组合更直接。
- 通过 Reflex 包装前端依赖，可以保持项目主开发链条仍然以 Python 为主，而不是切换成单独的前端仓库。

**Alternatives considered**

- 方案 A：TradingView Lightweight Charts。
  - 放弃原因：主图体验很好，但多副图、指标面板和复杂组合布局需要更多自定义实现。
- 方案 B：Reflex 内置基础图表直接承担 K 线。
  - 放弃原因：对专业实时 K 线和增量更新语义支持不够强。

### 3. bootstrap 与增量更新拆成“全量首屏 + 浏览器内增量应用”

**Decision**

页面初始化时通过 bootstrap 接口获取完整首屏快照，然后把后续图表更新、指标更新和订阅确认消息交给浏览器图表组件在本地应用。

**Rationale**

- 首屏全量快照适合通过 HTTP 获取，便于恢复页面和重建上下文。
- 后续增量应用放在浏览器内，可以避免每次消息都触发 Reflex 全页状态变化。
- 这与现有 transport 门面的“REST bootstrap + WebSocket 增量”协议天然匹配。

**Alternatives considered**

- 方案 A：首屏也完全靠 WebSocket 拉齐。
  - 放弃原因：初始化复杂度更高，调试成本更高，也不利于首屏缓存命中。

### 4. 前端显式区分 forming / closed bar 与 provisional / finalized 指标

**Decision**

浏览器图表组件必须把 forming bar 和 closed bar 视为不同更新语义；同时指标渲染层要显式识别 `provisional` 与 `finalized`，避免把临时值误展示成最终值。

**Rationale**

- 这是当前后端已经承诺的协议语义，前端不能把它抹平。
- 专业看盘体验中，未闭合 K 线与已闭合 K 线的“稳定程度”不同，指标也一样。
- 显式区分后，后续告警提示、颜色标识和闪烁策略更容易扩展。

**Alternatives considered**

- 方案 A：前端收到什么就直接覆盖图表，不区分形成中和已确认。
  - 放弃原因：会让用户误解当前 bar 和指标是否已经稳定。

### 5. 页面切换采用“先重建 bootstrap，再重建订阅”的保守策略

**Decision**

当用户切换 symbol、period 或 indicator set 时，前端先销毁旧图表上下文，重新请求 bootstrap，再建立新订阅，而不是试图在前端做跨上下文拼补。

**Rationale**

- 当前阶段优先保证正确性与可维护性，而不是做最复杂的前端状态复用。
- 这样能与现有的订阅确认和退订语义保持一致，减少旧 topic 泄漏风险。
- 也更适合当前 MEMORY-first 的单进程运行模式。

**Alternatives considered**

- 方案 A：尽量在前端本地复用旧 bar 数据，只追加差异。
  - 放弃原因：对 symbol / period / indicator 交叉切换来说复杂度过高，错误成本大。

## Risks / Trade-offs

- [图表库包装层引入前端依赖复杂度] → 通过单一包装组件隔离第三方依赖，避免页面代码到处散落集成细节。
- [高频消息在浏览器中堆积导致卡顿] → 只保留当前图表所需窗口数据，增量消息做局部更新，并限制历史窗口长度。
- [forming / provisional 语义被前端误用] → 在图表组件协议中显式保留对应字段，并补充验证用例。
- [切换 symbol / period 时旧订阅残留] → 统一采用“退订旧 topic → 重建 bootstrap → 订阅新 topic”的顺序，并验证订阅确认消息。
- [Reflex 与浏览器图表库集成细节存在框架兼容风险] → 先以最小组件包装验证编译和运行，再逐步增加指标叠加与交互能力。

## Migration Plan

1. 新增前端图表 capability 规格，明确页面渲染、bootstrap 装载和增量语义。
2. 补一个最小可编译的 Reflex 图表包装层，先能显示首屏历史数据。
3. 接入 chart WebSocket，把增量 bar 与指标更新应用到浏览器图表。
4. 补齐页面切换、指标开关和会话重订阅逻辑。
5. 通过手工联调与自动化测试确认页面可见图表已形成稳定闭环。

## Open Questions

- 这次是否需要同时落地“分时图 + K 线图”两种展示，还是先把 K 线主链路做到稳定，再复用为分时图视图？
- 当前阶段是否接受通过 Reflex 包装少量浏览器依赖，还是必须限制为完全零额外前端包？
- 指标副图是首版就做独立面板，还是先做主图叠加 + 简化副图切换？
