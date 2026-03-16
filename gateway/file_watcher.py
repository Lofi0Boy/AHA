"""
File watcher — uses inotify (via watchdog) to detect handoff/ROADMAP changes.

Replaces fixed-interval polling for project data refresh.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

if TYPE_CHECKING:
    from flask_socketio import SocketIO

from .session_manager import _load_config


class _Handler(FileSystemEventHandler):
    """Debounced handler that emits refresh signal on file changes."""

    def __init__(self, socketio: SocketIO, debounce: float = 1.0):
        self.socketio = socketio
        self.debounce = debounce
        self._last_event = 0.0
        self._timer = None

    def _emit(self):
        self.socketio.emit("projects_changed", {})

    def on_any_event(self, event):
        if event.is_directory:
            return
        src = event.src_path
        if not (src.endswith(".md") or src.endswith(".json")):
            return

        now = time.time()
        self._last_event = now

        # Debounce: wait for quiet period before emitting
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.debounce, self._emit)
        self._timer.daemon = True
        self._timer.start()


def start_file_watcher(socketio: SocketIO) -> None:
    """Watch all project handoff dirs and ROADMAP files for changes."""
    config = _load_config()
    workspace = config.get("workspace", "")
    if not workspace:
        return

    workspace_path = Path(workspace)
    if not workspace_path.is_dir():
        return

    handler = _Handler(socketio)
    observer = Observer()

    # Watch each project's docs directory
    for d in workspace_path.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        docs_dir = d / "docs"
        if docs_dir.exists():
            observer.schedule(handler, str(docs_dir), recursive=True)

    observer.daemon = True
    observer.start()
