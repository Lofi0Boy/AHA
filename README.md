# MPM — Multi-Project Manager

A dashboard and orchestration system for managing all projects in MpmWorkspace.

Phase 1 is a read-only web dashboard: it reads each project's handoff files and ROADMAP, and displays everything in a multi-column thread view — one column per project, showing progress and next tasks at a glance.

Later phases add autonomous agent control (MPM daemon spawning Claude Code sessions per project) and communication gateways (Telegram, live CLI output).

---

## Dashboard (Phase 1)

```
┌─────────────────┬─────────────────┬─────────────────┐
│  saksak-kimchi  │ JHomelab_server │  JHomelab_app   │
│                 │                 │                 │
│ Phase 1 ██░░░░  │ Phase 1 ██████  │ Phase 1 ██████  │
│ 11/16 done      │ complete ✓      │ complete ✓      │
│                 │                 │                 │
│ Next:           │                 │                 │
│ · Live test run │                 │                 │
│ · Return coin   │                 │                 │
│   selector      │                 │                 │
│                 │                 │                 │
│ ── handoff ──   │                 │                 │
│ 26/03/13        │ 26/03/13        │ 26/03/13        │
│ Doc restructure │ Scripts reorg   │ Doc restructure │
│ ...             │ ...             │ ...             │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## Architecture Overview

```
[MPM Daemon — Python process, always running]         ← Phase 2
  ├── Per-project Claude Code sessions (one per project, persistent)
  ├── Async orchestration (parallel sub-agents, as_completed)
  ├── Result verification engine
  ├── ROADMAP + handoff auto-update
  └── I/O Multiplexer                                 ← Phase 3
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

## Components

| Directory | Phase | Role |
|-----------|-------|------|
| `dashboard/` | 1 | Web UI — read-only project status view |
| `daemon/` | 2 | Core orchestration process |
| `gateway/` | 3 | I/O multiplexer (CLI / Telegram bridge) |

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
