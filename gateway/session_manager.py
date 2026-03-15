"""
tmux session manager for MPM Gateway.

Manages per-project tmux sessions, detects running AI CLI processes,
and provides I/O bridging (send commands, capture output).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path(__file__).parent.parent / "data" / "cli_patterns.json"


class SessionState(Enum):
    OFF = "off"           # No tmux session
    IDLE = "idle"         # tmux session exists but no AI CLI running
    RUNNING = "running"   # AI CLI process detected (responding or waiting)


@dataclass
class SessionInfo:
    project: str
    tmux_name: str
    state: SessionState
    cli_name: Optional[str] = None   # e.g. "claude", "codex"
    pid: Optional[int] = None        # CLI process PID


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"patterns": [], "workspace": "", "tmux_prefix": "mpm"}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _run(cmd: list[str], timeout: int = 5) -> tuple[int, str]:
    """Run a command, return (returncode, stdout)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return -1, ""


def _tmux_session_name(prefix: str, project: str) -> str:
    return f"{prefix}-{project}"


# ---------------------------------------------------------------------------
# tmux operations
# ---------------------------------------------------------------------------

def list_tmux_sessions() -> list[str]:
    """Return list of active tmux session names."""
    rc, out = _run(["tmux", "list-sessions", "-F", "#{session_name}"])
    if rc != 0 or not out:
        return []
    return out.splitlines()


def create_session(project: str, cli_command: Optional[str] = None) -> SessionInfo:
    """Create a tmux session for a project, optionally starting a CLI command."""
    config = _load_config()
    prefix = config.get("tmux_prefix", "mpm")
    workspace = config.get("workspace", "")
    name = _tmux_session_name(prefix, project)
    project_dir = os.path.join(workspace, project)

    if not os.path.isdir(project_dir):
        raise ValueError(f"Project directory not found: {project_dir}")

    # Check if session already exists
    if name in list_tmux_sessions():
        return get_session_info(project)

    # Create session
    cmd = ["tmux", "new-session", "-d", "-s", name, "-c", project_dir]
    rc, _ = _run(cmd)
    if rc != 0:
        raise RuntimeError(f"Failed to create tmux session: {name}")

    # Start CLI if specified
    if cli_command:
        send_keys(project, cli_command)

    return get_session_info(project)


def kill_session(project: str) -> bool:
    """Kill a project's tmux session."""
    config = _load_config()
    prefix = config.get("tmux_prefix", "mpm")
    name = _tmux_session_name(prefix, project)
    rc, _ = _run(["tmux", "kill-session", "-t", name])
    return rc == 0


def send_keys(project: str, text: str) -> bool:
    """Send text input to a project's tmux session."""
    config = _load_config()
    prefix = config.get("tmux_prefix", "mpm")
    name = _tmux_session_name(prefix, project)
    rc, _ = _run(["tmux", "send-keys", "-t", name, text, "Enter"])
    return rc == 0


def capture_pane(project: str, lines: int = 200) -> str:
    """Capture current visible output from a project's tmux pane."""
    config = _load_config()
    prefix = config.get("tmux_prefix", "mpm")
    name = _tmux_session_name(prefix, project)
    # -p: print to stdout, -S: start line (negative = scrollback)
    rc, out = _run(["tmux", "capture-pane", "-t", name, "-p", "-S", f"-{lines}"])
    if rc != 0:
        return ""
    return out


# ---------------------------------------------------------------------------
# Process detection
# ---------------------------------------------------------------------------

def _detect_cli_in_session(tmux_name: str, patterns: list[str]) -> Optional[tuple[str, int]]:
    """Check if a known AI CLI process is running inside a tmux session.
    Returns (cli_name, pid) or None."""
    # Get the PID of the tmux pane's shell
    rc, pane_pid_str = _run([
        "tmux", "list-panes", "-t", tmux_name, "-F", "#{pane_pid}"
    ])
    if rc != 0 or not pane_pid_str:
        return None

    pane_pid = pane_pid_str.splitlines()[0].strip()

    # Find child processes of the pane shell
    rc, children = _run(["ps", "--ppid", pane_pid, "-o", "pid=,comm=", "--no-headers"])
    if rc != 0 or not children:
        return None

    for line in children.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) < 2:
            continue
        pid_str, comm = parts
        comm_lower = comm.lower()
        for pattern in patterns:
            if pattern.lower() in comm_lower:
                return (pattern, int(pid_str))

    return None


def _detect_external_sessions(
    workspace: str, patterns: list[str], known_tmux: set[str]
) -> list[SessionInfo]:
    """Detect AI CLI processes running outside of MPM tmux sessions."""
    results = []

    # Find all processes matching CLI patterns
    for pattern in patterns:
        rc, out = _run(["pgrep", "-a", "-i", pattern])
        if rc != 0 or not out:
            continue
        for line in out.splitlines():
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            pid = int(parts[0])

            # Check cwd
            cwd_link = f"/proc/{pid}/cwd"
            try:
                cwd = os.readlink(cwd_link)
            except OSError:
                continue

            # Is it under our workspace?
            if not cwd.startswith(workspace):
                continue

            # Extract project name
            rel = os.path.relpath(cwd, workspace)
            project = rel.split(os.sep)[0]

            # Skip if we already have a tmux session for this project
            if any(project in s for s in known_tmux):
                continue

            results.append(SessionInfo(
                project=project,
                tmux_name="",
                state=SessionState.RUNNING,
                cli_name=pattern,
                pid=pid,
            ))

    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_session_info(project: str) -> SessionInfo:
    """Get the current state of a project's session."""
    config = _load_config()
    prefix = config.get("tmux_prefix", "mpm")
    patterns = config.get("patterns", [])
    name = _tmux_session_name(prefix, project)

    if name not in list_tmux_sessions():
        return SessionInfo(project=project, tmux_name=name, state=SessionState.OFF)

    # Check for CLI process inside session
    cli = _detect_cli_in_session(name, patterns)
    if cli:
        return SessionInfo(
            project=project, tmux_name=name,
            state=SessionState.RUNNING, cli_name=cli[0], pid=cli[1],
        )

    return SessionInfo(project=project, tmux_name=name, state=SessionState.IDLE)


def get_all_sessions() -> list[dict]:
    """Get session status for all projects in the workspace."""
    config = _load_config()
    workspace = config.get("workspace", "")
    prefix = config.get("tmux_prefix", "mpm")
    patterns = config.get("patterns", [])

    if not workspace or not os.path.isdir(workspace):
        return []

    active_tmux = set(list_tmux_sessions())
    results: list[SessionInfo] = []

    # Check each project directory
    for d in sorted(Path(workspace).iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        name = _tmux_session_name(prefix, d.name)
        if name in active_tmux:
            results.append(get_session_info(d.name))
        else:
            results.append(SessionInfo(
                project=d.name, tmux_name=name, state=SessionState.OFF,
            ))

    return [
        {
            "project": s.project,
            "tmux_name": s.tmux_name,
            "state": s.state.value,
            "cli_name": s.cli_name,
            "pid": s.pid,
        }
        for s in results
    ]
