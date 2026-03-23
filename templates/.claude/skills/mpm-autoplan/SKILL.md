---
name: mpm-autoplan
description: |
  Auto-review pipeline — runs CEO, design, and eng review sequentially with
  auto-decisions using 6 decision principles. Surfaces taste decisions at a
  final approval gate. One command, fully reviewed plan out.
  Use when asked to "auto review", "autoplan", "run all reviews",
  "review this plan automatically", or "make the decisions for me".
  Proactively suggest when the user has a plan/feature request and wants the
  full review gauntlet without answering 15-30 intermediate questions.
---

# /mpm-autoplan — Auto-Review Pipeline

One command. Rough plan in, fully reviewed plan out.

/mpm-autoplan runs the CEO, design, and eng review skills at full depth — same rigor,
same sections, same methodology as running each skill manually. The only difference:
intermediate AskUserQuestion calls are auto-decided using the 6 principles below.
Taste decisions (where reasonable people could disagree) are surfaced at a final
approval gate.

---

## The 6 Decision Principles

These rules auto-answer every intermediate question:

1. **Choose completeness** — Ship the whole thing. Pick the approach that covers more edge cases.
2. **Boil lakes** — Fix everything in the blast radius (files modified by this plan + direct importers). Auto-approve expansions that are in blast radius AND < 1 day AI effort (< 5 files, no new infra).
3. **Pragmatic** — If two options fix the same thing, pick the cleaner one. 5 seconds choosing, not 5 minutes.
4. **DRY** — Duplicates existing functionality? Reject. Reuse what exists.
5. **Explicit over clever** — 10-line obvious fix > 200-line abstraction. Pick what a new contributor reads in 30 seconds.
6. **Bias toward action** — Merge > review cycles > stale deliberation. Flag concerns but don't block.

**Conflict resolution (context-dependent tiebreakers):**
- **CEO phase:** P1 (completeness) + P2 (boil lakes) dominate.
- **Eng phase:** P5 (explicit) + P3 (pragmatic) dominate.
- **Design phase:** P5 (explicit) + P1 (completeness) dominate.

---

## Decision Classification

Every auto-decision is classified:

**Mechanical** — one clearly right answer. Auto-decide silently.
Examples: run tests (always yes), reduce scope on a complete plan (always no).

**Taste** — reasonable people could disagree. Auto-decide with recommendation, but surface at the final gate. Three natural sources:
1. **Close approaches** — top two are both viable with different tradeoffs.
2. **Borderline scope** — in blast radius but 3-5 files, or ambiguous radius.
3. **Disagreements** — reviewer subagent recommends differently with a valid point.

---

## What "Auto-Decide" Means

Auto-decide replaces the USER'S judgment with the 6 principles. It does NOT replace
the ANALYSIS. Every section in the review skills must still be executed at the
same depth as the interactive version. The only thing that changes is who answers the
AskUserQuestion: you do, using the 6 principles, instead of the user.

**You MUST still:**
- READ the actual code, diffs, and files each section references
- PRODUCE every output the section requires (diagrams, tables, registries, artifacts)
- IDENTIFY every issue the section is designed to catch
- DECIDE each issue using the 6 principles (instead of asking the user)
- LOG each decision in the audit trail
- WRITE all required artifacts to disk

**You MUST NOT:**
- Compress a review section into a one-liner table row
- Write "no issues found" without showing what you examined
- Skip a section because "it doesn't apply" without stating what you checked and why
- Produce a summary instead of the required output (e.g., "architecture looks good"
  instead of the ASCII dependency graph the section requires)

"No issues found" is a valid output for a section — but only after doing the analysis.
State what you examined and why nothing was flagged (1-2 sentences minimum).
"Skipped" is never valid for a non-skip-listed section.

---

## Phase 0: Intake

### Step 1: Read context

- Read all `.mpm/docs/*.md` — foundation documents
- Read `.mpm/gstack/design-*.md` — office-hour design docs (if any)
- Read `.mpm/gstack/ceo-plans/*.md` — CEO plans (if any)
- Run `git log --oneline -30` and `git diff main --stat`
- Run `python3 .mpm/scripts/phase.py status` — current phase/goal state
- Detect UI scope: grep the plan/request for view/rendering terms (component, screen, form,
  button, modal, layout, dashboard, sidebar, nav, dialog). Require 2+ matches.

### Step 2: Determine pipeline

```
Always: Phase 1 (CEO) → Phase 3 (Eng)
If UI scope detected: Phase 1 (CEO) → Phase 2 (Design) → Phase 3 (Eng)
```

Output: "Here's what I'm working with: [plan summary]. UI scope: [yes/no].
Starting full review pipeline with auto-decisions."

---

## Phase 1: CEO Review (Strategy & Scope)

Run `/mpm-plan-ceo-review` at full depth.
Override: every AskUserQuestion → auto-decide using the 6 principles.

**Override rules:**
- Mode selection: SELECTIVE EXPANSION
- Premises: accept reasonable ones (P6), challenge only clearly wrong ones
- **GATE: Present premises to user for confirmation** — this is the ONE AskUserQuestion
  that is NOT auto-decided. Premises require human judgment.
- Alternatives: pick highest completeness (P1). If tied, pick simplest (P5).
  If top 2 are close → mark TASTE DECISION.
- Scope expansion: in blast radius + <1d AI → approve (P2). Outside → defer to TODOS.md (P3).
  Duplicates → reject (P4). Borderline (3-5 files) → mark TASTE DECISION.
- All review sections: run fully, auto-decide each issue, log every decision.

**Required outputs from Phase 1:**
- Premise challenge with specific premises named and evaluated
- All applicable review sections have findings OR explicit "examined X, nothing flagged"
- Error & Rescue Registry table (or noted N/A with reason)
- Failure Modes Registry table (or noted N/A with reason)
- "NOT in scope" section
- "What already exists" section
- Dream state delta
- Completion Summary

---

## Phase 2: Design Review (conditional — skip if no UI scope)

Run `/mpm-plan-design-review` at full depth — all 7 dimensions.
Override: every AskUserQuestion → auto-decide using the 6 principles.

**Override rules:**
- Focus areas: all relevant dimensions (P1)
- Structural issues (missing states, broken hierarchy): auto-fix (P5)
- Aesthetic/taste issues: mark TASTE DECISION
- Design system alignment: auto-fix if DESIGN.md exists and fix is obvious

**Required outputs from Phase 2:**
- All 7 dimensions evaluated with before/after scores
- Issues identified and auto-decided
- Completion Summary with overall design score

---

## Phase 3: Eng Review

Run `/mpm-plan-eng-review` at full depth.
Override: every AskUserQuestion → auto-decide using the 6 principles.

**Override rules:**
- Scope challenge: never reduce a complete plan (P2)
- Architecture choices: explicit over clever (P5)
- Test gaps: identify → decide whether to add or defer with rationale and principle → log
- TODOS.md: collect all deferred scope expansions from all phases, auto-write

**Required outputs from Phase 3:**
- Scope challenge with actual code analysis
- Architecture ASCII diagram
- Test diagram mapping codepaths to coverage
- "NOT in scope" section
- "What already exists" section
- Failure modes registry with critical gap flags
- Completion Summary
- TODOS.md updates (collected from all phases)

---

## Decision Audit Trail

After each auto-decision, log it. Write to `.mpm/gstack/autoplan-audit-{datetime}.md`:

```markdown
# /mpm-autoplan Decision Audit Trail
Started: [timestamp] | Branch: [branch]

| # | Phase | Decision | Principle | Rationale | Rejected |
|---|-------|----------|-----------|-----------|----------|
| 1 | CEO   | Accept premise: "X is the right problem" | P6 (action) | Evidence supports it | — |
| 2 | CEO   | Choose Approach A over B | P1 (completeness) | A covers edge cases | B: simpler but 80% coverage |
| 3 | CEO   | TASTE: Borderline scope expansion | P2 (boil lakes) | 4 files, ambiguous radius | Deferred option also viable |
```

Write one row per decision incrementally (via Edit). This keeps the audit on disk,
not accumulated in conversation context.

---

## Pre-Gate Verification

Before presenting the Final Approval Gate, verify that required outputs were actually
produced. Check each item:

**Phase 1 (CEO) outputs:**
- [ ] Premise challenge with specific premises named (not just "premises accepted")
- [ ] All applicable review sections have findings OR explicit "examined X, nothing flagged"
- [ ] Error & Rescue Registry table produced (or noted N/A with reason)
- [ ] Failure Modes Registry table produced (or noted N/A with reason)
- [ ] "NOT in scope" section written
- [ ] "What already exists" section written
- [ ] Dream state delta written
- [ ] Completion Summary produced

**Phase 2 (Design) outputs — only if UI scope detected:**
- [ ] All 7 dimensions evaluated with scores
- [ ] Issues identified and auto-decided

**Phase 3 (Eng) outputs:**
- [ ] Scope challenge with actual code analysis (not just "scope is fine")
- [ ] Architecture ASCII diagram produced
- [ ] Test diagram mapping codepaths to test coverage
- [ ] "NOT in scope" section written
- [ ] "What already exists" section written
- [ ] Failure modes registry with critical gap assessment
- [ ] Completion Summary produced

**Audit trail:**
- [ ] Decision Audit Trail has at least one row per auto-decision (not empty)

If ANY checkbox above is missing, go back and produce the missing output. Max 2
attempts — if still missing after retrying twice, proceed to the gate with a warning
noting which items are incomplete. Do not loop indefinitely.

---

## Phase 4: Final Approval Gate

**STOP here and present the final state to the user.**

```
## /mpm-autoplan Review Complete

### Plan Summary
[1-3 sentence summary]

### Decisions Made: [N] total ([M] auto-decided, [K] choices for you)

### Your Choices (taste decisions)
[For each taste decision:]
**Choice [N]: [title]** (from [phase])
I recommend [X] — [principle]. But [Y] is also viable:
  [1-sentence downstream impact if you pick Y]

### Auto-Decided: [M] decisions [see audit trail at .mpm/gstack/autoplan-audit-{datetime}.md]

### Review Scores
- CEO: [summary]
- Design: [summary or "skipped, no UI scope"]
- Eng: [summary]

### Deferred to TODOS.md
[Items auto-deferred with reasons]
```

**Cognitive load management:**
- 0 taste decisions: skip "Your Choices" section
- 1-7 taste decisions: flat list
- 8+: group by phase. Add warning: "This plan had unusually high ambiguity ([N] taste decisions). Review carefully."

AskUserQuestion options:
- A) Approve as-is (accept all recommendations)
- B) Approve with overrides (specify which taste decisions to change)
- C) Interrogate (ask about any specific decision)
- D) Revise (the plan itself needs changes — re-run affected phases, max 3 cycles)
- E) Reject (start over)

---

## Phase 5: Write Foundation Documents

On approval, synthesize the review outputs into foundation documents:

1. **`.mpm/docs/PROJECT.md`** — update with problem statement, demand evidence, vision, scope decisions from CEO review
2. **`.mpm/docs/ARCHITECTURE.md`** — update with architecture decisions, data flow diagrams, error handling patterns from Eng review

If these documents already exist, update the relevant sections rather than overwriting.

Then create tasks via `/mpm-task-write` based on the approved plan.

---

## Important Rules

- **Never abort.** The user chose /mpm-autoplan. Respect that choice. Surface all taste decisions, never redirect to interactive review.
- **Premises are the one gate.** The only non-auto-decided AskUserQuestion is the premise confirmation in Phase 1.
- **Log every decision.** No silent auto-decisions. Every choice gets a row in the audit trail.
- **Full depth means full depth.** Do not compress or skip sections from the review skills. "Full depth" means: read the code the section asks you to read, produce the outputs the section requires, identify every issue, and decide each one. A one-sentence summary of a section is not "full depth" — it is a skip. If you catch yourself writing fewer than 3 sentences for any review section, you are likely compressing.
- **Artifacts are deliverables.** Failure modes registry, error/rescue table, ASCII diagrams — these must exist on disk or in the plan file when the review completes. If they don't exist, the review is incomplete.
- **Sequential order.** CEO → Design → Eng. Each phase builds on the last.

---

Always respond in the user's language.
