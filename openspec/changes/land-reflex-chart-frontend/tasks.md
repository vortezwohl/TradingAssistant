## 1. 图表组件包装与项目入口

- [x] 1.1 选定并接入适合 Reflex 的浏览器图表引擎包装方案，完成最小可编译组件骨架
- [x] 1.2 在 `tradingassistant/frontend/` 下新增图表包装模块，定义 bootstrap 数据输入和增量更新输入契约
- [x] 1.3 调整 `rxconfig.py` 和前端入口结构，确保图表组件可被 Reflex 正常编译和加载

## 2. bootstrap 首屏渲染

- [x] 2.1 为页面增加 chart bootstrap 调用流程，获取历史 bars 与初始指标快照
- [x] 2.2 把 bootstrap 返回的 bars、主图指标和副图指标映射为图表组件可消费的数据结构
- [x] 2.3 为 bootstrap 失败、空数据和非法 payload 增加明确的页面反馈状态

## 3. 实时增量与会话切换

- [x] 3.1 接入 chart WebSocket 通道，处理订阅确认消息与图表增量 `bar_update`
- [x] 3.2 在浏览器图表组件内实现 forming / closed bar 的本地更新逻辑，避免把高频 bar 状态存入 Reflex State
- [x] 3.3 接入 provisional / finalized 指标更新语义，并在图表层或指标面板中体现区别
- [x] 3.4 实现 symbol、period、indicator 切换时的“退订旧 topic → 重建 bootstrap → 订阅新 topic”闭环

## 4. 页面交互与验收

- [x] 4.1 完善页面布局，把主图、成交量区和指标区组织成可见的看盘页面结构
- [x] 4.2 补充前端状态与组件测试，验证页面未把高频图表状态直接落入 Reflex State
- [x] 4.3 补充联调验收步骤，验证本地启动后可以看到首屏图表并接收实时增量更新
