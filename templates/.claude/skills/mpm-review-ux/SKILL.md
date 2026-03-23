---
name: mpm-review-ux
description: UX usability review — interaction states, accessibility, edge cases, real user simulation. UI tasks only.
---

# UX Usability Review

You are a hostile user trying to break the interface. Test every interaction, every state, every edge case.

## 1. First impression test

Navigate to the affected page. Before analyzing anything:
- What do you see first? Is it what the user should see first?
- Can you understand what this page does in 3 seconds?
- Is there a clear primary action?

Take a desktop screenshot as evidence.

## 2. Interaction walkthrough

**Click every button. Fill every form. Trigger every state.**

For each interactive element:
- Is it obviously clickable? (cursor changes, hover state exists)
- Does it give feedback when clicked? (loading indicator, state change)
- Does it do what you expect?

```bash
# Take screenshots of key interactions
google-chrome --headless --screenshot=.mpm/data/reviews/{task-id}-interaction.png --window-size=1400,900 <url>
```

## 3. State coverage

For each feature, verify ALL states exist:

| State | Check | FAIL if |
|-------|-------|---------|
| **Empty** | What shows when there's no data? | Blank screen, no guidance |
| **Loading** | What shows while fetching? | Frozen UI, no indicator |
| **Error** | What shows when something fails? | Generic "error", no recovery action |
| **Success** | What shows after completion? | No confirmation, user unsure if it worked |
| **Partial** | What shows with incomplete data? | Broken layout, missing fields |

## 4. Accessibility (CRITICAL)

- **Contrast**: text on background ≥ 4.5:1 ratio
- **Focus states**: tab through the page — can you see where focus is?
- **Alt text**: images have descriptive alt text
- **Labels**: form inputs have visible labels (not just placeholder)
- **Touch targets**: clickable areas ≥ 44px
- **Keyboard nav**: can you complete the task using only keyboard?

## 5. Edge cases

Test with:
- **Long text**: 47-character name, 200-character description
- **Zero results**: empty search, no matching data
- **Many results**: what happens with 100+ items? (pagination? infinite scroll? crash?)
- **Special characters**: `<script>`, `"quotes"`, emoji, unicode
- **Rapid clicks**: double-click submit, spam a button
- **Back button**: does it go where expected? Is state preserved?

## 6. Responsive

```bash
# Mobile screenshot
google-chrome --headless --screenshot=.mpm/data/reviews/{task-id}-mobile.png --window-size=375,812 <url>

# Tablet screenshot
google-chrome --headless --screenshot=.mpm/data/reviews/{task-id}-tablet.png --window-size=768,1024 <url>
```

Check:
- No horizontal scroll on mobile
- Text is readable without zooming
- Touch targets are large enough
- Content priority makes sense (most important first)

## 7. Pre-delivery checklist (from ui-ux-pro-max guidelines)

- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation
- [ ] `prefers-reduced-motion` respected
- [ ] No emojis used as icons

## Return format

```
UX REVIEW: PASS/FAIL
Issues:
- [issue 1: what's wrong + screenshot evidence + how to fix]
- [issue 2: ...]
Screenshots:
- .mpm/data/reviews/{task-id}-desktop.png
- .mpm/data/reviews/{task-id}-mobile.png
```

**Screenshots are mandatory.** No screenshots = automatic FAIL of this review.
