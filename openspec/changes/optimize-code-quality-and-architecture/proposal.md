## Why

项目在完成了多轮功能迭代（行情接入、图表管线、终端 UI）后，代码库中积累了若干代码质量债务和架构异味：
两个前端文件分别达到 874 行和 1200 行，transport 层的 `create_app` 函数圈复杂度超标至 15，部分模块存在未使用的导入和潜在的数据截断风险，且前端与后端模块的语言规范不一致。这些问题当前不影响功能，但会持续侵蚀可维护性和协作效率。

## What Changes

- 清理 `charting/aggregator.py` 中 4 个未使用的导入（`timedelta`、`Any`、`KlineEvent`、`BarRecord`）
- 为 `frontend/charting.py` 中 12 处 `zip()` 调用添加 `strict=True`，消除静默数据截断风险
- 将 `transport/app.py` 的 `create_app` 函数（142 行/圈复杂度 15）拆分为独立的路由模块，外部 API 和行为不变
- 将 `frontend/charting.py`（1200 行）拆分为 `models.py`、`studies.py`、`renders.py`、`utils.py` 四个聚焦模块
- 修复 7 个文件的 import 排序问题
- 修复 `frontend/app.py` 中 8 处函数间多余空行
- 统一 `frontend/` 下 4 个文件的 docstring 语言为中文简体，与项目其余 30 个文件保持一致
- 在 `pyproject.toml` 中添加 ruff 配置，固化代码质量门禁规则

## Capabilities

### New Capabilities
- `code-quality-enforcement`: 通过 ruff 配置固化为项目的持续代码质量门禁，覆盖导入排序、zip 严格模式、未使用导入检测、docstring 格式等规则；同时修复 `frontend/app.py` 中函数间多余空行
- `frontend-module-architecture`: 将前端巨型文件拆分为数据模型、技术指标、渲染引擎、工具函数四个独立模块，建立清晰的文件级职责边界；统一前端模块 docstring 语言为中文简体
- `transport-module-split`: 将 `create_app` 的 3 个 WebSocket 路由提取为独立文件，降低函数圈复杂度至 10 以内

### Modified Capabilities
（无——本次变更不修改任何已有 spec 级需求，所有改动均为实现层重构，外部行为不变）

## Impact

- 受影响文件：`charting/aggregator.py`、`frontend/charting.py`、`frontend/app.py`、`frontend/state.py`、`frontend/theme.py`、`transport/app.py`
- 新增文件：`transport/ws_chart.py`、`transport/ws_quote.py`、`transport/ws_alert.py`、`transport/ws_helpers.py`、`frontend/models.py`、`frontend/studies.py`、`frontend/renders.py`、`frontend/utils.py`
- 配置文件：`pyproject.toml`（追加 ruff 配置节）
- 不影响外部 API、数据协议或用户可见行为
- 现有测试应全部保持通过
