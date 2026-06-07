## Context

当前仓库尚未开始正式实现，只有依赖声明与一份架构设计 HTML 文档。已确认的关键外部约束如下：

- 前端使用 `Reflex`，但高频实时状态不能直接压进 `Reflex State`。
- 服务门面使用 `FastAPI`，负责 REST / WebSocket / SSE 协议出口。
- 上游数据源为 `iTick`，本地已安装 `itick-sdk 0.1.0`，其 Python SDK 是薄封装，核心是 REST 与线程式 WebSocket 客户端。
- 指标能力由 `OpenTrade 1.1.0` 补充，适合做历史初始化与离线一致性校验，不适合作为高频实时总线。
- 运行态默认不依赖 Redis，系统必须先在 `MEMORY` 模式下可用，但后续需要保留升级到 Redis 的抽象边界。

这个变更是明显的跨模块架构变更，覆盖接入、缓存、分发、聚合、指标、页面与迁移路径，属于需要先做设计再实现的类型。

## Goals / Non-Goals

**Goals:**

- 定义一套以 `MEMORY` 为默认运行模式的增强版看盘系统架构。
- 支持历史回填、实时分时、实时 1m K 线、从 1m 聚合多周期、指标增量计算。
- 明确缓存、广播、订阅注册的抽象接口，避免将来从 `MEMORY` 升级到 Redis 时重写核心业务逻辑。
- 定义 `FastAPI` 门面、行情内核、指标引擎、`Reflex` 页面层之间的职责边界。
- 为后续 `/opsx:apply` 阶段提供可以直接拆成代码任务的实施顺序。

**Non-Goals:**

- 本设计不包含最终视觉稿与具体图表库接入代码。
- 本设计不实现交易下单、账户、风控执行或策略回测。
- 本设计不解决商业授权、数据再分发许可和生产运维容量采购。
- 本设计不要求第一阶段就支持多实例横向扩容。

## Decisions

### 1. 采用“行情内核独立于 Reflex 状态”的双层架构

**Decision**

把实时行情、K 线、指标和主题分发都放在 `FastAPI` 后的行情内核中；`Reflex` 只负责页面状态、用户交互状态和页面编排。

**Rationale**

- `Reflex` 内部有状态管理、事件处理队列和多种 state manager 语义，适合页面状态，不适合承接所有高频行情事件。
- 高频实时状态与页面状态分离后，后续扩 symbol、扩页面和扩推送类型时复杂度更可控。

**Alternatives considered**

- 方案 A：全部放进 `Reflex State`。
  - 放弃原因：高频更新会导致状态膨胀、事件排队和序列化成本失控。
- 方案 B：页面直接连接 iTick。
  - 放弃原因：无法集中管理订阅、缓存、限流和共享热状态。

### 2. 默认运行态采用 MEMORY，但所有共享基础设施通过抽象接口访问

**Decision**

第一阶段以进程内 `MEMORY` 作为缓存、广播与订阅注册承载方式，同时定义三类接口：

- `CacheStore`
- `TopicBus`
- `SubscriptionRegistry`

默认实现分别为：

- `MemoryCacheStore`
- `InMemoryTopicBus`
- `InMemorySubscriptionRegistry`

**Rationale**

- 现在不引入 Redis，可以降低搭建成本、减少系统复杂度、缩短第一阶段验证路径。
- 如果业务逻辑直接访问全局字典，后续迁移 Redis 会非常痛苦；先定义抽象能把迁移成本压到基础设施层。

**Alternatives considered**

- 方案 A：一开始就上 Redis。
  - 放弃原因：当前阶段优先验证实时链路与模块边界，不需要过早引入分布式复杂度。
- 方案 B：纯内存且不抽象接口。
  - 放弃原因：后续升级成本会从“替换存储后端”变成“重写业务结构”。

### 3. 统一以标准化领域事件作为实时主链路输入

**Decision**

不让业务层直接消费 iTick 原始消息，而是先经由适配层转换成领域事件：

- `TickEvent`
- `QuoteEvent`
- `KlineEvent`
- `DepthEvent`
- `ConnectionEvent`

所有后续聚合、指标和推送只依赖标准化事件。

**Rationale**

- 上游协议、字段名和消息格式属于典型变化点，必须通过 Adapter 隔离。
- 统一事件模型后，未来增加其他数据源或回放测试时不需要重写下游逻辑。

**Alternatives considered**

- 方案 A：下游直接解析原始 JSON。
  - 放弃原因：协议耦合会扩散到所有模块。

### 4. 历史初始化与实时增量计算分离

**Decision**

- 历史窗口初始化阶段：允许使用 `OpenTrade` 做 DataFrame 级指标补齐。
- 实时阶段：采用增量状态模型，优先 O(1) 更新，窗口指标使用 ring buffer / deque。

**Rationale**

- `OpenTrade` 在历史增强与指标覆盖上很强，但不是为高频每笔实时更新设计的。
- 分离初始化与增量后，可以同时兼顾开发效率和运行效率。

**Alternatives considered**

- 方案 A：每次新事件都全量重算 DataFrame。
  - 放弃原因：计算成本与窗口长度、订阅数线性放大，无法支撑增强版目标。

### 5. 多周期统一从 1m 或更细粒度基线聚合

**Decision**

实时 K 线链路默认维护 1m forming bar，再从 1m 聚合出 5m / 15m / 30m / 60m / 日线等高周期。

**Rationale**

- 能减少上游重复订阅。
- 所有指标都围绕统一 bar pipeline 计算，逻辑更稳定。

**Alternatives considered**

- 方案 A：每个周期都直接订阅上游。
  - 放弃原因：订阅面扩大、事件风暴增大、状态一致性更难保证。

### 6. 对外协议按用途分流，不做单一大通道

**Decision**

FastAPI 对外至少区分三类通道：

- bootstrap REST：首屏历史与图表初始化
- chart push：图表增量推送
- quote push：列表行情推送
- alert push：异动 / 指标事件推送

**Rationale**

- 不同前端区域的数据频率和粒度不同，拆通道能减少无关流量。
- 后续 Redis 升级时，不同 topic 也更容易映射到独立频道。

**Alternatives considered**

- 方案 A：所有消息都走一个 WebSocket。
  - 放弃原因：协议复杂、客户端过滤负担重、后续扩展难控。

## Risks / Trade-offs

- [MEMORY 模式不支持天然横向扩容] → 通过 `CacheStore / TopicBus / SubscriptionRegistry` 抽象隔离，并在设计上禁止业务直接依赖全局字典。
- [iTick Python SDK 使用线程模型] → 在适配层集中处理线程与异步桥接，避免线程语义泄漏到业务逻辑。
- [OpenTrade 与实时链路节奏不一致] → 明确其角色是“初始化器 + 校验器”，不把它放到高频主链路。
- [多周期聚合可能引入边界错误] → 先把 1m bar 闭合规则和交易时段规则独立测试，再级联验证高周期。
- [Reflex 页面可能误吸收实时状态] → 在模块边界和任务拆分中明确禁止将逐笔行情存入 `Reflex State`。
- [未来升级 Redis 时协议不兼容] → 所有缓存条目、事件 envelope、topic key、订阅 key 均使用稳定序列化结构。

## Migration Plan

### Phase 1：MEMORY 落地

1. 建立项目目录与基础抽象接口。
2. 实现 `MemoryCacheStore`、`InMemoryTopicBus`、`InMemorySubscriptionRegistry`。
3. 打通 iTick 接入、历史回填、1m bar、实时推送与页面 bootstrap。
4. 完成指标初始化和首批增量指标。

### Phase 2：增强与校验

1. 扩充指标集合。
2. 增加一致性校验工具，对比增量结果与 OpenTrade 全量结果。
3. 优化 topic 分流、节流与缓存淘汰策略。

### Phase 3：平滑升级 Redis

1. 新增 `RedisCacheStore`、`RedisTopicBus`、`RedisSubscriptionRegistry` 实现。
2. 保持业务服务构造函数签名不变，仅替换基础设施注入。
3. 先在单实例环境下开启 Redis 后端验证读写与广播一致性。
4. 再验证多 worker 下的共享订阅、热缓存与重连恢复。
5. 若升级失败，可切回 MEMORY 实现，不影响上层模块接口。

## Open Questions

- iTick 当前实际套餐是否覆盖实时 `kline@1`，还是需要退化为 `tick/quote` 自组 1m bar？
- 当前项目计划优先覆盖哪些市场与 symbol 命名规则？
- 图表层最终使用 Reflex 内置图表封装，还是需要定制更专业的 K 线组件包装？
- 是否要在第一阶段就支持 SSE 与 WebSocket 双协议，还是先统一走 WebSocket？
