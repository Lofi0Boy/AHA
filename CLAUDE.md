# MPM — Development Rules

Inherits common rules from `../CLAUDE.md`.

Respond in Korean. Keep all documents in English.

---

## Session Start

Read the latest file in `docs/handoff/` and `docs/ROADMAP.md` to understand the current state.
Refer to `docs/ARCHITECTURE.md` and `README.md` as needed.

---

## Project Structure

This project manages other projects in MpmWorkspace. Do not modify files in sibling project directories unless explicitly instructed.

---

## Code Guidelines

- Daemon must never silently swallow errors — surface them loudly so failures are obvious.
- State must be persisted to disk on every change (crash recovery).
- All sub-agent communication is async — no blocking waits.
