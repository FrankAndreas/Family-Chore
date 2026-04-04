---
name: backend-review
description: Conducts a structured Backend Code Review focusing on FastAPI best practices, asynchronous performance, data validation, error handling, and database interaction. Produces a scored findings report with prioritised fixes.
---

# Backend Systems Review

Perform a comprehensive backend systems review of the codebase. The review is **findings-only** — identify issues, do NOT apply fixes.

## When to Trigger
- User asks for a "backend review", "API audit", "FastAPI check", or similar.
- User mentions reviewing specific API endpoints, background tasks, or database interactions for quality.

## Review Workflow

### Phase 1 — Scope & Context (ask user)
Before starting, confirm:
1. **Scope**: Entire backend, or specific router(s)/service(s)?
2. **Focus areas**: Any specific concerns (performance, database queries, typing)?

### Phase 2 — Code Audit
Read the target source files and evaluate against **all standards** (see `references/backend-checklist.md`). For each standard:
- Scan relevant code patterns (Router declarations, Dependency Injection, SQLAlchemy sessions, Pydantic schemas, etc.)
- Record findings as `{ID, Standard, Severity, Finding, File(s)}`

#### Severity Rubric
| Level | Icon | Meaning |
|-------|------|---------|
| High | 🔴 | Causes runtime exceptions, severe performance degradation, or data corruption |
| Medium | 🟡 | Code smell, edge case bug, or notable departure from standard patterns |
| Low | 🟢 | Style issue, minor optimization, or best-practice gap |
| Good | ✅ | Positive finding worth preserving |

### Phase 3 — Report
Generate a markdown report in `docs/reviews/backend-review-YYYY-MM-DD.md` using the template in `references/report-template.md`. The report MUST include:

1. **Header** — Reviewer, date, scope, app type.
2. **Standards table** — List of all standards used.
3. **Findings by standard** — One table per standard with ID, severity, finding, file(s). Include ✅ positive findings too.
4. **Summary scorecard** — Star rating (1–5) per standard with key notes.
5. **Overall Backend Maturity** — Weighted average score.
6. **Top Priority Fixes** — Ordered by severity × impact, linking finding IDs.
7. **Tracking section** — Blank checkboxes for each fix, ready for progress tracking.

### Phase 4 — Handoff
Present the report artifact to the user. Highlight the top priority fixes and ask if they have questions. Do NOT start fixing issues unless explicitly asked.

## Quality Rules
- Every finding must reference specific file(s) and line ranges where possible.
- Include at least one ✅ positive finding per standard where applicable.
- Keep findings actionable: state *what* is wrong and *why* it matters.
- Load `references/backend-checklist.md` for the detailed checklist before starting.
