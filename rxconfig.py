"""定义 Reflex 项目的最小运行配置。

当前配置的目标是让本仓库可以被 Reflex CLI 正确识别和编译。
页面源码位于 ``tradingassistant/frontend/app.py``，项目名称保持与包名一致，
方便后续继续扩展为完整的前后端闭环看盘应用。
"""

from __future__ import annotations

import reflex as rx


config = rx.Config(
    app_name="tradingassistant",
    app_module_import="tradingassistant.frontend.app",
    frontend_port=3000,
    backend_port=8002,
    api_url="http://127.0.0.1:8002",
)
