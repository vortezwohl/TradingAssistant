"""统一加载 `.env` 并向前后端入口提供共享配置。"""

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
        default: 缺失时使用的默认值。

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
        default: 缺失时使用的默认值。

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
        raise ValueError(f"环境变量 {name} 必须是整数，当前值为 {value!r}。") from exc


def _build_http_url(host: str, port: int) -> str:
    """基于 host 与 port 生成 HTTP 基础地址。

    Args:
        host: 监听或访问主机。
        port: 端口。

    Returns:
        去除尾部斜杠的 URL。
    """

    return f"http://{host}:{port}".rstrip("/")


FRONTEND_HOST = _get_env_str("TRADINGASSISTANT_FRONTEND_HOST", "127.0.0.1")
FRONTEND_PORT = _get_env_int("TRADINGASSISTANT_FRONTEND_PORT", 3000)
FRONTEND_URL = _get_env_str(
    "TRADINGASSISTANT_FRONTEND_URL",
    _build_http_url(FRONTEND_HOST, FRONTEND_PORT),
).rstrip("/")

REFLEX_BACKEND_HOST = _get_env_str(
    "TRADINGASSISTANT_REFLEX_BACKEND_HOST",
    "127.0.0.1",
)
REFLEX_BACKEND_PORT = _get_env_int("TRADINGASSISTANT_REFLEX_BACKEND_PORT", 8002)
REFLEX_API_URL = _get_env_str(
    "TRADINGASSISTANT_REFLEX_API_URL",
    _build_http_url(REFLEX_BACKEND_HOST, REFLEX_BACKEND_PORT),
).rstrip("/")

APP_BACKEND_HOST = _get_env_str("TRADINGASSISTANT_APP_BACKEND_HOST", "127.0.0.1")
APP_BACKEND_PORT = _get_env_int("TRADINGASSISTANT_APP_BACKEND_PORT", 8001)
APP_BACKEND_URL = _get_env_str(
    "TRADINGASSISTANT_APP_BACKEND_URL",
    _build_http_url(APP_BACKEND_HOST, APP_BACKEND_PORT),
).rstrip("/")

API_BASE_URL = _get_env_str(
    "TRADINGASSISTANT_API_BASE_URL",
    APP_BACKEND_URL,
).rstrip("/")
ITICK_TOKEN = os.getenv("TRADINGASSISTANT_ITICK_TOKEN", "").strip()
