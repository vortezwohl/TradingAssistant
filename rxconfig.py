"""Minimal runtime configuration for the Reflex project."""

from __future__ import annotations

import reflex as rx

from tradingassistant.settings import FRONTEND_PORT, REFLEX_API_URL, REFLEX_BACKEND_PORT

config = rx.Config(
    app_name="tradingassistant",
    app_module_import="tradingassistant.frontend.app",
    frontend_port=FRONTEND_PORT,
    backend_port=REFLEX_BACKEND_PORT,
    api_url=REFLEX_API_URL,
)
