"""加载 `.env` 并为前后端入口提供共享配置。

当前配置约定优先服务于本机开发场景：
- 端口使用独立环境变量控制；
- URL 默认由本机回环地址和端口推导；
- 只有在需要跨主机、反向代理或容器映射时，才额外覆盖 URL。
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=False)


def _get_env_str(name: str, default: str) -> str:
    """读取字符串环境变量。

    Args:
        name: 环境变量名。
        default: 未设置时使用的默认值。

    Returns:
        去除首尾空白后的配置值。
    """
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped or default


def _get_env_int(name: str, default: int) -> int:
    """读取整数环境变量。

    Args:
        name: 环境变量名。
        default: 未设置时使用的默认值。

    Returns:
        转换后的整数值。

    Raises:
        ValueError: 当环境变量不是合法整数时抛出。
    """
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    if not stripped:
        return default
    try:
        return int(stripped)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable {name} must be an integer, got {value!r}."
        ) from exc


def _build_http_url(host: str, port: int) -> str:
    """根据 host 和 port 构造 HTTP 基础地址。

    Args:
        host: 监听或访问使用的主机名。
        port: 端口号。

    Returns:
        去除尾部斜杠后的 URL。
    """
    return f"http://{host}:{port}".rstrip("/")


def _get_env_url(name: str, *, host: str, port: int) -> str:
    """读取 URL 覆盖项，未设置时按 host 和 port 推导。

    Args:
        name: 环境变量名。
        host: 默认主机名。
        port: 默认端口号。

    Returns:
        去除尾部斜杠后的 URL。
    """
    return _get_env_str(name, _build_http_url(host, port)).rstrip("/")


LOCALHOST = "0.0.0.0"

FRONTEND_PORT = _get_env_int("TRADINGASSISTANT_FRONTEND_PORT", 3000)
FRONTEND_URL = _get_env_url(
    "TRADINGASSISTANT_FRONTEND_URL",
    host=LOCALHOST,
    port=FRONTEND_PORT,
)

REFLEX_BACKEND_PORT = _get_env_int("TRADINGASSISTANT_REFLEX_BACKEND_PORT", 8002)
REFLEX_API_URL = _get_env_url(
    "TRADINGASSISTANT_REFLEX_API_URL",
    host=LOCALHOST,
    port=REFLEX_BACKEND_PORT,
)

APP_BACKEND_HOST = _get_env_str("TRADINGASSISTANT_APP_BACKEND_HOST", "127.0.0.1")
APP_BACKEND_PORT = _get_env_int("TRADINGASSISTANT_APP_BACKEND_PORT", 8001)
APP_BACKEND_URL = _get_env_url(
    "TRADINGASSISTANT_APP_BACKEND_URL",
    host=LOCALHOST,
    port=APP_BACKEND_PORT,
)

API_BASE_URL = _get_env_str(
    "TRADINGASSISTANT_API_BASE_URL",
    APP_BACKEND_URL,
).rstrip("/")
ITICK_TOKEN = os.getenv("TRADINGASSISTANT_ITICK_TOKEN", "").strip()
