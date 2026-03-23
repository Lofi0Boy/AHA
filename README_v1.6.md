# MPM — Multi Project Manager

AI가 코드를 짜는 동안 사람은 컴퓨터 앞에 붙어있어야 한다. 답변이 끝나면 확인하고, 다음 지시를 내리고, 다른 프로젝트로 넘어가면 아까 뭘 하고 있었는지 잊어버린다. 프로젝트가 2개만 돼도 context switching 지옥이다.

**MPM은 인간의 기획·검토 ↔ AI 개발 간의 비동기 시스템이다.**

- AI는 혼자 task를 뽑아서 개발하고, 자체 리뷰까지 마친다
- 인간은 자기 속도로 기획하고, 쌓인 결과물을 한꺼번에 검토한다
- 컴퓨터 앞에 안 붙어있어도 개발이 멈추지 않는다

비동기가 성립하려면 두 가지가 보장돼야 한다:

1. **AI가 혼자서도 쓸 만한 결과를 내야 한다** — 개발 완성도, 디자인 준수, 자가 검증까지. 사람이 돌아왔을 때 "다 다시 해"가 나오면 비동기의 의미가 없다.
2. **사람이 개발 AI와 직접 대화하지 않아도 일을 시킬 수 있어야 한다** — Planner AI와의 대화만으로 태스크가 생성되고, 개발 AI가 알아서 뽑아가서 실행한다.

이걸 보장하기 위해 foundation 문서(제품 정의, 아키텍처, 디자인 시스템, 검증 방법)로 AI의 판단 기준을 잡고, 다단계 리뷰(기능·코드·UX·디자인)로 품질을 걸러내고, 대시보드로 인간에게 리뷰 데이터를 보여준다. 스킬과 외부 도구가 많아 보이지만, 전부 이 두 가지 보장을 위한 것이다.

**v1.6** — [gstack](https://github.com/garrytan/gstack)의 sprint review 방법론과 [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)의 design intelligence 엔진을 통합해서, 제품 정의부터 코드 리뷰까지 품질 게이트를 강화했다.

---

## Sprint Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PROJECT INIT                                │
│                                                                     │
│  /mpm-init                                                          │
│    Step 1-2: Scan + Share understanding                             │
│    Step 3:   Project Documentation                                  │
│      3a. /mpm-office-hour        → design doc (.mpm/gstack/)       │
│      3b. /mpm-plan-ceo-review    → CEO plan (.mpm/gstack/ceo-plans/)│
│      3c. /mpm-plan-eng-review    → engineering lock-in              │
│      3d. Write PROJECT.md + ARCHITECTURE.md                         │
│    Step 4:   /mpm-init-design    → DESIGN.md + tokens/             │
│    Step 5:   VERIFICATION.md                                        │
│    Step 6:   Define Phase 1                                         │
│    Step 7:   Define Goals + Tasks (user approves before creation)   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                         TASK LIFECYCLE                               │
│                                                                     │
│  future ──pop──→ dev ──result──→ agent-review ──pass──→ human-review│
│                   ↑                   │                       │     │
│                   └───────fail────────┘                 approve/    │
│                                       │                reject/     │
│                                    3x fail──escalate──→ discard    │
│                                                           │        │
│                                                           ↓        │
│                                                         past       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### PPGT Hierarchy

```
Project (PROJECT.md)
  └─ Phase (phases.json)
       └─ Goal (phases.json)
            └─ Task (future/current/review/past)
```

| Level | What it is | Who creates | Example |
|-------|-----------|-------------|---------|
| **Project** | Name + description + vision | Human + Planner | "MPM — Multi Project Manager" |
| **Phase** | Milestone with verifiable completion | Planner proposes, human approves | "MVP Dashboard" |
| **Goal** | User-facing capability within a phase | Planner writes | "Live task board with drag-and-drop" |
| **Task** | Atomic work unit (single function, 1-2 evidence) | Planner writes | "Add WebSocket endpoint for task updates" |

### Foundation Documents

All stored in `.mpm/docs/`. Injected into every session via `hook-session-start.sh`.

| Document | Purpose | Created by |
|----------|---------|------------|
| **PROJECT.md** | Problem, users, demand evidence, vision, scope, success criteria | /mpm-office-hour + /mpm-plan-ceo-review |
| **ARCHITECTURE.md** | System design, component boundaries, data flow, tech decisions | /mpm-plan-eng-review |
| **DESIGN.md** + `tokens/` | Design system (aesthetic, typography, color, spacing, motion) + token code files | /mpm-init-design |
| **VERIFICATION.md** | Available verification tools and methods for this project | /mpm-init Step 5 |
| **FEEDBACK.md** | Accumulated human review verdicts — planner and reviewer learn from past judgments | Auto-appended on every human review |

---

## Project Initialization

### Step 3: Product Definition Pipeline (gstack-based)

The init process runs three review skills in sequence. Each reads the previous skill's output.

#### /mpm-office-hour

Two modes: **Startup** (six forcing questions — demand reality, status quo, specificity, wedge, observation, future-fit) and **Builder** (generative brainstorming). Includes:

- Anti-sycophancy rules — takes positions, challenges premises, pushes twice
- Premise challenge — is this the right problem?
- Mandatory alternatives — 2-3 implementation approaches with effort/risk
- Visual sketch — HTML wireframe rendered via browse tool (if available)
- Spec review loop — subagent adversarial review (5 dimensions, max 3 iterations)

**Output:** Design document saved to `.mpm/gstack/design-{datetime}.md`

#### /mpm-plan-ceo-review

Four modes: Scope Expansion, Selective Expansion, Hold Scope, Scope Reduction. Includes:

- Pre-review system audit (git log, TODOs, existing code)
- Nuclear scope challenge + premise challenge
- 10-section review: architecture, errors, security, data flow, code quality, tests, performance, observability, deployment, long-term trajectory
- Design & UX review (Section 11, if UI scope detected)
- Dream state mapping (current → plan → 12-month ideal)

**Output:** CEO plan saved to `.mpm/gstack/ceo-plans/{date}-{feature-slug}.md`

#### /mpm-plan-eng-review

Locks in the execution plan. Includes:

- Scope challenge (complexity check: 8+ files or 2+ new classes = smell)
- Search check (built-in exists? current best practice? known footguns?)
- 4-section review: architecture, code quality, tests, performance
- Failure modes registry (no test + no error handling + silent = critical gap)

**Output:** Review findings in completion summary, feeds into ARCHITECTURE.md

### Step 4: Design System (ui-ux-pro-max + gstack design-consultation)

#### /mpm-init-design

Combines data-driven recommendations with AI design consultation:

1. **search.py** (161 industry rules, 67 styles, 161 color palettes, 57 font pairings) generates a baseline recommendation
2. **Design consultant** adjusts for project context with SAFE/RISK breakdown
3. **Competitive research** via WebSearch + browse tool (optional)
4. **HTML preview page** with realistic product mockups, light/dark toggle
5. **Coherence validation** — if user changes one section, checks rest still works

**Output:** `.mpm/docs/DESIGN.md` + `.mpm/docs/tokens/`

---

## Task System

### Task Writing (/mpm-task-write)

| Rule | Detail |
|------|--------|
| **Granularity** | Single function, verifiable with 1-2 evidence items |
| **Split triggers** | Evidence ≥ 3, file areas ≥ 2, AND-connected requirements, multiple verbs |
| **Foundation grounding** | Planner reads all `.mpm/docs/` before writing, cites specific sections |
| **Self-contained prompts** | Dev agent can start from prompt alone without reading docs |
| **UI tasks** | Must reference DESIGN.md, tokens/, and instruct dev to follow `/ui-ux-pro-max` guidelines |

### Task Schema

```json
{
  "id": "unique_id",
  "title": "One-line summary",
  "prompt": "Context and non-goals",
  "goal": "Verifiable acceptance criteria (set by planner)",
  "approach": "How to implement (set by dev)",
  "verification": "How to verify (set by planner)",
  "result": "Actual outcome (set by dev)",
  "memo": "Session summary (set by dev)",
  "status": "future|dev|agent-review|human-review|past",
  "agent_reviews": [],
  "human_review": null,
  "created": "YYMMDDHHmm",
  "session_id": null,
  "parent_goal": "goal_id"
}
```

### Task Lifecycle

| Status | Location | Meaning |
|--------|----------|---------|
| `future` | `future.json` | Queued |
| `dev` | `current/{session}.json` | Developer working |
| `agent-review` | `current/{session}.json` | Reviewer verifying |
| `human-review` | `review/{task_id}.json` | Awaiting human approval (dev freed) |
| `past` | `past/YYMMDD.json` | Done |

---

## Agent Review System

The reviewer is an **orchestrator** that determines which reviews are needed and runs them all, accumulating failures.

```
reviewer (orchestrator)
  ├── Analyze task → is it UI? (git diff for .tsx/.jsx/.vue/.css/.html)
  ├── /mpm-review-functional  (always)  — does it actually work?
  ├── /mpm-review-code        (always)  — code quality + security
  ├── /mpm-review-ux          (UI only) — usability + accessibility + states
  ├── /mpm-review-design      (UI only) — token compliance + AI slop detection
  └── Aggregate → ALL must pass, or accumulated FAIL reasons returned
```

### /mpm-review-functional
- Run task verification methods yourself (don't trust dev's claim)
- Test unhappy paths: bad input, missing data, errors, concurrent access
- Check for silent errors in console/logs
- Verify data flow: create → read → update → delete

### /mpm-review-code
- Architecture compliance (ARCHITECTURE.md patterns)
- Error handling (named exceptions, no catch-all)
- DRY violations, security (hardcoded secrets, injection vectors)
- Complexity (>5 branches = suggest refactor)

### /mpm-review-ux (UI tasks only)
- First impression test: can you understand the page in 3 seconds?
- Click every button, fill every form, trigger every state
- State coverage: empty, loading, error, success, partial — all must exist
- Accessibility: contrast ≥ 4.5:1, keyboard nav, focus states, 44px touch targets
- Edge cases: 47-char names, 0 results, 10k results, special characters
- Responsive: desktop + mobile + tablet screenshots (mandatory)

### /mpm-review-design (UI tasks only)
- Token compliance: grep for hardcoded hex/px values in changed files
- DESIGN.md alignment: typography, color, spacing, motion
- AI slop detection: 10-pattern blacklist (instant FAIL)
- Visual consistency: does this page belong to the same app?

**Verdict:** PASS only if ALL reviews pass. When in doubt, FAIL. Human's time is the most expensive resource.

---

## Agents

### Planner

| | Detail |
|---|---|
| Model | Opus |
| Tools | Read, Grep, Glob, restricted Bash, Write, Edit, WebSearch, WebFetch |
| Cannot | Edit source code |
| Skills | mpm-init, mpm-init-design, mpm-task-write, mpm-recycle, mpm-office-hour, mpm-plan-ceo-review, mpm-plan-eng-review, mpm-plan-design-review |

### Developer (default session)

| | Detail |
|---|---|
| Tools | All tools |
| Cannot | `task.py add` (must go through planner), `task.py complete` (human only) |
| Skills | mpm-next, mpm-autonext, ui-ux-pro-max, design-system, ui-styling |

### Reviewer (orchestrator)

| | Detail |
|---|---|
| Tools | Read, Grep, Glob, restricted Bash, Skill (review skills only) |
| Cannot | Edit, Write, Agent (read-only) |
| maxTurns | 30 |
| Skills | mpm-review-functional, mpm-review-code, mpm-review-ux, mpm-review-design |

---

## Skill Catalog

### MPM Core (20 skills)

| Category | Skill | Purpose |
|----------|-------|---------|
| **Init** | mpm-init | 7-step project initialization |
| | mpm-init-design | Design system creation (search.py + AI consultant) |
| **Planning** | mpm-office-hour | Product definition (startup/builder modes) |
| | mpm-plan-ceo-review | Strategic review (4 scope modes, 11-section review) |
| | mpm-plan-eng-review | Engineering review (4-section, failure modes) |
| | mpm-plan-design-review | Design plan review (7-pass, 0-10 rating) |
| **Task** | mpm-task-write | Task creation with granularity rules |
| | mpm-next | Pop and execute next task |
| | mpm-autonext | Auto-process task queue |
| | mpm-recycle | Recycle rejected tasks |
| **Review** | mpm-review-functional | Functionality verification |
| | mpm-review-code | Code quality + security |
| | mpm-review-ux | UX usability + accessibility |
| | mpm-review-design | Design consistency + AI slop detection |

### Design Intelligence (ui-ux-pro-max, 7 skills)

| Skill | Purpose |
|-------|---------|
| ui-ux-pro-max | Design engine: search.py (161 products, 67 styles, 161 palettes, 57 fonts) + 99 UX rules + pre-delivery checklist |
| design-system | Token architecture (primitive → semantic → component), CSS variables, Tailwind integration |
| ui-styling | shadcn/ui components + Tailwind CSS utilities + canvas design |
| brand | Brand voice, visual identity, messaging, asset management |
| design | Unified design: logo (55 styles, Gemini AI), CIP (50 deliverables), social photos, icons |
| banner-design | Banner creation (22 styles: social, ads, web, print) |
| slides | Presentation generation with Chart.js + design tokens |

---

## Harnessing Strategy

### Control Layers

```
Deterministic (guaranteed)          Non-deterministic (agent judgment)
─────────────────────────           ──────────────────────────────────
Hooks                               Agent definitions (.claude/agents/)
  Shell scripts on lifecycle           Frontmatter: tools, model
  events. Can block, inject,           Body: behavioral guidance
  run commands. Cannot be
  ignored.                          Skills (.claude/skills/)
                                       Procedural knowledge
Scripts (.mpm/scripts/)                Agent interprets steps
  task.py, phase.py
  Schema enforcement               Rules (.claude/rules/)
  File locking                        Always loaded, shared constraints
```

### Defense Table

| Failure | Defense |
|---------|---------|
| Dev edits without task | `hook-pretool-task-check.sh` BLOCKS Edit/Write |
| Dev doesn't spawn reviewer | `hook-review.sh` re-triggers on every Stop |
| Dev skips review via `task.py complete` | `task.py` enforces: only `review/` → past |
| Reviewer doesn't call `task.py review` | Spawn counter tracks attempts, escalates after 3 |
| Reviewer passes bad work | Human review catches it; FEEDBACK.md calibrates future reviews |
| Reviewer misses UX/design issues | Separate review skills (ux, design) with specific checklists |
| 3x reviewer fail | `task.py escalate` → `review/` for human judgment |
| Planner writes vague tasks | task-write skill forces foundation doc grounding + self-contained prompts |
| Planner misses rejected tasks | `hook-planner-start.sh` detects and directs |
| Agent ignores skill steps | No defense (inherent LLM limitation) |

---

## Async Operations

### Planner ↔ Dev (async)

```
Terminal 1: claude --agent planner    → creating tasks in future.json
Terminal 2: dev with /mpm-autonext    → popping and executing tasks
```

`task.py` uses `fcntl.flock` on all `future.json` operations to prevent corruption.

### Dev ↔ Reviewer (sync)

Reviewer runs as a subagent inside the dev session. Immediate feedback enables immediate fixes.

### Dev ↔ Human Review (async)

After reviewer passes, task moves to `review/`. Dev is freed for the next task. Human reviews via dashboard at their own pace.

---

## File Structure

```
.mpm/
├── data/
│   ├── future.json              # Task queue
│   ├── current/                 # Dev working (one per session)
│   ├── review/                  # Awaiting human review
│   ├── past/                    # Completed tasks by date
│   ├── phases.json              # Phase/Goal hierarchy
│   └── reviews/                 # Reviewer screenshots
├── docs/
│   ├── PROJECT.md               # Product definition + vision
│   ├── ARCHITECTURE.md          # Engineering patterns + conventions
│   ├── DESIGN.md                # Design system + aesthetic direction
│   ├── VERIFICATION.md          # Verification methods
│   ├── FEEDBACK.md              # Human review history
│   └── tokens/                  # Design token code files (CSS/JS/JSON)
├── gstack/
│   ├── design-{datetime}.md     # Office-hour design documents
│   └── ceo-plans/               # CEO review plans
└── scripts/
    ├── task.py                  # Task state machine
    ├── phase.py                 # Phase/Goal operations
    └── hook-*.sh                # Lifecycle hooks

.claude/
├── agents/
│   ├── planner.md               # Planning agent
│   └── reviewer.md              # Review orchestrator
├── skills/
│   ├── mpm-*/                   # MPM core skills (14)
│   ├── ui-ux-pro-max/           # Design engine + search.py + data/
│   ├── design-system/           # Token architecture
│   ├── ui-styling/              # shadcn/ui + Tailwind
│   ├── brand/                   # Brand identity
│   ├── design/                  # Logo, CIP, social, icons
│   ├── banner-design/           # Banner creation
│   └── slides/                  # Presentations
├── rules/
│   └── mpm-workflow.md          # Task workflow (loaded every session)
└── settings.json                # Hook definitions
```

---

## Hook Reference

| Hook Event | Script | Action |
|------------|--------|--------|
| SessionStart | `hook-notify.sh active` | Dashboard status → active |
| SessionStart | `hook-init-check.sh` | Prompt planner if PROJECT.md missing |
| SessionStart | `hook-session-start.sh` | Inject all `.mpm/docs/*.md` into context |
| SessionStart | `hook-is-native-planner.sh` | Route to planner hook if `--agent planner` |
| SubagentStart (planner) | `hook-planner-start.sh` | Inject docs + status + gap directive |
| SubagentStart (reviewer) | `hook-reviewer-start.sh` | Inject task + docs + tokens + FEEDBACK + git diff |
| UserPromptSubmit | `hook-notify.sh working` | Dashboard status → working |
| UserPromptSubmit | `hook-task-reminder.sh` | Show current task or "spawn @planner" |
| PreToolUse (Edit\|Write) | `hook-pretool-task-check.sh` | BLOCK if no task (`.mpm/`/`.claude/` exempt) |
| PermissionRequest | `hook-notify.sh waiting` | Dashboard status → waiting |
| Stop | `hook-notify.sh waiting` | Dashboard status → waiting |
| Stop | `hook-review.sh` | Trigger reviewer if `agent-review` |
| Stop | `hook-autonext-stop.sh` | Auto-next queue management |

---

## Installation

```bash
uv tool install git+https://github.com/Lofi0Boy/MPM.git
mpm onboard      # port, timezone, workspace
mpm dashboard    # start web UI
mpm init         # initialize a project
```

### Dependencies (optional)

| Dependency | Used by | Install |
|------------|---------|---------|
| gstack browse tool | Visual sketches, design review screenshots | `git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup` |
| Headless Chrome | Screenshots (fallback if browse unavailable) | `apt install google-chrome-stable` or `brew install --cask google-chrome` |
