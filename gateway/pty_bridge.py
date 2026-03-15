"""
PTY bridge — connects tmux sessions to WebSocket clients via pseudo-terminals.

For each subscribed project, spawns `tmux attach -t <session>` inside a PTY
and bridges the raw byte stream to/from SocketIO.
"""

from __future__ import annotations

import fcntl
import os
import pty
import select
import struct
import termios
import threading
import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from flask_socketio import SocketIO

from .session_manager import _load_config, _tmux_session_name, list_tmux_sessions


class PtySession:
    """A PTY running `tmux attach` for one project."""

    def __init__(self, project: str, tmux_name: str):
        self.project = project
        self.tmux_name = tmux_name
        self.master_fd: Optional[int] = None
        self.pid: Optional[int] = None
        self.alive = False

    def start(self) -> bool:
        """Spawn tmux attach in a PTY. Returns True on success."""
        if self.tmux_name not in list_tmux_sessions():
            return False

        child_pid, master_fd = pty.fork()
        if child_pid == 0:
            # Child process — exec tmux attach
            os.execvp("tmux", ["tmux", "attach-session", "-t", self.tmux_name])
        else:
            # Parent process
            self.master_fd = master_fd
            self.pid = child_pid
            self.alive = True
            return True

    def write(self, data: bytes) -> None:
        """Write input to the PTY."""
        if self.master_fd is not None and self.alive:
            try:
                os.write(self.master_fd, data)
            except OSError:
                self.alive = False

    def read(self, size: int = 16384) -> Optional[bytes]:
        """Read from the PTY with short timeout."""
        if self.master_fd is None or not self.alive:
            return None
        try:
            r, _, _ = select.select([self.master_fd], [], [], 0.01)
            if r:
                return os.read(self.master_fd, size)
        except OSError:
            self.alive = False
        return None

    def resize(self, rows: int, cols: int) -> None:
        """Resize the PTY."""
        if self.master_fd is not None:
            try:
                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
            except OSError:
                pass

    def stop(self) -> None:
        """Close the PTY (tmux session stays alive)."""
        self.alive = False
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None
        if self.pid is not None:
            try:
                os.kill(self.pid, 9)
                os.waitpid(self.pid, os.WNOHANG)
            except OSError:
                pass
            self.pid = None


# Active PTY sessions: sid -> PtySession
_sessions: dict[str, PtySession] = {}
_lock = threading.Lock()


def attach(sid: str, project: str) -> bool:
    """Attach a WebSocket client to a project's tmux session via PTY."""
    config = _load_config()
    prefix = config.get("tmux_prefix", "mpm")
    tmux_name = _tmux_session_name(prefix, project)

    # Close existing PTY for this sid first
    detach(sid)

    session = PtySession(project, tmux_name)
    if not session.start():
        return False

    with _lock:
        _sessions[sid] = session
    return True


def detach(sid: str) -> None:
    """Detach a WebSocket client."""
    with _lock:
        session = _sessions.pop(sid, None)
    if session:
        session.stop()


def write_input(sid: str, data: str) -> None:
    """Send input from WebSocket to PTY."""
    with _lock:
        session = _sessions.get(sid)
    if session:
        session.write(data.encode("utf-8", errors="replace"))


def resize(sid: str, rows: int, cols: int) -> None:
    """Resize PTY for a client."""
    with _lock:
        session = _sessions.get(sid)
    if session:
        session.resize(rows, cols)


def start_reader(socketio: SocketIO) -> None:
    """Background thread that reads from all active PTYs and emits to clients."""

    def _loop():
        while True:
            with _lock:
                items = list(_sessions.items())

            if not items:
                time.sleep(0.05)
                continue

            for sid, session in items:
                if not session.alive:
                    continue
                try:
                    data = session.read()
                    if data:
                        socketio.emit("pty_output", {
                            "data": data.decode("utf-8", errors="replace"),
                        }, to=sid)
                except Exception:
                    session.alive = False

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
