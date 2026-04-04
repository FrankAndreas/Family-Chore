---
name: ux-review
description: Conducts a structured UX design review of frontend code against 12 industry standards (Nielsen heuristics, WCAG 2.1 AA, responsive design, i18n, component architecture, etc). Produces a scored findings report with prioritised fixes.
---

# UX Design Review

Perform a comprehensive UX review of the frontend codebase. The review is **findings-only** — identify issues, do NOT apply fixes.

## When to Trigger
- User asks for a "UX review", "usability audit", "accessibility check", "design review", or similar.
- User mentions reviewing a specific component or page for UX quality.

## Review Workflow

### Phase 1 — Scope & Context (ask user)
Before starting, confirm:
1. **Scope**: Entire frontend, or specific component(s)/page(s)?
2. **App context**: What type of app, who are the users? (Skip if already known from codebase.)
3. **Focus areas**: Any specific concerns (accessibility, mobile, i18n)?

### Phase 2 — Code Audit
Read the target source files and evaluate against **all 12 standards** (see `references/standards-checklist.md`). For each standard:
- Scan relevant code patterns (ARIA attrs, media queries, i18n calls, component size, CSS tokens, etc.)
- Record findings as `{ID, Standard, Severity, Finding, File(s)}`

#### Severity Rubric
| Level | Icon | Meaning |
|-------|------|---------|
| High | 🔴 | Blocks accessibility, breaks core UX, or violates a hard standard |
| Medium | 🟡 | Degrades experience noticeably but has a workaround |
| Low | 🟢 | Polish item, best-practice gap, or minor inconsistency |
| Good | ✅ | Positive finding worth preserving |

### Phase 3 — Visual Audit (browser)
Use the **browser subagent** to visually inspect the running app:
1. Navigate key user flows (login, dashboard, main features).
2. Resize viewport to mobile (375px), tablet (768px), desktop (1440px).
3. Check: visual hierarchy, spacing, contrast, responsive layout, loading states, error states.
4. Capture screenshots of notable issues for the report.

### Phase 4 — Report
Generate a markdown report in `docs/reviews/ux-review-YYYY-MM-DD.md` using the template in `references/report-template.md`. The report MUST include:

1. **Header** — Reviewer, date, scope, app type.
2. **Standards table** — List of all 12 standards used.
3. **Findings by standard** — One table per standard with ID, severity, finding, file(s). Include ✅ positive findings too.
4. **Summary scorecard** — Star rating (1–5) per standard with key notes.
5. **Overall UX maturity** — Weighted average score.
6. **Top 5 priority fixes** — Ordered by severity × impact, linking finding IDs.
7. **Tracking section** — Blank checkboxes for each fix, ready for progress tracking.

### Phase 5 — Handoff
Present the report artifact to the user. Highlight:
- The overall score
- The top 5 priority fixes
- Any questions or ambiguous findings that need user input

Do NOT start fixing issues unless explicitly asked.

## Quality Rules
- Every finding must reference specific file(s) and line ranges where possible.
- Include at least one ✅ positive finding per standard where applicable — acknowledge good work.
- Keep findings actionable: state *what* is wrong and *why* it matters, not just the rule violated.
- If a standard is fully satisfied, still list it with a ✅ row.
- Load `references/standards-checklist.md` for the detailed per-standard checklist before starting the audit.
