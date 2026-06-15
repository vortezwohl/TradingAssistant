"""Default ASGI entry point and local dual-process launcher for development."""

from __future__ import annotations

import contextlib
import os
import subprocess
import sys
import time
from pathlib import Path

from tradingassistant.backend.runtime import create_default_app
from tradingassistant.settings import (
    API_BASE_URL,
    APP_BACKEND_HOST,
    APP_BACKEND_PORT,
    APP_BACKEND_URL,
    FRONTEND_URL,
)

PROJECT_ROOT = Path(__file__).resolve().parent

app = create_default_app()


def _resolve_reflex_executable() -> str:
    """Return the currently available Reflex executable path."""
    script_dir = Path(sys.executable).resolve().parent
    candidates = [
        script_dir / "reflex.exe",
        script_dir / "reflex",
        PROJECT_ROOT / ".venv" / "Scripts" / "reflex.exe",
        PROJECT_ROOT / ".venv" / "bin" / "reflex",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "reflex"


def _build_backend_command() -> list[str]:
    """Build the startup command for the FastAPI backend facade."""
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--host",
        APP_BACKEND_HOST,
        "--port",
        str(APP_BACKEND_PORT),
    ]


def _build_frontend_command() -> list[str]:
    """Build the startup command for the Reflex frontend dev server."""
    return [_resolve_reflex_executable(), "run"]


def _build_frontend_env() -> dict[str, str]:
    """Inject the unified API base URL into the Reflex frontend environment."""
    env = os.environ.copy()
    env["TRADINGASSISTANT_API_BASE_URL"] = API_BASE_URL
    return env


def _terminate_process_tree(process: subprocess.Popen | None) -> None:
    """Terminate the entire child process tree."""
    if process is None or process.poll() is not None:
        return

    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

    with contextlib.suppress(subprocess.TimeoutExpired):
        process.wait(timeout=5)


def _run_dev_stack() -> int:
    """Launch both the backend service and the Reflex frontend simultaneously."""
    backend_process = None
    frontend_process = None
    try:
        print(f"[dev] backend: {APP_BACKEND_URL}")
        print(f"[dev] frontend: {FRONTEND_URL}")
        if API_BASE_URL != APP_BACKEND_URL:
            print(f"[dev] frontend api target: {API_BASE_URL}")
        backend_process = subprocess.Popen(
            _build_backend_command(),
            cwd=PROJECT_ROOT,
        )
        frontend_process = subprocess.Popen(
            _build_frontend_command(),
            cwd=PROJECT_ROOT,
            env=_build_frontend_env(),
        )

        while True:
            backend_returncode = backend_process.poll()
            frontend_returncode = frontend_process.poll()

            if backend_returncode is not None:
                return backend_returncode
            if frontend_returncode is not None:
                return frontend_returncode

            time.sleep(0.5)
    except KeyboardInterrupt:
        return 0
    finally:
        _terminate_process_tree(frontend_process)
        _terminate_process_tree(backend_process)


if __name__ == "__main__":
    raise SystemExit(_run_dev_stack())
