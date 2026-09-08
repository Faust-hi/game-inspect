"""Readiness gate for start.bat: open the browser only for OUR services.

The launcher used to sleep 10 seconds and open the browser blindly, so a
foreign process on the same port could be opened instead (D43.5). This script
polls both endpoints and verifies ownership markers in the bodies:

* backend 127.0.0.1:8000/api/health must contain "version" and "database";
* frontend 127.0.0.1:5173/ must contain id="root".

Exit code 0 only when both owners answer in time.
"""
from __future__ import annotations

import http.client
import sys
import time

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
TIMEOUT_S = 90
INTERVAL_S = 2


def backend_ready(body: bytes) -> bool:
    """Our backend health payload carries version and database fields."""
    return b'"version"' in body and b'"database"' in body


def frontend_ready(body: bytes) -> bool:
    """Our frontend index carries the React root mount point."""
    return b'id="root"' in body


def _get(port: int, path: str) -> bytes | None:
    try:
        connection = http.client.HTTPConnection(BACKEND_HOST, port, timeout=3)
        connection.request("GET", path)
        return connection.getresponse().read()
    except Exception:  # noqa: BLE001 — not up yet, keep polling
        return None


def wait(timeout_s: float = TIMEOUT_S) -> tuple[bool, bool]:
    """Poll until both owners answer or the deadline passes."""
    deadline = time.time() + timeout_s
    ok_backend = ok_frontend = False
    while time.time() < deadline and not (ok_backend and ok_frontend):
        if not ok_backend:
            body = _get(BACKEND_PORT, "/api/health")
            ok_backend = body is not None and backend_ready(body)
        if not ok_frontend:
            body = _get(FRONTEND_PORT, "/")
            ok_frontend = body is not None and frontend_ready(body)
        if not (ok_backend and ok_frontend):
            time.sleep(INTERVAL_S)
    return ok_backend, ok_frontend


def main() -> int:
    ok_backend, ok_frontend = wait()
    print(f"backend: {ok_backend} frontend: {ok_frontend}")
    return 0 if (ok_backend and ok_frontend) else 1


if __name__ == "__main__":
    raise SystemExit(main())
