## Why

当前项目已经明确了目标技术栈，但还缺少一套能够直接进入实现阶段的详细落地方案。现在需要把“基于 iTick 的增强版看盘 WebApp”从架构思路收敛为可执行变更，确保系统先以 `MEMORY` 模式稳定落地，同时从一开始就为后续平滑升级到 Redis 保留明确的抽象边界。

## What Changes

- 新增一个以 `FastAPI + Reflex + iTick + OpenTrade` 为核心的增强版看盘系统方案，覆盖分时图、实时 K 线、指标增量计算和多标的订阅分发。
- 明确采用 `MEMORY` 作为默认运行态存储与广播基础，不把 Redis 作为初始实现前置条件。
- 新增缓存、广播、订阅注册三类抽象接口，避免业务逻辑直接绑定进程内字典。
- 定义历史回填、实时订阅、K 线聚合、指标引擎、图表推送、页面状态的职责边界。
- 定义平滑升级到 Redis 的迁移路径，包括替换点、兼容策略和阶段性验证方式。

## Capabilities

### New Capabilities
- `market-data-ingestion`: 接入 iTick REST / WebSocket，并把原始行情事件标准化为系统内部事件模型。
- `memory-first-runtime`: 使用 `MEMORY` 作为默认缓存、主题广播和订阅注册承载方式，并约束实现不得直接依赖全局可变结构。
- `realtime-chart-pipeline`: 支持分时图、实时 1m K 线、多周期聚合、形成中 bar 与闭合后 bar 的统一实时处理链路。
- `incremental-indicator-engine`: 支持基于历史初始化与实时增量更新的指标引擎，并允许使用 OpenTrade 作为初始化与校验补充源。
- `transport-and-session-facade`: 通过 FastAPI 对外暴露 bootstrap、图表推送、列表行情和预警事件接口，并隔离 Reflex 页面层与行情内核。
- `redis-upgrade-seams`: 预留从 `MEMORY` 平滑迁移到 Redis 的抽象边界、兼容约束与迁移步骤。

### Modified Capabilities

无。

## Impact

- 影响系统设计与后续实现目录，预计会新增行情接入、聚合计算、缓存抽象、推送门面、页面状态管理等模块。
- 影响 API 设计，需要定义 bootstrap REST、图表增量 WebSocket / SSE、行情列表推送和预警事件协议。
- 影响运行方式，当前默认不依赖 Redis，但实现时必须保留可升级接口。
- 影响测试策略，需要补充历史初始化、实时事件、指标一致性、缓存抽象替换与升级迁移验证。
