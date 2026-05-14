---
name: performance-review
description: Conducts a structured Performance and Scalability Review focusing on caching, asynchronous processing, network efficiency, and rendering bottlenecks. Produces a scored findings report with prioritised fixes.
---

# Performance & Scalability Review

Perform a comprehensive performance review of the codebase. The review is **findings-only** — identify issues, do NOT apply fixes.

## When to Trigger
- User asks for a "performance review", "load audit", "speed check", or similar.
- User mentions optimizing API response times, database queries, or frontend load times.

## Review Workflow

### Phase 1 — Scope & Context (ask user)
Before starting, confirm:
1. **Scope**: Entire stack, backend API, or frontend delivery?
2. **Focus areas**: Database bottlenecks, memory leaks, payload sizes, Core Web Vitals?

### Phase 2 — Code Audit
Read the target source files and evaluate against **all standards** (see `references/performance-checklist.md`). For each standard:
- Scan relevant code patterns (SQL queries, API payloads, asynchronous tasks, caching headers)
- Record findings as `{ID, Standard, Severity, Finding, File(s)}`

#### Severity Rubric
| Level | Icon | Meaning |
|-------|------|---------|
| High | 🔴 | O(N^2) or worse algorithms, N+1 query bugs, main thread blocking, memory leaks |
| Medium | 🟡 | Missing pagination, large uncompressed payloads, lack of caching |
| Low | 🟢 | Minor asset optimization, micro-optimizations |
| Good | ✅ | Positive finding worth preserving |

### Phase 3 — Report
Generate a markdown report in `docs/reviews/performance-review-YYYY-MM-DD.md` using the template in `references/report-template.md`. The report MUST include:

1. **Header** — Reviewer, date, scope, app type.
2. **Standards table** — List of all standards used.
3. **Findings by standard** — One table per standard with ID, severity, finding, file(s).
4. **Summary scorecard** — Star rating (1–5) per standard.
5. **Overall Performance Maturity** — Weighted average score.
6. **Top Priority Fixes** — Ordered by severity × impact.

### Phase 4 — Handoff
Present the report artifact to the user. Highlight the top priority fixes. Do NOT start fixing issues unless explicitly asked.

## Quality Rules
- Keep findings actionable. Focus on algorithmic efficiency and data transfer costs.
- Load `references/performance-checklist.md` for the detailed checklist before starting.
