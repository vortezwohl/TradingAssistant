"""Load `.env` and provide shared configuration for frontend/backend entry points."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=False)


def _get_env_str(name: str, default: str) -> str:
    """Read a string environment variable.

    Args:
        name: Environment variable name.
        default: Default value when missing.

    Returns:
        Configuration value with leading/trailing whitespace stripped.
    """
    value = os.getenv(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped or default


def _get_env_int(name: str, default: int) -> int:
    """Read an integer environment variable.

    Args:
        name: Environment variable name.
        default: Default value when missing.

    Returns:
        The converted integer value.

    Raises:
        ValueError: Raised when the environment variable is not a valid integer.
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
    """Build an HTTP base URL from host and port.

    Args:
        host: Listen or access host.
        port: Port number.

    Returns:
        URL with trailing slash removed.
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
