"""
Parse project data and load .mpm/ task system for each project in MpmWorkspace.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

WORKSPACE_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path, default=None):
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def _save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Task system v2 — .mpm/data/{future,current,past}
# ---------------------------------------------------------------------------

def _data_path(project_dir: Path) -> Path:
    return project_dir / ".mpm" / "data"


def load_future(project_dir: Path) -> list:
    return _load_json(_data_path(project_dir) / "future.json", default=[])


def save_future(project_dir: Path, data: list) -> None:
    _save_json(_data_path(project_dir) / "future.json", data)


def load_current_tasks(project_dir: Path) -> list:
    """Load all active tasks from current/ directory."""
    current_dir = _data_path(project_dir) / "current"
    if not current_dir.exists():
        return []
    tasks = []
    for f in current_dir.glob("*.json"):
        task = _load_json(f)
        if task:
            tasks.append(task)
    return tasks


def save_current_task(project_dir: Path, session_id: str, data: dict) -> None:
    _save_json(_data_path(project_dir) / "current" / f"{session_id}.json", data)


def delete_current_task(project_dir: Path, session_id: str) -> bool:
    path = _data_path(project_dir) / "current" / f"{session_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False


def load_past(project_dir: Path, date_str: str | None = None) -> list:
    """Load past tasks. If date_str given, load that day only. Otherwise load all."""
    past_dir = _data_path(project_dir) / "past"
    if not past_dir.exists():
        return []
    if date_str:
        return _load_json(past_dir / f"{date_str}.json", default=[])
    # Load all past files, newest first
    tasks = []
    for f in sorted(past_dir.glob("*.json"), reverse=True):
        day_tasks = _load_json(f, default=[])
        tasks.extend(day_tasks)
    return tasks


def append_past(project_dir: Path, task: dict) -> None:
    """Append a completed task to today's past file."""
    from datetime import datetime, timezone, timedelta
    kst = timezone(timedelta(hours=9))
    date_str = datetime.now(kst).strftime("%y%m%d")
    past_dir = _data_path(project_dir) / "past"
    path = past_dir / f"{date_str}.json"
    existing = _load_json(path, default=[])
    existing.append(task)
    _save_json(path, existing)


# ---------------------------------------------------------------------------
# PROJECT.md
# ---------------------------------------------------------------------------

def load_project_md(project_dir: Path) -> str:
    path = project_dir / ".mpm" / "docs" / "PROJECT.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Legacy compat aliases (status/next_tasks/history → new structure)
# ---------------------------------------------------------------------------

def load_status(project_dir: Path) -> dict:
    """Return first current task as status, or empty dict."""
    tasks = load_current_tasks(project_dir)
    return tasks[0] if tasks else {}


def save_status(project_dir: Path, data: dict) -> None:
    session_id = data.get("session_id", "unknown")
    save_current_task(project_dir, session_id, data)


def load_next_tasks(project_dir: Path) -> list:
    return load_future(project_dir)


def save_next_tasks(project_dir: Path, data: list) -> None:
    save_future(project_dir, data)


def load_history(project_dir: Path) -> list:
    return load_past(project_dir)


def save_history(project_dir: Path, data: list) -> None:
    # Legacy: overwrite is not supported in v2, use append_past instead
    pass


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CheckItem:
    text: str
    done: bool


@dataclass
class Phase:
    number: int
    name: str
    goal: str
    items: list[CheckItem] = field(default_factory=list)

    @property
    def done_count(self) -> int:
        return sum(1 for i in self.items if i.done)

    @property
    def total_count(self) -> int:
        return len(self.items)

    @property
    def is_complete(self) -> bool:
        return self.total_count > 0 and self.done_count == self.total_count

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "name": self.name,
            "goal": self.goal,
            "done_count": self.done_count,
            "total_count": self.total_count,
            "is_complete": self.is_complete,
            "items": [{"text": i.text, "done": i.done} for i in self.items],
        }


@dataclass
class Commit:
    """Legacy handoff commit entry."""
    number: int
    timestamp: str
    summary: str
    details: str

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "timestamp": self.timestamp,
            "summary": self.summary,
            "details": self.details,
        }


@dataclass
class Handoff:
    """Legacy handoff file (docs/handoff/*.md)."""
    filename: str
    commits: list[Commit]
    next_tasks: list[str]

    @property
    def headline(self) -> str:
        if self.commits:
            return self.commits[0].summary
        return "—"

    def to_dict(self) -> dict:
        return {
            "filename": self.filename,
            "headline": self.headline,
            "commits": [c.to_dict() for c in self.commits],
            "next_tasks": self.next_tasks,
        }


@dataclass
class ProjectData:
    name: str
    phases: list[Phase]
    handoffs: list[Handoff]
    current_tasks: list[dict] = field(default_factory=list)
    future_tasks: list[dict] = field(default_factory=list)
    past_tasks: list[dict] = field(default_factory=list)
    project_md: str = ""
    description: str = ""
    error: Optional[str] = None

    # Legacy compat
    @property
    def status(self) -> Optional[dict]:
        return self.current_tasks[0] if self.current_tasks else None

    @property
    def next_tasks(self) -> list[dict]:
        return self.future_tasks

    @property
    def history(self) -> list[dict]:
        return self.past_tasks

    def current_phase(self) -> Optional[Phase]:
        for phase in self.phases:
            if not phase.is_complete:
                return phase
        return self.phases[-1] if self.phases else None

    def to_dict(self) -> dict:
        cp = self.current_phase()
        return {
            "name": self.name,
            "phases": [p.to_dict() for p in self.phases],
            "current_phase": cp.to_dict() if cp else None,
            "handoffs": [h.to_dict() for h in self.handoffs],
            "current_tasks": self.current_tasks,
            "future_tasks": self.future_tasks,
            "past_tasks": self.past_tasks,
            "project_md": self.project_md,
            # Legacy compat keys
            "status": self.status,
            "next_tasks": self.next_tasks,
            "history": self.history,
            "description": self.description,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_roadmap(path: Path) -> list[Phase]:
    text = path.read_text(encoding="utf-8")
    phases: list[Phase] = []

    for section in re.split(r"^## ", text, flags=re.MULTILINE):
        m = re.match(r"Phase (\d+):\s*(.+)", section)
        if not m:
            continue

        number = int(m.group(1))
        name = m.group(2).strip()

        goal_m = re.search(r"^Goal:\s*(.+)", section, re.MULTILINE)
        goal = goal_m.group(1).strip() if goal_m else ""

        items: list[CheckItem] = []
        for item_m in re.finditer(r"^- \[(x| )\] (.+)", section, re.MULTILINE):
            done = item_m.group(1) == "x"
            text = item_m.group(2).strip().rstrip(" ✓").strip()
            items.append(CheckItem(text=text, done=done))

        phases.append(Phase(number=number, name=name, goal=goal, items=items))

    return phases


def parse_handoff(path: Path) -> Handoff:
    """Parse legacy handoff files (### Commit N format)."""
    text = path.read_text(encoding="utf-8")
    filename = path.stem
    commits: list[Commit] = []
    next_tasks: list[str] = []

    session_m = re.search(
        r"^## This Session\s*\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if session_m:
        for cs in re.split(r"^### ", session_m.group(1), flags=re.MULTILINE):
            cm = re.match(r"Commit (\d+) \((\w+)\) — (.+?)\n(.*)", cs, re.DOTALL)
            if not cm:
                continue
            commits.append(Commit(
                number=int(cm.group(1)),
                timestamp=cm.group(2),
                summary=cm.group(3).strip(),
                details=cm.group(4).strip(),
            ))

    next_m = re.search(
        r"^## Next Tasks\s*\n(.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if next_m:
        for task_m in re.finditer(r"^- \[ \] (.+)", next_m.group(1), re.MULTILINE):
            next_tasks.append(task_m.group(1).strip())

    return Handoff(filename=filename, commits=commits, next_tasks=next_tasks)


def load_project_description(project_dir: Path) -> str:
    """Extract first non-header paragraph from README.md."""
    readme = project_dir / "README.md"
    if not readme.exists():
        return ""
    try:
        text = readme.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            return stripped
        return ""
    except Exception:
        return ""


def load_project(project_dir: Path) -> ProjectData:
    name = project_dir.name

    # Try ROADMAP.md (legacy) or PROJECT.md (v2)
    roadmap_path = project_dir / "docs" / "ROADMAP.md"
    phases: list[Phase] = []
    if roadmap_path.exists():
        try:
            phases = parse_roadmap(roadmap_path)
        except Exception as e:
            return ProjectData(name=name, phases=[], handoffs=[], error=f"ROADMAP parse error: {e}")

    # Legacy handoffs
    handoffs: list[Handoff] = []
    handoff_dir = project_dir / "docs" / "handoff"
    if handoff_dir.exists():
        for hf in sorted(handoff_dir.glob("*.md"), reverse=True):
            try:
                handoffs.append(parse_handoff(hf))
            except Exception as e:
                handoffs.append(Handoff(
                    filename=hf.stem,
                    commits=[],
                    next_tasks=[f"Parse error: {e}"],
                ))

    # Task system v2
    current_tasks = load_current_tasks(project_dir)
    future_tasks = load_future(project_dir)
    past_tasks = load_past(project_dir)
    project_md = load_project_md(project_dir)
    description = load_project_description(project_dir)

    return ProjectData(
        name=name,
        phases=phases,
        handoffs=handoffs,
        current_tasks=current_tasks,
        future_tasks=future_tasks,
        past_tasks=past_tasks,
        project_md=project_md,
        description=description,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_all_projects() -> list[dict]:
    projects: list[ProjectData] = []
    for d in sorted(WORKSPACE_ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        # Recognize project if it has ROADMAP.md (legacy) or .mpm/ (v2)
        has_roadmap = (d / "docs" / "ROADMAP.md").exists()
        has_mpm = (d / ".mpm").is_dir()
        if not has_roadmap and not has_mpm:
            continue
        projects.append(load_project(d))
    return [p.to_dict() for p in projects]
