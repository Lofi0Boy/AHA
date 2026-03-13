# ROADMAP

## Overview
Orchestration system for MpmWorkspace. MPM daemon manages per-project Claude Code sessions, verifies task results, and communicates with the user via web dashboard and Telegram. Currently in **Phase 1**.

---

## Phase 1: Core Daemon

Goal: Working daemon that can spawn and manage Claude Code sessions per project, execute tasks in parallel, and route results to the user.

- [ ] Project scaffold (directory structure, CLAUDE.md, git init)
- [ ] `daemon/orchestrator.py` — spawn Claude Code CLI sessions, maintain per-project session IDs
- [ ] `daemon/state.py` — in-memory + disk state store
- [ ] Parallel task execution (`asyncio.as_completed`)
- [ ] Session reset on compaction (detect compaction event → terminate → respawn with handoff)
- [ ] `daemon/verifier.py` — git log / test run / health check verification per task type
- [ ] PM Agent loop — reads all project ROADMAPs, determines next tasks, evaluates results

---

## Phase 2: Gateway (I/O Multiplexer)

Goal: Web dashboard renders daemon output; Telegram bridge toggles on/off.

- [ ] `gateway/multiplexer.py` — route Claude CLI stdout to registered channels
- [ ] Web dashboard — basic log/output renderer
- [ ] `gateway/telegram.py` — forward output to Telegram; inject replies as stdin
- [ ] Telegram toggle setting

---

## Phase 3: Dashboard

Goal: Full web UI for monitoring project status, active sessions, pending decisions, and task history.

- [ ] Project status cards (ROADMAP progress per project)
- [ ] Active session viewer (live output per sub-agent)
- [ ] Pending decisions queue (items awaiting user input)
- [ ] Task history log

---

## External Connections

Part of the **MpmWorkspace** alongside `saksak-kimchi`, `JHomelab_server`, `JHomelab_app`.
MPM manages these projects but has no runtime dependency on them.
