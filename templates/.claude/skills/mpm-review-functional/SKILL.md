---
name: mpm-review-functional
description: Verify that the implementation actually works. Run verification methods, test unhappy paths, check for silent errors.
---

# Functional Review

Verify the implementation actually does what the task's `goal` says. Not "similar to" — exactly.

## Do not trust the dev's claim. Run everything yourself.

### 1. Run task verification

Execute every verification method listed in the task's `verification` field. Record pass/fail for each.

### 2. Test the running app

If the task involves a running service:
```bash
# Find the app
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || \
curl -s -o /dev/null -w "%{http_code}" http://localhost:5100 2>/dev/null || \
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null
```

### 3. Test unhappy paths

For each feature the task implements, test:
- **Bad input**: empty string, null, wrong type, too long, special characters
- **Missing data**: what happens when the data doesn't exist?
- **Error conditions**: network timeout, server error, permission denied
- **Concurrent access**: if applicable, what happens with simultaneous requests?

### 4. Check for silent errors

```bash
# Check console/logs for errors
# For web apps:
google-chrome --headless --screenshot=/dev/null --window-size=1,1 <url> 2>&1 | grep -i error || true

# For Python:
python3 -W all <script> 2>&1 | grep -iE 'error|warning|exception' || true
```

### 5. Verify data flow

If the task involves data persistence:
- Create → verify it's stored
- Read → verify it returns the right data
- Update → verify the change persists
- Delete → verify it's actually gone

## Return format

```
FUNCTIONAL REVIEW: PASS/FAIL
Issues:
- [issue 1: what's wrong + where + how to fix]
- [issue 2: ...]
Evidence:
- [curl output, test results, screenshots, etc.]
```
