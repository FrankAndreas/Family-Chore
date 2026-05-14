---
name: frontend-review
description: Conducts a structured Frontend Code Review focusing on React best practices, Hook dependency management, state architecture, and bundle optimization. Produces a scored findings report with prioritised fixes.
---

# Frontend Systems Review

Perform a comprehensive frontend systems review of the codebase. The review is **findings-only** — identify issues, do NOT apply fixes.

## When to Trigger
- User asks for a "frontend review", "React audit", "component check", or similar.
- User mentions reviewing specific React components, hooks, or state management for quality.

## Review Workflow

### Phase 1 — Scope & Context (ask user)
Before starting, confirm:
1. **Scope**: Entire frontend, or specific component(s)/page(s)?
2. **Focus areas**: Any specific concerns (re-renders, state management, bundle size)?

### Phase 2 — Code Audit
Read the target source files and evaluate against **all standards** (see `references/frontend-checklist.md`). For each standard:
- Scan relevant code patterns (React Hooks, Context API/Redux, Component structure, CSS-in-JS/Tailwind, etc.)
- Record findings as `{ID, Standard, Severity, Finding, File(s)}`

#### Severity Rubric
| Level | Icon | Meaning |
|-------|------|---------|
| High | 🔴 | Causes infinite loops, severe memory leaks, or broken core functionality |
| Medium | 🟡 | Unnecessary re-renders, stale closures, or notable departure from standard patterns |
| Low | 🟢 | Style issue, minor optimization, or best-practice gap |
| Good | ✅ | Positive finding worth preserving |

### Phase 3 — Report
Generate a markdown report in `docs/reviews/frontend-review-YYYY-MM-DD.md` using the template in `references/report-template.md`. The report MUST include:

1. **Header** — Reviewer, date, scope, app type.
2. **Standards table** — List of all standards used.
3. **Findings by standard** — One table per standard with ID, severity, finding, file(s). Include ✅ positive findings too.
4. **Summary scorecard** — Star rating (1–5) per standard with key notes.
5. **Overall Frontend Maturity** — Weighted average score.
6. **Top Priority Fixes** — Ordered by severity × impact, linking finding IDs.
7. **Tracking section** — Blank checkboxes for each fix, ready for progress tracking.

### Phase 4 — Handoff
Present the report artifact to the user. Highlight the top priority fixes and ask if they have questions. Do NOT start fixing issues unless explicitly asked.

## Quality Rules
- Every finding must reference specific file(s) and line ranges where possible.
- Include at least one ✅ positive finding per standard where applicable.
- Keep findings actionable: state *what* is wrong and *why* it matters.
- Load `references/frontend-checklist.md` for the detailed checklist before starting.
