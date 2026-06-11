## Why

当前仓库已经具备 MEMORY-first 的行情后端、bootstrap 接口和 WebSocket 门面，但 Reflex 前端仍停留在页面骨架阶段，尚未把历史回填、实时增量、指标叠加和周期切换真正落到可见图表上。现在需要把“后端已准备好”的能力真正交付为“用户能看到并操作的看盘页面”，否则整条实时链路仍缺少最关键的前端闭环。

## What Changes

- 为 Reflex 页面补齐真正的图表落地能力，包括首屏 bootstrap 拉取、图表增量消息接入和图形渲染容器。
- 引入适合 K 线 / 分时展示的前端图表集成方案，并封装为 Python 侧可维护的组件或包装层，避免把页面实现退化为零散脚本拼接。
- 明确前端页面如何处理 forming bar、closed bar、provisional 指标和 finalized 指标，保证图形显示语义与后端协议一致。
- 补齐前端交互闭环，包括 symbol 切换、周期切换、指标开关、自选切换以及订阅重建。
- 为前端图表接入补充可验证约束，确保高频运行态仍留在传输与浏览器侧，而不是重新塞回 Reflex State。

## Capabilities

### New Capabilities
- `reflex-chart-rendering`: 定义 Reflex 页面中的图表组件包装、bootstrap 数据装载、前端增量应用与交互展示行为

### Modified Capabilities
- `realtime-chart-pipeline`: 补充前端如何消费 bootstrap 与增量 bar 的显示要求，包括 forming / closed bar 的页面语义
- `transport-and-session-facade`: 补充图表前端订阅确认、重订阅和页面切换期间会话行为要求
- `incremental-indicator-engine`: 补充前端对 provisional / finalized 指标输出的渲染与切换要求

## Impact

- 影响 `tradingassistant/frontend/` 下的 Reflex 页面、状态模型和图表集成方式。
- 可能需要新增一个前端图表包装模块，以及与 `main.py` / `rxconfig.py` 兼容的运行结构。
- 影响前端依赖策略，需要明确是否通过 Reflex 支持的方式引入浏览器图表库或自定义组件包装。
- 影响联调与验证方式，需要补充“页面可见图表已正确展示 bootstrap 与实时增量”的测试或验收步骤。
