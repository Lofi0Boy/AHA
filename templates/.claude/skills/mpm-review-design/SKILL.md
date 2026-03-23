---
name: mpm-review-design
description: Design consistency review — token compliance, DESIGN.md alignment, AI slop detection, visual consistency. UI tasks only.
---

# Design Consistency Review

Verify the implementation matches the project's design system. Read DESIGN.md and tokens/ from the injected context before starting.

## 1. Token compliance

**No hardcoded values allowed.** Scan changed files for violations:

```bash
# Find hardcoded colors
git diff --name-only | xargs grep -n '#[0-9a-fA-F]\{3,8\}' 2>/dev/null | head -20

# Find hardcoded pixel values that should use spacing tokens
git diff --name-only | xargs grep -n '[^0-9]px' 2>/dev/null | grep -vE 'border.*1px|0px' | head -20

# Find hardcoded font families
git diff --name-only | xargs grep -n 'font-family' 2>/dev/null | head -10
```

For each finding: does it use a token from `.mpm/docs/tokens/`, or is it hardcoded? Hardcoded values that should be tokens → FAIL.

## 2. DESIGN.md alignment

Compare the implementation against DESIGN.md:

| DESIGN.md section | Check |
|-------------------|-------|
| **Aesthetic Direction** | Does the overall feel match? |
| **Typography** | Are the specified fonts used? Correct roles (heading vs body)? |
| **Color** | Primary, secondary, semantic colors match? |
| **Spacing** | Base unit and density match? |
| **Layout** | Grid approach, max content width, border-radius scale? |
| **Motion** | Easing and duration within specified ranges? |

## 3. AI slop detection

**Instant FAIL if any of these patterns appear:**

1. Purple/violet/indigo gradient backgrounds
2. 3-column feature grid with icons in colored circles
3. Icons in colored circles as section decoration
4. Centered everything with uniform spacing
5. Uniform bubbly border-radius on every element
6. Decorative blobs, floating circles, wavy SVG dividers
7. Emoji as design elements
8. Colored left-border on cards
9. Generic hero copy ("Welcome to [X]", "Unlock the power of...")
10. Cookie-cutter section rhythm (hero → 3 features → testimonials → pricing → CTA)

## 4. Visual consistency

Take a screenshot and compare with existing pages:

```bash
google-chrome --headless --screenshot=.mpm/data/reviews/{task-id}-design.png --window-size=1400,900 <url>
```

Check:
- Does this page look like it belongs to the same app?
- Consistent header/footer/navigation style?
- Same spacing rhythm as other pages?
- Same button/card/form component styles?

## 5. Component patterns

- New components: do they follow existing vocabulary from DESIGN.md?
- Reused components: are they used consistently (same props/variants)?
- No ad-hoc one-off styles that bypass the design system

## Return format

```
DESIGN REVIEW: PASS/FAIL
Token violations: [count]
AI slop detected: [yes/no — which patterns]
DESIGN.md mismatches: [list]
Issues:
- [issue 1: "Button uses #ccc instead of token --color-primary (#2563eb)" + file:line]
- [issue 2: ...]
Screenshot: .mpm/data/reviews/{task-id}-design.png
```
