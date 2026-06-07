## 1. 项目骨架与基础抽象

- [x] 1.1 规划并创建后端核心模块目录，至少覆盖市场接入、缓存抽象、订阅注册、主题广播、K 线聚合、指标引擎、传输门面与页面层对接模块
- [x] 1.2 定义统一领域事件模型，包括 `TickEvent`、`QuoteEvent`、`KlineEvent`、`DepthEvent` 与连接状态事件
- [x] 1.3 定义 `CacheStore`、`TopicBus`、`SubscriptionRegistry` 三类基础接口及其输入输出契约
- [x] 1.4 实现 `MemoryCacheStore`、`InMemoryTopicBus`、`InMemorySubscriptionRegistry` 的首版内存实现
- [x] 1.5 为基础抽象补充最小单元测试，验证接口行为和默认实现语义

## 2. iTick 接入与标准化

- [x] 2.1 封装 iTick REST 访问层，支持 symbol 查询、历史 K 线拉取和必要快照读取
- [x] 2.2 封装 iTick WebSocket 接入层，统一处理连接、心跳、重连和消息读取
- [x] 2.3 实现原始 iTick 消息到领域事件的标准化转换逻辑
- [x] 2.4 为市场接入层补充错误处理与连接状态事件输出
- [x] 2.5 补充接入层测试或回放样例，验证标准化字段与异常分支

## 3. 历史回填与实时图表主链路

- [x] 3.1 实现历史回填服务，优先命中 `MemoryCacheStore`，未命中时回源 iTick REST
- [x] 3.2 实现 1m forming bar 与 closed bar 的状态模型
- [x] 3.3 实现从 tick / quote 更新 forming 1m bar 的逻辑
- [x] 3.4 实现 1m bar 闭合规则与新 bar 初始化逻辑
- [x] 3.5 实现从 1m bar 聚合 5m、15m、30m、60m 等高周期 bar 的逻辑
- [x] 3.6 为历史回填、forming bar 和多周期聚合补充测试

## 4. 指标引擎

- [x] 4.1 实现基于历史窗口的指标初始化器，并接入 OpenTrade 作为批量初始化来源
- [x] 4.2 实现首批增量指标状态模型，至少覆盖 MA、EMA、MACD、RSI、BOLL
- [x] 4.3 为窗口型指标引入 ring buffer 或 deque 结构，避免全量重算
- [x] 4.4 实现 provisional / finalized 指标输出标记
- [x] 4.5 补充一致性校验工具，抽样对比增量指标与 OpenTrade 全量结果

## 5. 传输门面与会话订阅

- [x] 5.1 设计并实现 chart bootstrap REST 接口
- [x] 5.2 设计并实现图表增量推送通道
- [x] 5.3 设计并实现列表行情推送通道
- [x] 5.4 设计并实现 session 到 topic 的订阅注册、取消订阅和连接清理逻辑
- [x] 5.5 通过 `TopicBus` 把图表、列表和预警推送从处理器层解耦出来
- [x] 5.6 补充传输门面测试，验证 bootstrap 后接增量推送的完整链路

## 6. Reflex 页面层对接

- [x] 6.1 规划 Reflex 页面状态边界，明确哪些状态留在页面层，哪些状态通过 FastAPI 获取
- [x] 6.2 实现基础看盘页面的 bootstrap 调用流程
- [x] 6.3 接入图表增量通道，实现分时图与实时 K 线局部刷新
- [x] 6.4 接入指标开关、自选切换和周期切换等页面交互
- [x] 6.5 验证页面层未把高频逐笔行情状态直接存入 Reflex State

## 7. MEMORY 路线稳定化

- [x] 7.1 为内存缓存增加淘汰策略或失效策略，避免热状态无限增长
- [x] 7.2 为订阅注册和 topic 广播补充无订阅回收逻辑
- [x] 7.3 增加日志、指标和最小可观测性，至少覆盖命中率、订阅数、延迟和重连次数
- [x] 7.4 进行单机多页面联调，验证共享订阅与本地广播行为

## 8. Redis 平滑升级预留

- [x] 8.1 固化 cache key、topic key、snapshot payload 的稳定序列化结构
- [x] 8.2 为 `CacheStore`、`TopicBus`、`SubscriptionRegistry` 编写可替换实现约束测试
- [x] 8.3 设计 `RedisCacheStore`、`RedisTopicBus`、`RedisSubscriptionRegistry` 的接口适配说明
- [x] 8.4 编写从 MEMORY 升级到 Redis 的验证清单，包括单实例切换和多 worker 切换
