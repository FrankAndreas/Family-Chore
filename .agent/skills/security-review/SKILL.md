---
name: security-review
description: Conducts a structured Security Code Review aligned with the OWASP API Security Top 10 to identify vulnerabilities in authorization, authentication, data handling, and configuration. Produces a scored findings report.
---

# Security Systems Review

Perform a comprehensive security review of the codebase. The review is **findings-only** — identify issues, do NOT apply fixes.

## When to Trigger
- User asks for a "security review", "vulnerability audit", "OWASP check", or similar.

## Review Workflow

### Phase 1 — Scope & Context (ask user)
Before starting, confirm:
1. **Scope**: Entire system, specific endpoints, or frontend?
2. **Focus**: Any specific concerns like JWT handling, BOLA/IDOR, injections?

### Phase 2 — Code Audit
Evaluate source code against the **OWASP standards** (see `references/security-checklist.md`). For each standard:
- Scan relevant code patterns (Auth middlewares, Pydantic/Data validation, endpoints using IDs, CORS configs, secrets usage).
- Record findings as `{ID, Standard, Severity, Finding, File(s)}`

#### Severity Rubric
| Level | Icon | Meaning |
|-------|------|---------|
| High | 🔴 | Exploitable vulnerability that exposes data or allows unauthorized actions (e.g. BOLA, hardcoded secrets, injection) |
| Medium | 🟡 | Missing defense-in-depth, weak tokens, too broad CORS, missing rate limits |
| Low | 🟢 | Configuration tweak, outdated dependency, header missing |
| Good | ✅ | Secure pattern properly applied (e.g. good BOLA check, secure hashing) |

### Phase 3 — Report
Generate a markdown report in `docs/reviews/security-review-YYYY-MM-DD.md` using the template in `references/report-template.md`. The report MUST include:

1. **Header** — Reviewer, date, scope.
2. **Standards table** — List of all standards used.
3. **Findings by standard** — One table per standard.
4. **Summary scorecard** — Star rating (1–5) per standard.
5. **Overall Security Posture** — Weighted average score.
6. **Top Priority Fixes** — Ordered by severity.
7. **Tracking section** — Blank checkboxes.

### Phase 4 — Handoff
Present the report to the user and await instruction. Warn user about high severity issues immediately.
