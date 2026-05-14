---
name: test-review
description: Conducts a structured QA and Test Code Review focusing on test coverage, mocking strategies, assertion quality, and reliability. Produces a scored findings report with prioritised fixes.
---

# Test & QA Systems Review

Perform a comprehensive testing systems review of the codebase. The review is **findings-only** — identify issues, do NOT apply fixes.

## When to Trigger
- User asks for a "test review", "QA audit", "test suite check", or similar.
- User mentions reviewing test files, mock strategies, or fixing flaky tests.

## Review Workflow

### Phase 1 — Scope & Context (ask user)
Before starting, confirm:
1. **Scope**: Entire test suite, specific feature tests, frontend vs backend?
2. **Focus areas**: Flaky tests, mocking strategies, test coverage?

### Phase 2 — Code Audit
Read the target source files and evaluate against **all standards** (see `references/test-checklist.md`). For each standard:
- Scan relevant code patterns (Pytest fixtures, Jest/Vitest setups, Mocking libraries, Assertions)
- Record findings as `{ID, Standard, Severity, Finding, File(s)}`

#### Severity Rubric
| Level | Icon | Meaning |
|-------|------|---------|
| High | 🔴 | Flaky tests, false positives (tests that always pass), or completely missing critical coverage |
| Medium | 🟡 | Over-mocking (testing implementation rather than behavior), slow tests |
| Low | 🟢 | Assertion clarity, setup/teardown hygiene, naming conventions |
| Good | ✅ | Positive finding worth preserving |

### Phase 3 — Report
Generate a markdown report in `docs/reviews/test-review-YYYY-MM-DD.md` using the template in `references/report-template.md`. The report MUST include:

1. **Header** — Reviewer, date, scope, app type.
2. **Standards table** — List of all standards used.
3. **Findings by standard** — One table per standard with ID, severity, finding, file(s).
4. **Summary scorecard** — Star rating (1–5) per standard.
5. **Overall QA Maturity** — Weighted average score.
6. **Top Priority Fixes** — Ordered by severity × impact.

### Phase 4 — Handoff
Present the report artifact to the user. Highlight the top priority fixes. Do NOT start fixing issues unless explicitly asked.

## Quality Rules
- Keep findings actionable.
- Load `references/test-checklist.md` for the detailed checklist before starting.
