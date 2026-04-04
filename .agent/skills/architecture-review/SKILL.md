---
name: architecture-review
description: Conducts a structured Software Architecture Review evaluating cohesion, coupling, SOLID principles, clean architecture patterns, and structural health to identify technical debt and modularity improvements. Produces a scored findings report.
---

# Software Architecture Review

Perform a comprehensive architecture review of the codebase. The review is **findings-only** — identify issues, do NOT apply fixes.

## When to Trigger
- User asks for an "architecture review", "system design check", "coupling audit", or similar.

## Review Workflow

### Phase 1 — Scope & Context (ask user)
Before starting, confirm:
1. **Scope**: Entire system, frontend-only, backend-only?
2. **Goals**: Are we focused on modularity, preparing for scaling, or identifying technical debt?

### Phase 2 — Code Audit
Evaluate source code against **all standards** (see `references/architecture-checklist.md`). For each standard:
- Scan relevant code patterns (Layer boundaries, dependencies, interfaces/abstractions, folder structures, etc.)
- Record findings as `{ID, Standard, Severity, Finding, File(s)}`

#### Severity Rubric
| Level | Icon | Meaning |
|-------|------|---------|
| High | 🔴 | Severe architectural flaw, extreme coupling, cyclical dependency, or high risk of breaking changes |
| Medium | 🟡 | Defeats layered isolation, leaks domain details, tight coupling without immediate breakage |
| Low | 🟢 | Minor inconsistency, opportunity for better abstraction, structural polish |
| Good | ✅ | Positive finding worth preserving (e.g. good decoupling) |

### Phase 3 — Report
Generate a markdown report in `docs/reviews/arch-review-YYYY-MM-DD.md` using the template in `references/report-template.md`. The report MUST include:

1. **Header** — Reviewer, date, scope.
2. **Standards table** — List of all standards used.
3. **Findings by standard** — One table per standard.
4. **Summary scorecard** — Star rating (1–5) per standard.
5. **Overall Architecture Maturity** — Weighted average score.
6. **Top Priority Fixes** — Ordered by severity.
7. **Tracking section** — Blank checkboxes.

### Phase 4 — Handoff
Present the report to the user and await instruction.

## Quality Rules
- Focus on structure, dependencies, and boundaries over syntax tweaks.
- Highlight instances where UI logic, business logic, and database logic bleed into each other.
