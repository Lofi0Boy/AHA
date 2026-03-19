"""
File watcher — uses inotify (via watchdog) to detect .mpm/data/ changes.

Emits per-project refresh signals so only the affected column re-renders.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEventHandler, EVENT_TYPE_MODIFIED, EVENT_TYPE_CREATED, EVENT_TYPE_DELETED, EVENT_TYPE_MOVED
from watchdog.observers import Observer

if TYPE_CHECKING:
    from flask_socketio import SocketIO

from .session_manager import _load_config


class _ProjectHandler(FileSystemEventHandler):
    """Per-project debounced handler that emits project-specific refresh."""

    def __init__(self, socketio: SocketIO, cache: dict, project_name: str, debounce: float = 1.5):
        self.socketio = socketio
        self._cache = cache
        self.project_name = project_name
        self.debounce = debounce
        self._timer = None

    def _emit(self):
        self._cache["data"] = None
        self.socketio.emit("project_changed", {"project": self.project_name})

    _WRITE_EVENTS = {EVENT_TYPE_MODIFIED, EVENT_TYPE_CREATED, EVENT_TYPE_DELETED, EVENT_TYPE_MOVED}

    def on_any_event(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".json"):
            return
        if event.event_type not in self._WRITE_EVENTS:
            return

        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.debounce, self._emit)
        self._timer.daemon = True
        self._timer.start()


def start_file_watcher(socketio: SocketIO, cache: dict | None = None) -> None:
    """Watch each project's .mpm/data/ directory for JSON changes."""
    config = _load_config()
    projects = config.get("projects", [])
    if not projects:
        return

    c = cache if cache is not None else {}
    observer = Observer()

    for project_path in projects:
        d = Path(project_path)
        if not d.is_dir():
            continue
        data_dir = d / ".mpm" / "data"
        if data_dir.exists():
            handler = _ProjectHandler(socketio, c, d.name)
            observer.schedule(handler, str(data_dir), recursive=True)

    observer.daemon = True
    observer.start()
