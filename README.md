# MPM — Multi-Project Manager

An orchestration system for managing multiple Claude Code agents across projects in the MpmWorkspace.

MPM acts as the central control plane: it spawns and manages per-project Claude Code sessions, verifies task results, updates project documentation autonomously, and communicates with the user through multiple channels (CLI, web dashboard, Telegram).

---

## Architecture Overview

```
[MPM Daemon — Python process, always running]
  ├── Per-project Claude Code sessions (one per project, persistent)
  ├── Async orchestration (parallel sub-agents, as_completed)
  ├── Result verification engine
  ├── ROADMAP + handoff auto-update
  └── I/O Multiplexer
        ├── Web Dashboard (renders CLI output)
        └── Telegram Bridge (toggle on/off)
```

---

## Projects Managed

| Project | Description |
|---------|-------------|
| `saksak-kimchi` | Kimchi premium arbitrage bot |
| `JHomelab_server` | Home server backend |
| `JHomelab_app` | Home lab Android/web app |

---

## Components (planned)

| Directory | Role |
|-----------|------|
| `daemon/` | Core orchestration process |
| `dashboard/` | Web UI for monitoring and control |
| `gateway/` | I/O multiplexer (CLI / Telegram bridge) |

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Agent execution | Claude Code CLI (`--resume`) | Full local file control, no tool reimplementation |
| Session model | One persistent session per project | Avoid repeated doc loading; compaction triggers handoff + session reset |
| PM Agent | Claude Code CLI (cwd: MpmWorkspace/) | Needs access to all project files |
| State management | Python daemon holds state | Claude API calls are stateless; daemon provides continuity |
| User communication | CLI as base; dashboard renders output; Telegram bridges I/O | Single source of truth, channel-agnostic |
| Parallel execution | `asyncio.as_completed` | Handle sub-agent completions as they arrive, not serially |
