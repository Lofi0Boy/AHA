---
name: mpm-init-design
description: Initialize DESIGN.md (concept/rules) and design token code files — from project analysis, reference URL, or user description.
---

# Initialize Design System

Create two outputs:
1. **DESIGN.md** — design concept, principles, component patterns, rules (human/AI readable document)
2. **Token code file** — initial design token values in the project's tech stack format (CSS variables, Tailwind config, JSON, etc.)

Tokens created here are a **starting point**. They will be refined and expanded during development as the Planner creates tasks.

---

## Step 1: Understand the project direction

Read PROJECT.md and ARCHITECTURE.md to understand:
- What kind of product is this? (dashboard, landing page, admin panel, mobile app, etc.)
- Who are the users?
- What tech stack is used? (React+Tailwind, vanilla CSS, React Native, etc.)

---

## Step 2: Get design input from user

Ask the user for design direction. Accept **either or both**:

### Option A: Reference website URL
1. User provides URL(s) of sites they like
2. Use WebFetch to read the page's CSS — extract actual color values, fonts, spacing, radius, shadows
3. Use these extracted values as the basis for tokens

### Option B: Describe the feeling
1. User describes what they want: "minimal", "glassmorphism", "dark corporate", etc.
2. AI generates initial tokens based on the description

### Option C: Analyze current project
Use when the project already has UI code.
1. Scan existing stylesheets, component files, theme configs
2. Extract or document existing design patterns
3. Formalize into tokens if not already structured

If the user provides both a URL and a description, combine them — extract from the URL and adjust to match the described feeling.

---

## Step 3: Generate token code file

Based on the project's tech stack (detected from ARCHITECTURE.md or package.json):

| Tech stack | Token file format | Example path |
|------------|------------------|--------------|
| Tailwind CSS | `tailwind.config.ts` theme extend | `tailwind.config.ts` |
| Vanilla CSS | CSS custom properties | `src/styles/tokens.css` |
| SCSS/Sass | Variables file | `src/styles/_tokens.scss` |
| React Native | JS/TS theme object | `src/theme/tokens.ts` |
| Any | W3C DTCG JSON | `tokens.json` |

**Start with essential tokens only:**
- Colors: primary, secondary, background, text, border (minimum)
- Typography: font family, 2-3 size levels
- Spacing: base unit
- Border radius: 1-2 values

More tokens will be added as development progresses and new components are designed.

Place the token file in the project's existing style directory. If none exists, create one that fits the project structure.

---

## Step 4: Write DESIGN.md

Write to `.mpm/docs/DESIGN.md` — this is a **concept and rules document**, not the token source of truth.

```markdown
# Design System

## Concept
Overall design direction and principles.

## Source
Where the design originated from (e.g., "Inspired by example.com" or "Glassmorphism style per user request").

## Token File
Path to the actual token code file: `src/styles/tokens.css` (or wherever it was placed).
This is the single source of truth for token values.

## Component Patterns
(To be filled as components are designed during development.)

## Rules
Project-specific design constraints and decisions.
```

---

## Step 5: Confirmation

Show both DESIGN.md and the token code file to the user for review.
Apply any corrections before finalizing.

---

Always respond in the user's language.
