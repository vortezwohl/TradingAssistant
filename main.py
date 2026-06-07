"""提供项目根目录下的默认 ASGI 入口。

通过该文件，开发者可以直接使用 uvicorn 启动本项目的 FastAPI 门面，
而无需手工编写依赖装配脚本。
"""

from __future__ import annotations

from tradingassistant.runtime import create_default_app


app = create_default_app()
