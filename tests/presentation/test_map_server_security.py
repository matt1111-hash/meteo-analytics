"""Security tests for map-server temp-dir isolation (P2 finding #3 / CWE-200).

The map view used to ``os.chdir`` into the shared system temp dir and serve it
via an unauthenticated ``SimpleHTTPRequestHandler`` — exposing every readable
temp file to any localhost peer. These tests lock in the fix: a private 0700
dir and a handler bound to it.
"""

from __future__ import annotations

import http.client
import shutil
import socketserver
import stat
import tempfile
import threading
from pathlib import Path

import pytest

# map_interactions pulls in PySide6, which needs the libEGL system library.
# Headless CI runners (ubuntu) lack libEGL, so the import fails there — skip the
# module instead of aborting collection. The tests run locally (real desktop).
try:
    from src.presentation.gui.map.map_interactions import (
        create_map_temp_dir,
        make_map_request_handler,
    )
except ImportError as exc:  # pragma: no cover - environment-dependent
    pytest.skip(
        f"map_interactions (PySide6/Qt) unavailable in this environment: {exc}",
        allow_module_level=True,
    )


def test_create_map_temp_dir_is_dedicated_and_owner_only() -> None:
    """The served dir is a private (0700) dir, distinct from the shared temp."""
    path = Path(create_map_temp_dir())
    try:
        assert path.is_dir()
        assert path.resolve() != Path(tempfile.gettempdir()).resolve()
        mode = stat.S_IMODE(path.stat().st_mode)
        assert mode == 0o700
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _start_bound_server(directory: str) -> tuple[socketserver.TCPServer, int, threading.Thread]:
    """Start a TCPServer bound to ``directory`` on an ephemeral port."""
    handler = make_map_request_handler(directory)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port, thread


def _get(host: str, port: int, path: str) -> int:
    conn = http.client.HTTPConnection(host, port, timeout=5)
    try:
        conn.request("GET", path)
        response = conn.getresponse()
        response.read()
        return response.status
    finally:
        conn.close()


def test_handler_serves_only_files_inside_the_directory() -> None:
    """A file in the shared temp dir (the old served root) must NOT be served."""
    served = Path(create_map_temp_dir())
    inside_file = served / "map.html"
    outside_file = Path(tempfile.gettempdir()) / "meteo_test_outside_secret.txt"

    inside_file.write_text("<html>map</html>")
    outside_file.write_text("secret")

    httpd = None
    try:
        httpd, port, _thread = _start_bound_server(str(served))
        # A file inside the bound directory is served.
        assert _get("127.0.0.1", port, "/map.html") == 200
        # A sibling file in the shared temp dir is NOT served (404, not exposed).
        assert _get("127.0.0.1", port, "/meteo_test_outside_secret.txt") == 404
        # Traversal attempts stay inside the bound root.
        assert _get("127.0.0.1", port, "/../meteo_test_outside_secret.txt") == 404
    finally:
        if httpd is not None:
            httpd.shutdown()
            httpd.server_close()
        shutil.rmtree(served, ignore_errors=True)
        if outside_file.exists():
            outside_file.unlink()
