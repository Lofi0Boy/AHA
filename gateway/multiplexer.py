"""
I/O Multiplexer — streams tmux pane output to connected WebSocket clients.

Runs as a background thread, polling tmux capture-pane for each subscribed
project and emitting diffs to SocketIO clients.
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from .session_manager import capture_pane, get_all_sessions

if TYPE_CHECKING:
    from flask_socketio import SocketIO

# Per-project state: last captured output
_last_output: dict[str, str] = {}
# Projects that have at least one WebSocket subscriber
_subscribed: set[str] = set()
_lock = threading.Lock()


def subscribe(project: str) -> str:
    """Subscribe to a project's output stream. Returns current output."""
    with _lock:
        _subscribed.add(project)
    return capture_pane(project)


def unsubscribe(project: str) -> None:
    with _lock:
        _subscribed.discard(project)


def start_polling(socketio: SocketIO, interval: float = 0.5) -> None:
    """Start background thread that polls tmux and emits output diffs."""

    def _poll_loop():
        while True:
            with _lock:
                projects = set(_subscribed)

            for project in projects:
                output = capture_pane(project)
                prev = _last_output.get(project, "")
                if output != prev:
                    _last_output[project] = output
                    socketio.emit("terminal_output", {
                        "project": project,
                        "output": output,
                    })

            time.sleep(interval)

    t = threading.Thread(target=_poll_loop, daemon=True)
    t.start()
