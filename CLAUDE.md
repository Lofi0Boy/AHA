# MPM — Development Rules

Inherits common rules from `../CLAUDE.md`.

---

## Project Boundary

This project manages other projects in MpmWorkspace. Do not modify files in sibling project directories unless explicitly instructed.

---

## Code Guidelines

- Daemon must never silently swallow errors — surface them loudly so failures are obvious.
- State must be persisted to disk on every change (crash recovery).
- All sub-agent communication is async — no blocking waits.
