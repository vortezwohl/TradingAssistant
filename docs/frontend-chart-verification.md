# Reflex 图表前端联调步骤

本文档用于验证 `land-reflex-chart-frontend` 变更已经形成可运行闭环。

## 1. 启动 FastAPI 门面

在项目根目录执行：

```powershell
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

预期结果：

- `http://127.0.0.1:8000/api/chart/bootstrap` 可访问；
- `ws://127.0.0.1:8000/ws/chart/session-local` 可建立连接；
- 默认无 `TRADINGASSISTANT_ITICK_TOKEN` 时，后端会使用演示历史数据。

## 2. 启动 Reflex 前端

另开一个终端，在项目根目录执行：

```powershell
.venv\Scripts\python.exe -m reflex run
```

若本机 Reflex 默认端口不是 `3000`，以终端输出为准。

## 3. 页面验收

打开 Reflex 页面后，按以下顺序验证：

1. 页面左侧能看到标的、周期和指标开关控件；
2. 页面主区域能看到首屏 K 线图、成交量区、MACD/RSI 区和指标面板；
3. 右侧指标面板会显示 bootstrap bar 数量和当前通道状态；
4. 切换 `HK.00700` / `US.AAPL` 或切换 `1m` / `5m` 后，图表会重新拉取 bootstrap；
5. 切换 MA / MACD / RSI 开关后，图表上下文会重建，旧 topic 会关闭，新的 topic 会重新订阅；
6. 当后端推送 `subscription_ack` 时，指标面板中的“通道状态”会更新为已确认；
7. 当后端推送 `bar_update` 时，forming bar 会覆盖最后一根 bar，closed bar 会追加成新 bar；
8. 指标面板会把 `provisional` 显示为“形成中”，`finalized` 显示为“已确认”。

## 4. 自动化验证

执行以下命令验证当前前端状态边界与契约：

```powershell
.venv\Scripts\python.exe -m unittest tests.test_frontend
```

如需一起回归后端传输与 bootstrap 契约，可再执行：

```powershell
.venv\Scripts\python.exe -m unittest tests.test_transport tests.test_frontend
```

## 5. Reflex 编译验证

当前仓库已经验证以下编译链路：

```powershell
@'
from reflex.utils.prerequisites import get_and_validate_app
app_info = get_and_validate_app(reload=False, check_if_schema_up_to_date=False)
app_info.app._compile(prerender_routes=False, dry_run=True, use_rich=False, trigger="manual-test")
print("compiled-dry-run-ok")
'@ | .venv\Scripts\python.exe -
```

预期结果：

- 输出 `compiled-dry-run-ok`；
- 说明 `rxconfig.py`、`tradingassistant.frontend.app` 入口和页面组件树已可被 Reflex 正常识别；
- 若 `reflex export --no-zip` 在本机仍长时间停留，则优先排查本地前端导出工具链或网络下载阶段，而不是本次页面代码本身。
