# 本地启动与 WebSocket 说明

> 当前仓库已收敛本机开发环境变量。
> 默认只需要维护端口类变量：
> `TRADINGASSISTANT_FRONTEND_PORT`、
> `TRADINGASSISTANT_REFLEX_BACKEND_PORT`、
> `TRADINGASSISTANT_APP_BACKEND_PORT`、
> `TRADINGASSISTANT_ITICK_TOKEN`。
> 只有在前端或浏览器需要连接非本机默认地址时，才额外设置
> `TRADINGASSISTANT_FRONTEND_URL`、
> `TRADINGASSISTANT_REFLEX_API_URL`、
> `TRADINGASSISTANT_APP_BACKEND_URL`、
> `TRADINGASSISTANT_API_BASE_URL`。

本文档记录当前仓库在本机的推荐启动方式、端口分工，以及“为什么页面看起来像 WebSocket 没连上”的定位结论。

## 1. 端口分工

当前项目需要区分两套后端通道：

- `3000`：Reflex 前端页面
- `8002`：业务 FastAPI 门面
- `8080`：Reflex 内部后端

这三者职责不同：

- `8002` 负责业务接口和业务实时通道，例如：
  - `GET /api/chart/bootstrap`
  - `WS /ws/chart/session-local`
  - `WS /ws/quotes/session-local`
  - `WS /ws/alerts/session-local`
- `8080` 负责 Reflex 自己的内部状态同步和事件循环，例如：
  - `GET /ping`
  - `GET /_health`
  - `WS /_event`（通过 Socket.IO 建立）

## 2. 为什么不能继续用 8000

本机原来的 `8000` 端口已被其他 `httpd.exe` 进程占用，不属于本项目。

如果继续让页面或 Reflex 内部事件通道指向 `8000`，就会出现以下问题：

- 业务前端会连错后端；
- Reflex 内部事件通道会误连外部服务；
- 页面可能出现看起来像 “Connection Error” 或 “WebSocket 未连接” 的误判。

因此当前仓库已经调整为：

- 业务后端默认走 `8002`
- Reflex 内部后端默认走 `8080`

## 3. 启动步骤

### 3.1 启动业务 FastAPI 后端

在项目根目录执行：

```powershell
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8002
```

预期结果：

- `http://127.0.0.1:8002/api/chart/bootstrap` 可访问；
- `ws://127.0.0.1:8002/ws/chart/session-local` 可建立连接；
- 默认无 `TRADINGASSISTANT_ITICK_TOKEN` 时，后端会使用演示历史数据。

### 3.2 启动 Reflex 前端与内部后端

另开一个终端，在项目根目录执行：

```powershell
.venv\Scripts\python.exe -m reflex run
```

预期结果：

- 前端页面运行在 `http://127.0.0.1:3000`
- Reflex 内部后端运行在 `http://127.0.0.1:8080`
- `http://127.0.0.1:8080/ping` 返回 `"pong"`
- `http://127.0.0.1:8080/_health` 返回 `{"status": true}`

## 4. 页面验收

启动完成后，打开：

- `http://127.0.0.1:3000`

建议按以下顺序验证：

1. 页面左侧能看到标的、周期和指标开关控件。
2. 页面主区域能看到图表容器和指标面板。
3. 右侧指标面板会显示 bootstrap bar 数量和通道状态。
4. 切换 `HK.00700` / `US.AAPL` 或切换 `1m` / `5m` 后，图表会重新拉取 bootstrap。
5. 业务图表通道建立后，指标面板中的“通道状态”会更新为“订阅已确认: chart:HK.00700:1m”之类的文案。

## 5. WebSocket 说明

### 5.1 页面里有两类“连接”

页面同时依赖两套连接：

- Reflex 内部连接：`ws://localhost:8080/_event`
- 业务图表连接：`ws://127.0.0.1:8002/ws/chart/session-local`

二者不要混淆。

### 5.2 “Connection Error” 不等于业务图表后端坏了

Reflex 页面源码中包含一个默认 overlay 组件，用于在内部事件通道失败时显示连接提示。

需要注意：

- 页面源码中即使出现 `Connection Error:` 的容器，也不必然代表当前连接失败；
- 真正要判断是否异常，应结合以下信号：
  - `8080/ping` 是否正常；
  - `8080/_health` 是否正常；
  - `8002/api/chart/bootstrap` 是否正常；
  - 业务图表 WebSocket 是否收到 `subscription_ack`。

### 5.3 当前已验证通过的事实

当前这套端口分工已经验证通过：

- `http://127.0.0.1:3000` 返回 `200`
- `http://127.0.0.1:8002/api/chart/bootstrap?...` 返回 `200`
- `http://127.0.0.1:8080/ping` 返回 `200`
- `http://127.0.0.1:8080/_health` 返回 `200`
- `ws://127.0.0.1:8002/ws/chart/session-local` 收到 `subscription_ack`
- `ws://localhost:8080/_event` 可通过 Socket.IO 成功建立连接

## 6. 与代码对应的关键位置

- Reflex 配置：`rxconfig.py`
- 业务后端默认地址：`tradingassistant/frontend/state.py`
- 业务 WebSocket 门面：`tradingassistant/transport/app.py`
- 启动入口：`main.py`

## 7. 常见故障排查

### 7.1 打开页面后没有图表数据

优先检查：

- `8002` 的业务后端是否已启动；
- 若未显式设置 `TRADINGASSISTANT_API_BASE_URL`，是否默认跟随业务后端端口；
- 若显式设置了 `TRADINGASSISTANT_API_BASE_URL`，其值是否确实指向可访问的业务 API；
- `http://127.0.0.1:8002/api/chart/bootstrap` 是否能返回 `200`。

### 7.2 页面提示连接异常

优先检查：

- `8080` 的 Reflex 内部后端是否已启动；
- `http://127.0.0.1:8080/ping` 是否返回 `pong`；
- `http://127.0.0.1:8080/_health` 是否返回 `{"status": true}`。

### 7.3 端口冲突

如果 `3000`、`8002`、`8080` 中任一端口被占用，先释放冲突进程，或统一修改配置后再启动。
