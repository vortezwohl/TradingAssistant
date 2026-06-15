## Context

TradingAssistant 项目当前处于 MEMORY 路线的功能交付后期。核心业务链路（行情接入 → K 线聚合 → 指标计算 → WebSocket 推送 → Reflex 终端 UI）已跑通，但代码结构在快速迭代中积累了以下问题：

- **文件膨胀**: `frontend/charting.py` (1200 行/31 函数) 和 `frontend/app.py` (874 行/24 函数) 混合了数据生成、图表渲染、UI 布局三类职责
- **函数复杂**: `transport/app.py` 的 `create_app` 142 行/圈复杂度 15/70 语句，内部嵌套 7 个函数
- **代码卫生**: 4 个未使用导入、12 处 `zip()` 缺少 `strict=` 参数、7 个文件 import 未排序、8 处多余空行
- **语言不一致**: `frontend/` 下 4 个文件使用英文，其余 30 个文件使用中文

## Goals / Non-Goals

**Goals:**
- 将两个最大文件控制在 400 行以内，每个文件承担单一职责
- 将 `create_app` 圈复杂度从 15 降至 ≤10
- 消除所有 ruff 报告的高优先级问题（F401/I001/B905/E302）
- 统一前端模块语言为中文简体
- 添加 ruff 配置文件，固化代码质量门禁

**Non-Goals:**
- 不新增任何功能特性
- 不改变 WebSocket 协议、REST API 或 Reflex State 接口
- 不接入真实行情数据源（前端仍使用 mock）
- 不处理 ITICK_TOKEN 泄露问题
- 不修复 D400/D415/RUF002（中文 docstring 不适合英文句号/半角标点规则）

## Decisions

### Decision 1: frontend/charting.py 按职责纵向拆分为 4 文件

**选择**: `models.py`（数据生成）+ `studies.py`（指标计算）+ `renders.py`（SVG 渲染）+ `utils.py`（工具函数）

**备选方案**: 按函数大小水平拆分（如 part1/part2）

**理由**: 纵向拆分让每个文件职责单一，新加入的开发者可以按"我需要改数据模型 → 去 models.py"的方式快速定位。水平拆分只是把问题切成两份同样臃肿的文件。

### Decision 2: create_app 路由提取为独立模块，而非类封装

**选择**: 3 个 WebSocket 路由各自独立文件（`ws_chart.py`、`ws_quote.py`、`ws_alert.py`），公共逻辑提取到 `ws_helpers.py`

**备选方案**: 用类封装 WebSocket 管理逻辑，或保留在一个大文件中

**理由**: 独立模块与现有 FastAPI 路由注册模式一致（`@app.websocket(...)` 装饰器），不引入新的抽象层。每个路由文件只依赖自身需要的导入，减少上下文负担。

### Decision 3: 保留原 charting.py 作为兼容重导出层

**选择**: 原 `frontend/charting.py` 在拆分后变为重导出文件，从四个子模块 import 所有公开符号

**备选方案**: 直接删除 charting.py，修改所有引用

**理由**: `app.py` 和 `state.py` 大量 `from . import charting` 和 `charting.xxx` 引用。保留兼容层可以渐进式迁移，先拆结构再逐步更新引用路径。最小化本次变更的 diff 面。

### Decision 4: ruff 配置写在 pyproject.toml

**选择**: 在 `pyproject.toml` 中添加 `[tool.ruff.lint]` 配置节

**备选方案**: 独立 `.ruff.toml` 文件

**理由**: 项目已有 `pyproject.toml`，集中管理配置更统一。

### Decision 5: aggregator.py 的 QuoteEvent/TickEvent 移至 TYPE_CHECKING

**选择**: 使用 `TYPE_CHECKING` 条件导入

**理由**: `QuoteEvent` 和 `TickEvent` 仅在函数类型标注中使用（dataclass 的 `slots=True` 配合 `from __future__ import annotations` 已经在运行时不需要它们），移至 `TYPE_CHECKING` 可减少不必要的运行时导入。

## Risks / Trade-offs

- **[风险] 拆分后 import 环依赖** → **缓解**: 四个新文件按依赖层次排序（utils ← models ← studies ← renders），每层只向下依赖，不形成环；兼容层 `charting.py` 作为最外层聚合
- **[风险] WebSocket 路由提取后测试失败** → **缓解**: 路由行为完全不变，仅移动位置；先运行现有 `test_transport.py` 全量测试确认基准，拆分后再运行确认无回归
- **[风险] zip(strict=True) 暴露隐藏的数据长度不匹配 bug** → **缓解**: 这正是 `strict=True` 的目的——如果 mock 数据中两个列表长度不一致，修改后会直接报错而非静默截断，可以及时发现并修复数据生成逻辑
- **[权衡] 拆分增加文件数量（+7 个）** → **接受**: 每个文件 ≤400 行 vs 两个 1000 行级文件，可维护性的提升远超文件数量的增加

## Migration Plan

1. 第一轮（低风险自动修复）: ruff --fix 处理 import 排序、空行、docstring 空行
2. 第二轮（手动精确修复）: 清理 aggregator.py 导入、添加 zip strict=
3. 第三轮（transport 拆分）: 创建 ws_*.py 文件，修改 create_app，运行 transport 测试
4. 第四轮（frontend 拆分）: 创建四个子模块，charting.py 改为兼容层，运行 frontend 测试
5. 第五轮（语言统一）: 修改 4 个前端文件的 docstring
6. 回滚策略: 每一步的改动都是独立的、可单独 revert；不依赖数据库迁移或配置变更

## Open Questions

- （无——所有设计决策已在本轮讨论中明确）
